import logging, random
import sqlite3
import random
import time
import table
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config, chat, exam, create

instructions_for_filling_the_dictionary = 'Enter words in the format \n word == word / word \n You can add values separated by slashes.'
T = table.Table()

def get_chat(update):
    chatId = int(update["message"]["chat"]["id"])
    if chat.has_chat(chatId):
        return chat.get_chat(chatId)
    return chat.new_chat(chatId,
                         update["message"]["chat"]["first_name"],
                         update["message"]["chat"]["username"])


def send_message(bot, update, text):
    update.message.reply_text(text)

def start(bot, update):
    ch = get_chat(update)
    update.message.reply_text("Hi %s, i'm your bot" % ch.firstName)
    update.message.reply_text("If this is your first visit to me, you can call the /help command. You will receive tips for using the bot.")
    #update.message.reply_text("firstName: " + ch.firstName)
    #if ch.userName: update.message.reply_text("userName: " + ch.userName)
    #update.message.reply_text(("KKRRHH".rstrip("H")).lstrip("K"))
    #word = ("   ".rstrip(" ")).lstrip(" ")
    #if (word == ""): update.message.reply_text("+")

def end(bot, update):
    ch = get_chat(update)
    if (ch.status == "create"):
        ce = ch._created_exam
        #T.insert_into_table(ce.words())
        #ce.reset()
        update.message.reply_text("you finished creating " + ce.getName())
    elif (ch.status == "train"):
        tr = ch._trained_exam
        update.message.reply_text("you finished training " + tr.getName())
    elif (ch.status == "exam"):
        ex = ch._current_exam
        update.message.reply_text("you have finished examining " + ex.getName())
    elif (ch.status == "delete"):
        die = ch._delete_in_exam
        update.message.reply_text("you have finished taking the words from exam " + die.getName())
    elif (ch.status == "add"):
        ate = ch._add_to_exam
        update.message.reply_text("you have finished adding words to " + ate.getName())
    else:
        update.message.reply_text("no active actions")
    ch.end()
    #?

def exists(update, exam_name): #проверка того, есть ли название среди названий экзаменов в EXAM(но название может быть в EXAM_OWNER)
    global T
    ch = get_chat(update)
    if (T.exist_in_the_table(exam_name)):
        if (T.exam_owner_id(exam_name) == ch._chatId):
            update.message.reply_text("The action will not be completed. You already have an exam named " + exam_name)
        else:
            update.message.reply_text("The action will not be completed. The exam name " + exam_name + " is already taken by another user.")
        return True
    return False

def multiple_actions_error_output(update):
    ch = get_chat(update)
    if (ch.status == "create"):
        ce = ch._created_exam
        update.message.reply_text("You cannot do this action because you are creating an exam called " + ce.getName() + ". You can finish creating an exam using the command /end")
    elif (ch.status == "train"):
        tr = ch._trained_exam
        update.message.reply_text("You cannot do this action because you are training for an exam called " + tr.getName() + ". You can finish training with the command /end")
    elif (ch.status == "exam"):
        ex = ch._current_exam
        update.message.reply_text("You cannot do this action because you are being tested. You can end the exam using the /end command")
    elif (ch.status == "delete"):
        die = ch._delete_in_exam
        update.message.reply_text("You cannot do this action because you are deleting data from exam " + die.getName() + ". You can end the uninstall with the /end command")
    elif (ch.status == "add"):
        ate = ch._add_to_exam
        update.message.reply_text("You cannot do this action because you are adding data to exam " + ate.getName() + ". You can finish adding with the /end command")
    else:
        update.message.reply_text("no active actions")

