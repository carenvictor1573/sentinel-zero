import streamlit as st
import boto3
import pandas as pd

# ----------------------------
# CONFIG
# ----------------------------
REGION = "eu-north-1"
TABLE_NAME = "AlertHistoryTable"

# ----------------------------
# PAGE SETTINGS
# ----------------------------
st.set_page_config(page_title="Sentinel Zero Dashboard", layout="wide")

st.title("🚨 Sentinel Zero Security Dashboard")

# ----------------------------
# CONNECT TO AWS
# ----------------------------
@st.cache_data(ttl=30)  # refresh every 30 sec
def load_data():
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    response = table.scan()
    items = response.get('Items', [])

    return items

items = load_data()

if not items:
    st.warning("No alerts found in DynamoDB")
    st.stop()

# ----------------------------
# DATAFRAME
# ----------------------------
df = pd.DataFrame(items)

# Fix numeric types
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
    except:
        pass

# Convert timestamp
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# ----------------------------
# SIDEBAR FILTER
# ----------------------------
st.sidebar.header("🔍 Filters")

severity_filter = st.sidebar.selectbox(
    "Select Severity",
    ["ALL", "HIGH", "MEDIUM", "LOW"]
)

if severity_filter != "ALL":
    df = df[df['severity'] == severity_filter]

# ----------------------------
# METRICS
# ----------------------------
st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Alerts", len(df))
col2.metric("HIGH Alerts", int((df['severity'] == "HIGH").sum()))
col3.metric("MEDIUM Alerts", int((df['severity'] == "MEDIUM").sum()))

# ----------------------------
# TABLE VIEW
# ----------------------------
st.subheader("📄 Alert Data")
st.dataframe(df, use_container_width=True)

# ----------------------------
# CHARTS
# ----------------------------
col1, col2 = st.columns(2)

# Top IPs
with col1:
    st.subheader("🌍 Top Suspicious IPs")
    if 'ip' in df.columns:
        st.bar_chart(df['ip'].value_counts())

# Top Actions
with col2:
    st.subheader("⚠️ Top Risk Actions")
    if 'action' in df.columns:
        st.bar_chart(df['action'].value_counts())

# ----------------------------
# TIME SERIES
# ----------------------------
if 'timestamp' in df.columns:
    st.subheader("📈 Alerts Over Time")

    time_series = df.set_index('timestamp').resample('1min').size()

    st.line_chart(time_series)

# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.success("✅ Dashboard connected to AWS DynamoDB (Live Data)")