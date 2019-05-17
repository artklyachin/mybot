import exam, create, train, delete, add

_chats = {}

class Chat:
    
    _chatId = {}
    _userName = None
    _firstName = None
    _status = "none"
    _exams = {}
    _created_exam = None
    _trained_exam = None
    _delete_in_exam = None
    _add_to_exam = None

    _current_exam = None

    def __init__(self, chatId, firstName, userName):
        self._chatId = chatId
        self._firstName = firstName
        self._userName = userName
        self._status = "none"
        _exam_serial = 0

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def firstName(self):
        return self._firstName

    @firstName.setter
    def firstName(self, value):
        self._firstName = value

    @property
    def userName(self):
        return self._userName

    @userName.setter
    def userName(self, value):
        self._userName = value


    def exam(self, exam_name, words):
        self._status = "exam"
        self._current_exam = exam.Exam(words, exam_name, 3)
        self._exams[exam_name] = self._current_exam
        return self._exams[exam_name].startExam()

    def train_exam(self, exam_name, words):
        self._status = "train"
        self._trained_exam = train.Train(words, exam_name)
        return self._trained_exam.getNext_word()


    def create_exam(self, exam_name):
        self._status = "create"
        self._created_exam = create.Create(exam_name)

    def delete_in_exam(self, exam_name):
        self._status = "delete"
        self._delete_in_exam = delete.Delete(exam_name)

    def add_to_exam(self, exam_name):
        self._status = "add"
        self._add_to_exam = add.Add(exam_name)

    def actions(self):
        ans = ""
        if (not self._created_exam is None):
            ans += "You create an exam: \n" + self._created_exam.getName() + "\n"
        if (not self._delete_in_exam is None):
            ans += "You delete words from: \n" + self._delete_in_exam.getName() + "\n"
        if (not self._trained_exam is None):
            ans += "You train the: \n" + self._trained_exam.getName() + "\n"
        if (not self._add_to_exam is None):
            ans += "You add words to : \n" + self._add_to_exam.getName() + "\n"
        if (len(self._exams) != 0):
            ans += "You will be exchanged for: \n"
            for elem in self._exams:
                ans += self._exams[elem].getName() + "\n"
        return ans

    def end(self):
        if (self._status == "exam"):
            del self._exams[self._current_exam.getName()]
            self._current_exam = None
        elif (self._status == "train"):
            self._trained_exam = None
        elif (self._status == "create"):
            self._created_exam = None
        elif (self._status == "delete"):
            self._created_exam = None
        elif (self._status == "add"):
            self._add_to_exam = None
        self._status = "none"



def has_chat(chatId):
    return chatId in _chats

def get_chat(chatId):
    return _chats[chatId]

def new_chat(chatId, firstName, userName):
    _chats[chatId] = Chat(chatId, firstName, userName)
    return _chats[chatId]