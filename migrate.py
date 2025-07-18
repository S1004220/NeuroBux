import sqlite3

sql = """
CREATE TABLE IF NOT EXISTS user_points (
    user TEXT PRIMARY KEY,
    points INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS badges (
    user TEXT,
    badge TEXT,
    earned_on TEXT
);
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS group_members (
    group_id INTEGER,
    user TEXT
);
CREATE TABLE IF NOT EXISTS shared_expenses (
    group_id INTEGER,
    spender TEXT,
    category TEXT,
    amount REAL,
    date TEXT,
    split_with TEXT
);
"""

with sqlite3.connect("expenses.db") as conn:
    conn.executescript(sql)
print("✅ Migration complete")