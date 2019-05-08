class Exam:
    _db = None
    _count_quetions = None
    _dic = None
    _exam_word1 = None
    _client_ans = None
    _index = None
    
    _word1_for_prepare = None
    _exam_status = None
    
    def __init__(self, words, count_qtns):
        self._db = words
        self._count_quetions = count_qtns 
        
        _dic = dict() 
        self._exam_word1 = list()
        self._exam_word2 = list()
        self._client_ans = list()
        
        for elem in words:
            word1 = elem[0][0]
            word2 = elem[0][1]
            if (not word1 in _dic):
                self._dic[word1] = set()
            self._dic[word1].insert(word2)
        self._starting_exam()        
            
    
    def starting_exam(self):
        if (self._exam_status != "prepare_exam"):
            return
        self._exam_status = "exam"
        for i in range(self._count_quetions):
            self.exam_word1.append(random.choice(list(self._dic.keys())))
        self._index = 0
        self.getQuestion()      
        
    def getQuestion(self):
        return self._exam_word1[self._index]
        
    def rem_client_answer(self, answer):
        self._client_ans.append(answer)
        self._index += 1
        if (self._index >= self._count_quetions): self.finish()
        else: self.quetion()     
        
    def getResult(self):
        if (self._exam_status != "prepare_exam"):
            return        
        ans = ""
        for i in range(self._index):
            word1 = self._exam_word1[i]
            client_answer = self._client_ans[i]
            if (client_answer in self._dic[word1]):
                ans += "True "
            else:
                ans += "False "
            ans += " your: " + client_answer + "  right: "
            for word2 in self._dic[word1]:
                ans += word2 + " "
            return ans     
          
    def repeat_exam(self):
        if (self._exam_status != "prepare_exam"):
            return        
        self.starting_exam()       
        
        
    def prepare_exam(self):
        if (self._exam_status != "exam"):
            return        
        self._exam_status = "exam"
        self.next_word()           
        
    def getNext_word(self):
        if (self._exam_status != "exam"):
            return        
        self._word1_for_prepare = random.choice(list(self._dic.keys()))
        return self._word1_for_prepare 
          
    def getAll_means(self):
        if (self._exam_status != "exam"):
            return        
        return list(self._dic[word1])     
    
        
    def end():
        self._exam_status = None  