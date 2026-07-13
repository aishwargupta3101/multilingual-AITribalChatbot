from backend.database.connection import DatabaseConnection
class MongoDB(DatabaseConnection):
    def __init__(self):
        super().__init__()
        self.client=None
        self.database=None