def new_exam(bot, update):
    global instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""): #в случае, если имя экззамена пустое
        update.message.reply_text("No correct. /new_exam <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (exists(update, exam_name)): #в случае если такой экзамен уже существует
        return
    ch.create_exam(exam_name)
    T.add_exam_name(exam_name, ch._chatId)
    send_message(bot, update, "You start creating an exam " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def train_exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch.status is None):
        multiple_actions_error_output(update)
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /train_exam <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (not T.exists(exam_name) and T.exist_in_the_table(exam_name)):
        update.message.reply_text("Аction cannot be performed. The exam exists, but it is empty.")
        return
    if (not T.exist_in_the_table(exam_name)):
        update.message.reply_text("the " + exam_name + " exam does not exist")
        return
    ch.train_exam(exam_name, T.list_words(exam_name))
    update.message.reply_text(ch._trained_exam.getNext_word())
    update.message.reply_text("/all_meanings")

def next_word(bot, update):
    ch = get_chat(update)
    if (ch.status != "train"):
        update.message.reply_text("This command only works in training mode.")
        multiple_actions_error_output(update)
        return
    tr = ch._trained_exam
    update.message.reply_text(tr.getNext_word())
    update.message.reply_text("/all_meanings")

def all_meanings(bot, update):
    ch = get_chat(update)
    if (ch.status != "train"):
        update.message.reply_text("This command only works in training mode.")
        multiple_actions_error_output(update)
        return
    tr = ch._trained_exam
    list_all_meanings = tr.getAll_meanings()
    ans = ""
    for elem in list_all_meanings:
        ans += elem + " / "
    update.message.reply_text(ans)
    update.message.reply_text("/next_word")

def exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch.status is None):
        multiple_actions_error_output(update)
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /exam <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (not T.exists(exam_name) and T.exist_in_the_table(exam_name)):
        update.message.reply_text("Аction cannot be performed. The exam exists, but it is empty.")
        return
    if (not T.exist_in_the_table(exam_name)):
        update.message.reply_text("the " + exam_name + " exam does not exist")
        return
    ch.exam(exam_name, T.list_words(exam_name))
    update.message.reply_text(ch._current_exam.startExam())

def repeat_exam(bot, update):
    ch = get_chat(update)
    ex = ch._current_exam
    if (ch.status != "exam"):
        update.message.reply_text("This command only works in exam mode.")
        multiple_actions_error_output(update)
        return
    if (not ex._finish):
        update.message.reply_text("You cannot use this command because you have not finished the previous test .")
        update.message.reply_text("If you want to finish the test and find out the results, then call the command /finish.")
        return
    update.message.reply_text(ex.startExam())

def finish(bot, update):
    ch = get_chat(update)
    if (ch.status != "exam"):
        update.message.reply_text("This command only works in exam mode.")
        multiple_actions_error_output(update)
        return
    ex = ch._current_exam
    if (ex._finish):
        update.message.reply_text("You're not taking an exam right now.")
        update.message.reply_text("If you want to pass another test for the exam " + ex._exam_name + ", then call the command /repeat_exam")
        return
    text = ex.getResult()
    update.message.reply_text(text)
    send_message(bot, update, "If you want to exit the exam mode, then call the command /end")

#скорее устаревшая функция
def actions(bot, update):
    ch = get_chat(update)
    text = ch.actions()
    if (text == ""):
        update.message.reply_text("no action")
    else:
        update.message.reply_text(text)

#скорее устаревшая функция
def finish_all_actions(bot, update):
    ch = get_chat(update)
    text = ch.finish_all_actions()
    update.message.reply_text("No more action")

