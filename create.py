import random

class Create:
    _exam_name = None
    _words = []

    def __init__(self, exam_name):
        self._exam_name = exam_name

    def parse_and_add(self, s):
        index_separator = 0
        if (s.find(" : ") != -1):
            index_separator = s.find(" : ")
        else:
            index_separator = s.find(":")
        s1 = s[:(index_separator + 1)]
        s2 = s[(index_separator + 2):]
        list_elem_word1 = list(s1.split(","))
        list_elem_word2 = list(s2.split(","))
        list_word1 = []
        list_word2 = []
        print(list_elem_word1, list_elem_word2)
        for el in list_elem_word1:
            first_ind = 0
            last_ind = len(el) - 1
            while (el[first_ind] == " "): first_ind += 1
            while (el[last_ind] == " "): last_ind -= 1
            list_word1.append(el[first_ind:(last_ind + 1)])
        print(list_word1, list_elem_word2)

        for el in list_elem_word2:
            first_ind = 0
            last_ind = len(el) - 1
            while (el[first_ind] == " "): first_ind += 1
            while (el[last_ind] == " "): last_ind -= 1
            list_word2.append(el[first_ind:(last_ind + 1)])
        print(list_word1, list_word2)
        for word1 in list_word1:
            for word2 in list_word2:
                print(word1 + "-" + word2)
                self._words.append((self._exam_name, word1, word2))

    def words(self):
        return self._words

    def reset(self):
        self._words = []

    def getName(self):
        return self._exam_name