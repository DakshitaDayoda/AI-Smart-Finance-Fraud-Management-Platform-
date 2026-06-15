# s.py
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
import plotly.graph_objects as go


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

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"]{
    font-family:'Poppins',sans-serif;
}

/* Main App */
.stApp{
    background:
    radial-gradient(circle at top right,
    rgba(124,58,237,.18),
    transparent 30%),

    radial-gradient(circle at bottom left,
    rgba(168,85,247,.12),
    transparent 30%),

    #0b1020;

    color:white;
}

/* Hide Streamlit Menu */
#MainMenu,
footer{
    visibility:hidden;
}

/* Main Container */
.block-container{
    padding-top:4rem !important;
    padding-left:2rem;
    padding-right:2rem;
    max-width:95%;
}

/* Titles */
h1{
    font-weight:800 !important;
    letter-spacing:-1px;
}

h2{
    font-weight:700 !important;
}

h3{
    font-weight:600 !important;
}

/* KPI Cards */
div[data-testid="metric-container"]{
    background:rgba(20,25,50,.85);
    border:1px solid rgba(168,85,247,.2);
    border-radius:24px;
    padding:22px;
    backdrop-filter:blur(12px);

    box-shadow:
    0 0 25px rgba(124,58,237,.15);

    transition:.3s;
}

div[data-testid="metric-container"]:hover{
    transform:translateY(-4px);

    box-shadow:
    0 0 35px rgba(168,85,247,.35);
}

/* Buttons */
.stButton > button{
    width:100%;
    height:58px;

    border:none;
    border-radius:18px;

    background:
    linear-gradient(
    135deg,
    #6D28D9,
    #8B5CF6
    );

    color:white;
    font-size:15px;
    font-weight:600;

    transition:.3s;
}

