import streamlit as st
import mimetypes
from PIL import Image
import io
import google.generativeai as genai
import tempfile
import os
import time

def upload_and_process_file(uploaded_file, preview_width=None):
    if uploaded_file is not None:
        file_extension = mimetypes.guess_extension(uploaded_file.type)
        try:
            if uploaded_file.type.startswith('image/'):
                return process_image(uploaded_file, preview_width)
            elif uploaded_file.type.startswith('video/') or uploaded_file.type.startswith('audio/'):
                return upload_to_gemini(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_extension}")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    return None

def process_image(uploaded_file, preview_width=None):
    image = Image.open(uploaded_file)
    if preview_width:
        width, height = image.size
        new_height = int(height * (preview_width / width))
        image.thumbnail((preview_width, new_height))
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

def get_gemini_response(chat, user_input, file=None):
    try:
        if file:
            response = chat.send_message([user_input, file])
        else:
            response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        st.error(f"Error getting Gemini response: {str(e)}")
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
