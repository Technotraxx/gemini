import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from helpers import clear_chat_history, display_chat_history
from settings import MODEL_OPTIONS, DEFAULT_GENERATION_CONFIG

def compact_file_uploader(label, accepted_types):
    uploaded_file = st.file_uploader(label, type=accepted_types, key="file_uploader")
    if uploaded_file:
        st.write("File uploaded successfully!")
    return uploaded_file

def horizontal_radio_buttons(options, key):
    cols = st.columns(len(options))
    for i, (option, col) in enumerate(zip(options, cols)):
        with col:
            if st.button(option, key=f"{key}_{i}", use_container_width=True):
                return option
    return None

def render_sidebar():
    with st.sidebar:
        st.title("🤖 Chat with Gemini")
        api_key = st.text_input("Enter your Gemini API Key", type="password")
        selected_model = st.selectbox("Select Gemini Model", list(MODEL_OPTIONS.keys()))
        
        generation_config = DEFAULT_GENERATION_CONFIG.copy()
        safety_settings = None
        
        with st.expander("Advanced Settings"):
            st.subheader("Generation Settings")
            generation_config["temperature"] = st.slider("Temperature", 0.0, 1.0, DEFAULT_GENERATION_CONFIG["temperature"])
            generation_config["top_p"] = st.slider("Top P", 0.0, 1.0, DEFAULT_GENERATION_CONFIG["top_p"])
            generation_config["top_k"] = st.slider("Top K", 1, 100, DEFAULT_GENERATION_CONFIG["top_k"])
            generation_config["max_output_tokens"] = st.slider("Max Output Tokens", 1, 8192, DEFAULT_GENERATION_CONFIG["max_output_tokens"])

            st.subheader("Safety Settings")
            safety_options = {
                "Block none": HarmBlockThreshold.BLOCK_NONE,
                "Block few": HarmBlockThreshold.BLOCK_ONLY_HIGH,
                "Block some": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                "Block most": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            }
            
            safety_categories = [
                ("Harassment", HarmCategory.HARM_CATEGORY_HARASSMENT),
                ("Hate Speech", HarmCategory.HARM_CATEGORY_HATE_SPEECH),
                ("Sexually Explicit", HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT),
                ("Dangerous Content", HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT)
            ]

            safety_settings = []
            for category_name, category in safety_categories:
                setting = st.selectbox(category_name, list(safety_options.keys()), index=0)
                safety_settings.append({
                    "category": category,
                    "threshold": safety_options[setting]
                })

    return api_key, selected_model, generation_config, safety_settings

def render_main_content(api_key, selected_model, MODEL_OPTIONS, generation_config, safety_settings):
    st.subheader("Chat History and Responses")
    
    # Clear chat button as an icon
    if st.button("🗑️", help="Clear Chat"):
        clear_chat_history()
        st.rerun()

    # Quick Analysis Options
    if 'processed_file' in st.session_state and 'prompts' in st.session_state:
        st.markdown("**Quick Analysis Options:**", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.prompts))
        for option, col in zip(st.session_state.prompts.keys(), cols):
            with col:
                if st.button(option, key=f"button_{option}", use_container_width=True):
                    st.session_state.current_analysis = {"action": option, "prompt": st.session_state.prompts[option]}
                    # Remove the message addition from here
                    st.rerun()

    # Chat input
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
    
    # Add a separator
    st.markdown("---")
    
    # Display chat history
    display_chat_history(st.session_state.get('messages', []))
