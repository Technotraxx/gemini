import streamlit as st
import mimetypes
from PIL import Image
import io
import google.generativeai as genai
import moviepy.editor as mp
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os

def upload_and_process_file(uploaded_file):
    if uploaded_file is not None:
        file_extension = mimetypes.guess_extension(uploaded_file.type)
        try:
            if file_extension in ['.png', '.jpg', '.jpeg']:
                return process_image(uploaded_file)
            elif file_extension in ['.mp4', '.avi', '.mov']:
                return process_video(uploaded_file)
            elif file_extension in ['.mp3', '.wav', '.ogg']:
                return process_audio(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_extension}")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    return None

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    return image

def process_video(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(uploaded_file.type)) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name

    try:
        video = mp.VideoFileClip(temp_path)
        thumbnail = video.get_frame(0)
        thumbnail_image = Image.fromarray(thumbnail)
        video.close()
    finally:
        os.unlink(temp_path)
    
    return thumbnail_image

def process_audio(uploaded_file):
    try:
        audio_data, sample_rate = sf.read(io.BytesIO(uploaded_file.getvalue()))
        plt.figure(figsize=(10, 2))
        plt.plot(audio_data)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        waveform_image = Image.open(buf)
        plt.close()
        return waveform_image
    except Exception as e:
        st.error(f"Error processing audio file: {str(e)}")
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

def init_chat_session(model_name):
    try:
        model = genai.GenerativeModel(model_name)
        return model.start_chat(history=[])
    except Exception as e:
        st.error(f"Error initializing chat session: {str(e)}")
        return None
