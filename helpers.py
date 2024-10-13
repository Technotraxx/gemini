import streamlit as st
import mimetypes
from PIL import Image
import io
import google.generativeai as genai
import tempfile
import os
import time
from moviepy.editor import VideoFileClip

def upload_and_process_file(uploaded_file):
    """
    Processes the uploaded file based on its MIME type.
    Returns a processed file object or PIL Image for images.
    """
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
    """
    Processes an image file and returns a PIL Image object.
    """
    try:
        image = Image.open(uploaded_file)
        # Optionally, perform image processing here (e.g., resizing, filtering)
        return image
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def upload_to_gemini(uploaded_file):
    """
    Uploads a video or audio file to Gemini and returns the file object.
    """
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(uploaded_file.type)) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        
        # Upload the file to Gemini
        file = genai.upload_file(temp_file_path, mime_type=uploaded_file.type)
        wait_for_file_active(file)
        return file
    except Exception as e:
        st.error(f"Error uploading file to Gemini: {str(e)}")
        return None
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def wait_for_file_active(file, timeout=300, check_interval=5):
    """
    Waits for the uploaded file to become active.
    Raises an exception if the file processing fails or times out.
    """
    start_time = time.time()
    while file.state.name == "PROCESSING":
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            raise Exception(f"File {file.name} processing timed out.")
        st.text("Processing file... Please wait.")
        time.sleep(check_interval)
        file = genai.get_file(file.name)
    if file.state.name != "ACTIVE":
        raise Exception(f"File {file.name} failed to process. Current state: {file.state.name}")

def get_gemini_response(chat, user_input, file=None, generation_config=None):
    """
    Sends a message to Gemini and returns the response text.
    Supports optional media and generation configuration.
    """
    try:
        if generation_config is None:
            generation_config = {}
        
        # Prepare parameters based on generation_config
        send_kwargs = {}
        if 'temperature' in generation_config:
            send_kwargs['temperature'] = generation_config['temperature']
        if 'top_p' in generation_config:
            send_kwargs['top_p'] = generation_config['top_p']
        if 'top_k' in generation_config:
            send_kwargs['top_k'] = generation_config['top_k']
        if 'max_output_tokens' in generation_config:
            send_kwargs['max_output_tokens'] = generation_config['max_output_tokens']
        
        if file:
            response = chat.send_message([user_input, file], **send_kwargs)
        else:
            response = chat.send_message(user_input, **send_kwargs)
        return response.text
    except Exception as e:
        st.error(f"Error getting Gemini response: {str(e)}")
        return None

def manage_chat_session(model, history):
    """
    Manages the chat session with the AI model based on history.
    Returns a chat object.
    """
    try:
        chat = model.start_chat(history=history)
        return chat
    except Exception as e:
        st.error(f"Error managing chat session: {str(e)}")
        return None

def display_chat_history(messages):
    """
    Displays the chat history using Streamlit's chat_message.
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def init_chat_session(model_name):
    """
    Initializes a new chat session with the specified model.
    Returns a chat object.
    """
    try:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        st.error(f"Error initializing chat session: {str(e)}")
        return None

def clear_chat_history():
    """
    Clears the chat history and reinitializes the chat session.
    """
    st.session_state.messages = []
    st.session_state.chat = init_chat_session(st.session_state.current_model)

def extract_video_frames(uploaded_file, interval=5):
    """
    Extracts frames from a video file at specified interval (in seconds).
    Returns a list of PIL Image objects.
    """
    temp_file_path = None
    frames = []
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(uploaded_file.type)) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

        video = VideoFileClip(temp_file_path)
        duration = video.duration
        frame_times = list(range(0, int(duration), interval))
        for t in frame_times:
            frame = video.get_frame(t)
            pil_image = Image.fromarray(frame)
            frames.append(pil_image)
        video.close()
        return frames
    except Exception as e:
        st.error(f"Error extracting video frames: {str(e)}")
        return []
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
