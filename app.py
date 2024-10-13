import streamlit as st
import google.generativeai as genai
from helpers import (
    upload_and_process_file, 
    manage_chat_session, 
    display_chat_history, 
    get_gemini_response, 
    init_chat_session,
    clear_chat_history,
    extract_video_frames
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

    if st.button("Clear Chat"):
        clear_chat_history()
        st.rerun()

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

# File upload
if 'chat' in st.session_state:
    uploaded_file = st.file_uploader("Upload an image, video, or audio file (optional)", 
                                     type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'ogg'])
    if uploaded_file:
        st.session_state.processed_file = upload_and_process_file(uploaded_file)
        if uploaded_file.type.startswith('image/'):
            st.image(st.session_state.processed_file, caption='Uploaded Image', use_column_width=True)
        elif uploaded_file.type.startswith('video/'):
            st.video(uploaded_file)
            if st.checkbox("Extract frames for analysis"):
                frame_interval = st.slider("Select frame interval (seconds)", 1, 60, 10)
                st.session_state.frames = extract_video_frames(uploaded_file, frame_interval)
                st.write(f"Extracted {len(st.session_state.frames)} frames")
                st.image(st.session_state.frames[0], caption="First extracted frame", use_column_width=True)
        elif uploaded_file.type.startswith('audio/'):
            st.audio(uploaded_file)

    # Display chat history
    display_chat_history(st.session_state.get('messages', []))

    # Streamlined chat input and media selection
    user_input = st.chat_input("Ask Gemini or enter a prompt...")
    if user_input:
        media_options = ["No media"]
        if 'processed_file' in st.session_state:
            media_options.append("Uploaded file")
        if 'frames' in st.session_state:
            media_options.append("Extracted frame")
        
        media_option = st.radio("Include media with your message:", media_options)
        
        media = None
        if media_option == "Uploaded file" and 'processed_file' in st.session_state:
            media = st.session_state.processed_file
        elif media_option == "Extracted frame" and 'frames' in st.session_state:
            frame_index = st.selectbox("Select frame:", range(len(st.session_state.frames)))
            media = st.session_state.frames[frame_index]

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)
        
        with st.spinner("Gemini is thinking..."):
            response = get_gemini_response(st.session_state.chat, user_input, media)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)

else:
    st.info("Enter your API Key in the sidebar to start chatting.")
