import streamlit as st
import mimetypes
from PIL import Image
import io
import google.generativeai as genai
import tempfile
import os
import time
from moviepy.editor import VideoFileClip
from google.api_core import exceptions
import re

def upload_and_process_file(uploaded_file):
    if uploaded_file is not None:
        file_extension = mimetypes.guess_extension(uploaded_file.type)
        try:
            if uploaded_file.type.startswith('image/'):
                return process_image(uploaded_file)
            elif uploaded_file.type.startswith('video/') or uploaded_file.type.startswith('audio/'):
                return upload_to_gemini(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_extension}")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    return None

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    return image

def upload_to_gemini(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(uploaded_file.type)) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name
    try:
        file = genai.upload_file(temp_path, mime_type=uploaded_file.type)
        wait_for_file_active(file)
        return file
    finally:
        os.unlink(temp_path)

def wait_for_file_active(file):
    while file.state.name == "PROCESSING":
        st.text("Processing file... Please wait.")
        time.sleep(5)
        file = genai.get_file(file.name)
    if file.state.name != "ACTIVE":
        raise Exception(f"File {file.name} failed to process")

def get_gemini_response(chat, user_input, file=None, safety_settings=None):
    try:
        if safety_settings:
            chat.model.safety_settings = safety_settings
        if file:
            response = chat.send_message([user_input, file])
        else:
            response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        error_message = str(e)
        if "finish_reason: SAFETY" in error_message:
            # Extract safety categories and their probabilities
            safety_info = re.findall(r"category: (\w+) probability: (\w+)", error_message)
            
            user_message = ("The response was blocked due to safety concerns. "
                            "The content was flagged for the following reasons:\n")
            for category, probability in safety_info:
                if probability != "NEGLIGIBLE":
                    category_name = category.replace('HARM_CATEGORY_', '').replace('_', ' ').title()
                    user_message += f"- {category_name} (Probability: {probability.lower()})\n"
            
            user_message += ("\nPlease try rephrasing your request or adjusting the safety settings "
                             "if you believe this is an error.")
            
            st.warning(user_message)
            return user_message
        else:
            st.error(f"Error getting Gemini response: {error_message}")
            return None

def manage_chat_session(model, history):
    if not history or history[-1]['role'] == 'user':
        chat = model.start_chat(history=history[:-1])
        response = chat.send_message(history[-1]['parts'][0])
    else:
        chat = model.start_chat(history=history)
    return chat

def display_chat_history(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def init_chat_session(model_name):
    try:
        model = genai.GenerativeModel(model_name)
        return model.start_chat(history=[])
    except Exception as e:
        st.error(f"Error initializing chat session: {str(e)}")
        return None

def clear_chat_history():
    st.session_state.messages = []
    st.session_state.chat = init_chat_session(st.session_state.current_model)

def extract_video_frames(uploaded_file, interval):
    with tempfile.NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(uploaded_file.type)) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name

    try:
        video = VideoFileClip(temp_path)
        duration = video.duration
        frames = []
        for t in range(0, int(duration), interval):
            frame = video.get_frame(t)
            pil_image = Image.fromarray(frame)
            frames.append(pil_image)
        video.close()
        return frames
    finally:
        os.unlink(temp_path)
