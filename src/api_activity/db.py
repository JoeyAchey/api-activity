import sqlite3
from contextlib import closing


def connect():
    return sqlite3.connect("activity.db")

class Database:
    def __init__(self):
        self.conn = connect()
        self.create_users_table()

    def create_users_table(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
                """
            )
    def add_user(self, username: str, hashed_pwd: str) -> bool:
        try:
            with self.conn, closing(self.conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pwd),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_password(self, username: str) -> str:
        with closing(self.conn.cursor()) as cursor:
            row = cursor.execute(
                "SELECT password FROM users WHERE username = ?", (username,)
            ) .fetchone()
            return row[0] if row is not None else None
        