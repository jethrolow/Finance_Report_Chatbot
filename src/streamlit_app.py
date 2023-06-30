import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import get_text_from_pdf, chunk_text_from_whole_text, convert_text_vectorstore, get_conversation_chain, handle_user_input

# test


def main():
    load_dotenv()

    st.set_page_config(
    page_title="Financial Statements Q&A Chatbot!",
    page_icon="owl",
    layout="centered",
    initial_sidebar_state="expanded",
    )
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    st.header(":owl: Financial Statements Q&A Chatbot! :owl:")
    col1, col2= st.columns(2)


    
    with col1:
        st.header("Chat")
        user_question = st.text_input("Ask me a question relating to the financial statements")
        if user_question:
            response = handle_user_input(user_question, st.session_state.conversation)
            # st.write(type(response['chat_history'][0]))
            st.write(response['answer'])

        with st.sidebar:
            st.subheader("Model Selection")
            model_type = st.radio(label = "Please choose the LLM model to run chatbot", options = ('OpenAI',"HuggingFace"))
            st.subheader("Upload your financial statements")
            fs_pdf_docs = st.file_uploader("You can upload more than one financial statement documents. Please ensure file is in PDF format.", accept_multiple_files = True)

            if st.button("OK"):
                with st.spinner("In progress..."):
                    whole_text = get_text_from_pdf(fs_pdf_docs=fs_pdf_docs)
                    chunked_text = chunk_text_from_whole_text(whole_text)
                    vectorstore = convert_text_vectorstore(chunked_text)
                    if vectorstore is not None:
                        st.write("Conversion to vectorstore completed!")
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                    

if __name__ == '__main__':
    main()