import streamlit as st
import pandas as pd
import plotly.express as px
import re

from src.pipeline.pipeline import process_logs
from src.llm.llm_summary import ask_llm

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="AI Monitoring Dashboard", layout="wide")

# -------------------------
# THEME
# -------------------------
theme = st.sidebar.toggle("🌗 Dark Mode", True)
template = "plotly_dark" if theme else "plotly_white"

# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
<style>
/* Layout */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* KPI Cards */
.metric-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}

/* Section Title */
.section {
    font-size: 22px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
}

/* Chat */
.chat-user {
    background-color: #1e3a8a;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 6px;
}

.chat-bot {
    background-color: #065f46;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("⚙️ Control Panel")
page = st.sidebar.radio("Navigation", ["Dashboard", "Analytics", "Alerts", "Logs", "AI Chat"])

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# -------------------------
# TITLE
# -------------------------
st.title("🚀 AI Security & Log Monitoring Dashboard")
st.caption("Real-time log analysis with ML + AI insights")

if not uploaded_file:
    st.info("Upload a CSV file to begin")
    st.stop()

# -------------------------
# LOAD DATA
# -------------------------
with open("temp.csv", "wb") as f:
    f.write(uploaded_file.getbuffer())

output = process_logs("temp.csv")
summary = output["summary"]
df = pd.DataFrame(output["processed_logs"])

# -------------------------
# HELPER
# -------------------------
def metric_card(title, value):
    return f"""
    <div class="metric-card">
        <div style="color:#9ca3af">{title}</div>
        <div style="font-size:28px;font-weight:bold">{value}</div>
    </div>
    """

def highlight_ip(text):
    return re.sub(r'(\\b\\d{1,3}(?:\\.\\d{1,3}){3}\\b)', r'**\\1**', text)

# -------------------------
# DASHBOARD
# -------------------------
if page == "Dashboard":

    st.markdown('<div class="section">📊 System Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(metric_card("Total Logs", len(df)), unsafe_allow_html=True)
    col2.markdown(metric_card("High Severity", summary["severity_summary"].get("High", 0)), unsafe_allow_html=True)
    col3.markdown(metric_card("Critical", summary["severity_summary"].get("Critical", 0)), unsafe_allow_html=True)
    col4.markdown(metric_card("Alerts", len(summary["alerts"])), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            pd.DataFrame(summary["category_summary"].items(), columns=["Category", "Count"]),
            names="Category",
            values="Count"
        )
        fig.update_layout(template=template)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            pd.DataFrame(summary["severity_summary"].items(), columns=["Severity", "Count"]),
            x="Severity",
            y="Count"
        )
        fig.update_layout(template=template)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # -------------------------
    # AI INSIGHTS
    # -------------------------
    st.markdown('<div class="section">🤖 AI Insights</div>', unsafe_allow_html=True)

    llm_text = output["llm_summary"]
    sections = llm_text.split("\n\n")

    for section in sections:
        section = highlight_ip(section)

        if "Summary" in section:
            st.info("🔵 " + section)

        elif "Critical Issues" in section:
            st.error("🔴 " + section)

        elif "Action Plan" in section:
            st.warning("🟠 " + section)

        else:
            st.markdown(section)

# -------------------------
# ANALYTICS
# -------------------------
elif page == "Analytics":

    st.markdown('<div class="section">📈 Log Trends</div>', unsafe_allow_html=True)

    df["time"] = pd.to_datetime(df["timestamp"]).dt.floor("min")
    time_df = df.groupby("time").size().reset_index(name="count")

    fig = px.line(time_df, x="time", y="count")
    fig.update_layout(template=template)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section">🔥 Top Issues</div>', unsafe_allow_html=True)

    for issue in summary["top_issues"]:
        st.warning(f"{issue[0]} → {issue[1]} occurrences")

# -------------------------
# ALERTS
# -------------------------
elif page == "Alerts":

    st.markdown('<div class="section">🚨 Alerts</div>', unsafe_allow_html=True)

    for alert in summary["alerts"]:
        msg = f"{alert['type']}: {alert['message']}"

        if alert["severity"] == "High":
            st.error("🔴 " + msg)
        elif alert["severity"] == "Medium":
            st.warning("🟠 " + msg)
        else:
            st.info("🔵 " + msg)

# -------------------------
# LOGS
# -------------------------
elif page == "Logs":

    st.markdown('<div class="section">📄 Logs Explorer</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    severity = col1.selectbox("Severity", ["All"] + list(df["severity"].unique()))
    category = col2.selectbox("Category", ["All"] + list(df["category"].unique()))

    filtered = df.copy()

    if severity != "All":
        filtered = filtered[filtered["severity"] == severity]

    if category != "All":
        filtered = filtered[filtered["category"] == category]

    st.dataframe(filtered, use_container_width=True, height=500)

# -------------------------
# AI CHAT
# -------------------------
elif page == "AI Chat":

    st.markdown('<div class="section">🧠 AI Log Assistant</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask something about logs...")

    if user_input:
        with st.spinner("Thinking..."):
            answer = ask_llm(user_input, summary)

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", answer))

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="chat-user">🧑 {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 {msg}</div>', unsafe_allow_html=True)