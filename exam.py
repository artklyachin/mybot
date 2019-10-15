import random

class Exam:
    _num_questions = None #максимальное количество вопросов к клиенту, за один проход экзамена. Обычно равно 3.
    _words = {}
    _exam_questions = []
    _client_ans = [] #список ответов клиента при статусе exam
    _question_index = None #количество ответов клиента на экзамене
    _exam_name = None
    _finish = True #начало экзамена true, конец False

    def __init__(self, words, exam_name, num_questions):
        self._num_questions = num_questions
        self._exam_name = exam_name

        self._words = {}
        self._exam_questions = []
        self._client_ans = []
        for elem in words:
            word1 = elem[0]
            word2 = elem[1]
            if (not word1 in self._words):
                self._words[word1] = set()
            self._words[word1].add(word2)

    def startExam(self):
        self._finish = False
        self._exam_questions = []
        self._client_ans = []
        self._question_index = 0
        for i in range(self._num_questions):
            self._exam_questions.append(random.choice(list(self._words.keys())))
        return self.getQuestion()

    def getQuestion(self):
        return self._exam_questions[self._question_index]
        
    def addAnswer(self, answer):
        self._client_ans.append(answer)
        self._question_index += 1 #количество ответов клиента на экзамене.
        if (self._question_index >= self._num_questions):
            return self.getResult() #экзамен закончен. Вывод ответов.
        else:
            return self.getQuestion() #экзамен не закончен. Задаём экзаминационный вопрос к клиенту.
        
    def getResult(self): #Вывод ответов к экзамену.
        self._finish = True
        ans = ""
        for i in range(self._question_index):
            word1 = self._exam_questions[i]
            client_answer = self._client_ans[i]
            if (client_answer in self._words[word1]):
                ans += "True! "
            else:
                ans += "False. "
            ans += "word: " + word1 + ", your answer: " + client_answer + ",  right: "
            for word2 in self._words[word1]:
                ans += word2 + " / "
            ans += "\n"
        if (self._question_index == 0):
            ans += "no answer"
        ans += "\n You can /repeat_exam"
        self._question_index = 0
        return ans
          
    def repeat_exam(self):
        return self.starting_exam()

    def getWord(self):
        if (not self._finish):
            return self._exam_questions[self._question_index]
        return None

    #def getWords(self):
    #    words = []
    #    for (w in self.w)
    #    if (not self._finish):
    #        return self._exam_questions[self._question_index]
    #    return None

    def getName(self):
        return self._exam_name