def add_to_exam(bot, update):
    global T, instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch.status is None):
        multiple_actions_error_output(update)
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /add_to_exam <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (not T.exist_in_the_table(exam_name)):
        update.message.reply_text("Аction cannot be performed. The exam exists, but it is empty.")
        return
    if (T.exam_owner_id(exam_name) != ch._chatId and not ch._admin_mode):
        update.message.reply_text("You cannot edit this exam because you are not the creator of it.")
        return
    ch.add_to_exam(exam_name)
    send_message(bot, update, "You start to add to the " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def delete_in_exam(bot, update):
    global T, instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch.status is None):
        multiple_actions_error_output(update)
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /delete_in_exam <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (not T.exists(exam_name) and T.exist_in_the_table(exam_name)):
        update.message.reply_text("Аction cannot be performed. The exam exists, but it is empty.")
        return
    if (not T.exist_in_the_table(exam_name)):
        update.message.reply_text("the " + exam_name + " exam does not exist")
        return
    if (T.exam_owner_id(exam_name) != ch._chatId and not ch._admin_mode):
        update.message.reply_text("You cannot edit this exam because you are not the creator of it.")
        return
    ch.delete_in_exam(exam_name)
    send_message(bot, update, "You start deleting words from the " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def delete_exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch.status is None):
        multiple_actions_error_output(update)
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /delete_exam <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (not T.exist_in_the_table(exam_name)):
        update.message.reply_text("the " + exam_name + " exam does not exist")
        return
    if (T.exam_owner_id(exam_name) != ch._chatId and not ch._admin_mode):
        update.message.reply_text("You cannot edit this exam because you are not the creator of it.")
        return
    T.remove_exam(exam_name)
    send_message(bot, update, "removed " + exam_name)

def show_table(bot, update):
    send_message(bot, update, "No.")


def list_exams(bot, update):
    global T
    ch = get_chat(update)
    list_name = T.list_exams()
    send_message(bot, update, "all exam titles:")
    for elem in list_name:
        if (elem[1] == ch._chatId):
            send_message(bot, update, elem[0] + " - This is your exam")
        else:
            send_message(bot, update, elem[0])

