"""
Syntego – Animated, Professional UI
Run:  streamlit run ui.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from utils.bill_scanner import scan_bill
from utils.expenseTracker import ExpenseManager, IncomeManager
from utils.synbot import SynBot
from utils.rewards import get_points, get_badges, check_monthly_budget
from utils.groups import create_group, join_group, add_shared_expense, get_group_expenses
from auth import AuthManager

# --------------------------------------------------
# Page config & dark/light toggle
# --------------------------------------------------
st.set_page_config(
    page_title="Syntego",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
/* ---------- Sidebar Animation ---------- */
[data-testid="stSidebar"] {
    background: rgba(18,18,18,0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255,255,255,0.08);
    animation: slideIn 0.4s ease-out;
}
@keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to   { transform: translateX(0);   opacity: 1; }
}

/* ---------- Icon Buttons (no radio) ---------- */
.nav-btn {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    width: 100%;
    margin: 0.2rem 0;
    padding: 0.7rem 1rem;
    border: none;
    border-radius: 12px;
    background: rgba(255,255,255,0.08);
    color: #eee;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.nav-btn:hover {
    background: rgba(255,255,255,0.20);
    box-shadow: 0 0 12px rgba(255,255,255,0.15);
    transform: translateY(-1px);
}
.nav-btn.active {
    background: rgba(0,255,255,0.25);
    box-shadow: 0 0 16px rgba(0,255,255,0.35);
}
/* Ripple effect */
.nav-btn::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px; height: 5px;
    background: rgba(255,255,255,0.6);
    border-radius: 50%;
    opacity: 0;
    transform: scale(1,1) translate(-50%,-50%);
    animation: ripple 0.6s ease-out;
}
@keyframes ripple {
    0%   { transform: scale(0,0)   translate(-50%,-50%); opacity: 0.5;}
    100% { transform: scale(40,40) translate(-50%,-50%); opacity: 0;}
}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Auth
# --------------------------------------------------
auth = AuthManager()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

def login_page():
    st.title("💰 Syntego")
    st.markdown("### AI-powered finance tracker")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("login"):
            email = st.text_input("📧 Email")
            pwd = st.text_input("🔒 Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if auth.login(email, pwd):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    with col2:
        with st.form("register"):
            new_email = st.text_input("📧 New Email")
            new_pwd = st.text_input("🔐 New Password", type="password")
            if st.form_submit_button("Register", use_container_width=True):
                if auth.register(new_email, new_pwd):
                    st.success("Registered! Please log in.")
                else:
                    st.error("User already exists")

# --------------------------------------------------
# Main app
# --------------------------------------------------
exp_mgr = ExpenseManager()
inc_mgr = IncomeManager()
synbot = SynBot()

def main_app():
    # ---------- Sidebar with animated icon buttons ----------
    with st.sidebar:
        st.title("Navigation")
        pages = {
            "📊 Dashboard": dashboard,
            "➕ Add Transaction": add_tx_page,
            "📑 View Expenses": view_expenses,
            "👨‍👩‍👧‍👦 Groups": groups_page,
            "💬 AI Coach": ai_coach,
        }
        for label in pages:
            if st.button(label, key=label, use_container_width=True,
                         help=None, type="secondary"):
                st.session_state.page = label
        st.markdown("---")

        # Rewards widget
        with st.expander("🏆 Rewards"):
            st.metric("Points", get_points(st.session_state.user_email))
            for b, d in get_badges(st.session_state.user_email):
                st.write(f"• {b} ({d})")

        if st.button("Logout 👋", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Route to the selected page
    page = st.session_state.get("page", "📊 Dashboard")
    pages[page]()

# --------------------------------------------------
# Page functions (unchanged)
# --------------------------------------------------
def dashboard():
    st.header("📊 Dashboard")
    exp_data = exp_mgr.get_expenses(st.session_state.user_email)
    inc_data = inc_mgr.get_income(st.session_state.user_email)

    df_exp = pd.DataFrame(exp_data, columns=["User", "Category", "Amount", "Date"])
    df_inc = pd.DataFrame(inc_data, columns=["User", "Amount", "Date"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💸 Total Spent", f"₹{df_exp['Amount'].sum():,.2f}")
    with col2:
        st.metric("💵 Total Income", f"₹{df_inc['Amount'].sum():,.2f}")
    with col3:
        st.metric("💰 Net", f"₹{df_inc['Amount'].sum() - df_exp['Amount'].sum():,.2f}")

    budget = st.number_input("Monthly budget", value=10000, step=500, key="budget")
    if st.button("Check budget"):
        if check_monthly_budget(st.session_state.user_email, budget):
            st.balloons()
            st.success("Badge earned! 🏅")

    if not df_exp.empty:
        df_exp["Date"] = pd.to_datetime(df_exp["Date"])
        fig = px.bar(
            df_exp,
            x="Date",
            y="Amount",
            color="Category",
            title="Monthly Spending by Category",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

        df_combined = pd.concat(
            [
                df_exp[["Date", "Amount"]].assign(Type="Expense"),
                df_inc[["Date", "Amount"]].assign(Type="Income"),
            ]
        )
        fig2 = px.bar(
            df_combined,
            x="Date",
            y="Amount",
            color="Type",
            title="Income vs Expenses",
            template="plotly_white",
        )
        st.plotly_chart(fig2, use_container_width=True)

def add_tx_page():
    st.header("➕ Add Transaction")
    option = st.radio("Type", ["Expense", "Income"], horizontal=True)
    with st.form("tx_form"):
        if option == "Expense":
            category = st.text_input("Category")
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
        else:
            category = None
            amount = st.number_input("Income Amount", min_value=0.0, step=0.01)
        tx_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Save", use_container_width=True)
        if submitted:
            if option == "Expense":
                exp_mgr.add_expense(
                    st.session_state.user_email, category, amount, str(tx_date)
                )
            else:
                inc_mgr.add_income(st.session_state.user_email, amount, str(tx_date))
            st.success("Saved!")

        if option == "Expense":
            st.subheader("👨‍👩‍👧‍👦 Shared expense (optional)")
            grp_name = st.text_input("Group name")
            members = st.text_input("Split with (comma-separated emails)").split(",")
            if st.form_submit_button("Add Shared Expense", use_container_width=True):
                add_shared_expense(
                    grp_name,
                    st.session_state.user_email,
                    category,
                    amount,
                    [m.strip() for m in members],
                )
                st.success("Shared expense saved!")
            # --- Bill Scanner ---
    st.subheader("📸 Scan bill (optional)")
    uploaded_file = st.file_uploader("Upload receipt JPG/PNG", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
            vendor, amt, dt_str = scan_bill(uploaded_file, st.session_state.user_email)
            st.success(f"Scanned: {vendor} – ₹{amt} on {dt_str}")

def view_expenses():
    st.header("📑 View Expenses")
    data = exp_mgr.get_expenses(st.session_state.user_email)
    if data:
        df = pd.DataFrame(data, columns=["User", "Category", "Amount", "Date"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No expenses logged yet.")

def groups_page():
    st.header("👨‍👩‍👧‍👦 Groups & Shared Expenses")
    grp_name = st.text_input("Create or join group")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create"):
            create_group(grp_name)
            st.success("Group created")
    with col2:
        if st.button("Join"):
            join_group(st.session_state.user_email, grp_name)
            st.success("Joined group")
    if st.checkbox("Show group expenses"):
        data = get_group_expenses(grp_name)
        if data:
            df = pd.DataFrame(data, columns=["Spender", "Category", "Amount", "Date", "Split"])
            st.dataframe(df)
        else:
            st.info("No shared expenses yet.")

def ai_coach():
    st.header("💬 AI Coach")
    exp_data = exp_mgr.get_expenses(st.session_state.user_email)
    inc_data = inc_mgr.get_income(st.session_state.user_email)
    df_exp = pd.DataFrame(exp_data, columns=["User", "Category", "Amount", "Date"])
    df_inc = pd.DataFrame(inc_data, columns=["User", "Amount", "Date"])

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask me anything…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        answer = synbot.answer(prompt, df_exp, df_inc)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

# --------------------------------------------------
# Routing
# --------------------------------------------------
if st.session_state.logged_in:
    main_app()
else:
    login_page()