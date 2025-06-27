# =========================
# 💬 frontend/streamlit_app.py (Final stable version - safely clears input after submit)
# =========================
import streamlit as st
import requests
from datetime import datetime
from streamlit.components.v1 import html

# Page Setup
st.set_page_config(page_title="📅 AI Meeting Scheduler", layout="centered")

st.markdown("""
<style>
.chat-container {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.user {
    background-color: #d1e7ff;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
}
.bot {
    background-color: #e9ecef;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Calendar Booking Assistant")
st.caption("Book meetings smartly using natural language")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

BACKEND_URL = "http://localhost:8000"

try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=3)
    if health.status_code != 200:
        st.error("⚠️ Backend is not healthy.")
except Exception as e:
    st.error(f"❌ Cannot connect to backend: {e}")

# Input form
with st.form(key="chat_form"):
    user_input = st.text_input(
        "💬 Ask to book a meeting (e.g. 'next Sunday at 3PM'):",
        key="chat_input",
        value="" if st.session_state.clear_input else None
    )
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_input, "session_id": "default"},
            timeout=10
        )
        if response.status_code == 200:
            reply = response.json()
            response_text = reply["response"]
            st.session_state.messages.append({"role": "bot", "content": response_text})
            if reply.get("booking_confirmed"):
                st.success("🎉 Your meeting has been booked successfully!")
                st.balloons()
        else:
            st.error(f"❌ Backend Error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Could not reach backend: {e}")

    st.session_state.clear_input = True
    st.experimental_rerun()

# Reset clear_input after rerun
if st.session_state.clear_input:
    st.session_state.clear_input = False

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-container user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-container bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("💡 How to Use")
    st.markdown("""
    ### Try asking:
    - "Book a meeting tomorrow at 4 PM"
    - "Schedule call next Sunday afternoon"
    - "Meeting on July 3rd at 11 AM"

    ✅ The assistant will:
    - Understand natural language
    - Offer time slots
    - Let you confirm bookings easily
    """)






