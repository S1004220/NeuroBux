import sqlite3

class AuthManager:
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT)''')
        self.conn.commit()

    def register(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            return False
        cursor.execute("INSERT INTO users VALUES (?,?)", (email, password))
        self.conn.commit()
        return True

    def login(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        return cursor.fetchone() is not None
