import sqlite3
import os
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite')
        self._init_db()

    def _init_db(self):
        with self.get_connection() as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL,
                         time TEXT NOT NULL,
                         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                         )
                         ''')
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

db = Database()