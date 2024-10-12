import streamlit as st
import mimetypes
from PIL import Image
import io
import google.generativeai as genai

def upload_and_process_file(uploaded_file):
    if uploaded_file is not None:
        file_extension = mimetypes.guess_extension(uploaded_file.type)
        if file_extension in ['.png', '.jpg', '.jpeg']:
            return process_image(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
    return None

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    return image

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

def get_gemini_response(chat, user_input, image=None):
    if image:
        response = chat.send_message([user_input, image])
    else:
        response = chat.send_message(user_input)
    return response.text

def init_chat_session(model_name):
    model = genai.GenerativeModel(model_name)
    return model.start_chat(history=[])
