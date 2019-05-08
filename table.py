class Table:
        
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
      
    def add_to_table(self, exam_name, s):
        self.process_ans_insert_into_table(exam_name, s)
      
    def insert_in_table(self, tup):
        print("()", tup)
        self.table.executemany('INSERT INTO EXAM VALUES (?, ?, ?)', tup)
        self.conn.commit()
        
    def all_word1(self, exam_name):
        self.table.execute('SELECT DISTINCT WORD1 FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))
        list_tup = self.table.fetchall()
        list_word1 = list()
        for elem in list_tup:
            list_word1.append(elem[0])
        return list_word1 
        
    def all_word2_are_word1(self, exam_name, word1):
        self.table.execute('SELECT DISTINCT WORD2 FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ?', (exam_name, word1))
        list_tup = self.table.fetchall()
        list_word2 = list()
        for elem in list_tup:
            list_word2.append(elem[0])
        return list_word2   
    
    def show_table(self):
        update.message.reply_text("Secret funtion!:") 
        self.table.execute('SELECT EXAM_NAME, WORD1, WORD2 FROM EXAM')   
        list_tup = self.table.fetchall()
        list_ans = list()
        for elem in list_tup:
            list_ans.append([elem[0], elem[1], elem[2]])
        return list_ans 
            
    def compare_with_the_correct_answer(self, exam_name, word1, word2):
        self.table.execute('SELECT COUNT(*) FROM EXAM WHERE EXAM_NAME = ? AND WORD1 = ? AND WORD2 = ?', (exam_name, word1, word2))  
        num = self.table.fetchall()[0][0]
        return (num > 0)
    
    def existence_check_exam_name(self, exam_name):
        self.table.execute('SELECT COUNT(*) FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))  
        num = self.table.fetchall()[0][0]
        return (num > 0)        
    
    def list_exams(self):
        self.table.execute('SELECT DISTINCT EXAM_NAME FROM EXAM')   
        list_tup = self.table.fetchall()
        list_exams = list()
        for elem in list_tup:
            list_exams.append(elem[0])
        return list_exams 
        
    def list_words(self, exam_name):           
        self.table.execute('SELECT WORD1, WORD2 FROM EXAM WHERE EXAM_NAME = ?', (exam_name,))   
        list_tup = self.table.fetchall()
        list_word1_ans_word2 = list()
        for elem in list_tup:
            list_word1_ans_word2.append([elem[0], elem[1]])
        return list_word1_ans_word2        

    def process_ans_insert_into_table(self, exam_name, s):
        s = s.replace(',', '')
        s = s.replace(';', '')
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
                self.insert_in_table((exam_name, word1, word2))        