import random

class Exam:
    _num_questions = None
    _words = {}
    _exam_questions = []
    _client_ans = []
    _question_index = None
    _exam_name = None

    def __init__(self, words, exam_name, num_questions):
        self._num_questions = num_questions
        self._exam_name = exam_name

        _words = {}
        self._exam_questions = []
        self._client_ans = []
        
        for elem in words:
            word1 = elem[0]
            word2 = elem[1]
            if (not word1 in self._words):
                self._words[word1] = set()
            self._words[word1].add(word2)

    def startExam(self):
        for i in range(self._num_questions):
            self._exam_questions.append(random.choice(list(self._words.keys())))
        self._question_index = 0
        return self.getQuestion()

    def getQuestion(self):
        return self._exam_questions[self._question_index]
        
    def addAnswer(self, answer):
        self._client_ans.append(answer)
        self._question_index += 1
        if (self._question_index >= self._num_questions):
            return self.getResult()
        else:
            return self.getQuestion()
        
    def getResult(self):
        ans = ""
        for i in range(self._question_index):
            word1 = self._exam_questions[i]
            client_answer = self._client_ans[i]
            if (client_answer in self._words[word1]):
                ans += "True "
            else:
                ans += "False "
            ans += " your: " + client_answer + "  right: "
            for word2 in self._words[word1]:
                ans += word2 + " "
            ans += "\n"
        return ans
          
    def repeat_exam(self):
        return self.starting_exam()


    def getName(self):
        return self._exam_name