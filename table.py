import os
import sqlite3


class Table:
        
    def __init__(self):
        #if os.path.isfile('school2.db'):
        #    os.remove('school2.db')
        self.conn = sqlite3.connect('school2.db', check_same_thread=False)
        self.table = self.conn.cursor()         
        self.table.execute('''
            CREATE TABLE IF NOT EXISTS EXAM(
                EXAM_NAME CHAR(40) NOT NULL,
                WORD1 CHAR(40) NOT NULL,
                WORD2 CHAR(40) NOT NULL,
                PRIMARY KEY(EXAM_NAME, WORD1, WORD2)) 
        ''')
        #primary key определяет приоритеты в сортировке
        self.table.execute('''
            CREATE TABLE IF NOT EXISTS EXAM_OWNER(
                OWNER_ID INTEGER NOT NULL,
                EXAM_NAME CHAR(40) NOT NULL,
                PRIMARY KEY(OWNER_ID, EXAM_NAME))
        ''')

    def add_to_table(self, exam_name, s): #добавление в таблицу EXAM
        self.process_ans_insert_into_table(exam_name, s) #добавление в таблицу EXAM, не нашёл этой функции
    #? не используется

    def add_exam_name(self, exam_name, owner_id): #добавление в таблицу EXAM_OWNER
        self.table.executemany('INSERT INTO EXAM_OWNER VALUES (?, ?)', [(owner_id, exam_name)])
        self.conn.commit()

    def insert_into_table(self, rows): #добавление в таблицу EXAM
        self.table.executemany('INSERT INTO EXAM VALUES (?, ?, ?)', rows)
        self.conn.commit()

    def all_word1(self, exam_name): #вывод всех word1 для определённого экзамена
        self.table.execute('SELECT DISTINCT WORD1 FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))
        list_tup = self.table.fetchall()
        list_word1 = list()
        for elem in list_tup:
            list_word1.append(elem[0])
        return list_word1 
        
    def all_word2_are_word1(self, exam_name, word1): #вывод всех word2 для определённого word1 в определённом экзамене
        self.table.execute('SELECT DISTINCT WORD2 FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ?', (exam_name, word1))
        list_tup = self.table.fetchall()
        list_word2 = list()
        for elem in list_tup:
            list_word2.append(elem[0])
        return list_word2   
    
    def show_table(self): #полный вывод таблицы EXAM
        self.table.execute('SELECT EXAM_NAME, WORD1, WORD2 FROM EXAM')
        list_tup = self.table.fetchall()
        list_ans = list()
        for elem in list_tup:
            list_ans.append([elem[0], elem[1], elem[2]])
        return list_ans

    def show_table(self): #полный вывод таблицы EXAM_OWNER
        self.table.execute('SELECT OWNER_ID, EXAM_NAME FROM EXAM_OWNER')
        list_tup = self.table.fetchall()
        list_ans = list()
        for elem in list_tup:
            list_ans.append([elem[1], elem[0]])
        return list_ans
            
    def compare_with_the_correct_answer(self, exam_name, word1, word2): #проверка присутсвия в EXAM строки с определёнными word1, word2, exam_name
        self.table.execute('SELECT COUNT(*) FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ? AND WORD2 = ?', (exam_name, word1, word2))  
        num = self.table.fetchall()[0][0]
        return (num > 0)
    
    def exists(self, exam_name): #проверка присутсвия в EXAM названия exam_name
        self.table.execute('SELECT COUNT(*) FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))  
        num = self.table.fetchall()[0][0]
        return (num > 0)

    def exist_in_the_table (self, exam_name): #проверка присутсвия в EXAM_OWNER названия exam_name
        self.table.execute('SELECT COUNT(*) FROM EXAM_OWNER WHERE EXAM_NAME = ?', (exam_name,))
        num = self.table.fetchall()[0][0]
        return (num > 0)

    def check_entry_into_the_exam(self, s):
        for elem in s:
            if(not self.compare_with_the_correct_answer(elem[0], elem[1], elem[2])):
                return elem
        return None

    def remove_from_table(self, s): #удаление из EXAM строки с определёнными word1, word2, exam_name
        self.table.executemany('DELETE FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ? AND WORD2 = ?', s)
        self.conn.commit()

    def remove_from_table_EXAM_OWNER(self, s): #удаление из EXAM_OWNER строки с определёнными owner_id, exam_name
        self.table.executemany('DELETE FROM EXAM_OWNER WHERE OWNER_ID = ? AND EXAM_NAME = ?', s)
        self.conn.commit()

    def remove_exam(self, exam_name): #удаление из EXAM и EXAM_OWNER всех строк с именем экзамена exam_name
        self.table.execute('DELETE FROM EXAM WHERE EXAM_NAME = ?', (exam_name, ))
        self.table.execute('DELETE FROM EXAM_OWNER WHERE EXAM_NAME = ?', (exam_name,))
        self.conn.commit()
    
    def list_exams(self): #вывод всех названий экзаменов из EXAM
        list_exams = list()

        #ненужный код
        #self.table.execute('SELECT DISTINCT EXAM_NAME FROM EXAM')
        #list_tup = self.table.fetchall()
        #for elem in list_tup:
        #    list_exams.append([elem[0], 0])
        #    #self.table.executemany('INSERT INTO EXAM_OWNER VALUES (?, ?)', [(151365661, elem[0])])
        #self.conn.commit()

        self.table.execute('SELECT OWNER_ID, EXAM_NAME FROM EXAM_OWNER')
        list_tup = self.table.fetchall()
        for elem in list_tup:
            list_exams.append([elem[1], elem[0]])
        return list_exams
        
    def list_words(self, exam_name): #вывод всех word1, word2 для определённого экзамена
        self.table.execute('SELECT WORD1, WORD2 FROM EXAM WHERE EXAM_NAME = ? ORDER BY WORD1, WORD2', (exam_name,))
        list_tup = self.table.fetchall()
        list_word1_ans_word2 = list()
        for elem in list_tup:
            list_word1_ans_word2.append([elem[0], elem[1]])
        return list_word1_ans_word2

    def change_name(self, old_name, new_name):
        return

    def exam_owner_id(self, exam_name):
        self.table.execute('SELECT OWNER_ID FROM EXAM_OWNER WHERE EXAM_NAME = ?', (exam_name,))
        return self.table.fetchall()[0][0]

        #self.conn.commit() - сохраняет таблицу
    #помни про [] у executemany