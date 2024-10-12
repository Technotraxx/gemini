# Gemini model options
MODEL_OPTIONS = {
    "Gemini 1.5 Flash": "gemini-1.5-flash",
    "Gemini 1.5 Flash-8B": "gemini-1.5-flash-8b",
    "Gemini 1.5 Pro": "gemini-1.5-pro"
}

# Default generation config
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
}

# Image analysis prompts
IMAGE_PROMPTS = {
    "Describe": "Describe this image in detail.",
    "Identify Objects": "List and describe the main objects in this image.",
    "Analyze Colors": "Analyze the color palette and mood of this image.",
    "Detect Text": "Identify and transcribe any text visible in this image.",
    "Suggest Caption": "Suggest a creative caption for this image.",
}

# Streamlit page config
PAGE_CONFIG = {
    "page_title": "Chat with Gemini!",
    "page_icon": ":robot_face:",
    "layout": "wide",
}

# Video analysis prompts
VIDEO_PROMPTS = {
    "Describe Scene": "Describe the main scene in this video thumbnail.",
    "Identify Objects": "List and describe the main objects visible in this video thumbnail.",
    "Analyze Action": "What action or activity seems to be happening in this video based on the thumbnail?",
    "Suggest Title": "Suggest a title for this video based on the thumbnail.",
}

# Audio analysis prompts
AUDIO_PROMPTS = {
    "Describe Waveform": "Describe the characteristics of this audio waveform.",
    "Guess Genre": "Based on the waveform, what genre of music or type of audio might this be?",
    "Analyze Pattern": "Are there any notable patterns or repetitions in this audio waveform?",
    "Estimate Duration": "Based on the waveform, estimate the possible duration of this audio.",
}
