import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import *
from streamlit_chat import message as st_message

def main():

    # Load environment variables for API key
    load_dotenv()

    # set page config
    st.set_page_config(
    page_title="Financial Reports Q&A Chatbot!",
    page_icon="owl",
    layout= "wide",
    initial_sidebar_state="expanded",
    )

    #initialise session_state variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "history_model" not in st.session_state:
        st.session_state.history_model = []
    if "source" not in st.session_state:
        st.session_state.source = []
    if "final_store" not in st.session_state:
        st.session_state.final_store = None
    if "input_text" not in st.session_state:
        st.session_state.input_text = None

    st.markdown("<h1 style='text-align: center; color: white;'>Financial Reports Q&A Chatbot!</h1>", unsafe_allow_html=True)

    st.header("Chat")
    
    with st.sidebar:
        st.subheader("Upload your financial statements")
        pdf_file = st.file_uploader("Upload a financial statement document. Please ensure file is in PDF format.", accept_multiple_files = False)

        if st.button("OK"):
            with st.spinner("Reading your document..."):
                # preprocessing
                st.session_state.final_store = preprocessing(pdf_file= pdf_file)
                if st.session_state.final_store is not None:
                    st.write("Ready! You can start chatting with your financial reports!")

    # generate answers
    st.text_input("Ask me a question relating to the financial statements", key = "input_text", on_change = generate_answer)

    #display chats
    for chat in st.session_state.history:
        st_message(**chat)

if __name__ == '__main__':
    main()