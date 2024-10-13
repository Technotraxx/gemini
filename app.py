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
from settings import MODEL_OPTIONS, DEFAULT_GENERATION_CONFIG, IMAGE_PROMPTS, VIDEO_PROMPTS, AUDIO_PROMPTS, PAGE_CONFIG, ACCEPTED_FILE_TYPES

# Configure Streamlit page
st.set_page_config(**PAGE_CONFIG, layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = None
if 'chat_input_key' not in st.session_state:
    st.session_state.chat_input_key = 0

# Sidebar configuration
with st.sidebar:
    st.title("Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    selected_model = st.selectbox("Select Gemini Model", list(MODEL_OPTIONS.keys()))
    
    show_advanced = st.checkbox("Show Advanced Settings")
    
    if show_advanced:
        st.subheader("Advanced Settings")
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

# Main content
left_column, right_column = st.columns([2, 3])

with left_column:
    st.title("🤖 Chat with Gemini")

    if st.button("Clear Chat"):
        clear_chat_history()
        st.session_state.chat_input_key += 1
        st.rerun()

    # File upload
    uploaded_file = st.file_uploader("Upload an image, video, or audio file (optional)", 
                                     type=ACCEPTED_FILE_TYPES)
    if uploaded_file:
        st.session_state.processed_file = upload_and_process_file(uploaded_file)
        if uploaded_file.type.startswith('image/'):
            st.image(st.session_state.processed_file, caption='Uploaded Image', use_column_width=False, width=300)
            prompts = IMAGE_PROMPTS
        elif uploaded_file.type.startswith('video/'):
            st.video(uploaded_file, start_time=0)
            prompts = VIDEO_PROMPTS
        elif uploaded_file.type.startswith('audio/'):
            st.audio(uploaded_file)
            prompts = AUDIO_PROMPTS
        
        # Horizontal Quick Analysis Options
        st.subheader("Quick Analysis Options")
        cols = st.columns(len(prompts))
        for i, (action, prompt) in enumerate(prompts.items()):
            with cols[i]:
                if st.button(action):
                    st.session_state.current_analysis = {"action": action, "prompt": prompt}
                    st.rerun()

    # Chat input
    chat_input_container = st.container()
    with chat_input_container:
        with st.form(key=f"chat_form_{st.session_state.chat_input_key}"):
            user_input = st.text_input("Ask Gemini or enter a prompt...", key=f"user_input_{st.session_state.chat_input_key}")
            submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            media = st.session_state.get('processed_file')
            st.session_state.current_input = {"text": user_input, "media": media}
            st.session_state.chat_input_key += 1
            st.rerun()

with right_column:
    st.subheader("Chat History and Responses")
    
    # Display chat history
    display_chat_history(st.session_state.get('messages', []))

    # Process current analysis or input
    if 'current_analysis' in st.session_state:
        with st.spinner(f"Analyzing with {st.session_state.current_analysis['action']}..."):
            if 'frames' in st.session_state and st.session_state.get('processed_file') and st.session_state.processed_file.type.startswith('video/'):
                responses = []
                for j, frame in enumerate(st.session_state.frames):
                    response = get_gemini_response(st.session_state.chat, f"{st.session_state.current_analysis['prompt']} (Frame {j+1})", frame)
                    responses.append(f"Frame {j+1}: {response}")
                response = "\n\n".join(responses)
            else:
                response = get_gemini_response(st.session_state.chat, st.session_state.current_analysis['prompt'], st.session_state.get('processed_file'))
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").markdown(response)
        del st.session_state.current_analysis

    if 'current_input' in st.session_state:
        st.session_state.messages.append({"role": "user", "content": st.session_state.current_input['text']})
        st.chat_message("user").markdown(st.session_state.current_input['text'])
        
        with st.spinner("Gemini is thinking..."):
            response = get_gemini_response(st.session_state.chat, st.session_state.current_input['text'], st.session_state.current_input['media'])
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)
        del st.session_state.current_input
