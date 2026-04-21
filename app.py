import streamlit as st
import pandas as pd
import plotly.express as px

from src.pipeline.pipeline import process_logs
from src.llm.llm_summary import ask_llm

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="AI Monitoring Dashboard", layout="wide")

# -------------------------
# THEME
# -------------------------
# theme = st.sidebar.toggle("🌗 Dark Mode", True)

# template = "plotly_dark" if theme else "plotly_white"

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

if not uploaded_file:
    st.info("Upload a CSV file to start")
    st.stop()

# Save file
with open("temp.csv", "wb") as f:
    f.write(uploaded_file.getbuffer())

# Process logs
output = process_logs("temp.csv")
summary = output["summary"]
df = pd.DataFrame(output["processed_logs"])

# -------------------------
# DASHBOARD
# -------------------------
if page == "Dashboard":

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Logs", len(df))
    col2.metric("High", summary["severity_summary"].get("High", 0))
    col3.metric("Critical", summary["severity_summary"].get("Critical", 0))
    col4.metric("Alerts", len(summary["alerts"]))

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

    st.markdown("## 🤖 AI Insights")
    st.success(output["llm_summary"])


# -------------------------
# ANALYTICS
# -------------------------
elif page == "Analytics":

    st.subheader("📈 Log Trends")

    df["time"] = pd.to_datetime(df["timestamp"]).dt.floor("min")
    time_df = df.groupby("time").size().reset_index(name="count")

    fig = px.line(time_df, x="time", y="count")
    fig.update_layout(template=template)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 🔥 Top Issues")
    for issue in summary["top_issues"]:
        st.write(f"{issue[0]} → {issue[1]}")


# -------------------------
# ALERTS
# -------------------------
elif page == "Alerts":

    st.subheader("🚨 Alerts")

    for alert in summary["alerts"]:
        if alert["severity"] == "High":
            st.error(f"{alert['type']}: {alert['message']}")
        elif alert["severity"] == "Medium":
            st.warning(f"{alert['type']}: {alert['message']}")
        else:
            st.info(f"{alert['type']}: {alert['message']}")


# -------------------------
# LOGS
# -------------------------
elif page == "Logs":

    st.subheader("📄 Logs Explorer")

    col1, col2 = st.columns(2)

    severity = col1.selectbox("Severity", ["All"] + list(df["severity"].unique()))
    category = col2.selectbox("Category", ["All"] + list(df["category"].unique()))

    filtered = df.copy()

    if severity != "All":
        filtered = filtered[filtered["severity"] == severity]

    if category != "All":
        filtered = filtered[filtered["category"] == category]

    st.dataframe(filtered, use_container_width=True)


# -------------------------
# AI CHAT (REAL)
# -------------------------
elif page == "AI Chat":

    st.subheader("🧠 AI Log Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask something about logs:")

    if user_input:
        with st.spinner("Thinking..."):
            answer = ask_llm(user_input, summary)

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", answer))

    # Display chat
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")