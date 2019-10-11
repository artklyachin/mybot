import logging, random
import sqlite3
import random
import time
import table
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config, chat, exam, create

instructions_for_filling_the_dictionary = 'Enter words in the format \n word : word, word \n You can add values ​​through comma.'
T = table.Table()
status = "none"

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

def end(bot, update):
    ch = get_chat(update)
    if (ch.status == "create"):
        ce = ch._created_exam
        T.insert_into_table(ce.words())
        ce.reset()
        update.message.reply_text("you finished creating " + ce.getName())
    elif (ch.status == "train"):
        tr = ch._trained_exam
        update.message.reply_text("you finished training " + tr.getName())
        ch.end()
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

def exists(update, exam_name):
    global T
    if (T.exists(exam_name)):
        update.message.reply_text("exam " + exam_name + " already exists")
        return True
    return False

def not_exists(update, exam_name):
    global T
    if (not T.exists(exam_name)):
        update.message.reply_text("the " + exam_name + " exam does not exist")
        return True
    return False

def validation_check_1(update, exam_name):
    ch = get_chat(update)
    if (not ch._created_exam is None and ch._created_exam.getName() == exam_name):
        update.message.reply_text("No action, this exam is being created")
        return True
    if (not ch._trained_exam is None and ch._trained_exam.getName() == exam_name):
        update.message.reply_text("No action, you are training on this exam")
        return True
    flag_in_exam = False
    for elem in ch._exams:
        if (elem.getName() == exam_name):
            flag_in_exam = True
            break
    if (flag_in_exam):
        update.message.reply_text("No action, you are examining for this exam")
    return False

def validation_check_2(update, exam_name):
    ch = get_chat(update)
    if (not ch._created_exam is None and ch._created_exam.getName() == exam_name):
        update.message.reply_text("No action, this exam is being created")
        return True
    if (not ch._add_to_exam is None and ch._add_to_exam.getName() == exam_name):
        update.message.reply_text("No action, now add words to this exam")
        return True
    if (not ch._delete_in_exam is None and ch._delete_in_exam.getName() == exam_name):
        update.message.reply_text("No action, now remove the words from this exam")
        return True
    return False


def new_exam(bot, update):
    global instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch._created_exam is None):
        update.message.reply_text("You can only create one examine. Now you are creating an " + ch._created_exam.getName())
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /new_exam <name>")
        return
    if (exists(update, exam_name)):
        return
    cr = ch.create_exam(exam_name)
    send_message(bot, update, "You start creating an exam " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def continue_create_exam(bot, update):
    global instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    cr = ch._created_exam
    if (cr.getName() is None):
        update.message.reply_text("No exams are being created")
        return
    if (exam_name != ""):
        update.message.reply_text("You can continue to create only the " + cr.getName() + ". Correct: /continue_create_exam")
        return
    ch.status = "create"
    send_message(bot, update, "you continue to create " + cr.getName())
    send_message(bot, update, instructions_for_filling_the_dictionary)

def train_exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch._trained_exam is None):
        update.message.reply_text("You can train on only one exam. You are now training on the " + ch._trained_exam.getName())
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /train_exam <name>")
        return
    if (not_exists(update, exam_name)):
        return
    if (validation_check_2(update, exam_name)):
        return
    ch.train_exam(exam_name, T.list_words(exam_name))
    update.message.reply_text(ch._trained_exam.getNext_word())
    update.message.reply_text("/all_meanings")

def next_word(bot, update):
    ch = get_chat(update)
    if (ch.status != "train"):
        update.message.reply_text("Now do not train on any of the exams.")
        return
    tr = ch._trained_exam
    update.message.reply_text(tr.getNext_word())
    update.message.reply_text("/all_meanings")

def all_meanings(bot, update):
    ch = get_chat(update)
    if (ch.status != "train"):
        update.message.reply_text("You are not being trained.")
        return
    tr = ch._trained_exam
    list_all_meanings = tr.getAll_meanings()
    ans = ""
    for elem in list_all_meanings:
        ans += elem + ", "
    update.message.reply_text(ans)
    update.message.reply_text("/next_word")

