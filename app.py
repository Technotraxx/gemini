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
    st.subheader("Chat History and Responses")
    
    # Clear chat button as an icon
    if st.button("🗑️", help="Clear Chat"):
        clear_chat_history()
        st.rerun()

    # Chat input (keep this at the top)
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel(
                MODEL_OPTIONS[selected_model],
                generation_config=generation_config,
                safety_settings=safety_settings if safety_settings else None
            )
            if 'chat' not in st.session_state or st.session_state.current_model != MODEL_OPTIONS[selected_model]:
                st.session_state.current_model = MODEL_OPTIONS[selected_model]
                st.session_state.chat = model.start_chat(history=[])
                st.session_state.messages = []
            
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

                st.session_state.current_input = {"text": user_input, "media": media}
                st.rerun()
        except Exception as e:
            st.error(f"Error configuring API Key: {str(e)}")
    else:
        st.info("Enter your API Key in the sidebar to start chatting.")

    # Quick Analysis Options
    if 'processed_file' in st.session_state and 'prompts' in st.session_state:
        st.markdown("**Quick Analysis Options:**", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.prompts))
        for option, col in zip(st.session_state.prompts.keys(), cols):
            with col:
                if st.button(option, key=f"button_{option}", use_container_width=True):
                    st.session_state.current_analysis = {"action": option, "prompt": st.session_state.prompts[option]}
                    st.rerun()

    # Process current analysis or input
    if 'current_analysis' in st.session_state:
        user_message = f"[{st.session_state.current_analysis['action']}] {st.session_state.current_analysis['prompt']}"
        st.session_state.messages.append({"role": "user", "content": user_message})
        
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
        del st.session_state.current_analysis
        st.rerun()
        
    if 'current_input' in st.session_state:
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input['text']})
        
        with st.spinner("Gemini is thinking..."):
            response = get_gemini_response(st.session_state.chat, st.session_state.current_input['text'], st.session_state.current_input['media'], safety_settings)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        del st.session_state.current_input
        st.rerun()

    # Display chat history
    display_chat_history(st.session_state.get('messages', []))
