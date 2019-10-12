import random

class Create:
    _exam_name = None
    _owner_id = None
    _words = []

    def __init__(self, exam_name, _chatId):
        self._exam_name = exam_name
        self._owner_id = _chatId

    def parse_and_add(self, s):
        index_separator = s.find("==")
        s1 = s[:(index_separator)]
        s2 = s[(index_separator + 2):]
        list_elem_word1 = list(s1.split("/"))
        list_elem_word2 = list(s2.split("/"))
        list_word1 = []
        list_word2 = []
        print(list_elem_word1, list_elem_word2)
        for el in list_elem_word1:
            word = (el.rstrip(" ")).lstrip(" ")
            if (word != ""): list_word1.append(word)
        for el in list_elem_word2:
            word = (el.rstrip(" ")).lstrip(" ")
            if (word != ""): list_word2.append(word)
        print(list_word1, list_word2)
        for word1 in list_word1:
            for word2 in list_word2:
                print(word1 + "==" + word2)
                self._words.append((self._exam_name, word1, word2))

    def words(self):
        return self._words

    def reset(self):
        self._words = []

    def getName(self):
        return self._exam_name