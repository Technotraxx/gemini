import streamlit as st
from importlib.metadata import version, PackageNotFoundError
from packaging import version as pkg_version  # To compare versions
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

import warnings
# Suppress SyntaxWarnings from moviepy (temporary workaround)
warnings.filterwarnings("ignore", category=SyntaxWarning, module="moviepy")

# ----------------------------
# 1. Streamlit Version Check
# ----------------------------
required_version = "1.21.0"
try:
    current_version = version("streamlit")
    if pkg_version.parse(current_version) < pkg_version.parse(required_version):
        st.error(f"Please update Streamlit to version {required_version} or higher to use chat features.")
        st.stop()
except PackageNotFoundError:
    st.error("Streamlit is not installed.")
    st.stop()

# ----------------------------
# 2. Configure Streamlit Page
# ----------------------------
st.set_page_config(**PAGE_CONFIG, layout="wide")

# ----------------------------
# 3. Initialize Session State
# ----------------------------
def initialize_session_state():
    """Initialize all necessary session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None
    if 'chat' not in st.session_state:
        st.session_state.chat = None
    if 'processed_file' not in st.session_state:
        st.session_state.processed_file = None
    if 'frames' not in st.session_state:
        st.session_state.frames = []
    if 'generation_config' not in st.session_state:
        st.session_state.generation_config = DEFAULT_GENERATION_CONFIG
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'current_input' not in st.session_state:
        st.session_state.current_input = None

initialize_session_state()

# ----------------------------
# 4. Sidebar Configuration
# ----------------------------
with st.sidebar:
    st.title("Configuration")
    
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    selected_model = st.selectbox("Select Gemini Model", list(MODEL_OPTIONS.keys()))
    
    show_advanced = st.checkbox("Show Advanced Settings")
    
    if show_advanced:
        st.subheader("Advanced Settings")
        temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.generation_config["temperature"])
        top_p = st.slider("Top P", 0.0, 1.0, st.session_state.generation_config["top_p"])
        top_k = st.slider("Top K", 1, 100, st.session_state.generation_config["top_k"])
        max_output_tokens = st.slider("Max Output Tokens", 1, 8192, st.session_state.generation_config["max_output_tokens"])

        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
        }
        st.session_state.generation_config = generation_config
    else:
        st.session_state.generation_config = DEFAULT_GENERATION_CONFIG

    # Configure Gemini API
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(MODEL_OPTIONS[selected_model])
            
            # Initialize or switch chat session if model or generation config changes
            if (st.session_state.chat is None) or (st.session_state.current_model != MODEL_OPTIONS[selected_model]) or (st.session_state.generation_config != DEFAULT_GENERATION_CONFIG):
                st.session_state.current_model = MODEL_OPTIONS[selected_model]
                st.session_state.chat = init_chat_session(st.session_state.current_model, st.session_state.generation_config)
                st.session_state.messages = []
            
            st.success("API Key configured successfully!")
        except genai.GenerativeAIError as e:
            st.error(f"Gemini API Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error configuring API Key: {str(e)}")
    else:
        st.warning("Please enter your Gemini API Key to start chatting.")

# ----------------------------
# 5. Main Content Layout
# ----------------------------
left_column, right_column = st.columns([2, 3])

# ----------------------------
# 5.1 Left Column: Chat Interface
# ----------------------------
with left_column:
    st.title("🤖 Chat with Gemini")

    if st.button("Clear Chat"):
        clear_chat_history()
        st.experimental_rerun()

    # File upload
    uploaded_file = st.file_uploader(
        "Upload an image, video, or audio file (optional)", 
        type=ACCEPTED_FILE_TYPES
    )
    
    if uploaded_file:
        try:
            st.session_state.processed_file = upload_and_process_file(uploaded_file)
            
            # Display uploaded media
            if uploaded_file.type.startswith('image/'):
                st.image(
                    st.session_state.processed_file, 
                    caption='Uploaded Image', 
                    use_column_width=False, 
                    width=300
                )
                prompts = IMAGE_PROMPTS
            elif uploaded_file.type.startswith('video/'):
                st.video(uploaded_file, start_time=0)
                st.session_state.frames = extract_video_frames(uploaded_file)
                prompts = VIDEO_PROMPTS
            elif uploaded_file.type.startswith('audio/'):
                st.audio(uploaded_file)
                prompts = AUDIO_PROMPTS
            else:
                prompts = {}
                st.warning("Unsupported file type uploaded.")
            
            # Horizontal Quick Analysis Options
            if prompts:
                st.subheader("Quick Analysis Options")
                cols = st.columns(len(prompts))
                for i, (action, prompt) in enumerate(prompts.items()):
                    with cols[i]:
                        if st.button(action):
                            st.session_state.current_analysis = {"action": action, "prompt": prompt}
                            st.experimental_rerun()
            else:
                st.info("No analysis options available for the uploaded file type.")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    # Chat input
    if st.session_state.chat:
        user_input = st.chat_input("Ask Gemini or enter a prompt...")
        if user_input:
            media_options = ["No media"]
            if st.session_state.processed_file:
                media_options.append("Uploaded file")
            if st.session_state.frames:
                media_options.append("Extracted frame")
            
            media_option = st.radio("Include media with your message:", media_options, key="media_option")
            
            media = None
            if media_option == "Uploaded file" and st.session_state.processed_file:
                media = st.session_state.processed_file
            elif media_option == "Extracted frame" and st.session_state.frames:
                frame_index = st.selectbox("Select frame:", range(len(st.session_state.frames)), key="frame_select")
                media = st.session_state.frames[frame_index]
            elif media_option in ["Uploaded file", "Extracted frame"]:
                st.error("Selected media option is not available.")
            
            st.session_state.current_input = {"text": user_input, "media": media}
            st.experimental_rerun()
    else:
        st.info("Enter your API Key in the sidebar to start chatting.")

# ----------------------------
# 5.2 Right Column: Chat History and Responses
# ----------------------------
with right_column:
    st.subheader("Chat History and Responses")
    
    # Display chat history
    display_chat_history(st.session_state.get('messages', []))
    
    # Process current analysis
    if st.session_state.current_analysis:
        action = st.session_state.current_analysis['action']
        prompt = st.session_state.current_analysis['prompt']
        
        with st.spinner(f"Analyzing with {action}..."):
            try:
                if (
                    st.session_state.frames 
                    and st.session_state.processed_file 
                    and st.session_state.processed_file.type.startswith('video/')
                ):
                    responses = []
                    for j, frame in enumerate(st.session_state.frames):
                        frame_prompt = f"{prompt} (Frame {j+1})"
                        response = get_gemini_response(
                            st.session_state.chat, 
                            frame_prompt, 
                            frame
                        )
                        responses.append(f"**Frame {j+1}:** {response}")
                    response_combined = "\n\n".join(responses)
                else:
                    response_combined = get_gemini_response(
                        st.session_state.chat, 
                        prompt, 
                        st.session_state.get('processed_file')
                    )
                
                if response_combined:
                    st.session_state.messages.append({"role": "assistant", "content": response_combined})
                    st.chat_message("assistant").markdown(response_combined)
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
        
        st.session_state.current_analysis = None

    # Process current user input
    if st.session_state.current_input:
        user_text = st.session_state.current_input['text']
        user_media = st.session_state.current_input['media']
        
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.chat_message("user").markdown(user_text)
        
        with st.spinner("Gemini is thinking..."):
            try:
                response = get_gemini_response(
                    st.session_state.chat, 
                    user_text, 
                    user_media
                )
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.chat_message("assistant").markdown(response)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
        
        st.session_state.current_input = None

# ----------------------------
# 6. Helper Function Definitions
# ----------------------------
# Note: Ensure that all helper functions in helpers.py are updated to handle the new parameters if necessary.
# For example, get_gemini_response should no longer accept generation_config as it's now set during chat session initialization.

# ----------------------------
# 7. Additional Recommendations
# ----------------------------
# - **Logging**: For production, consider implementing logging to monitor application behavior and errors.
# - **Caching**: Use Streamlit's caching mechanisms to cache expensive operations if applicable.
# - **Security**: Ensure that uploaded files are securely handled and validated to prevent security vulnerabilities.
# - **Performance**: Optimize media processing, especially for large video files, possibly by limiting the number of frames extracted or using asynchronous processing.
