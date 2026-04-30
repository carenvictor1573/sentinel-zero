import streamlit as st
import boto3
import pandas as pd
import requests

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Sentinel Zero", layout="wide")

# ----------------------------
# SESSION STATE (LOGIN)
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ----------------------------
# 🔐 LOGIN PAGE
# ----------------------------
if not st.session_state.logged_in:

    # Center the login box
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style='text-align: center; margin-top: 80px;'>
                <h1 style='margin-bottom: 5px;'>🚨 Sentinel Zero</h1>
                <p style='color: gray;'>Security Monitoring Dashboard</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🔐 Login")

        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Login", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ----------------------------
# 🚨 DASHBOARD
# ----------------------------
st.title("🚨 Sentinel Zero Security Dashboard")

REGION = "eu-north-1"
TABLE_NAME = "AlertHistoryTable"

# ----------------------------
# 🌍 IP → COUNTRY
# ----------------------------
def get_country(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        return response.json().get("country", "Unknown")
    except:
        return "Unknown"

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data(ttl=60)
def load_data():
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)
    return table.scan().get('Items', [])

items = load_data()

if not items:
    st.warning("No alerts found")
    st.stop()

df = pd.DataFrame(items)

# Fix types
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
    except:
        pass

# Timestamp
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# Add country
if 'ip' in df.columns:
    df['country'] = df['ip'].apply(get_country)

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("🔍 Filters")

severity_filter = st.sidebar.selectbox(
    "Severity", ["ALL", "HIGH", "MEDIUM", "LOW"]
)

if severity_filter != "ALL":
    df = df[df['severity'] == severity_filter]

# ----------------------------
# METRICS
# ----------------------------
st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Alerts", len(df))
col2.metric("HIGH", int((df['severity'] == "HIGH").sum()))
col3.metric("MEDIUM", int((df['severity'] == "MEDIUM").sum()))

# ----------------------------
# 🔥 TOP ATTACKER
# ----------------------------
if not df.empty and 'ip' in df.columns:
    top_ip = df['ip'].value_counts().idxmax()
    st.info(f"🔥 Most Active IP: {top_ip}")

# ----------------------------
# TABLE
# ----------------------------
st.subheader("📄 Alert Data")
st.dataframe(df, use_container_width=True)

# ----------------------------
# CHARTS
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Top IPs")
    if 'ip' in df.columns:
        st.bar_chart(df['ip'].value_counts())

with col2:
    st.subheader("⚠️ Actions")
    if 'action' in df.columns:
        st.bar_chart(df['action'].value_counts())

# ----------------------------
# COUNTRY CHART
# ----------------------------
if 'country' in df.columns:
    st.subheader("🌍 Attacker Countries")
    st.bar_chart(df['country'].value_counts())

# ----------------------------
# TIME SERIES
# ----------------------------
if 'timestamp' in df.columns:
    st.subheader("📈 Activity Timeline")
    ts = df.set_index('timestamp').resample('1min').size()
    st.line_chart(ts)

# ----------------------------
# LOGOUT
# ----------------------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.success("✅ Live AWS Security Monitoring")