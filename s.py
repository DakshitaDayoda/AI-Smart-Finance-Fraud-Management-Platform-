# app.py
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import joblib
import mysql.connector
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import yfinance as yf
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np
import requests
from openai import OpenAI


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Login Security System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

/* Main App */
.stApp{
    background: linear-gradient(
        135deg,
        #0b1020,
        #111827,
        #161b33
    );
    color:white;
}

/* Hide Streamlit Menu */
#MainMenu,
footer{
    visibility:hidden;
}

/* Main Container */
.block-container{
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
    max-width:95%;
}

/* Title */
.main-title{
    color:white;
    font-size:42px;
    font-weight:700;
    text-align:center;
    margin-bottom:30px;
}

/* Dashboard Cards */
div[data-testid="metric-container"]{
    background: rgba(22,27,51,0.85);
    border:1px solid rgba(138,92,246,0.25);
    border-radius:20px;
    padding:20px;
    box-shadow:
        0 0 15px rgba(138,92,246,.25);
}

/* Buttons */
.stButton > button{
    width:100%;
    border-radius:16px;
    border:none;
    background:linear-gradient(
        135deg,
        #5B21B6,
        #7C3AED,
        #A855F7
    );
    color:white;
    font-weight:600;
    height:55px;
    transition:0.3s;
}

.stButton > button:hover{
    transform:translateY(-3px);
    box-shadow:
      0 0 20px rgba(168,85,247,.6);
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:
    linear-gradient(
        180deg,
        #0f172a,
        #111827
    );
    border-right:
    1px solid rgba(168,85,247,.3);
}

/* Input Fields */
.stTextInput input,
.stNumberInput input,
.stDateInput input{
    background:#1a1f38;
    color:white;
    border-radius:12px;
    border:1px solid #7C3AED;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"]{
    background:#1a1f38;
    border-radius:12px;
}

/* DataFrame */
[data-testid="stDataFrame"]{
    border-radius:18px;
    overflow:hidden;
    border:1px solid rgba(168,85,247,.3);
}

/* Chat Messages */
[data-testid="stChatMessage"]{
    background:rgba(20,25,50,.85);
    border-radius:18px;
    border:1px solid rgba(168,85,247,.2);
    padding:12px;
}

/* Success Card */
.safe-box{
    background:
    linear-gradient(
        135deg,
        #059669,
        #10B981
    );
    padding:25px;
    border-radius:18px;
    text-align:center;
    font-size:24px;
    font-weight:bold;
    color:white;
}

/* Danger Card */
.danger-box{
    background:
    linear-gradient(
        135deg,
        #DC2626,
        #EF4444
    );
    padding:25px;
    border-radius:18px;
    text-align:center;
    font-size:24px;
    font-weight:bold;
    color:white;
}

/* Charts */
.element-container{
    border-radius:20px;
}

/* Cards */
.glass-card{
    background:rgba(20,25,50,.8);
    backdrop-filter:blur(14px);
    border:1px solid rgba(168,85,247,.2);
    border-radius:24px;
    padding:25px;
    box-shadow:
        0 0 25px rgba(168,85,247,.15);
            }
            
.glass-card:hover{
    transform:translateY(-5px);
    transition:0.3s;
    box-shadow:0 0 25px rgba(168,85,247,.5);
}
    
</style>
""", unsafe_allow_html=True)

# ================= SQLITE (LOGIN DB) =================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT
)
""")
conn.commit()

def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= MYSQL (EXPENSE DB) =================
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",  
        database="expense_tracker"
    )

# ================= LOAD MODELS =================
@st.cache_resource
def load_model():
    return joblib.load("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 6\\login_security_model.pkl")

@st.cache_resource
def load_fraud_model():
    return joblib.load("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 1\\fraud_model.pkl")

@st.cache_resource
def load_encoders():
    return joblib.load("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 1\\encoders.pkl")

@st.cache_resource
def load_loan_model():
    return joblib.load("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 4\\loan_risk_model.pkl")

@st.cache_resource
def load_currency_model():
    return joblib.load("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 8\\currency_model.pkl")

@st.cache_resource
def load_base_date():
    return joblib.load("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 8\\base_date.pkl")

