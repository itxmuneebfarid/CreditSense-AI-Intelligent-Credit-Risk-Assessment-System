import streamlit as st
import pandas as pd
import numpy as np
import joblib
import uuid
import logging
from datetime import datetime
from pathlib import Path

# ===========================================================
# PAGE CONFIG
# ===========================================================
st.set_page_config(
    page_title="Credit Risk Assessment",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MODEL_PATH = Path(__file__).with_name("my_model.pkl")

# ===========================================================
# GLOBAL STYLES
# ===========================================================
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at 10% 10%, #0f1729 0%, #0a0e1a 55%, #06090f 100%);
        color: #e7ecf5;
    }

    section[data-testid="stSidebar"] {
        background: #0b111f;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1100px; }

    h1, h2, h3, h4 { color: #f2f5fb !important; letter-spacing: -0.02em; }

    /* ---------- Cards ---------- */
    .glass-card {
        background: linear-gradient(155deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 28px 30px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    }

    .metric-card {
        background: linear-gradient(155deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 22px;
        text-align: left;
        transition: transform .15s ease, border-color .15s ease;
    }
    .metric-card:hover { transform: translateY(-3px); border-color: rgba(120,160,255,0.35); }
    .metric-label { font-size: 0.78rem; color: #93a1bd; text-transform: uppercase; letter-spacing: .08em; }
    .metric-value { font-size: 1.9rem; font-weight: 700; margin-top: 4px; }

    .pill {
        display: inline-block; padding: 4px 12px; border-radius: 999px;
        font-size: 0.75rem; font-weight: 600; letter-spacing: .03em;
    }
    .pill-low { background: rgba(46,204,113,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.35); }
    .pill-mod { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.35); }
    .pill-high { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.35); }

    /* ---------- Buttons ---------- */
    .stButton>button {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.12);
        background: linear-gradient(135deg, #3b6fe0, #6a4fe0);
        color: white;
        font-weight: 600;
        padding: 0.55rem 1.2rem;
        transition: all .15s ease;
    }
    .stButton>button:hover {
        border-color: rgba(255,255,255,0.3);
        box-shadow: 0 6px 18px rgba(90,100,230,0.35);
        transform: translateY(-1px);
    }

    .step-track { display:flex; gap:6px; margin-bottom: 26px; }
    .step-dot { height:6px; flex:1; border-radius: 4px; background: rgba(255,255,255,0.08); }
    .step-dot.active { background: linear-gradient(90deg,#3b6fe0,#6a4fe0); }

    /* ---------- Receipt ---------- */
    .receipt {
        background: #0d1220;
        border: 1px dashed rgba(255,255,255,0.25);
        border-radius: 14px;
        padding: 30px 34px;
        font-family: 'Courier New', monospace;
        color: #d6ddec;
        max-width: 560px;
        margin: 0 auto;
    }
    .receipt hr { border: none; border-top: 1px dashed rgba(255,255,255,0.25); margin: 14px 0; }
    .receipt-row { display:flex; justify-content: space-between; font-size: 0.92rem; margin: 4px 0; }
    .receipt-title { text-align:center; font-size: 1.05rem; font-weight: 700; letter-spacing: .08em; }
    .receipt-sub { text-align:center; color: #93a1bd; font-size: 0.75rem; margin-bottom: 6px; }

    .brand-title {
        font-size: 2.1rem; font-weight: 800;
        background: linear-gradient(135deg, #7fa8ff, #b98fff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .muted { color: #93a1bd; }
</style>
""", unsafe_allow_html=True)

# ===========================================================
# SESSION STATE INIT
# ===========================================================
defaults = {
    "page": "login",
    "logged_in": False,
    "username": "",
    "applicant": {},
    "history": [],          # list of past assessments this session
    "last_result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def go(page):
    st.session_state.page = page
    st.rerun()

# ===========================================================
# MODEL LOADING
# ===========================================================
@st.cache_resource
def load_model():
    try:
        if MODEL_PATH.exists():
            return joblib.load(MODEL_PATH), None
        return None, f"Model file not found at {MODEL_PATH.absolute()}"
    except Exception as exc:
        return None, str(exc)

# ===========================================================
# PAGE: LOGIN
# ===========================================================
def render_login():
    left, mid, right = st.columns([1, 1.3, 1])
    with mid:
        st.markdown("<div style='text-align:center; margin-bottom: 28px;'>", unsafe_allow_html=True)
        st.markdown("<div class='brand-title'>💳 CreditSense</div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>Sign in to access the risk assessment console</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="admin")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                remember = st.checkbox("Remember me", value=True)
                submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if username.strip() == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    go("dashboard")
                else:
                    st.error("Invalid username or password.")

            st.markdown(
                "<p class='muted' style='font-size:0.78rem; margin-top:10px;'>"
                "Demo credentials — username: <b>admin</b> &nbsp;|&nbsp; password: <b>admin123</b></p>",
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

# ===========================================================
# SIDEBAR (shown once logged in)
# ===========================================================
def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 👋 {st.session_state.username or 'User'}")
        st.caption("Credit Risk Analyst")
        st.markdown("---")
        if st.button("📊 Dashboard", use_container_width=True):
            go("dashboard")
        if st.button("📝 New Assessment", use_container_width=True):
            st.session_state.applicant = {}
            go("details")
        if st.button("ℹ️ About", use_container_width=True):
            go("about")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

# ===========================================================
# PAGE: DASHBOARD
# ===========================================================
def render_dashboard():
    st.markdown("<div class='brand-title'>Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Overview of your assessment activity this session</p>", unsafe_allow_html=True)
    st.write("")

    history = st.session_state.history
    total = len(history)
    high = sum(1 for h in history if h["level"] == "HIGH")
    mod = sum(1 for h in history if h["level"] == "MODERATE")
    low = sum(1 for h in history if h["level"] == "LOW")
    avg_risk = np.mean([h["prob"] for h in history]) * 100 if history else 0.0

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Total Assessments", f"{total}"),
        (c2, "Low Risk", f"{low}"),
        (c3, "Moderate Risk", f"{mod}"),
        (c4, "High Risk", f"{high}"),
    ]
    for col, label, value in cards:
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{label}</div>"
                f"<div class='metric-value'>{value}</div></div>",
                unsafe_allow_html=True
            )

    st.write("")
    colA, colB = st.columns([1.4, 1])

    with colA:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Average Predicted Default Risk")
        st.progress(min(float(avg_risk) / 100, 1.0))
        st.write(f"**{avg_risk:.2f}%** across {total} assessment(s) this session.")
        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Quick Action")
        st.write("Start a new applicant evaluation.")
        if st.button("➕ Start New Assessment", use_container_width=True):
            st.session_state.applicant = {}
            go("details")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Recent Assessments")
    if not history:
        st.caption("No assessments yet — run your first one to see it here.")
    else:
        df_hist = pd.DataFrame([
            {
                "Receipt ID": h["receipt_id"],
                "Time": h["timestamp"],
                "Loan Amount": f"${h['loan_amnt']:,.0f}",
                "Risk %": f"{h['prob']*100:.2f}%",
                "Level": h["level"],
            } for h in reversed(history)
        ])
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ===========================================================
# PAGE: APPLICANT DETAILS
# ===========================================================
def render_details():
    st.markdown("<div class='step-track'>"
                 "<div class='step-dot active'></div>"
                 "<div class='step-dot active'></div>"
                 "<div class='step-dot'></div>"
                 "</div>", unsafe_allow_html=True)
    st.markdown("### 📝 Applicant & Loan Details")
    st.caption("Step 3 of 5 — fill in the applicant profile to run the risk model")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    with st.form("details_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**👤 Applicant Profile**")
            person_age = st.number_input("Age", min_value=18, max_value=100, value=28, step=1)
            person_income = st.number_input("Annual Income ($)", min_value=0.0, value=55000.0, step=1000.0)
            person_emp_length = st.number_input("Employment Length (Years)", min_value=0.0, max_value=60.0, value=3.0, step=0.5)
            person_home_ownership = st.selectbox("Home Ownership", ["RENT", "OWN", "MORTGAGE", "OTHER"])

        with col2:
            st.markdown("**💰 Loan Information**")
            loan_amnt = st.number_input("Requested Loan Amount ($)", min_value=500.0, value=10000.0, step=500.0)
            loan_int_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=40.0, value=11.0, step=0.1)
            loan_intent = st.selectbox("Loan Intent", ["EDUCATION", "HOMEIMPROVEMENT", "MEDICAL", "PERSONAL", "VENTURE", "DEBTCONSOLIDATION"])

        with col3:
            st.markdown("**📜 Credit History**")
            loan_grade = st.selectbox("Loan Grade", ["A", "B", "C", "D", "E", "F", "G"])
            cb_person_default_on_file = st.selectbox("Historical Default on File?", ["N", "Y"])
            applicant_name = st.text_input("Applicant Name (for receipt)", placeholder="John Doe")

        submitted = st.form_submit_button("Continue to Risk Assessment →", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        st.session_state.applicant = {
            "applicant_name": applicant_name.strip() or "N/A",
            "person_age": person_age,
            "person_income": person_income,
            "person_emp_length": person_emp_length,
            "person_home_ownership": person_home_ownership,
            "loan_amnt": loan_amnt,
            "loan_int_rate": loan_int_rate,
            "loan_intent": loan_intent,
            "loan_grade": loan_grade,
            "cb_person_default_on_file": cb_person_default_on_file,
        }
        go("result")

    if st.button("← Back to Dashboard"):
        go("dashboard")

# ===========================================================
# PREDICTION LOGIC
# ===========================================================
def run_prediction(model, a):
    loan_percent_income = a["loan_amnt"] / a["person_income"] if a["person_income"] > 0 else 0.0

    raw_data = {
        'person_age': float(a["person_age"]),
        'person_income': float(a["person_income"]),
        'person_emp_length': float(a["person_emp_length"]),
        'loan_amnt': float(a["loan_amnt"]),
        'loan_int_rate': float(a["loan_int_rate"]),
        'loan_percent_income': float(loan_percent_income),
        'cb_person_default_on_file_Y': 1.0 if a["cb_person_default_on_file"] == "Y" else 0.0,
    }

    model_features = [
        'person_age', 'person_income', 'person_emp_length', 'loan_amnt',
        'loan_int_rate', 'loan_percent_income', 'cb_person_default_on_file_Y',
        'person_home_ownership_OTHER', 'person_home_ownership_OWN', 'person_home_ownership_RENT',
        'loan_intent_EDUCATION', 'loan_intent_HOMEIMPROVEMENT', 'loan_intent_MEDICAL',
        'loan_intent_PERSONAL', 'loan_intent_VENTURE',
        'loan_grade_B', 'loan_grade_C', 'loan_grade_D', 'loan_grade_E', 'loan_grade_F', 'loan_grade_G'
    ]

    raw_data['person_home_ownership_OTHER'] = 1.0 if a["person_home_ownership"] == 'OTHER' else 0.0
    raw_data['person_home_ownership_OWN'] = 1.0 if a["person_home_ownership"] == 'OWN' else 0.0
    raw_data['person_home_ownership_RENT'] = 1.0 if a["person_home_ownership"] == 'RENT' else 0.0

    for intent in ['EDUCATION', 'HOMEIMPROVEMENT', 'MEDICAL', 'PERSONAL', 'VENTURE']:
        raw_data[f'loan_intent_{intent}'] = 1.0 if a["loan_intent"] == intent else 0.0

    for grade in ['B', 'C', 'D', 'E', 'F', 'G']:
        raw_data[f'loan_grade_{grade}'] = 1.0 if a["loan_grade"] == grade else 0.0

    input_df = pd.DataFrame([raw_data])[model_features].astype('float32')
    probabilities = model.predict_proba(input_df.to_numpy())[0]
    return float(probabilities[1])

# ===========================================================
# PAGE: RESULT + DIGITAL RECEIPT
# ===========================================================
def render_result():
    a = st.session_state.applicant
    if not a:
        st.warning("No applicant data found. Please fill in the details form first.")
        if st.button("Go to Details"):
            go("details")
        return

    model, err = load_model()
    if model is None:
        st.error("🤖 Model could not be loaded. Please check the logs or path.")
        if err:
            st.caption(f"Error details: {err}")
        st.stop()

    try:
        default_prob = run_prediction(model, a)
    except Exception as e:
        logging.error(f"Prediction failed: {str(e)}")
        st.error("An error occurred while processing your request. Please try again later.")
        return

    if default_prob >= 0.50:
        level, pill_class, banner = "HIGH", "pill-high", ("error", "⚠️ HIGH RISK — Application flagged for potential default.")
    elif default_prob >= 0.30:
        level, pill_class, banner = "MODERATE", "pill-mod", ("warning", "⚡ MODERATE RISK — Requires manual underwriting / verification.")
    else:
        level, pill_class, banner = "LOW", "pill-low", ("success", "✅ LOW RISK — Application satisfies standard low-risk threshold.")

    receipt_id = "CR-" + uuid.uuid4().hex[:10].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # store in history once per result view (avoid duplicate on rerun of same result)
    if st.session_state.last_result != receipt_id and st.session_state.get("_pending_store", True):
        pass

    st.markdown("<div class='step-track'>"
                 "<div class='step-dot active'></div>"
                 "<div class='step-dot active'></div>"
                 "<div class='step-dot active'></div>"
                 "</div>", unsafe_allow_html=True)
    st.markdown("### 📊 Risk Assessment Result")

    r1, r2 = st.columns([1, 1.2])
    with r1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Calculated Default Risk</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-value' style='font-size:2.6rem;'>{default_prob*100:.2f}%</div>", unsafe_allow_html=True)
        st.progress(float(default_prob))
        st.markdown(f"<span class='pill {pill_class}'>{level} RISK</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r2:
        kind, msg = banner
        getattr(st, kind)(msg)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("**Applicant Summary**")
        st.write(f"Name: **{a['applicant_name']}**")
        st.write(f"Age: **{a['person_age']}** | Income: **${a['person_income']:,.0f}**")
        st.write(f"Loan: **${a['loan_amnt']:,.0f}** at **{a['loan_int_rate']}%** interest")
        st.write(f"Intent: **{a['loan_intent']}** | Grade: **{a['loan_grade']}**")
        st.markdown("</div>", unsafe_allow_html=True)

    # Save to history (only once per generated receipt)
    already_logged = any(h["receipt_id"] == receipt_id for h in st.session_state.history)
    if not already_logged:
        st.session_state.history.append({
            "receipt_id": receipt_id,
            "timestamp": timestamp,
            "loan_amnt": a["loan_amnt"],
            "prob": default_prob,
            "level": level,
        })
    st.session_state.last_result = receipt_id

    st.write("")
    st.markdown("### 🧾 Digital Receipt")

    loan_percent_income = a["loan_amnt"] / a["person_income"] if a["person_income"] > 0 else 0.0

    receipt_html = f"""
    <div class='receipt'>
        <div class='receipt-title'>CREDITSENSE RISK RECEIPT</div>
        <div class='receipt-sub'>Digitally generated assessment record</div>
        <hr>
        <div class='receipt-row'><span>Receipt ID</span><span>{receipt_id}</span></div>
        <div class='receipt-row'><span>Date/Time</span><span>{timestamp}</span></div>
        <div class='receipt-row'><span>Issued By</span><span>{st.session_state.username}</span></div>
        <hr>
        <div class='receipt-row'><span>Applicant</span><span>{a['applicant_name']}</span></div>
        <div class='receipt-row'><span>Age</span><span>{a['person_age']}</span></div>
        <div class='receipt-row'><span>Annual Income</span><span>${a['person_income']:,.0f}</span></div>
        <div class='receipt-row'><span>Employment (yrs)</span><span>{a['person_emp_length']}</span></div>
        <div class='receipt-row'><span>Home Ownership</span><span>{a['person_home_ownership']}</span></div>
        <hr>
        <div class='receipt-row'><span>Loan Amount</span><span>${a['loan_amnt']:,.0f}</span></div>
        <div class='receipt-row'><span>Interest Rate</span><span>{a['loan_int_rate']}%</span></div>
        <div class='receipt-row'><span>Loan Intent</span><span>{a['loan_intent']}</span></div>
        <div class='receipt-row'><span>Loan Grade</span><span>{a['loan_grade']}</span></div>
        <div class='receipt-row'><span>Loan % of Income</span><span>{loan_percent_income*100:.2f}%</span></div>
        <div class='receipt-row'><span>Prior Default on File</span><span>{a['cb_person_default_on_file']}</span></div>
        <hr>
        <div class='receipt-row'><span><b>DEFAULT RISK</b></span><span><b>{default_prob*100:.2f}%</b></span></div>
        <div class='receipt-row'><span><b>RISK LEVEL</b></span><span><b>{level}</b></span></div>
        <hr>
        <div class='receipt-sub'>Generated by CreditSense • Not a financial decision on its own</div>
    </div>
    """
    st.markdown(receipt_html, unsafe_allow_html=True)

    receipt_text = f"""========================================
        CREDITSENSE RISK RECEIPT
========================================
Receipt ID       : {receipt_id}
Date/Time        : {timestamp}
Issued By        : {st.session_state.username}
----------------------------------------
Applicant        : {a['applicant_name']}
Age              : {a['person_age']}
Annual Income    : ${a['person_income']:,.0f}
Employment (yrs) : {a['person_emp_length']}
Home Ownership   : {a['person_home_ownership']}
----------------------------------------
Loan Amount      : ${a['loan_amnt']:,.0f}
Interest Rate    : {a['loan_int_rate']}%
Loan Intent      : {a['loan_intent']}
Loan Grade       : {a['loan_grade']}
Loan % of Income : {loan_percent_income*100:.2f}%
Prior Default    : {a['cb_person_default_on_file']}
----------------------------------------
DEFAULT RISK     : {default_prob*100:.2f}%
RISK LEVEL       : {level}
========================================
Generated by CreditSense
"""

    st.write("")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "⬇️ Download Receipt (.txt)",
            data=receipt_text,
            file_name=f"{receipt_id}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with d2:
        if st.button("🔁 New Assessment", use_container_width=True):
            st.session_state.applicant = {}
            go("details")
    with d3:
        if st.button("📊 Back to Dashboard", use_container_width=True):
            go("dashboard")

# ===========================================================
# PAGE: ABOUT
# ===========================================================
def render_about():
    st.markdown("<div class='brand-title'>About CreditSense</div>", unsafe_allow_html=True)
    st.write("")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📌 What is this project?")
    st.write(
        "CreditSense is a Credit Risk & Loan Default Assessment console. It lets an analyst "
        "log in, enter an applicant's personal, employment, and loan details, and instantly "
        "receive a machine-learning-driven probability of default. Each completed assessment "
        "produces a digital receipt that records the applicant's profile, the calculated risk "
        "score, and the resulting risk tier (Low, Moderate, High) for audit and record-keeping."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛠️ Tech Stack")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            "- **Frontend / UI:** Streamlit (custom CSS theming)\n"
            "- **Backend Logic:** Python\n"
            "- **ML Model:** XGBoost classifier (`predict_proba`)\n"
            "- **Model Serialization:** joblib (`my_model.pkl`)\n"
        )
    with t2:
        st.markdown(
            "- **Data Handling:** pandas, NumPy\n"
            "- **Feature Engineering:** one-hot encoding for home ownership, loan intent, loan grade\n"
            "- **Session State:** Streamlit `st.session_state` (auth, form data, history)\n"
            "- **Output Artifacts:** on-screen + downloadable digital receipt (.txt)\n"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📤 What output does it produce?")
    st.write(
        "For every applicant evaluated, the app outputs: a **default probability percentage**, "
        "a **risk tier classification** (Low / Moderate / High) with recommended next action, "
        "a running **dashboard summary** of all assessments made in the session, and a "
        "**digital receipt** (viewable in-app and downloadable) containing a unique receipt ID, "
        "timestamp, full applicant snapshot, and final risk verdict."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("👨‍💻 Developer")
    st.markdown(
        "**Muneeb Farid** is the developer of this project — responsible for the end-to-end "
        "design and build, including the ML integration, feature engineering pipeline, and the "
        "full Streamlit frontend experience (login, dashboard, assessment flow, and receipt system)."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("← Back to Dashboard"):
        go("dashboard")

# ===========================================================
# ROUTER
# ===========================================================
if st.session_state.page == "login" or not st.session_state.logged_in:
    render_login()
else:
    render_sidebar()
    page = st.session_state.page
    if page == "dashboard":
        render_dashboard()
    elif page == "details":
        render_details()
    elif page == "result":
        render_result()
    elif page == "about":
        render_about()
    else:
        render_dashboard()