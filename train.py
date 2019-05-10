import random

class Train:
    _words = None
    _train_questions = None
    _exam_name = None

    def __init__(self, words, exam_name):
        self._words = {}
        self._exam_name = exam_name

        for elem in words:
            word1 = elem[0]
            word2 = elem[1]
            if (not word1 in self._words):
                self._words[word1] = set()
            self._words[word1].add(word2)

    def getNext_word(self):
        self._train_questions = random.choice(list(self._words.keys()))
        return self._train_questions
          
    def getAll_meanings(self):
        return list(self._words[self._train_questions])


    def getName(self):
        return self._exam_name