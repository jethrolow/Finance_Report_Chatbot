
import streamlit as st
import nest_asyncio
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_parse import LlamaParse
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
import os
nest_asyncio.apply()

embed_model = OpenAIEmbedding(model="text-embedding-3-small")
llm = OpenAI(model="gpt-3.5-turbo-0125")

Settings.llm = llm
Settings.embed_model = embed_model

def preprocessing(pdf_file):

    # save pdf_file to a temporary location
    file_path = "temp.pdf"
    with open(file_path, "wb") as f:
        f.write(pdf_file.getbuffer())

    # use llama parser
    documents = LlamaParse(result_type="markdown",
                        api_key=os.environ.get("LLAMA_CLOUD_API_KEY"),  # can also be set in your env as LLAMA_CLOUD_API_KEY
                        verbose=True,).load_data(file_path)
    node_parser = MarkdownElementNodeParser()
    llm=OpenAI(model="gpt-3.5-turbo-0125", api_key= os.environ.get("OPENAI_API_KEY"), num_workers=2)
    nodes = node_parser.get_nodes_from_documents(documents)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

    recursive_index = VectorStoreIndex(nodes=base_nodes + objects)
    reranker = FlagEmbeddingReranker(
    top_n=5,
    model="BAAI/bge-reranker-large",
    )

    recursive_query_engine = recursive_index.as_query_engine(
        similarity_top_k=15, node_postprocessors=[reranker], verbose=True
    )
    return recursive_query_engine

    
def generate_answer()-> None:

    recursive_query_engine = st.session_state.final_store

    user_message = st.session_state.input_text

    # generate the new query with the user message and the past conversation
    history = parse_history(st.session_state.history)
    new_query = f"Context: {history} User: {user_message}\n"

    # generate the response from the model
    response = recursive_query_engine.query(new_query)
    
    st.session_state.history.append({"message": user_message, "is_user": True})
    st.session_state.history.append({"message": response['answer'], "is_user": False})

def parse_history(history):
    query = ""
    for chat in history:
        if chat["is_user"]:
            user_message = chat["message"]
        else:
            bot_message = chat["message"]
        # combine user and bot messages as a template for the query
        query += f"User: {user_message}\nBot: {bot_message}\n"
    return query

                                  


