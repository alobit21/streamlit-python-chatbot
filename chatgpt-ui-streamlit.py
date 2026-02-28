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

#update the interface with the previous messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
#create the chat input box
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    #get the response from the model
    with st.chat_message("assistant"):
        client = st.session_state["model"]
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": message["role"], "content": message["content"]}
                for message in st.session_state["messages"]
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        
        response = st.write_stream(stream)
    st.session_state["messages"].append({"role": "assistant", "content": response})