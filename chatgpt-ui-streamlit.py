from openai import OpenAI
import streamlit as st
import os

#give title to the page
st.title("OpenAI ChatGPT")

#initialize session variable at the start once
if 'model' not in st.session_state:
    st.session_state.model = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
    
#create sidebar to adjust parameters
st.sidebar.header("Parameters")
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
max_tokens = st.sidebar.slider("Max Tokens", min_value=1, max_value=4096, value=1024, step=1)

