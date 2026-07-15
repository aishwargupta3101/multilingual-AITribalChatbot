from  backend.database.connection import mongodb

class Collections:
    @property
    def users(self):
        return mongodb.database.users
    @property
    def sessions(self):
        return mongodb.database.sessions
    @property
    def chat_history(self):
        return mongodb.database.chat_history
    @property
    def documents(self):
        return mongodb.database.documents
    @property
    def logs(self):
        return mongodb.database.logs

collections = Collections()