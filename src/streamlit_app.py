import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import *

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
    if "is_finance_report" not in st.session_state:
        st.session_state.is_finance_report = ""
    if "final_store" not in st.session_state:
        st.session_state.final_store = None

    st.markdown("<h1 style='text-align: center; color: white;'>Financial Reports Q&A Chatbot!</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:

        st.header("Chat")
        
        with st.sidebar:
            st.subheader("Upload your financial statements")
            fr_pdf_docs = st.file_uploader("You can upload more than one financial statement documents. Please ensure file is in PDF format.", accept_multiple_files = True)

            if st.button("OK"):
                with st.spinner("Reading your document..."):
                    # preprocessing
                    final_store = preprocessing(fr_pdf_docs= fr_pdf_docs)
                    if final_store is not None:
                        st.write("Ready! You can start chatting with your financial reports!")
            if st.session_state.is_finance_report is not None:
                st.write(st.session_state.is_finance_report)

        # generate answers
        st.text_input("Ask me a question relating to the financial statements", key = "input_text", on_change = generate_answer)

        #display chats
        for chat in st.session_state.history:
            st_message(**chat)

    # show source documents
    with col2:
        st.header("Source")
        st.write("""This is the source document for the latest response from the ChatBot.
        Inspect the source document to ensure factual truth of the response""")
        if st.session_state.source:
            st.write(st.session_state.source)

if __name__ == '__main__':
    main()