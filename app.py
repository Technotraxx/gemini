import streamlit as st
import google.generativeai as genai
from helpers import (
    upload_and_process_file, 
    manage_chat_session, 
    display_chat_history, 
    get_gemini_response, 
    init_chat_session
)
from settings import MODEL_OPTIONS, DEFAULT_GENERATION_CONFIG, IMAGE_PROMPTS, VIDEO_PROMPTS, AUDIO_PROMPTS, PAGE_CONFIG

# Configure Streamlit page
st.set_page_config(**PAGE_CONFIG)

# Sidebar for configuration
with st.sidebar:
    st.title("Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    selected_model = st.selectbox("Select Gemini Model", list(MODEL_OPTIONS.keys()))
    
    with st.expander("Advanced Settings"):
        temperature = st.slider("Temperature", 0.0, 1.0, DEFAULT_GENERATION_CONFIG["temperature"])
        top_p = st.slider("Top P", 0.0, 1.0, DEFAULT_GENERATION_CONFIG["top_p"])
        top_k = st.slider("Top K", 1, 100, DEFAULT_GENERATION_CONFIG["top_k"])
        max_output_tokens = st.slider("Max Output Tokens", 1, 8192, DEFAULT_GENERATION_CONFIG["max_output_tokens"])

    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_output_tokens": max_output_tokens,
    }

# Main chat interface
st.title("🤖 Chat with Gemini")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_OPTIONS[selected_model])
        if 'chat' not in st.session_state or st.session_state.current_model != MODEL_OPTIONS[selected_model]:
            st.session_state.current_model = MODEL_OPTIONS[selected_model]
            st.session_state.chat = model.start_chat(history=[])
            st.session_state.messages = []
        st.success("API Key configured successfully!")
    except Exception as e:
        st.error(f"Error configuring API Key: {str(e)}")
else:
    st.warning("Please enter your Gemini API Key to start chatting.")

# Display chat messages
display_chat_history(st.session_state.get('messages', []))

# User input
if 'chat' in st.session_state:
    user_input = st.chat_input("Ask Gemini...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        
        response = get_gemini_response(st.session_state.chat, user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)

# File upload and analysis
if 'chat' in st.session_state:
    uploaded_file = st.file_uploader("Upload an image, video, or audio file for analysis", 
                                     type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg'])
    if uploaded_file:
        processed_file = upload_and_process_file(uploaded_file)
        if processed_file:
            if uploaded_file.type.startswith('image/'):
                st.image(processed_file, caption='Uploaded Image', use_column_width=True)
                prompts = IMAGE_PROMPTS
            elif uploaded_file.type.startswith('video/'):
                st.video(uploaded_file)
                prompts = VIDEO_PROMPTS
            elif uploaded_file.type.startswith('audio/'):
                st.audio(uploaded_file)
                prompts = AUDIO_PROMPTS
            
            cols = st.columns(len(prompts))
            for i, (action, prompt) in enumerate(prompts.items()):
                if cols[i].button(action):
                    response = get_gemini_response(st.session_state.chat, prompt, processed_file)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.chat_message("assistant").markdown(response)

else:
    st.info("Enter your API Key in the sidebar to start chatting.")

else:
    st.info("Enter your API Key in the sidebar to start chatting.")
