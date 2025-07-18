import sqlite3, datetime as dt
from typing import List, Tuple

DB = "expenses.db"

def add_points(user: str, pts: int):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT OR IGNORE INTO user_points(user,points) VALUES (?,0)", (user,))
        c.execute("UPDATE user_points SET points = points + ? WHERE user = ?", (pts, user))

def get_points(user: str) -> int:
    with sqlite3.connect(DB) as c:
        cur = c.execute("SELECT points FROM user_points WHERE user = ?", (user,))
        row = cur.fetchone()
        return row[0] if row else 0

def award_badge(user: str, badge: str):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO badges(user,badge,earned_on) VALUES (?,?,?)",
                  (user, badge, dt.date.today().isoformat()))

def get_badges(user: str) -> List[Tuple[str, str]]:
    with sqlite3.connect(DB) as c:
        return c.execute("SELECT badge,earned_on FROM badges WHERE user = ?", (user,)).fetchall()

def check_monthly_budget(user: str, budget: float) -> bool:
    """Return True if user stayed under budget and earns a badge."""
    import utils.expenseTracker as et
    exp_mgr = et.ExpenseManager()
    total = sum(r[2] for r in exp_mgr.get_expenses(user))  # amount index
    if total <= budget:
        add_points(user, 50)
        award_badge(user, "Budget Boss 🏅")
        return True
    return False