@st.cache_resource
def load_stock_model():
    with open("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 3\\stock_model.pkl", "rb") as f:
        return pickle.load(f)



model = load_model()
fraud_model = load_fraud_model()
encoders = load_encoders()
loan_model = load_loan_model()
currency_model = load_currency_model()
base_date = load_base_date()
stock_model = load_stock_model()

# ================= SESSION STATE =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []


# ================= AUTH SYSTEM =================
if not st.session_state.logged_in:

    menu = st.sidebar.radio("Navigation", ["Sign In", "Sign Up"])

    if menu == "Sign Up":
        st.subheader("📝 Create New Account")

        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if password != confirm_password:
                st.error("Passwords do not match")
            elif username == "":
                st.error("Enter username")
            else:
                try:
                    c.execute(
                        "INSERT INTO users VALUES(?,?,?)",
                        (username, email, make_hash(password))
                    )
                    conn.commit()
                    st.success("Account created successfully!")
                except:
                    st.error("Username already exists")

    else:
        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign In"):
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, make_hash(password))
            )
            user = c.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Invalid username or password")

# ================= MAIN APP =================
else:

    st.sidebar.success(f"👤 {st.session_state.username}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "home"
        st.rerun()


    # ================= HOME =================

    if st.session_state.page == "home":

        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <h1 style="font-size:42px;">
                🛡️ AI Financial Intelligence Platform
            </h1>
            <p style="color:#9CA3AF;font-size:18px;">
                Fraud Detection • Stock Prediction • Loan Risk • Currency Forecasting
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.success(f"Welcome {st.session_state.username}")

        # ================= KPI CARDS =================
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric("Security Events", "120", "+12%")

        with k2:
            st.metric("Transactions", "6100", "+8%")

        with k3:
            st.metric("Fraud Alerts", "35", "-4%")

        with k4:
            st.metric("Predictions", "4500", "+15%")

        st.markdown("<br>", unsafe_allow_html=True)

    
        # ================= FIRST ROW =================
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            if st.button("🛡️ Security Analysis", use_container_width=True):
                st.session_state.page = "security"
                st.rerun()

        with c2:
            if st.button("💳 Fraud Detection", use_container_width=True):
                st.session_state.page = "fraud"
                st.rerun()

        with c3:
            if st.button("💰 Expense Tracker", use_container_width=True):
                st.session_state.page = "expense"
                st.rerun()

        with c4:
            if st.button("🏦 Loan Risk Check", use_container_width=True):
                st.session_state.page = "loan"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ================= SECOND ROW =================
        c5, c6, c7, c8 = st.columns(4)

        with c5:
            if st.button("📊 AI Finance Report", use_container_width=True):
                st.session_state.page = "report"
                st.rerun()

        with c6:
            if st.button("💱 Currency Prediction", use_container_width=True):
                st.session_state.page = "currency"
                st.rerun()

        with c7:
            if st.button("📈 Stock Prediction", use_container_width=True):
                st.session_state.page = "stock"
                st.rerun()

        with c8:
            if st.button("🤖 AI Chatbot", use_container_width=True):
                st.session_state.page = "chatbot"
                st.rerun()

        st.markdown("---")

        # ================= LOGOUT =================
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "home"
            st.rerun()

    # ================= SECURITY PAGE =================
    elif st.session_state.page == "security":

        st.markdown("## 🛡️ Login Security Prediction")

        failed_attempts = st.number_input("Failed Login Attempts", 0, 50, 0)
        login_hour = st.slider("Login Hour", 0, 23, 12)
        unknown_device = st.selectbox("Unknown Device", ["No", "Yes"])

        if st.button("🔍 Analyze Login Security"):

            unknown_device_value = 1 if unknown_device == "Yes" else 0

            input_data = pd.DataFrame(
                [[failed_attempts, login_hour, unknown_device_value]],
                columns=["failed_attempts", "login_hour", "unknown_device"]
            )

            prediction = model.predict(input_data)[0]

            if prediction == 0:
                st.markdown("<div class='safe-box'>✅ SAFE LOGIN DETECTED</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='danger-box'>⚠️ SUSPICIOUS LOGIN DETECTED</div>", unsafe_allow_html=True)

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # ================= FRAUD PAGE =================
    elif st.session_state.page == "fraud":

        st.markdown("## 💳 Fraud Detection")

        merchant = st.selectbox("Merchant", list(encoders["merchant"].classes_))
        category = st.selectbox("Category", list(encoders["category"].classes_))
        gender = st.selectbox("Gender", list(encoders["gender"].classes_))
        state = st.selectbox("State", list(encoders["state"].classes_))

        cc_num = st.number_input("cc_num", value=123456789)
        amt = st.number_input("amt", value=100.0)
        zip_code = st.number_input("zip", value=10001)
        lat = st.number_input("lat", value=40.0)
        long_val = st.number_input("long", value=-74.0)
        city_pop = st.number_input("city_pop", value=50000)
        unix_time = st.number_input("unix_time", value=1700000000)
        merch_lat = st.number_input("merch_lat", value=40.5)
        merch_long = st.number_input("merch_long", value=-73.5)
        year = st.number_input("year", value=2024)
        month = st.number_input("month", value=1)
        day = st.number_input("day", value=1)
        hour = st.slider("hour", 0, 23, 12)

        if st.button("🔍 Detect Fraud"):

            input_data = pd.DataFrame([[
                cc_num,
                encoders["merchant"].transform([merchant])[0],
                encoders["category"].transform([category])[0],
                amt,
                encoders["gender"].transform([gender])[0],
                encoders["state"].transform([state])[0],
                zip_code,
                lat,
                long_val,
                city_pop,
                unix_time,
                merch_lat,
                merch_long,
                year,
                month,
                day,
                hour
            ]], columns=[
                'cc_num','merchant','category','amt','gender','state',
                'zip','lat','long','city_pop','unix_time',
                'merch_lat','merch_long','year','month','day','hour'
            ])

            prediction = fraud_model.predict(input_data)[0]

            if prediction == 1:
                st.error("⚠ Fraud Detected")
            else:
                st.success("✅ Genuine Transaction")

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # ================= 💰 EXPENSE TRACKER =================
    elif st.session_state.page == "expense":

        st.markdown("## 💰 Expense Tracker (MySQL)")

        conn = get_mysql_connection()
        cur = conn.cursor()

        amount = st.number_input("Amount")
        category = st.text_input("Category")
        t_type = st.selectbox("Type", ["Income", "Expense"])
        date = st.date_input("Date")
        note = st.text_area("Note")

        if st.button("Add Transaction"):
            sql = """
            INSERT INTO transactions (amount, category, type, date, note)
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(sql, (amount, category, t_type, date, note))
            conn.commit()
            st.success("Transaction Added!")

        st.subheader("📄 Transactions")

        df = pd.read_sql("SELECT * FROM transactions", conn)
        st.dataframe(df)

        income = df[df["type"].str.lower() == "income"]["amount"].sum()
        expense = df[df["type"].str.lower() == "expense"]["amount"].sum()

        st.metric("Income", income)
        st.metric("Expense", expense)
        st.metric("Balance", income - expense)

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # ================= LOAN RISK CHECK =================
    elif st.session_state.page == "loan":

        st.markdown("## 🏦 Loan Risk Prediction")

        income = st.number_input("Income", value=50000)
        loan_amount = st.number_input("Loan Amount", value=300000)
        interest_rate = st.number_input("Interest Rate (%)", value=10.0)
        tenure = st.number_input("Tenure (Years)", value=5)
        emi = st.number_input("EMI", value=6500)

        if st.button("🔍 Check Loan Risk"):

            input_data = pd.DataFrame([[
                income,
                loan_amount,
                interest_rate,
                tenure,
                emi
            ]], columns=[
                "income", "loan_amount", "interest_rate", "tenure", "emi"
            ])

            prediction = loan_model.predict(input_data)[0]

            if prediction == 0:
                st.success("✅ SAFE LOAN APPROVED")
                st.markdown("### 🟢 Low Risk Customer")
            else:
                st.error("❌ HIGH RISK LOAN")
                st.markdown("### 🔴 Loan Rejected Risky Profile")

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # ================= AI FINANCE REPORT =================
    elif st.session_state.page == "report":

        st.markdown("## 📊 AI Finance Report Generator")

        # Load CSVs (same as your model)
        expense_data = pd.read_csv(r"C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 2\\expense_history.csv")
        fraud_data = pd.read_csv(r"C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 1\\fraudTest.csv")
        loan_data = pd.read_csv(r"C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 5\\CEAS_08.csv")

        total_expense = expense_data["Amount"].sum()

        fraud_cases = 0
        if "Result" in fraud_data.columns:
            fraud_cases = (fraud_data["Result"] == "Fraud").sum()

        high_risk_loans = 0
        if "Risk" in loan_data.columns:
            high_risk_loans = (loan_data["Risk"] == "High").sum()

        summary = []

        if total_expense > 10000:
            summary.append("High spending detected.")

        if fraud_cases > 0:
            summary.append("Fraud transactions found.")

        if high_risk_loans > 0:
            summary.append("High loan risk users detected.")

        if not summary:
            summary.append("Financial activity is normal.")

        summary_text = "\n".join(summary)

        st.metric("Total Expense", total_expense)
        st.metric("Fraud Cases", fraud_cases)
        st.metric("High Risk Loans", high_risk_loans)

        st.subheader("📌 Summary")
        st.write(summary_text)

        # Chart
        plt.figure()
        expense_data.groupby("Category")["Amount"].sum().plot(kind="bar")
        plt.title("Expense Analysis")
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()

        st.image("chart.png")

        # PDF Generator
        def create_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            pdf.cell(200, 10, "AI FINANCE REPORT", ln=True)
            pdf.ln(5)

            pdf.cell(200, 10, f"Total Expense: {total_expense}", ln=True)
            pdf.cell(200, 10, f"Fraud Cases: {fraud_cases}", ln=True)
            pdf.cell(200, 10, f"High Risk Loans: {high_risk_loans}", ln=True)

            pdf.ln(10)
            pdf.multi_cell(0, 10, summary_text)

            pdf.image("chart.png", x=10, y=120, w=180)

            return pdf.output(dest="S")

        if st.button("📄 Generate PDF Report"):
            pdf_data = create_pdf()

            with open("AI_Report.pdf", "wb") as f:
                f.write(pdf_data)

            st.success("PDF Generated Successfully!")

            with open("AI_Report.pdf", "rb") as f:
                st.download_button(
                    "⬇ Download PDF",
                    f,
                    file_name="AI_Report.pdf"
                )

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # ================= CURRENCY PREDICTION =================
    elif st.session_state.page == "currency":

        st.markdown("## 💱 USD → INR Exchange Rate Prediction")

        date_input = st.date_input("Select Date")

        if st.button("📊 Predict Exchange Rate"):

            import pandas as pd

            future_date = pd.to_datetime(date_input)

            days = (future_date - base_date).days

            prediction = currency_model.predict([[days]])[0]

            st.success(f"📅 Date: {date_input}")
            st.success(f"💱 Predicted USD → INR Rate: {round(prediction, 2)}")

        # ================= OPTIONAL CHART =================
        st.subheader("📈 Trend Visualization")

        df = pd.read_csv("C:\\Users\\user\\Desktop\\Dakshita_04\\Work\\Model 8\\USD_INR_Exchange.csv")
        df["Date"] = pd.to_datetime(df["Date"])
        df["Days"] = (df["Date"] - df["Date"].min()).dt.days

        target = "Rate" if "Rate" in df.columns else "Close"

        X = df[["Days"]]
        df["Predicted"] = currency_model.predict(X)

        st.line_chart(df.set_index("Date")[["Predicted"]])

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()


    # ================= STOCK PREDICTION =================
    elif st.session_state.page == "stock":

        st.markdown("## 📈 Stock Price Prediction")

        stock = st.text_input("Enter Stock Symbol", "AAPL")

        if st.button("Predict Stock"):

            try:

                data = yf.download(stock, period="6mo")

                if data.empty:
                    st.error("No data found.")
                else:

                    st.subheader("Current Stock Information")

                    st.write(
                        f"Current Price: {round(float(data['Close'].iloc[-1]),2)}"
                    )

                    st.write(
                        f"Highest Price: {round(float(data['High'].max()),2)}"
                    )

                    st.write(
                        f"Lowest Price: {round(float(data['Low'].min()),2)}"
                    )

                    st.write(
                        f"Average Volume: {int(data['Volume'].mean())}"
                    )

                    # Prepare Data
                    stock_df = data[['Close']].copy()
                    stock_df['Days'] = np.arange(len(stock_df))

                    X = stock_df[['Days']]
                    y = stock_df['Close']

                    model = LinearRegression()
                    model.fit(X, y)

                    next_day = np.array([[len(stock_df)]])
                    prediction = model.predict(next_day)

                    st.success(
                        f"Predicted Next Day Price: ₹{round(float(prediction[0]),2)}"
                    )

                    # Price Chart
                    fig, ax = plt.subplots(figsize=(10,5))

                    ax.scatter(
                        stock_df['Days'],
                        stock_df['Close'],
                        label="Actual Price"
                    )

                    ax.plot(
                        stock_df['Days'],
                        model.predict(X),
                        color='red',
                        label="Prediction Line"
                    )

                    ax.legend()
                    ax.set_title("Stock Price Prediction")

                    st.pyplot(fig)

                    # Closing Price Chart
                    fig2, ax2 = plt.subplots(figsize=(10,5))

                    ax2.plot(
                        data.index,
                        data['Close']
                    )

                    ax2.set_title(f"{stock} Closing Price")

                    st.pyplot(fig2)

                    # Moving Average
                    stock_df['MA20'] = (
                        stock_df['Close']
                        .rolling(20)
                        .mean()
                    )

                    fig3, ax3 = plt.subplots(figsize=(10,5))

                    ax3.plot(
                        stock_df['Close'],
                        label="Close"
                    )

                    ax3.plot(
                        stock_df['MA20'],
                        label="MA20"
                    )

                    ax3.legend()

                    st.pyplot(fig3)

                    # Daily Returns
                    stock_df['Daily Return'] = (
                        stock_df['Close']
                        .pct_change()
                    )

                    fig4, ax4 = plt.subplots(figsize=(10,5))

                    stock_df['Daily Return'].hist(
                        bins=50,
                        ax=ax4
                    )

                    ax4.set_title(
                        "Daily Return Distribution"
                    )

                    st.pyplot(fig4)

                    # Investment Calculator
                    investment = st.number_input(
                        "Investment Amount",
                        value=10000
                    )

                    first_price = float(data['Close'].iloc[0])
                    last_price = float(data['Close'].iloc[-1])

                    shares = investment / first_price

                    final_value = shares * last_price

                    profit = final_value - investment

                    st.metric(
                        "Final Value",
                        round(final_value,2)
                    )

                    st.metric(
                        "Profit/Loss",
                        round(profit,2)
                    )

                    # Save Model
                    with open(
                        "stock_model.pkl",
                        "wb"
                    ) as file:
                        pickle.dump(model, file)

            except Exception as e:
                st.error(str(e))

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()

    # ================= CHATBOT =================
    elif st.session_state.page == "chatbot":

        st.markdown("## 🤖 AI Assistant")

        st.info("Ask anything about finance, loans, fraud, stocks, business, coding, etc.")

        # Display previous messages
        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Type your question...")

        if prompt:

            # User Message
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            # Basic Rule-Based Responses
            user_text = prompt.lower()

            if "loan" in user_text:
                response = """
                Loan risk depends on:
                - Income
                - EMI
                - Loan Amount
                - Interest Rate
                """

            elif "fraud" in user_text:
                response = """
                Fraud transactions often show:
                - Unusual amount
                - New merchant
                - Suspicious location
                """

            elif "stock" in user_text:
                response = """
                Stock prices depend on:
                - Market trends
                - Company earnings
                - Investor sentiment
                """

            elif "expense" in user_text:
                response = """
                Track expenses regularly and keep
                spending lower than income.
                """

            elif "hello" in user_text or "hi" in user_text:
                response = f"Hello {st.session_state.username}! 👋"

            else:
                response = """
                I am your AI Finance Assistant.

                I can help with:
                - Fraud Detection
                - Loan Risk
                - Expense Tracking
                - Currency Prediction
                - Stock Analysis
                - Coding Questions
                """

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            with st.chat_message("assistant"):
                st.markdown(response)

        if st.button("🗑 Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        if st.button("⬅ Back"):
            st.session_state.page = "home"
            st.rerun()    