def list_words(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /list_words <name>")
        return
    if (exam_name.find(" ") != -1): #в случае, если имя содержит пробел
        update.message.reply_text("No correct. The title should not contain spaces. Enter /new_exam <name> again")
        return
    if (not T.exists(exam_name) and T.exist_in_the_table(exam_name)):
        update.message.reply_text("The exam exists, but it is empty.")
        return
    if (not T.exist_in_the_table(exam_name)):
        update.message.reply_text("the " + exam_name + " exam does not exist")
        return
    list_words = T.list_words(exam_name)

    send_message(bot, update, "all word == word pairs in " + exam_name + ":")
    for elem in list_words:
        send_message(bot, update, elem[0] + " == " + elem[1])


def change_name(bot, update):
    global T
    ch = get_chat(update)
    names = list(get_text_in_request(update.message.text).split())
    if (not ch.status is None):
        multiple_actions_error_output(update)
        return
    if (len(names) < 2 or len(names) > 2):
        update.message.reply_text("No correct. /change_name <old_name> <new_name>")
        return
    if (not T.exist_in_the_table(names[0])):
        update.message.reply_text("the " + names[0] + " exam does not exist")
        return
    if (T.exam_owner_id(names[0]) != ch._chatId and not ch._admin_mode):
        update.message.reply_text("You cannot edit this exam because you are not the creator of it.")
        return
    if (exists(update, names[1])): #в случае если такой экзамен уже существует
        return
    T.change_name(names[0], names[1])
    update.message.reply_text("the exam has been renamed from " + names[0] + " to " + names[1])

def commands(bot, update): #вывод всех команд
    send_message(bot, update, '''
- /start
- /end
- /new_exam <exam_name>
- /train_exam <exam_name>
- - - /next_word  
- - - /all_meanings
- /exam <exam_name>
- - - /repeat_exam
- - - /finish
- /add_to_exam <exam_name>
- /change_name <name> <new_name>
- /delete_in_exam <exam_name>
- /delete_exam <exam_name>
- /list_exams 
- /list_words <exam_name>
- /status
- /commands
- /help    
    ''')


def help(bot, update):  # вывод всех команд
    send_message(bot, update, '''
/start - hello command
 /end - command ending any mode. (exam creation, training, etc.)
 /new_exam <exam_name> - command that creates an exam. (starts the creation mode)
 /train_exam <exam_name> - command that starts the training mode.
  /next_word - command that gets the word question. (only in training mode)
  /all_meanings - command that gets answers to the word question. (only in training mode)
 /exam <exam_name> - command that starts testing. (starts exam mode)
  /repeat_exam - command that launches a new test in the same exam. (only in exam mode)
  /finish - command that gets test results prematurely. (only in exam mode)
 /add_to_exam <exam_name> - command that starts the mode of adding data to the exam.
 /change_name <old_name> <new_name> - command that allows you to change the name of the exam.
 /delete_in_exam <exam_name> - command that starts the mode of deleting data from the exam.
 /delete_exam <exam_name> - command that deletes the exam.
 /list_exams - displaying a list of all exams from a common base.
 /list_words <exam_name> - output of all data from the exam.
 /status - current bot mode.
 /commands - list of all commands.
 /help - a list of all commands with a short explanation to them.
        ''')

def get_message(bot, update): #при получении любой незнакомой функции или любого текста
    ch = get_chat(update)
    client_answer = update.message.text #сообщение от клиента
    if ch.status == "exam": #получаем ответ от клиента. Делаем 1 шаг экзамена.
        ex = ch._current_exam #объект - рассматриваемый экзамен. тип:exam.
        if (ex._finish):
            send_message(bot, update, "You are not taking the test now.")
            send_message(bot, update, "If you want to pass another test for the " + ex._exam_name + " exam, then call the command  /repeat_exam")
            send_message(bot, update, "If you want to exit the exam mode, then call the command /end")
            return
        response = ex.addAnswer(client_answer) #проводим шаг экзамена. Получаем следующий вопрос или ответы.
        send_message(bot, update, response)
        if (ex._finish): send_message(bot, update, "If you want to exit the exam mode, then call the command /end")
    elif ch.status == "create":
        ce = ch._created_exam
        ans = client_answer
        ans.replace(" ", "")
        index_separator = ans.find("==")
        if (index_separator == -1 or index_separator == 0 or index_separator == len(ans) - 1 or ans.find("//") != -1 or ans.find("/=") != -1 or ans.find("=/") != -1 or ans.find("===") != -1):
            send_message(bot, update, "Not correct. " + instructions_for_filling_the_dictionary)
            send_message(bot, update, "If you want to finish creating an exam, then call the command /end")
            return
        ce.parse_and_add(client_answer)
        T.insert_into_table(ce.words())
        ce.reset()
        send_message(bot, update, "added in %s" % ce.getName())
    elif ch.status == "train":
        response = "train, do not accept text"
        send_message(bot, update, response)
        send_message(bot, update, "If you want to end the training, then call the command /end")
    elif ch.status == "delete":
        die = ch._delete_in_exam
        ans = client_answer
        ans.replace(" ", "")
        index_separator = ans.find("==")
        if (index_separator == -1 or index_separator == 0 or index_separator == len(ans) - 1 or ans.find("//") != -1 or ans.find("/=") != -1 or ans.find("=/") != -1 or ans.find("===") != -1):
            send_message(bot, update, "Not correct. " + instructions_for_filling_the_dictionary)
            send_message(bot, update, "If you want to complete the deletion, then call the command /end")
            return
        die.parse_and_delete(client_answer)
        response = T.check_entry_into_the_exam(die.words())
        T.remove_from_table(die.words())
        die.reset()
        send_message(bot, update, "deleting from %s" % die.getName())
    elif ch.status == "add":
        ate = ch._add_to_exam
        ans = client_answer
        ans.replace(" ", "")
        index_separator = ans.find("==")
        if (index_separator == -1 or index_separator == 0 or index_separator == len(ans) - 1 or ans.find("//") != -1 or ans.find("/=") != -1 or ans.find("=/") != -1 or ans.find("===") != -1):
            send_message(bot, update, "Not correct. " + instructions_for_filling_the_dictionary)
            send_message(bot, update, "If you want to finish adding, then call the command /end")
            return
        ate.parse_and_add(client_answer)
        T.insert_into_table(ate.words())
        ate.reset()
        send_message(bot, update, "added in %s" % ate.getName())
    else:
        #response = "Your status is unknown: "
        #if (ch.status is None): response += "None"
        #else: response += ch.status
        #send_message(bot, update, response)
        send_message(bot, update, "Action or command not recognized.")
        send_message(bot, update, "The bot is waiting for a command. He has no mod now.")
        send_message(bot, update, "А list of all commands with a short explanation: /help")

def status2(bot, update):
    ch = get_chat(update)
    response = ""
    if (ch._status is None): response += "None"
    else: response += ch._status
    if (ch._admin_mode): response += " +admin mode"
    send_message(bot, update, response)

def admmode(bot, update):
    ch = get_chat(update)
    state = get_text_in_request(update.message.text)
    if (state == "on"):
        ch._admin_mode = True
        send_message(bot, update, "Admin mode is included. This mode is not for public use. When working with an object, you get the same rights as its owner.")
    elif (state == "off"):
        ch._admin_mode = False
        send_message(bot, update, "Admin mode is disabled")


def error(update, context): #в случае вознекновения ошибки она выводится в logger (здесь в поток вывода)
    """Log Errors caused by update."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def get_text_in_request(text): #?
    part = text.split(" ", 1)
    return part[1] if len(part) == 2 else ""

def parametrs_for_updater(): #каждой команде сопоставляется функция
    global mybot

    logging.basicConfig(format='%(message)s', level=logging.INFO)
    updater = Updater(config.telegram_token)
    dispatcher = updater.dispatcher    
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('end', end))
    
    dispatcher.add_handler(CommandHandler('new_exam', new_exam))
    #dispatcher.add_handler(CommandHandler('continue_create_exam', continue_create_exam))
    
    dispatcher.add_handler(CommandHandler('train_exam', train_exam))
    dispatcher.add_handler(CommandHandler('next_word', next_word))
    dispatcher.add_handler(CommandHandler('all_meanings', all_meanings))
    #dispatcher.add_handler(CommandHandler('continue_train', continue_train))
    
    dispatcher.add_handler(CommandHandler('exam', exam))
    dispatcher.add_handler(CommandHandler('repeat_exam', repeat_exam))
    dispatcher.add_handler(CommandHandler('finish', finish))
    #dispatcher.add_handler(CommandHandler('continue_exam', continue_exam))

    dispatcher.add_handler(CommandHandler('delete_in_exam', delete_in_exam))
    #dispatcher.add_handler(CommandHandler('continue_delete_in_exam', continue_delete_in_exam))

    dispatcher.add_handler(CommandHandler('add_to_exam', add_to_exam))
    #dispatcher.add_handler(CommandHandler('continue_add_to_exam', continue_add_to_exam))

    dispatcher.add_handler(CommandHandler('delete_exam', delete_exam))

    dispatcher.add_handler(CommandHandler('actions', actions))
    dispatcher.add_handler(CommandHandler('finish_all_actions', finish_all_actions))

    dispatcher.add_handler(CommandHandler('show_table', show_table))
    dispatcher.add_handler(CommandHandler('list_exams', list_exams))
    dispatcher.add_handler(CommandHandler('list_words', list_words))
    dispatcher.add_handler(CommandHandler('status', status2))
    dispatcher.add_handler(CommandHandler('change_name', change_name))
    dispatcher.add_handler(CommandHandler('commands', commands))
    dispatcher.add_handler(CommandHandler('help', help))

    dispatcher.add_handler(CommandHandler('admmode', admmode))
    
    dispatcher.add_error_handler(error)  #функция, вызываемая в случае ошибки
    
    dispatcher.add_handler(MessageHandler(Filters.text, get_message)) #при получении любого другово сообщения
    
    return updater
   

def main():
    global T
    updater = parametrs_for_updater()
    #T.insert_into_table([("exam1", "car", "автомобиль")])
    #T.insert_into_table([("exam1", "table", "стол")])
    #T.insert_into_table([("exam1", "glass", "стакан")])
    #T.insert_into_table([("exam1", "glass", "cтекло")])
    #T.insert_into_table([("exam2", "word", "слово")])
    updater.start_polling() #внутри цикл, получающий запросы
    updater.idle()

main()

#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/sendMessage?chat_id=151365661&text=Hello
#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/getUpdates
