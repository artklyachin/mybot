import random

class Create:
    _exam_name = None
    _words = []

    def __init__(self, exam_name):
        self._exam_name = exam_name

    def parse_and_add(self, s):
        s = s.replace(',', ' ')
        s = s.replace(';', ' ')
        list_elem = list(s.split())
        list_word1 = []
        list_word2 = []
        flag_for_word2 = False
        for el in list_elem:
            if (el == "-"): flag_for_word2 = True
            elif (not flag_for_word2): list_word1.append(el)
            else: list_word2.append(el)
        for word1 in list_word1:
            for word2 in list_word2:
                self._words.append((self._exam_name, word1, word2))

    def words(self):
        return self._words

    def reset(self):
        self._words = []

    def getName(self):
        return self._exam_name