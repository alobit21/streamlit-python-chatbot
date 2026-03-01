import streamlit as st
from google import genai

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="Gemini Chat",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Gemini Chatbot")

# -----------------------------
# Initialize Gemini client
# -----------------------------
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# Session state for messages and settings
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = "gemini-2.5-flash"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# -----------------------------
# Sidebar: Parameters & controls
# -----------------------------
with st.sidebar:
    st.header("Settings")

    # Model selection
    st.session_state.model = st.selectbox(
        "Select Model",
        options=[
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-flash-latest",
            "gemini-pro-latest"
        ],
        index=0
    )

    # Temperature slider
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1
    )

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []  # clear chat
        st.experimental_rerun = lambda: None
        st.experimental_rerun()  # reruns page

    st.markdown("---")
    st.markdown(
        """
        **Instructions:**  
        - Type your message in the chat box below.  
        - Adjust the temperature for creativity.  
        - Choose the model you want to use.  
        - Press "Clear Chat" to start over.
        """
    )

# -----------------------------
# Display chat messages
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# Chat input
# -----------------------------
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response from Gemini
    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model=st.session_state.model,
            contents=prompt
        )
        reply = response.text
        st.markdown(reply)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})