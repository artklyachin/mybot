class Chat:
    
    _chatId = None
    _userName = None
    _firstName = None
    _status = None
    
    def __init__(self, chatId, firstName, userName):
        self._chatId = chatId
        self._firstName = firstName
        self._userName = userName
        self._status = "none"
        
    def status(self):
        return self._status
    
    def setStatus(self, value):
        self._status = value
        
    def firstName(self):
        return self._firstName
    
    def setFirstName(self, value):
        self._firstName = value
        
    def userName(self):
        return self._userName
    
    def setUserName(self, value):
        self._userName = value