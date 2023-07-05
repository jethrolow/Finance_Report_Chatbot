from PyPDF2 import PdfReader
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from streamlit_chat import message as st_message
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.prompts import PromptTemplate

def get_text_from_pdf(fr_pdf_docs: list):
    text_output = ""
    for pdf_file in fr_pdf_docs:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text_output = text_output + page.extract_text()
    return text_output

def chunk_text_from_whole_text(whole_text: str):
    text_split = RecursiveCharacterTextSplitter(
        separators = ["\n\n", "\n", " ", ""],
        chunk_size = 1500,
        chunk_overlap = 200,
        length_function = len
    )
    chunks = text_split.split_text(whole_text)
    return chunks

def convert_text_vectorstore(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts = chunks, embedding = embeddings)
    return vectorstore

def process_query(user_question):
    # QA prompt
    system_template = """### Instruction ###
    Use the following pieces of context to answer the users question.
    ### Guidelines ###
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Your role is as a financial analyst
    No matter what the question is, you should always answer it in the context provided below.
    If you are unsure of the answer, just say "I do not know"
    ### context ###
    {context}"""

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain_type_kwargs = {"prompt": chat_prompt}

    # Condensed QA prompt
    memory_template = """
    Given the following chat history and a follow up question, rephrase the\
    follow up question to be a standalone question.\
    The follow up question may not always be based on the chat history.\
    If follow up question is not based on the chat history, do not rephrase it.\
    If follow up question is not based on the chat history, you should still answer it\
    in the context given below.\
    If the question is not related to the context below, just say that "I don't know".\
    Chat History:{chat_history}\
    Follow Up Question: {question}\
    Standalone Question:
    """
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(memory_template)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=st.session_state.final_store.as_retriever(),
        chain_type="stuff",
        return_source_documents=True,
        output_key="answer",
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs= chain_type_kwargs
    )
    response = chain({"question": user_question, "chat_history": st.session_state.history_model})
    st.session_state.history_model.append((user_question, response["answer"]))
    return response

def generate_answer():
    user_message = st.session_state.input_text
    response = process_query(user_message)

    st.session_state.history.append({"message": user_message, "is_user": True})
    st.session_state.history.append({"message": response['answer'], "is_user": False})
    st.session_state.source = (response['source_documents'])

def is_financial_report(vector_store):
    system_template = """Use the following pieces of context to answer the users question.\
    No matter what the question is, you should always answer it as truthfully and accurately as possible\\
    If you don't know the answer, just say that "I don't know", don't try to make up an answer.\
    Your task is to classify if the report is a financial report or not a financial report.\
    Again, your task is to classify if the report is a financial report or not a financial report.\
    ----------------
    {context}"""

    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}\Classification:"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)
    chain_type_kwargs = {"prompt": prompt}

    qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.0), chain_type="stuff", retriever=vector_store.as_retriever(), chain_type_kwargs=chain_type_kwargs)
    query = "Please classify if the report is a financial report or not a financial report"
    st.session_state.is_finance_report = qa.run(query)

def preprocessing(fr_pdf_docs):
    whole_text = get_text_from_pdf(fr_pdf_docs=fr_pdf_docs)
    chunked_text = chunk_text_from_whole_text(whole_text)
    vectorstore = convert_text_vectorstore(chunked_text)
    is_financial_report(vectorstore)
    st.session_state.final_store = vectorstore
    return vectorstore


                                  


