import streamlit as st
import pandas as pd
from src.agent import get_agent
from src.db import init_db
from src.utils import setup_logging
from dotenv import load_dotenv
import os

# Load Environment
load_dotenv()
setup_logging()

st.set_page_config(page_title="HR Agent", layout="wide", page_icon="🤖")

# Custom CSS for pure chat experience
st.markdown("""
<style>
    /* Remove default padding to maximize chat space */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    /* Hide Streamlit header/footer/hamburger */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style the chat input to float nicely */
    .stChatInput {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Logic: Data Loading & Init ---

data_path = "data/processed/cleaned_employees.csv"
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    st.error("🚨 Data Error: Pipeline output missing."); st.stop()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_model" not in st.session_state:
     st.session_state.agent_model = "gemini-2.5-flash"

# Agent Setup
if st.session_state.agent is None:
    try:
        db = init_db(df)
        st.session_state.agent = get_agent(db)
        st.toast("System Online: Connected to HR Database", icon="🟢")
    except Exception as e:
        st.error(f"Connection Failed: {e}")

# --- UI: Dashboard Toggler ---
with st.expander("📊 View HR Analytics Dashboard", expanded=False):
    st.markdown("### Executive Overview")
    
    # Top-level Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Employees", len(df))
    m2.metric("Avg Salary", f"${df['Salary'].mean():,.0f}")
    m3.metric("Departments", df['Department'].nunique())
    m4.metric("Regions", df['Region'].nunique())
    
    st.markdown("---")
    
    # Interactive Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💰 Salary by Department")
        # Helper for clean charts
        dept_salary = df.groupby("Department")["Salary"].mean().sort_values(ascending=True)
        st.bar_chart(dept_salary, color="#2E86C1") # Professional Blue
        
    with c2:
        st.subheader("🌍 Headcount by Region")
        region_counts = df["Region"].value_counts()
        st.bar_chart(region_counts, color="#28B463") # Professional Green
        
    # Row 2
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("🏆 Performance by Dept")
        # Stacked bar chart: Department vs Performance
        # Crosstab creates a matrix suitable for stacked bars
        perf_by_dept = pd.crosstab(df["Department"], df["Performance_Score"])
        st.bar_chart(perf_by_dept)

    with c4:
        # 1. Descriptive Statistics
        st.markdown("##### 📊 Descriptive Statistics")
        stats_md = ""
        # Numeric Stats
        for col in ["Salary", "Age"]:
             s = df[col]
             stats_md += f"- **{col}**: Mean={s.mean():,.1f}, Std={s.std():,.0f}\n"
        
        # Categorical Stats (Uniqueness)
        for col in ["Department", "Region", "Performance_Score"]:
            stats_md += f"- **{col}**: {df[col].nunique()} unique values\n"

        st.markdown(stats_md)

        # 2. Total Salary per Dept
        st.markdown("##### 💰 Total Salary Impact")
        dept_sum = df.groupby("Department")["Salary"].sum().sort_values(ascending=False)
        for dept, val in dept_sum.head(3).items():
             st.markdown(f"- **{dept}**: ${val:,.0f}")
        st.caption("*(Top 3 Departments)*")

        # 3. Quick Distribution Highlights
        st.markdown("##### 🌍 Regional & Performance Highlights")
        top_region = df['Region'].mode()[0]
        top_perf = df['Performance_Score'].mode()[0]
        st.markdown(f"- **Top Region**: {top_region} ({len(df[df['Region']==top_region])} employees)")
        st.markdown(f"- **Most Common Rating**: {top_perf}")

# --- UI: Main Chat Interface ---

# Header
st.markdown("<h3>🤖 HR Intelligence Assistant</h3>", unsafe_allow_html=True)

# Chat History
if not st.session_state.messages:
    st.info("👋 Welcome! I can answer questions about Salary, Regions, and Performance.", icon="ℹ️")

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about employees..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant", avatar="🤖"):
        if st.session_state.agent:
            try:
                with st.spinner("Analyzing..."):
                    response = st.session_state.agent.invoke(prompt)
                    
                    # Output Parsing
                    raw_output = response.get('output')
                    if isinstance(raw_output, list):
                        cleaned_text = ""
                        for item in raw_output:
                            if isinstance(item, dict) and 'text' in item:
                                cleaned_text += item['text']
                            elif isinstance(item, str):
                                cleaned_text += item
                        output_text = cleaned_text
                    else:
                        output_text = str(raw_output)

                    st.markdown(output_text)
                    st.session_state.messages.append({"role": "assistant", "content": output_text})
            except Exception as e:
                st.error(f"Processing Error: {e}")
        else:
            st.warning("Agent disconnected.")
