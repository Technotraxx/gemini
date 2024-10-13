import streamlit as st
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from settings import DEFAULT_GENERATION_CONFIG, MODEL_OPTIONS

def render_sidebar():
    with st.sidebar:
        st.title("🤖 Chat with Gemini")
        api_key = st.text_input("Enter your Gemini API Key", type="password")
        selected_model = st.selectbox("Select Gemini Model", list(MODEL_OPTIONS.keys()))
        
        show_advanced = st.checkbox("Show Advanced Settings")
        
        if show_advanced:
            st.subheader("Advanced Settings")
            temperature = st.slider("Temperature", 0.0, 1.0, DEFAULT_GENERATION_CONFIG["temperature"])
            top_p = st.slider("Top P", 0.0, 1.0, DEFAULT_GENERATION_CONFIG["top_p"])
            top_k = st.slider("Top K", 1, 100, DEFAULT_GENERATION_CONFIG["top_k"])
            max_output_tokens = st.slider("Max Output Tokens", 1, 8192, DEFAULT_GENERATION_CONFIG["max_output_tokens"])

            st.subheader("Safety Settings")
            safety_options = {
                "Block none": HarmBlockThreshold.BLOCK_NONE,
                "Block few": HarmBlockThreshold.BLOCK_ONLY_HIGH,
                "Block some": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                "Block most": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            }
            
            harassment_setting = st.selectbox("Harassment", list(safety_options.keys()), index=1)
            hate_speech_setting = st.selectbox("Hate Speech", list(safety_options.keys()), index=1)
            sexually_explicit_setting = st.selectbox("Sexually Explicit", list(safety_options.keys()), index=1)
            dangerous_content_setting = st.selectbox("Dangerous Content", list(safety_options.keys()), index=1)

            safety_settings = {
                HarmCategory.HARASSMENT: safety_options[harassment_setting],
                HarmCategory.HATE_SPEECH: safety_options[hate_speech_setting],
                HarmCategory.SEXUALLY_EXPLICIT: safety_options[sexually_explicit_setting],
                HarmCategory.DANGEROUS_CONTENT: safety_options[dangerous_content_setting]
            }

            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_output_tokens,
            }
        else:
            generation_config = DEFAULT_GENERATION_CONFIG
            safety_settings = None

    return api_key, selected_model, generation_config, safety_settings
