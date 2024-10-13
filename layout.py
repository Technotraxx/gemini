import streamlit as st

def compact_file_uploader(label, accepted_types):
    uploaded_file = st.file_uploader(label, type=accepted_types, key="file_uploader")
    if uploaded_file:
        st.write("File uploaded successfully!")
    return uploaded_file

def horizontal_radio_buttons(options, key):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button(options[0], key=f"{key}_1"):
            return options[0]
    with col2:
        if st.button(options[1], key=f"{key}_2"):
            return options[1]
    with col3:
        if st.button(options[2], key=f"{key}_3"):
            return options[2]
    with col4:
        if st.button(options[3], key=f"{key}_4"):
            return options[3]
    with col5:
        if st.button(options[4], key=f"{key}_5"):
            return options[4]
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
