import streamlit as st

def compact_file_uploader(label, accepted_types):
    uploaded_file = st.file_uploader(label, type=accepted_types, key="file_uploader")
    if uploaded_file:
        st.write("File uploaded successfully!")
    return uploaded_file

def horizontal_radio_buttons(options, key):
    cols = st.columns(len(options))
    for i, (option, col) in enumerate(zip(options, cols)):
        with col:
            if st.button(option, key=f"{key}_{i}"):
                return option
    return None

def floating_chat_input():
    st.markdown(
        """
        <style>
        .floating-chat-input {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 10px;
            background-color: white;
            z-index: 1000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    with st.container():
        st.markdown('<div class="floating-chat-input">', unsafe_allow_html=True)
        user_input = st.text_input("Ask Gemini or enter a prompt...", key="floating_chat_input")
        st.markdown('</div>', unsafe_allow_html=True)
    return user_input

def card_container(title, content):
    st.markdown(
        f"""
        <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
            <h3>{title}</h3>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
