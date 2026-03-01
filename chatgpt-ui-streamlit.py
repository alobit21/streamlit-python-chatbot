import streamlit as st
from google import genai

# -----------------------------
# Custom CSS for message alignment
# -----------------------------
st.markdown("""
<style>
.user-message {
    text-align: right;
    background-color: #1e88e5;
    padding: 10px;
    border-radius: 10px 10px 0 10px;
    margin: 10px 0;
    max-width: 80%;
    margin-left: auto;
    color: #ffffff; /* White text for dark blue background */
}

.assistant-message {
    text-align: left;
    background-color: #424242;
    padding: 10px;
    border-radius: 10px 10px 10px 0;
    margin: 10px 0;
    max-width: 80%;
    color: #ffffff; /* White text for dark gray background */
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="simple Chat",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Simple Chatbot")

# -----------------------------
# Initialize Gemini client
# -----------------------------
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# Session state for messages and settings
# -----------------------------
# Initialize session state (automatically persists until cleared)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = "gemini-2.5-flash"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# Load saved session from localStorage on page load
st.markdown("""
<script>
// Load session from localStorage when page loads
window.addEventListener('load', function() {
    const savedMessages = localStorage.getItem('chatbot_messages');
    const savedModel = localStorage.getItem('chatbot_model');
    const savedTemp = localStorage.getItem('chatbot_temperature');
    
    if (savedMessages) {
        // Send saved data to Streamlit
        const data = {
            messages: JSON.parse(savedMessages),
            model: savedModel || 'gemini-2.5-flash',
            temperature: parseFloat(savedTemp) || 0.7
        };
        
        // Use Streamlit's setComponentValue to restore session
        if (window.parent && window.parent.Streamlit) {
            window.parent.Streamlit.setComponentValue({session_data: data});
        }
    }
});

// Auto-save function
function saveSession(messages, model, temperature) {
    localStorage.setItem('chatbot_messages', JSON.stringify(messages));
    localStorage.setItem('chatbot_model', model);
    localStorage.setItem('chatbot_temperature', temperature.toString());
}

// Make saveSession available globally
window.saveSession = saveSession;
</script>
""", unsafe_allow_html=True)

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
        # Clear localStorage
        st.markdown("""
        <script>
        localStorage.removeItem('chatbot_messages');
        localStorage.removeItem('chatbot_model');
        localStorage.removeItem('chatbot_temperature');
        </script>
        """, unsafe_allow_html=True)
        st.rerun()  # reruns page

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
    if msg["role"] == "user":
        st.markdown(f'''
        <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin: 10px 0;">
            <div class="user-message">{msg["content"]}</div>
            <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #2196f3; margin-left: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">👤</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div style="display: flex; justify-content: flex-start; align-items: flex-start; margin: 10px 0;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #ff6b6b; margin-right: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">🤖</div>
            <div class="assistant-message">{msg["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

# -----------------------------
# Chat input
# -----------------------------
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'''
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin: 10px 0;">
        <div class="user-message">{prompt}</div>
        <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #2196f3; margin-left: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">👤</div>
    </div>
    ''', unsafe_allow_html=True)

    # Generate response from Gemini
    with st.spinner("Thinking..."):
        try:
            response = client.models.generate_content(
                model=st.session_state.model,
                contents=prompt
            )
            reply = response.text
            st.markdown(f'''
            <div style="display: flex; justify-content: flex-start; align-items: flex-start; margin: 10px 0;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #ff6b6b; margin-right: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">🤖</div>
                <div class="assistant-message">{reply}</div>
            </div>
            ''', unsafe_allow_html=True)

            # Save assistant message
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            # Auto-save to localStorage
            st.markdown(f"""
            <script>
            window.saveSession({st.session_state.messages}, '{st.session_state.model}', {st.session_state.temperature});
            </script>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            # Handle API quota exceeded and other errors
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                friendly_error = """
                **API Quota Exceeded**
                
                You have reached the free tier request limit for the Gemini API. Please consider the following options:
                
                **Current Status:**
                - Free tier limit: 20 requests per day
                - Quota reset: Tomorrow at midnight UTC
                
                **Solutions:**
                1. **Wait**: Please try again tomorrow after the quota has been reset.
                2. **Upgrade**: Obtain a paid API key from [Google AI Studio](https://aistudio.google.com/app/apikey) for increased limits.
                3. **Switch**: Utilize an alternative model if available within your current plan.
                
                **Note**: The free tier is intended for evaluation purposes. Paid plans offer significantly higher request limits.
                """
            else:
                friendly_error = f"""
                **API Error**
                
                An error occurred while processing your request:
                
                ```
                {error_msg}
                ```
                
                Please attempt your request again momentarily. If the issue persists, please verify your API configuration.
                """
            
            st.markdown(f'''
            <div style="display: flex; justify-content: flex-start; align-items: flex-start; margin: 10px 0;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #ff6b6b; margin-right: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">🤖</div>
                <div class="assistant-message">{friendly_error}</div>
            </div>
            ''', unsafe_allow_html=True)