.stButton > button:hover{
    transform:translateY(-3px);

    box-shadow:
    0 0 30px rgba(168,85,247,.55);
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:
    linear-gradient(
    180deg,
    #0B1020,
    #131B35
    );

    border-right:
    1px solid rgba(168,85,247,.15);
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input{
    background:#161B33;
    color:white;

    border-radius:15px;

    border:1px solid
    rgba(168,85,247,.25);
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"]{
    background:#161B33;
    border-radius:15px;
}

/* Dataframe */
[data-testid="stDataFrame"]{
    border-radius:20px;
    overflow:hidden;
    border:1px solid rgba(168,85,247,.2);
}

/* Chat Messages */
[data-testid="stChatMessage"]{
    background:rgba(20,25,50,.85);

    border-radius:18px;

    border:1px solid rgba(168,85,247,.15);

    padding:12px;
}

/* Success Box */
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

/* Danger Box */
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

/* Glass Card */
.glass-card{
    background:
    rgba(20,25,50,.72);

    backdrop-filter:blur(18px);

    border:
    1px solid rgba(168,85,247,.15);

    border-radius:30px;

    padding:30px;

    box-shadow:
    0 0 30px rgba(124,58,237,.15);

    transition:.3s;
}

.glass-card:hover{
    transform:translateY(-5px);

    box-shadow:
    0 0 40px rgba(168,85,247,.35);
}

/* Finance Card */
.fin-card{
    background:
    linear-gradient(
    145deg,
    rgba(25,25,45,.95),
    rgba(15,15,35,.95)
    );

    border-radius:28px;

    border:
    1px solid rgba(168,85,247,.15);

    box-shadow:
    0 0 25px rgba(124,58,237,.18),
    0 0 60px rgba(124,58,237,.08);

    padding:25px;

    backdrop-filter:blur(20px);
}

/* Animations */
@keyframes fadeUp{
    from{
        opacity:0;
        transform:translateY(20px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }
}

.glass-card,
.fin-card,
div[data-testid="metric-container"]{
    animation:fadeUp .7s ease;
}

/* ================= EXTRA PREMIUM THEME ================= */

/* Premium Buttons */
.stButton > button{
    background:linear-gradient(
        135deg,
        #5B21B6 0%,
        #7C3AED 50%,
        #A855F7 100%
    ) !important;

    color:white !important;

    font-weight:700 !important;

    letter-spacing:.5px;

    box-shadow:
        0 0 15px rgba(124,58,237,.35);

    transition:all .3s ease !important;
}

.stButton > button:hover{

    background:linear-gradient(
        135deg,
        #6D28D9,
        #8B5CF6,
        #C084FC
    ) !important;

    transform:
        translateY(-4px)
        scale(1.02);

    box-shadow:
        0 0 35px rgba(168,85,247,.65);
}

/* KPI Cards */
div[data-testid="metric-container"]{

    border-left:
    4px solid #A855F7 !important;

    background:
    linear-gradient(
        145deg,
        rgba(25,25,45,.95),
        rgba(15,15,35,.95)
    ) !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{

    background:
    linear-gradient(
        180deg,
        #0B1020,
        #131B35
    ) !important;

    box-shadow:
        5px 0 30px rgba(168,85,247,.12);
}

/* Sidebar Text */
section[data-testid="stSidebar"] label{
    color:white !important;
    font-weight:600 !important;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input{

    background:
    rgba(22,27,51,.95) !important;

    border:
    1px solid rgba(168,85,247,.25) !important;

    border-radius:15px !important;

    box-shadow:
    inset 0 0 10px rgba(168,85,247,.05);
}

/* Input Focus */
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus{

    border-color:#A855F7 !important;

    box-shadow:
    0 0 15px rgba(168,85,247,.45) !important;
}

/* Select Box */
.stSelectbox div[data-baseweb="select"]{

    background:#161B33 !important;

    border-radius:15px !important;

    border:
    1px solid rgba(168,85,247,.20);
}

/* Glass Card Upgrade */
.glass-card{

    background:
    linear-gradient(
        145deg,
        rgba(22,27,51,.92),
        rgba(15,20,35,.92)
    ) !important;

    border:
    1px solid rgba(168,85,247,.15);

    box-shadow:
    0 0 30px rgba(124,58,237,.20);

    position:relative;
}

/* Animated Border */
.glass-card::after{

    content:"";

    position:absolute;

    inset:0;

    border-radius:30px;

    padding:1px;

    background:
    linear-gradient(
        135deg,
        transparent,
        rgba(168,85,247,.5),
        transparent
    );

    -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);

    -webkit-mask-composite:xor;

    pointer-events:none;
}

/* Heading Glow */
h1,h2,h3{

    text-shadow:
    0 0 12px rgba(168,85,247,.25);
}

/* Text Selection */
::selection{

    background:#A855F7;

    color:white;
}

/* Premium Divider */
hr{

    border:none;

    height:1px;

    background:
    linear-gradient(
        90deg,
        transparent,
        rgba(168,85,247,.4),
        transparent
    );
}
            
/* ================= PREMIUM UI UPGRADE ================= */

/* Animated Background */
.stApp{
    background-size:400% 400%;
    animation:bgmove 15s ease infinite;
}

@keyframes bgmove{
    0%{background-position:0% 50%;}
    50%{background-position:100% 50%;}
    100%{background-position:0% 50%;}
}

/* Premium Scrollbar */
::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-track{
    background:#111827;
}

::-webkit-scrollbar-thumb{
    background:#7C3AED;
    border-radius:20px;
}

::-webkit-scrollbar-thumb:hover{
    background:#A855F7;
}

/* Glass Floating Effect */
.glass-card,
.fin-card{
    position:relative;
    overflow:hidden;
}

.glass-card::before,
.fin-card::before{
    content:"";
    position:absolute;
    top:-50%;
    left:-50%;
    width:200%;
    height:200%;

    background:
    linear-gradient(
        45deg,
        transparent,
        rgba(255,255,255,.04),
        transparent
    );

    transform:rotate(25deg);
    pointer-events:none;
}

/* Premium Glass Glow */
.glass-card{
    box-shadow:
        0 0 20px rgba(168,85,247,.20),
        0 0 40px rgba(168,85,247,.08),
        inset 0 0 1px rgba(255,255,255,.15);
}

/* Sidebar Glow */
section[data-testid="stSidebar"]{
    box-shadow:
        5px 0 30px rgba(168,85,247,.12);

    backdrop-filter:blur(25px);
}

/* KPI Shine Effect */
div[data-testid="metric-container"]{
    position:relative;
    overflow:hidden;
}

div[data-testid="metric-container"]::before{
    content:"";

    position:absolute;
    top:-120%;
    left:-50%;

    width:60%;
    height:300%;

    background:
    linear-gradient(
        rgba(255,255,255,0),
        rgba(255,255,255,.08),
        rgba(255,255,255,0)
    );

    transform:rotate(25deg);
}

/* Better KPI Hover */
div[data-testid="metric-container"]:hover{
    transform:translateY(-5px);

    box-shadow:
        0 0 35px rgba(168,85,247,.40);
}

/* Input Focus Glow */
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus{

    border-color:#A855F7 !important;

    box-shadow:
        0 0 15px rgba(168,85,247,.40) !important;
}

/* Selectbox Focus */
.stSelectbox{
    transition:.3s;
}

/* Better Button Hover */
.stButton > button:hover{
    transform:
        translateY(-4px)
        scale(1.02);

    box-shadow:
        0 0 35px rgba(168,85,247,.60);
}

/* Glass Card Hover */
.glass-card:hover,
.fin-card:hover{

    transform:
        translateY(-6px)
        scale(1.01);

    transition:.35s;

    box-shadow:
        0 0 50px rgba(168,85,247,.30);
}

/* Fade Animation */
@keyframes fadeUp{
    from{
        opacity:0;
        transform:translateY(20px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }
}

.glass-card,
.fin-card,
div[data-testid="metric-container"]{
    animation:fadeUp .7s ease;
}

/* Text Glow */
h1,h2{
    text-shadow:
        0 0 15px rgba(168,85,247,.20);
}

/* Premium Divider */
hr{
    border:none;
    height:1px;

    background:
    linear-gradient(
        90deg,
        transparent,
        rgba(168,85,247,.4),
        transparent
    );
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
    return joblib.load("login_security_model.pkl")

@st.cache_resource
def load_fraud_model():
    return joblib.load("fraud_model.pkl")

@st.cache_resource
def load_encoders():
    return joblib.load("encoders.pkl")

@st.cache_resource
def load_loan_model():
    return joblib.load("loan_risk_model.pkl")

@st.cache_resource
def load_currency_model():
    return joblib.load("currency_model.pkl")

@st.cache_resource
def load_base_date():
    return joblib.load("base_date.pkl")

@st.cache_resource
def load_stock_model():
    with open("stock_model.pkl", "rb") as f:
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

    st.sidebar.image(
        "https://cdn-icons-png.flaticon.com/512/2092/2092063.png", 
        width=100
    )

    st.sidebar.markdown("### AI Financial Intelligence")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio("Navigation", ["Sign In", "Sign Up"])


    if menu == "Sign Up":

        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            st.markdown("""<div class="glass-card">
                        <h1 style="text-align:center;color:white;">📝 Create New Account</h1>
                    </div>""", unsafe_allow_html=True)


            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Create Account", use_container_width=True):
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

            st.markdown('</div>', unsafe_allow_html=True)

    else:

        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            st.markdown("""<div class="glass-card">
                        <h1 style="text-align:center;color:white;">🔑 Login</h1>
                    </div>""", unsafe_allow_html=True)


            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Sign In", use_container_width=True):
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

            st.markdown('</div>', unsafe_allow_html=True)

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

        # ================= FINANCIAL TREND =================
        left,right = st.columns([3,1])

        with left:

            st.markdown("""
            <div style="
            background:rgba(20,25,50,.75);
            padding:25px;
            border-radius:25px;
            border:1px solid rgba(168,85,247,.15);
            box-shadow:0 0 30px rgba(124,58,237,.15);
            ">
            <h2 style="
            color:white;
            text-align:center;
            ">
            📈 FINANCIAL TREND
            </h2>
            </div>
            """, unsafe_allow_html=True)

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                    y=[12,15,13,18,16,22,25],
                    mode="lines",
                    name="Income",
                    line=dict(
                        color="#8B5CF6",
                        width=5,
                        shape="spline"
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(139,92,246,0.12)"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                    y=[18,16,14,15,13,12,10],
                    mode="lines",
                    name="Expense",
                    line=dict(
                        color="#F9A8D4",
                        width=5,
                        shape="spline"
                    ),
                    fill="tonexty",
                    fillcolor="rgba(249,168,212,0.08)"
                )
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=420,

                legend=dict(
                    orientation="h",
                    y=-0.15
                ),

                font=dict(color="white"),

                xaxis=dict(showgrid=False),

                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.08)"
                ),

                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10
                )
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        with right:

            st.markdown("""
            <div style="
            background:rgba(20,25,50,.75);
            padding:12px;
            border-radius:25px;
            height:190px;
            border:1px solid rgba(168,85,247,.15);
            box-shadow:0 0 25px rgba(124,58,237,.20);
            ">

            <h2 style="
            text-align:center;
            color:white;
            ">
            📊 FINANCIAL INSIGHTS
            </h2>

            <div style="height:15px;"></div>

            <div style="
            background:rgba(124,58,237,.12);
            padding:8px;
            border-radius:15px;
            margin-bottom:10px;
            ">
            <b style="color:#A855F7;">📈 Growth</b>
            <p style="color:white;margin:5px 0;">68%</p>
            </div>

            <div style="
            background:rgba(16,185,129,.12);
            padding:8px;
            border-radius:15px;
            margin-bottom:10px;
            ">
            <b style="color:#10B981;margin:0;">💰 Revenue</b>
            <p style="color:white;margin:3px 0;">₹4.5L</p>
            </div>

            <div style="
            background:rgba(245,158,11,.12);
            padding:8px;
            border-radius:15px;
            ">
            <b style="color:#F59E0B;margin:0;">🎁 Bonus</b>
            <p style="color:white;margin:3px 0;">₹61K</p>
            </div>

            </div>
            """, unsafe_allow_html=True)


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
