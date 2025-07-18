import sqlite3, json
DB = "expenses.db"

def create_group(name: str):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT OR IGNORE INTO groups(name) VALUES (?)", (name,))

def join_group(user: str, group_name: str):
    with sqlite3.connect(DB) as c:
        gid = c.execute("SELECT group_id FROM groups WHERE name = ?", (group_name,)).fetchone()
        if gid:
            c.execute("INSERT OR IGNORE INTO group_members(group_id,user) VALUES (?,?)",
                      (gid[0], user))

def add_shared_expense(group_name: str, spender: str, cat: str, amt: float,
                       split_with: list):
    with sqlite3.connect(DB) as c:
        gid = c.execute("SELECT group_id FROM groups WHERE name = ?", (group_name,)).fetchone()[0]
        c.execute("""INSERT INTO shared_expenses(group_id,spender,category,amount,date,split_with)
                     VALUES (?,?,?,?,date('now'),?)""",
                  (gid, spender, cat, amt, json.dumps(split_with)))

def get_group_expenses(group_name: str):
    with sqlite3.connect(DB) as c:
        return c.execute("""SELECT spender, category, amount, date, split_with
                            FROM shared_expenses
                            JOIN groups USING(group_id)
                            WHERE groups.name = ?
                            ORDER BY date DESC""", (group_name,)).fetchall()