def continue_train(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    tr = ch._trained_exam
    if (tr.getName() is None):
        update.message.reply_text("There are no exams you train in")
        return
    if (exam_name != ""):
        update.message.reply_text("You can continue to train only the " + tr.getName() + ". Correct: /continue_train")
        return
    ch.status = "train"
    update.message.reply_text("You continue to train on the " + tr.getName())
    update.message.reply_text(tr.getNext_word())
    update.message.reply_text("/all_meanings")

def exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /exam <name>")
        return
    if (not_exists(update, exam_name)):
        return
    if (validation_check_2(update, exam_name)):
        return
    ch.exam(exam_name, T.list_words(exam_name))
    update.message.reply_text(ch._current_exam.startExam())

def repeat_exam(bot, update):
    ch = get_chat(update)
    if (ch._current_exam is None and ch.status != "exam"):
        update.message.reply_text("The function is available if the current action")
        return
    ex = ch._current_exam
    update.message.reply_text(ex.startExam())

def finish(bot, update):
    ch = get_chat(update)
    if (ch._current_exam is None and ch.status != "exam"):
        update.message.reply_text("The function is available if the current action")
        return
    ex = ch._current_exam
    text = ex.getResult()
    update.message.reply_text(text)

def continue_exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /continue_exam <name>")
        return
    if (not exam_name in ch._exams):
        update.message.reply_text("You have not started the exam for this exam.")
        return
    ch.status = "exam"
    ch._current_exam = ch._exams[exam_name]
    ex = ch._current_exam
    response = ex.getWord()
    if (response is None):
        update.message.reply_text(ex.startExam())
    else:
        update.message.reply_text(response)

def actions(bot, update):
    ch = get_chat(update)
    text = ch.actions()
    if (text == ""):
        update.message.reply_text("None action")
    else:
        update.message.reply_text(text)

def finish_all_actions(bot, update):
    ch = get_chat(update)
    text = ch.finish_all_actions()
    update.message.reply_text("No more action")

def add_to_exam(bot, update):
    global T, instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch._add_to_exam is None):
        update.message.reply_text("You can add words in only one exam. You are now adding words to the " + ch._add_to_exam.getName())
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /add_to_exam <name>")
        return
    if (not_exists(update, exam_name)):
        return
    if (validation_check_1(update, exam_name)):
        return
    if (validation_check_2(update, exam_name)):
        return
    ch.add_to_exam(exam_name)
    send_message(bot, update, "You start to add to the " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def continue_add_to_exam(bot, update):
    global instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    ate = ch._add_to_exam
    if (ate.getName() is None):
        update.message.reply_text("There are no exams where you add words.")
        return
    if (exam_name != ""):
        update.message.reply_text("You can continue to add words only at " + ate.getName() + ". Correct: /continue_add_to_exam")
        return
    ch.status = "add"
    send_message(bot, update, "you continue to add from " + ate.getName())
    send_message(bot, update, instructions_for_filling_the_dictionary)

def delete_in_exam(bot, update):
    global T, instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (not ch._delete_in_exam is None):
        update.message.reply_text("You can delete words in only one exam. You are now deleting words in the " + ch.delete_in_exam.getName())
        return
    if (exam_name == ""):
        update.message.reply_text("No correct. /delete_in_exam <name>")
        return
    if (not_exists(update, exam_name)):
        return
    if (validation_check_1(update, exam_name)):
        return
    if (validation_check_2(update, exam_name)):
        return
    ch.delete_in_exam(exam_name)
    send_message(bot, update, "You start deleting words from the " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def continue_delete_in_exam(bot, update):
    global instructions_for_filling_the_dictionary
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    die = ch._delete_in_exam
    if (die.getName() is None):
        update.message.reply_text("There are no exams from which you delete words")
        return
    if (exam_name != ""):
        update.message.reply_text("You can only delete words from the " + die.getName() + ". Correct: /continue_delete_in_exam")
        return
    ch.status = "delete"
    send_message(bot, update, "you continue to delete from " + die.getName())
    send_message(bot, update, instructions_for_filling_the_dictionary)


def delete_exam(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /delete_exam <name>")
        return
    if (not_exists(update, exam_name)):
        return
    if (validation_check_1(update, exam_name)):
        return
    if (validation_check_2(update, exam_name)):
        return
    T.remove_exam(exam_name)
    send_message(bot, update, "removed " + exam_name)

def show_table(bot, update):
    print("No")

def list_exams(bot, update):
    global T
    list_name = T.list_exams()
    send_message(bot, update, "all exam titles:")
    for elem in list_name:
        send_message(bot, update, elem)

def list_words(bot, update):
    global T
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /list_words <name>")
        return
    if (not_exists(update, exam_name)):
        return
    list_words = T.list_words(exam_name)
    send_message(bot, update, "all word:word pairs in " + exam_name + ":")
    for elem in list_words:
        send_message(bot, update, elem[0] + " : " + elem[1])

def help(bot, update):
    send_message(bot, update, '''
        - /start
        - /end
        - /new_exam
        - - - /continue_create_exam
        - /train_exam
        - - - /next_word  
        - - - /all_meanings
        - - - /continue_train
        - /exam
        - - - /repeat_exam
        - - - /finish
        - - - /continue_exam
        - /add_to_exam
        - - - /continue_add_to_exam
        - /delete_in_exam
        - - - /continue_delete_in_exam
        - /delete_exam
        - /actions
        - /finish_all_actions
        - /show_table no
        - /list_exams
        - /list_words
        - /help
    ''')

def get_message(bot, update):
    ch = get_chat(update)
    client_answer = update.message.text
    if ch.status == "exam":
        ex = ch._current_exam
        if ex is None:
            send_message(bot, update, "Error. You are not in exam")
            return
        response = ex.addAnswer(client_answer)
        #if (not type(response) is list):
        send_message(bot, update, response)
        #else:
        #    for elem in response:
        #        send_message(bot, update, elem)
        #    update.message.reply_text("You can /repeat_exam")
    elif ch.status == "create":
        ce = ch._created_exam
        if not ce:
            send_message(bot, update, "Error. You are not creating a new exam")
            return
        ans = client_answer
        ans.replace(" ", "")
        ans.replace(";", ",")
        index_separator = ans.find(":")
        if (index_separator == -1 or index_separator == 0 or index_separator == len(ans) - 1 or ans.find(",,") != -1):
            send_message(bot, update, instructions_for_filling_the_dictionary)
            return
        ce.parse_and_add(client_answer)
        T.insert_into_table(ce.words())
        ce.reset()
        send_message(bot, update, "added in %s" % ce.getName())
    elif ch.status == "train":
        response = "train, do not accept text"
        send_message(bot, update, response)
    elif ch.status == "delete":
        die = ch._delete_in_exam
        if not die:
            send_message(bot, update, "Error. You are not deleting word from exam")
            return
        ans = client_answer
        ans.replace(" ", "")
        ans.replace(";", ",")
        index_separator = ans.find(":")
        if (index_separator == -1 or index_separator == 0 or index_separator == len(ans) - 1 or ans.find(",,") != -1):
            send_message(bot, update, instructions_for_filling_the_dictionary)
            return
        die.parse_and_delete(client_answer)
        response = T.check_entry_into_the_exam(die.words())
        if (not response is None):
            die.reset()
            send_message(bot, update, "In exam " + response[0] + " there is no " + response[1] + " : " + response[2])
            return
        response = T.remove_from_table(die.words())
        die.reset()
        send_message(bot, update, "deleting from %s" % die.getName())
    elif ch.status == "add":
        ate = ch._add_to_exam
        ans = client_answer
        ans.replace(" ", "")
        ans.replace(";", ",")
        index_separator = ans.find(":")
        if (index_separator == -1 or index_separator == 0 or index_separator == len(ans) - 1 or ans.find(",,") != -1):
            send_message(bot, update, instructions_for_filling_the_dictionary)
            return
        ate.parse_and_add(client_answer)
        T.insert_into_table(ate.words())
        ate.reset()
        send_message(bot, update, "added in %s" % ate.getName())
    else:
        response = "Your status is unknown: " + ch.status
        send_message(bot, update, response)


    
def error(update, context):
    """Log Errors caused by update."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def get_text_in_request(text):
    part = text.split(" ", 1)
    return part[1] if len(part) == 2 else ""
    
def parametrs_for_updater():
    global mybot

    logging.basicConfig(format='%(message)s', level=logging.INFO)
    updater = Updater(config.telegram_token)
    dispatcher = updater.dispatcher    
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('end', end))
    
    dispatcher.add_handler(CommandHandler('new_exam', new_exam))
    dispatcher.add_handler(CommandHandler('continue_create_exam', continue_create_exam))
    
    dispatcher.add_handler(CommandHandler('train_exam', train_exam))
    dispatcher.add_handler(CommandHandler('next_word', next_word))
    dispatcher.add_handler(CommandHandler('all_meanings', all_meanings))
    dispatcher.add_handler(CommandHandler('continue_train', continue_train))
    
    dispatcher.add_handler(CommandHandler('exam', exam))
    dispatcher.add_handler(CommandHandler('repeat_exam', repeat_exam))
    dispatcher.add_handler(CommandHandler('finish', finish))
    dispatcher.add_handler(CommandHandler('continue_exam', continue_exam))

    dispatcher.add_handler(CommandHandler('delete_in_exam', delete_in_exam))
    dispatcher.add_handler(CommandHandler('continue_delete_in_exam', continue_delete_in_exam))

    dispatcher.add_handler(CommandHandler('add_to_exam', add_to_exam))
    dispatcher.add_handler(CommandHandler('continue_add_to_exam', continue_add_to_exam))

    dispatcher.add_handler(CommandHandler('delete_exam', delete_exam))

    #dispatcher.add_handler(CommandHandler('add_in_exam', add_in_exam))

    dispatcher.add_handler(CommandHandler('actions', actions))
    dispatcher.add_handler(CommandHandler('finish_all_actions', finish_all_actions))

    dispatcher.add_handler(CommandHandler('show_table', show_table))
    dispatcher.add_handler(CommandHandler('list_exams', list_exams))
    dispatcher.add_handler(CommandHandler('list_words', list_words))
    dispatcher.add_handler(CommandHandler('help', help))
    
    dispatcher.add_error_handler(error)
    
    dispatcher.add_handler(MessageHandler(Filters.text, get_message))
    
    return updater
   

def main():
    global T
    updater = parametrs_for_updater()
    #T.insert_into_table([("exam1", "car", "автомобиль")])
    #T.insert_into_table([("exam1", "table", "стол")])
    #T.insert_into_table([("exam1", "glass", "стакан")])
    #T.insert_into_table([("exam1", "glass", "cтекло")])
    #T.insert_into_table([("exam2", "word", "слово")])
    updater.start_polling()
    updater.idle() 

main()

#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/sendMessage?chat_id=151365661&text=Hello
#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/getUpdates