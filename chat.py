import exam, create, train

_chats = {}

class Chat:
    
    _chatId = {}
    _userName = None
    _firstName = None
    _status = "none"
    _exams = {}
    _created_exam = None
    _trained_exam = None

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
        self.created_exam = create.Create(exam_name)

    def end(self):
        if (self._status == "exam"):
            del self._exams[self._current_exam.getName()]
            self._current_exam = None
        elif (self._status == "train"):
            self._trained_exam = None
        elif (self._status == "create"):
            self._created_exam = None
        self._status = "none"



def has_chat(chatId):
    return chatId in _chats

def get_chat(chatId):
    return _chats[chatId]

def new_chat(chatId, firstName, userName):
    _chats[chatId] = Chat(chatId, firstName, userName)
    return _chats[chatId]