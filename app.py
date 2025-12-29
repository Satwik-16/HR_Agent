import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Import our backend modules
from src.agent import get_agent, validate_response
from src.db import init_db, log_interaction
from src.utils import setup_logging

# --- 1. Configuration & Setup ---
load_dotenv()
setup_logging()

st.set_page_config(page_title="Verified HR Agent", layout="centered", page_icon="🛡️")

# --- 2. Custom CSS (Pure Chat Look) ---
st.markdown("""
<style>
    /* Clean up the top spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat Input Styling */
    .stChatInput {
        border-radius: 20px;
    }
    
    /* Verified Badge Styling */
    .verified-badge {
        color: #0f5132;
        background-color: #d1e7dd;
        border-color: #badbcc;
        padding: 0.5em;
        border-radius: 5px;
        font-size: 0.8em;
        margin-top: 5px;
        display: inline-block;
        font-weight: 500;
        border: 1px solid #badbcc;
    }
    
    /* Warning Badge Styling */
    .warning-badge {
        color: #664d03;
        background-color: #fff3cd;
        border-color: #ffecb5;
        padding: 0.5em;
        border-radius: 5px;
        font-size: 0.8em;
        margin-top: 5px;
        display: inline-block;
        font-weight: 500;
        border: 1px solid #ffecb5;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Data Initialization (Cached) ---
@st.cache_resource
def initialize_system():
    """
    Loads the cleaned dataset and initializes the in-memory SQLite database.
    This runs only once to improve performance.
    """
    csv_path = "data/processed/cleaned_employees.csv"
    
    if not os.path.exists(csv_path):
        return None, None
    
    try:
        # Load Data
        df = pd.read_csv(csv_path)
        # Init Database (src/db.py)
        db_instance = init_db(df)
        return df, db_instance
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, None

df, db = initialize_system()

# Stop if data is missing
if df is None:
    st.error("🚨 System Error: 'data/processed/cleaned_employees.csv' not found. Please run 'python -m src.etl' to generate it.")
    st.stop()

# --- 4. Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Agent (Cached in Session)
if "agent" not in st.session_state:
    try:
        st.session_state.agent = get_agent(db)
        # Subtle toast to indicate readiness
        st.toast("Secure Agent Online", icon="🛡️")
    except Exception as e:
        st.error(f"Agent Initialization Error: {e}")
        st.session_state.agent = None

# --- 5. UI: Header ---
st.title("🛡️ HR Intelligence Agent")
st.caption("Double-Check Architecture: SQL Agent + QA Critic")

# Welcome Message for new session
if not st.session_state.messages:
    st.info("👋 I am your verified HR assistant. I double-check every answer for accuracy.", icon="ℹ️")

# --- 6. UI: Chat History Loop ---
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        
        # Display existing verification badges
        if msg.get("verification"):
            if msg["verification"] == "VERIFIED_CORRECT":
                st.markdown('<div class="verified-badge">✅ Verified Correct</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="warning-badge">⚠️ QA Audit: {msg["verification"]}</div>', unsafe_allow_html=True)

# --- 7. UI: Chat Interaction ---
if prompt := st.chat_input("Ask a question (e.g., 'Who has the highest salary?')"):
    
    # 7.1 Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 7.2 Assistant Logic
    with st.chat_message("assistant", avatar="🤖"):
        if st.session_state.agent:
            try:
                # Generate Answer via SQL Agent
                with st.spinner("Analyzing..."):
                    res = st.session_state.agent.invoke(prompt)
                    
                    # Extract text from complex agent response structure
                    raw = res.get('output', "Recall Error")
                    
                    if isinstance(raw, dict) and 'text' in raw:
                         output_text = raw['text']
                    elif isinstance(raw, list):
                         output_text = "".join([str(item.get('text', item)) if isinstance(item, dict) else str(item) for item in raw])
                    else:
                         output_text = str(raw)

                # Execute Verification Layer (Double-Check)
                with st.spinner("Verifying logic..."):
                    validation_result = validate_response(prompt, output_text)

                # Render Response
                st.markdown(output_text)

                # Render Verification Badge
                if validation_result == "VERIFIED_CORRECT":
                    st.markdown('<div class="verified-badge">✅ Verified Correct</div>', unsafe_allow_html=True)
                    v_status = "VERIFIED_CORRECT"
                else:
                    st.markdown(f'<div class="warning-badge">⚠️ Audit Note: {validation_result}</div>', unsafe_allow_html=True)
                    v_status = validation_result

                # Log Interaction for Training/Audit
                log_interaction(db, prompt, output_text, v_status)
                
                # Update Session History
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": output_text,
                    "verification": v_status
                })

            except Exception as e:
                st.error(f"Processing Error: {e}")
        else:
            st.warning("Agent is currently unavailable. Please refresh.")
