"""
Untuk menjalankan:

>>> streamlit run fitassistmk1.py
"""

import os
import streamlit as st
import base64
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# 1. Performance: Use st.cache_data instead of experimental_memo
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img = get_img_as_base64("fitnessjournerbg1.jpg")

# ... (Keep your get_img_as_base64 function as is)

if img:
    page_bg_img = f"""
    <style>
    /* 1. Full Page Background */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* 2. Make content containers transparent */
    [data-testid="stMainViewContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stMain"] {{
        background-color: rgba(0,0,0,0) !important;
    }}

    /* 3. Style the Title (h1) */
    h1 {{
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        /* This creates a 'border' effect using 4 shadows */
        text-shadow: 
            -1px -1px 0 #000,  
             1px -1px 0 #000,
            -1px  1px 0 #000,
             1px  1px 0 #000;
        padding-bottom: 20px;
    }}

    /* 4. Optional: Style the text input labels to also be white */
    .stMarkdown p, label {{
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }}
    /* --- 1. Background for Chat Bubbles (User & Bot) --- */
    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.1) !important; /* Semi-transparent white/grey */
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px); /* Glassmorphism blur effect */
        border: 1px solid rgba(255, 255, 255, 0.15); /* Soft border */
    }}

    /* --- 2. Ensure all text inside bubbles is white and readable --- */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] h1, 
    [data-testid="stChatMessage"] h2, 
    [data-testid="stChatMessage"] h3 {{
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8); /* Shadow for text readability */
    }}

    /* --- 3. Style the Title (White with Black Border) --- */
    h1 {{
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        font-weight: 800;
        text-shadow: 
            -2px -2px 0 #000,  
             2px -2px 0 #000,
            -2px  2px 0 #000,
             2px  2px 0 #000; /* Creates the border line effect */
        padding-bottom: 20px;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
else:
    st.warning("⚠️ Background image 'fitnessjournerbg.jpg' not found in the directory.")

st.title("Your Fitness Partner 💪")

# 2. UI/UX: Move API Key to Sidebar
with st.sidebar:
    st.header("Settings")
    if "GROQ_API_KEY" not in st.session_state:
        groq_key = st.text_input("Groq API Key:", type="password")
        if st.button("Connect"):
            st.session_state["GROQ_API_KEY"] = groq_key
            st.rerun()
    else:
        st.success("API Key Connected!")
        if st.button("Reset Key"):
            del st.session_state["GROQ_API_KEY"]
            st.rerun()

# Stop if no API key
if "GROQ_API_KEY" not in st.session_state:
    st.info("Please enter your Groq API Key in the sidebar to begin.")
    st.stop()

# 3. Model Configuration
# Note: Ensure the model name is correct for the current Groq registry
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=st.session_state["GROQ_API_KEY"]
)

# Chat History Setup
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        SystemMessage(content=(
            "You are an expert fitness coach and nutritionist. "
            "Analyze the user's goals, weight, height, and frequency. "
            "Provide structured workout plans and meal suggestions. "
            "Always prioritize safety and suggest medical consultation for illnesses."
        ))
    ]

# Display History
for chat in st.session_state["chat_history"]:
    if isinstance(chat, SystemMessage):
        continue
    role = "user" if isinstance(chat, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(chat.content)

# Chat Input
user_chat = st.chat_input("Ex: I want to lose weight, 80kg, 175cm, 3x a week...")

if user_chat:
    # Display User Message
    with st.chat_message("user"):
        st.markdown(user_chat)
    st.session_state["chat_history"].append(HumanMessage(content=user_chat))

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state["chat_history"])
            st.markdown(response.content)
            st.session_state["chat_history"].append(response)