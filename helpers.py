import streamlit as st
import mimetypes
from PIL import Image
import io
import google.generativeai as genai
import moviepy.editor as mp
import soundfile as sf
import numpy as np

def upload_and_process_file(uploaded_file):
    if uploaded_file is not None:
        file_extension = mimetypes.guess_extension(uploaded_file.type)
        if file_extension in ['.png', '.jpg', '.jpeg']:
            return process_image(uploaded_file)
        elif file_extension in ['.mp4', '.avi', '.mov']:
            return process_video(uploaded_file)
        elif file_extension in ['.mp3', '.wav', '.ogg']:
            return process_audio(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
    return None

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    return image

def process_video(uploaded_file):
    # Save the uploaded file temporarily
    temp_path = f"temp_video{mimetypes.guess_extension(uploaded_file.type)}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Load the video and extract the first frame as a thumbnail
    video = mp.VideoFileClip(temp_path)
    thumbnail = video.get_frame(0)
    thumbnail_image = Image.fromarray(thumbnail)
    
    # Clean up
    video.close()
    import os
    os.remove(temp_path)
    
    return thumbnail_image

def process_audio(uploaded_file):
    # Read the audio file
    audio_data, sample_rate = sf.read(io.BytesIO(uploaded_file.getvalue()))
    
    # Generate a simple waveform image
    plt.figure(figsize=(10, 2))
    plt.plot(audio_data)
    plt.axis('off')
    
    # Save the plot to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert the buffer to an image
    waveform_image = Image.open(buf)
    
    return waveform_image

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
