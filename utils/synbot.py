import pandas as pd
import datetime as dt

class SynBot:
    """
    A tiny AI-like helper that answers questions about the
    user’s income & expense data.
    """

    # ---------- Public API ----------
    def answer(self, question: str, df_exp: pd.DataFrame, df_inc: pd.DataFrame) -> str:
        """
        question : str  – user’s free-form question
        df_exp   : pd.DataFrame – expenses with columns  [User, Category, Amount, Date]
        df_inc   : pd.DataFrame – incomes  with columns  [User, Amount, Date]
        """
        q = question.lower().strip()

        # Guard rails
        if df_exp.empty and df_inc.empty:
            return "I don’t see any transactions yet. Start logging some!"

        # 1) “How much did I spend on <category>?”
        if "spend" in q or "spent" in q:
            cat = self._extract_category(q, df_exp)
            if cat:
                total = df_exp[df_exp["Category"].str.lower() == cat]["Amount"].sum()
                return f"You spent **${total:.2f}** on {cat.title()} so far."

        # 2) “How much did I earn?”
        if "earn" in q or "income" in q:
            total_income = df_inc["Amount"].sum()
            return f"Your total recorded income is **${total_income:.2f}**."

        # 3) “How much did I spend this month?”
        if ("this month" in q or "current month" in q) and "spend" in q:
            mask = pd.to_datetime(df_exp["Date"]).dt.to_period("M") == dt.datetime.now().strftime("%Y-%m")
            total = df_exp.loc[mask, "Amount"].sum()
            return f"You spent **${total:.2f}** this month."

        # 4) “Give me advice on food savings”
        if "food" in q or "dining" in q:
            return self._food_advice(df_exp)

        # 5) Default fallback
        return (
            "Here are a few things you can ask me:\n"
            "- *How much did I spend on food?*\n"
            "- *How much did I earn?*\n"
            "- *How much did I spend this month?*"
        )

    # ---------- Internal helpers ----------
    def _extract_category(self, question: str, df_exp: pd.DataFrame) -> str | None:
        """Return the first matching category or None."""
        cats = [c.lower() for c in df_exp["Category"].unique()]
        for cat in cats:
            if cat in question:
                return cat
        return None

    def _food_advice(self, df_exp: pd.DataFrame) -> str:
        food = df_exp[df_exp["Category"].str.lower() == "food"]
        if food.empty:
            return "You haven’t logged any food expenses yet. Bon appétit!"
        total = food["Amount"].sum()
        latest = food.sort_values(by="Date", ascending=False).iloc[0]
        return (
            f"💡 To save on food:\n"
            f"• Your last food expense was **${latest['Amount']}** on {latest['Date']}.\n"
            f"• Total spent on food: **${total:.2f}**\n"
            f"• Try batch-cooking or meal-planning to cut costs."
        )