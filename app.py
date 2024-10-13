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
from settings import (
    MODEL_OPTIONS, 
    DEFAULT_GENERATION_CONFIG, 
    IMAGE_PROMPTS, 
    VIDEO_PROMPTS, 
    AUDIO_PROMPTS, 
    PAGE_CONFIG, 
    ACCEPTED_FILE_TYPES
)
from layout import (
    compact_file_uploader, 
    horizontal_radio_buttons,
    render_sidebar,
    render_main_content
)

# Configure Streamlit page
st.set_page_config(**PAGE_CONFIG, layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = None
if 'prompts' not in st.session_state:
    st.session_state.prompts = {}    

# Render sidebar
api_key, selected_model, generation_config, safety_settings = render_sidebar()

# Main content
left_column, _, right_column = st.columns([2, 1, 4])

with left_column:
    st.subheader("File Upload and Preview")
    uploaded_file = compact_file_uploader("Upload file", ACCEPTED_FILE_TYPES)
    if uploaded_file:
        st.session_state.processed_file = upload_and_process_file(uploaded_file)
        if uploaded_file.type.startswith('image/'):
            st.image(st.session_state.processed_file, caption='Uploaded Image', use_column_width=True)
            st.session_state.prompts = IMAGE_PROMPTS
        elif uploaded_file.type.startswith('video/'):
            st.video(uploaded_file, start_time=0)
            st.session_state.prompts = VIDEO_PROMPTS
        elif uploaded_file.type.startswith('audio/'):
            st.audio(uploaded_file)
            st.session_state.prompts = AUDIO_PROMPTS

with right_column:
    render_main_content(api_key, selected_model, MODEL_OPTIONS, generation_config, safety_settings if safety_settings else None)

    # Process current analysis or input
    if 'current_analysis' in st.session_state:
        with st.spinner(f"Analyzing with {st.session_state.current_analysis['action']}..."):
            if 'frames' in st.session_state and st.session_state.get('processed_file') and st.session_state.processed_file.type.startswith('video/'):
                responses = []
                for j, frame in enumerate(st.session_state.frames):
                    response = get_gemini_response(st.session_state.chat, f"{st.session_state.current_analysis['prompt']} (Frame {j+1})", frame, safety_settings)
                    responses.append(f"Frame {j+1}: {response}")
                response = "\n\n".join(responses)
            else:
                response = get_gemini_response(st.session_state.chat, st.session_state.current_analysis['prompt'], st.session_state.get('processed_file'), safety_settings)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").markdown(response)
        del st.session_state.current_analysis

    if 'current_input' in st.session_state:
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input['text']})
        st.chat_message("user").markdown(st.session_state.current_input['text'])
        
        with st.spinner("Gemini is thinking..."):
            response = get_gemini_response(st.session_state.chat, st.session_state.current_input['text'], st.session_state.current_input['media'], safety_settings)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)
        del st.session_state.current_input
