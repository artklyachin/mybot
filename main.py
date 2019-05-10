import logging, random
import sqlite3
import random
import time
import table
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config, chat, exam, create

instructions_for_filling_the_dictionary = 'Вводить слова в формате\n word - слово \n Через запятую можно добавить значения.'
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
    update.message.reply_text("Hi %s, i,m your bot" % ch.firstName)

def end(bot, update):
    global status
    ch = get_chat(update)
    if (status == "create"):
        ce = ch._created_exam
        T.insert_into_table(ce.words())
        ce.reset()
        ch.end()
    elif (status == "train"):
        ch.end()
    elif (status == "exam"):
        ch.end()
    status = "none"



def new_exam(bot, update):
    global T, status
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /new_exam <name>")
        return
    if ch.status == "create":
        end()
    cr = ch.create_exam(exam_name)
    status = "create"
    send_message(bot, update, "You start creating an exam " + exam_name)
    send_message(bot, update, instructions_for_filling_the_dictionary)

def train_exam(bot, update):
    global T, status
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /prepare_exam <name>")
        return
    if ch.status == "train":
        end()
    response = ch.train_exam(exam_name, T.list_words(exam_name))
    update.message.reply_text(response)
    update.message.reply_text("/all_meanings")
    status = "train"

def next_word(bot, update):
    ch = get_chat(update)
    tr = ch._trained_exam
    update.message.reply_text(tr.getNext_word())
    update.message.reply_text("/all_meanings")

def all_meanings(bot, update):
    ch = get_chat(update)
    tr = ch._trained_exam
    list_all_meanings = tr.getAll_meanings()
    ans = ""
    for elem in list_all_meanings:
        ans += elem + " "
    update.message.reply_text(ans)
    update.message.reply_text("/next_word")

def exam(bot, update):
    global T, status
    ch = get_chat(update)
    exam_name = get_text_in_request(update.message.text)
    if (exam_name == ""):
        update.message.reply_text("No correct. /exam <name>")
        return
    response = ch.exam(exam_name, T.list_words(exam_name))
    update.message.reply_text(response)
    status = "exam"

def repeat_exam(bot, update):
    ch = get_chat(update)
    ex = ch._current_exam
    update.message.reply_text(ex.startExam())

def finish(bot, update):
    ch = get_chat(update)
    ex = ch._current_exam
    text = ex.getResult()
    if (text == ""):
        update.message.reply_text("no answer")
    else:
        update.message.reply_text(text)
    update.message.reply_text("You can /repeat_exam")

def show_table(bot, update):
    print("No")

def list_exams(bot, update):
    print("No")

def list_words(bot, update):
    print("No")

def help(bot, update):
    send_message(bot, update, '''
        - /start
        - /end
        - /new_exam
        - /train_exam
        - - /next_word  
        - - /all_meanings
        - /exam
        - - /repeat_exam
        - - /finish
        - /show_table
        - /list_exams
        - /list_words
        - /help
    ''')

def get_message(bot, update):
    global status;
    ch = get_chat(update)
    client_answer = update.message.text
    if ch.status == "exam":
        ex = ch._current_exam
        if not ex:
            send_message(bot, update, "You are not in exam")
            return
        response = ex.addAnswer(client_answer)
        if (not type(response) is list):
            send_message(bot, update, response)
        else:
            for elem in response:
                send_message(bot, update, elem)
            update.message.reply_text("You can /repeat_exam")
    elif ch.status == "create":
        ce = ch._created_exam
        if not ce:
            send_message(bot, update, "You are not creating a new exam")
            return
        ce.parse_and_add(client_answer)
        T.insert_into_table(ce.words())
        ce.reset()
        send_message(bot, update, "added in %s" % ce.getName())
    elif ch.status == "train":
        response = "train, do not accept text"
        send_message(bot, update, response)
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
    
    dispatcher.add_handler(CommandHandler('train_exam', train_exam))
    dispatcher.add_handler(CommandHandler('next_word', next_word))
    dispatcher.add_handler(CommandHandler('all_meanings', all_meanings))

    
    dispatcher.add_handler(CommandHandler('exam', exam))
    dispatcher.add_handler(CommandHandler('repeat_exam', repeat_exam))
    dispatcher.add_handler(CommandHandler('finish', finish))
    
    dispatcher.add_handler(CommandHandler('show_table', show_table))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('list_exams', list_exams))
    dispatcher.add_handler(CommandHandler('list_words', list_words))
    dispatcher.add_handler(CommandHandler('help', help))
    
    dispatcher.add_error_handler(error)
    
    dispatcher.add_handler(MessageHandler(Filters.text, get_message))
    
    return updater
   

def main():
    global T
    updater = parametrs_for_updater()
    T.insert_into_table([("exam1", "car", "автомобиль")])
    T.insert_into_table([("exam1", "table", "стол")])
    T.insert_into_table([("exam1", "glass", "стакан")])
    T.insert_into_table([("exam1", "glass", "cтекло")])
    updater.start_polling()
    updater.idle() 

main()

#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/sendMessage?chat_id=151365661&text=Hello
#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/getUpdates