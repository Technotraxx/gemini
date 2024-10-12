import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Gemini!",
    page_icon=":robot_face:",
    layout="wide",
)

# Function to initialize or reset the chat session
def init_chat_session(model_name):
    model = genai.GenerativeModel(model_name)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

# Sidebar for configuration
with st.sidebar:
    st.title("Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    
    model_options = {
        "Gemini 1.5 Flash": "gemini-1.5-flash",
        "Gemini 1.5 Flash-8B": "gemini-1.5-flash-8b",
        "Gemini 1.5 Pro": "gemini-1.5-pro"
    }
    selected_model = st.selectbox("Select Gemini Model", list(model_options.keys()))
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            if 'chat' not in st.session_state or st.session_state.current_model != model_options[selected_model]:
                st.session_state.current_model = model_options[selected_model]
                init_chat_session(st.session_state.current_model)
            st.success("API Key configured successfully!")
        except Exception as e:
            st.error(f"Error configuring API Key: {str(e)}")
    else:
        st.warning("Please enter your Gemini API Key to start chatting.")

# Main chat interface
st.title("🤖 Chat with Gemini")

# Display chat messages
for message in st.session_state.get('messages', []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if 'chat' in st.session_state:
    user_input = st.chat_input("Ask Gemini...")
    if user_input:
        # Display user message
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get and display Gemini's response
        try:
            response = st.session_state.chat.send_message(user_input)
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error getting response from Gemini: {str(e)}")

# Option to upload image
if 'chat' in st.session_state:
    uploaded_file = st.file_uploader("Upload an image for analysis", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        if st.button('Analyze Image'):
            try:
                response = st.session_state.chat.send_message([image, "Describe this image"])
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error analyzing image: {str(e)}")

else:
    st.info("Enter your API Key in the sidebar to start chatting.")
