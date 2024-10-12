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
