import logging, random
import sqlite3
import random
import time
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
#import user


telegram_token = '859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs'
status = "none"


class table:
        
    def __init__(self):
        if os.path.isfile('school2.db'):
            os.remove('school2.db')    
        self.conn = sqlite3.connect('school2.db', check_same_thread=False)
        self.table = self.conn.cursor()         
        self.table.execute('''
            CREATE TABLE IF NOT EXISTS EXAM(
                EXAM_NAME,
                WORD1 CHAR(40) NOT NULL,
                WORD2 CHAR(40) NOT NULL,
                PRIMARY KEY(EXAM_NAME, WORD1, WORD2))
        ''')             
      
    def insert_in_table(self, s):
        print("()", s)
        self.table.executemany('INSERT INTO EXAM VALUES (?, ?, ?)', s)
        self.conn.commit()
        
    def all_word1(self, exam_name):
        self.table.execute('SELECT DISTINCT WORD1 FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))
        return list(self.table.fetchall())   
        
    def all_word2_are_word1(self, exam_name, word1):
        self.table.execute('SELECT DISTINCT WORD2 FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ?', (exam_name, word1))
        return list(self.table.fetchall())    
    
    def watch_table(self, bot, update):
        update.message.reply_text("Secret funtion!:") 
        self.table.execute('SELECT EXAM_NAME, WORD1, WORD2 FROM EXAM')   
        l = self.table.fetchall()
        for el in l:
            update.message.reply_text(el[0] + " " + el[1] + " " + el[2])
            
    def compare_with_the_correct_answer(self, exam_name, word1, word2):
        self.table.execute('SELECT COUNT(*) FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ? AND WORD2 = ?', (exam_name, word1, word2))  
        num = self.table.fetchall()[0][0]
        return (num > 0)
    
    def existence_check_exam_name(self, exam_name):
        self.table.execute('SELECT COUNT(*) FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))  
        num = self.table.fetchall()[0][0]
        return (num > 0)        
    
    def list_exams(self, bot, update):
        self.table.execute('SELECT EXAM_NAME FROM EXAM GROUP BY EXAM_NAME')   
        l = self.table.fetchall() 
        ans = "list of exams: \n"
        for el in l:
            ans += (el[0] + '\n')
        update.message.reply_text(ans)
        
    def list_words(self, bot, update):
        command_part = update.message.text.split(" ", 1)
        exam_name = command_part[1] if len(command_part) > 1 else ""         
        if (exam_name == ""):
            send_message(bot, update, "Please enter with exam name: \n /list_words <NAME>")
            return
        if(not self.existence_check_exam_name(exam_name)):
            send_message(bot, update, "this exam does not exist")
            return           
        list_word1 = self.all_word1(command_part[1])
        ans = "list of words the exam " + exam_name + ": \n"        
        for word1 in list_word1:
            ans += word1[0] + " - "
            list_word2 = self.all_word2_are_word1(exam_name, word1[0])
            for word2 in list_word2:
                ans += word2[0] + " "
            ans += '\n'
        update.message.reply_text(ans) 

class myBot:
    instructions_for_filling_the_dictionary = 'Вводить слова в формате\n word - слово \n Через запятую можно добавить значения.' 
    new_exam_name = ""
    exam_name = ""
    exam_word1 = list()
    client_ans = list()
    quetion_index = 0
    count_exam_quetions = 3
    
    
    def __init__(self):
        self.T = table()
             
    def process_ans_insert_into_table(self, bot, update, s):
        s = s.replace(',', '')
        s = s.replace(';', '')
        if (s.find(" - ") == -1):
            send_message(bot, update, "No correct \n " + self.instructions_for_filling_the_dictionary)
            return
        list_elem = list(s.split())
        list_word1 = list()
        list_word2 = list()
        flag_for_word2 = False
        for el in list_elem:
            if (el == "-"): flag_for_word2 = True
            elif (not flag_for_word2): list_word1.append(el)
            else: list_word2.append(el)
        for word1 in list_word1:
            for word2 in list_word2:
                self.T.insert_in_table([(self.new_exam_name, word1, word2)])    
         
    def dictionary_filling(self, bot, update, client_answer):
        self.process_ans_insert_into_table(bot, update, client_answer)   
        
    def finish(self, bot, update):
        if (status != "finish"):
            send_message(bot, update, "You cannot use this command")        
            return False  
        send_message(bot, update, "Correct answer:")
        for i in range(self.quetion_index):
            ans = ""
            if (self.T.compare_with_the_correct_answer(self.exam_name, self.exam_word1[i], self.client_ans[i])): 
                ans += "True "
            else: 
                ans += "False "
            ans += (" your: " + self.client_ans[i] + "  right: ")
            list_word2 = self.T.all_word2_are_word1(self.exam_name, self.exam_word1[i])
            for word2 in list_word2:
                ans += (word2[0] + " ")
            send_message(bot, update, ans)
        self.exam_word1 = list()
        self.client_ans = list()
        self.quetion_index = 0       
        update.message.reply_text("Do you want to /repeat_exam ?")          
        
    def anouther_quetion(self, bot, update):
        send_message(bot, update, self.exam_word1[self.quetion_index])
        
    def rem_client_answer(self, bot, update, answer):
        self.client_ans.append(answer)
        self.quetion_index += 1
        if (self.quetion_index >= self.count_exam_quetions): self.finish(bot, update)
        else: self.anouther_quetion(bot, update)    
    
    def repeat_exam(self, bot, update):
        global status
        if (status != "finish"):
            send_message(bot, update, "You cannot use this command")        
            return False  
        self.starting_exam(bot, update)
        
    def starting_exam(self, bot, update):
        for i in range(self.count_exam_quetions):
            word1 = random.choice(self.T.all_word1(self.exam_name))[0]
            self.exam_word1.append(word1)
        send_message(bot, update, "starting exam:")
        self.anouther_quetion(bot, update)     
        
    def next_word(self, bot, update):
        global status
        if (status != "repeat"):
            send_message(bot, update, "You cannot use this command")        
            return False         
        word1 = random.choice(self.T.all_word1(self.exam_name))[0]
        list_word2 = self.T.all_word2_are_word1(self.exam_name, word1)
        ans = word1 + " - "
        for word2 in list_word2:
            ans += word2[0] + " "
        ans += "\n  /next_word"
        send_message(bot, update, ans)
        


mybot = myBot()
   
def send_message(bot, update, text):
    update.message.reply_text(text) 
    
def get_text_in_request(text):
    part = text.split(" ", 1)
    return part[1] if len(part) == 2 else ""

    
def checks_for_incorrect_status(bot, update, exam_type):
    global mybot, status
    if (status != exam_type):
        send_message(bot, update, "You cannot use this command")        
        return False
    return True

def checks_for_incorrect_input(bot, update, exam_type, exam_name):
    global mybot
    if (exam_name == ""):
        send_message(bot, update, "Please enter with exam name: \n /" + exam_type + " <NAME>")
        return False
    if(not mybot.T.existence_check_exam_name(exam_name)):
        send_message(bot, update, "this exam does not exist")
        return False
    return True

def end(bot, update):
    global status;   
    send_message(bot, update, 'Ok')    
    status = "none"     
   
def start(bot, update):
    send_message(bot, update, 'Hi, I am exam bot')      
    

def exam(bot, update):
    global status, mybot   
    exam_name = get_text_in_request(update.message.text)
    if (not checks_for_incorrect_input(bot, update, "exam", exam_name)): return
    status = "finish"        
    mybot.exam_name = exam_name    
    mybot.starting_exam(bot, update)


def prepare_exam(bot, update):
    global status
    exam_name = get_text_in_request(update.message.text)
    if (not checks_for_incorrect_input(bot, update, "prepare_exam", exam_name)): return   
    status = "repeat" 
    mybot.exam_name = exam_name
    mybot.next_word(bot, update)


def new_exam(bot, update):
    global status, mybot
    new_exam_name = get_text_in_request(update.message.text)
    if (not checks_for_incorrect_input(bot, update, "new_exam", new_exam_name)): return
    send_message(bot, update, mybot.instructions_for_filling_the_dictionary)
    status = "dictionary_filling"    
    mybot.new_exam_name = new_exam_name
    

def get_message(bot, update):
    global status;    
    client_answer = update.message.text
    if (status == "dictionary_filling"): mybot.dictionary_filling(bot, update, client_answer)
    elif (status == "finish"): mybot.rem_client_answer(bot, update, client_answer)
    elif (status == "repeat"): next_word(bot, update, client_answer)
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
def status(bot, update):
    send_message(bot, update, status) 
    '''global status, mybot
    if (status == "none"):
        send_message(bot, update, "none action")
    elif (status == "dictionary_filling"):
        send_message(bot, update, "you fill out the words exam the name " + mybot.new_exam_name)
    elif (status == "finish"):
        send_message(bot, update, "you doing the exam the name " + mybot.exam_name)    
        send_message(bot, update, "your quetion: " + mybot.exam_word)     '''
        

def help(bot, update):
    send_message(bot, update, '''
        commands: 
        /new_exam <NAME> - create exam 
        /end - ending last action 
        /exam <NAME> - starting exam 
        /status - you can find your last action
        to the last question 
        /list_exams - list of all exams
        /list_words <NAME> - list of all words in exam
        Test function:
        of the call
        - /start
        - /end
        - /new_exam
        - /prepare_exam
        - - /next_word  
        - /exam
        - - /repeat_exam
        - - /finish
        - /show_table
        - /status
        - /list_exams
        - /list_words
        - /help
    ''')
    
def parametrs_for_updater():
    global mybot
    telegram_token = '859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs'
    
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    updater = Updater(telegram_token)    
    dispatcher = updater.dispatcher    
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('end', end))
    
    dispatcher.add_handler(CommandHandler('new_exam', new_exam))
    
    dispatcher.add_handler(CommandHandler('prepare_exam', prepare_exam))
    dispatcher.add_handler(CommandHandler('next_word', mybot.next_word))
    
    dispatcher.add_handler(CommandHandler('exam', exam))
    dispatcher.add_handler(CommandHandler('repeat_exam', mybot.repeat_exam))
    dispatcher.add_handler(CommandHandler('finish', mybot.finish))
    
    dispatcher.add_handler(CommandHandler('watch_table', mybot.T.watch_table))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('list_exams', mybot.T.list_exams))
    dispatcher.add_handler(CommandHandler('list_words', mybot.T.list_words))
    dispatcher.add_handler(CommandHandler('help', help))
    
    dispatcher.add_error_handler(error)
    
    dispatcher.add_handler(MessageHandler(Filters.text, get_message))
    
    return updater
   

def main():
    global mybot
    updater = parametrs_for_updater()
    mybot.T.insert_in_table([("exam1", "car", "автомобиль")])
    mybot.T.insert_in_table([("exam1", "table", "стол")])
    mybot.T.insert_in_table([("exam1", "glass", "стакан")])
    mybot.T.insert_in_table([("exam1", "glass", "cтекло")])   
    updater.start_polling()
    updater.idle() 

main()

#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/sendMessage?chat_id=151365661&text=Hello
#https://api.telegram.org/bot859423835:AAGfh15AaFV-qpOnyTDMk0tkDS50Wvnvxhs/getUpdates