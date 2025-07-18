import sqlite3

class ExpenseManager:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db", check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS expenses (
            user TEXT, category TEXT, amount REAL, date TEXT
        )''')
        self.conn.commit()

    def add_expense(self, user, category, amount, date):
        self.conn.execute("INSERT INTO expenses VALUES (?, ?, ?, ?)", (user, category, amount, date))
        self.conn.commit()

    def get_expenses(self, user):
        return self.conn.execute("SELECT * FROM expenses WHERE user=?", (user,)).fetchall()

class IncomeManager:
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db", check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS income (
            user TEXT, amount REAL, date TEXT
        )''')
        self.conn.commit()

    def add_income(self, user, amount, date):
        self.conn.execute("INSERT INTO income VALUES (?, ?, ?)", (user, amount, date))
        self.conn.commit()

    def get_income(self, user):
        return self.conn.execute("SELECT * FROM income WHERE user=?", (user,)).fetchall()
