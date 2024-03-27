from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI, ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from langchain_community.callbacks import get_openai_callback
import os
import logging
from utils.path_finder import get_parent_child_path

# Basic logging setup
logging.basicConfig(level=logging.DEBUG)

load_dotenv()


def create_vector_store(file_name, v_store_name, embeddings):
    data_directory_path = os.path.join(get_parent_child_path("data"), file_name)
    pdf_reader = PdfReader(data_directory_path)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text=text)

    v_store_name = v_store_name
    embeddings = embeddings

    # load the FAISS index if it exists
    if os.path.exists(get_parent_child_path(v_store_name)):
        v_store = FAISS.load_local(
            v_store_name, embeddings, allow_dangerous_deserialization=True
        )
    # otherwise, pickle then save the local store for later retrieval
    else:
        v_store = FAISS.from_texts(chunks, embeddings)
        v_store.save_local(get_parent_child_path(v_store_name))

    return v_store


def query_store(v_store, query):
    llm = OpenAI()
    chain = load_qa_chain(llm=llm, chain_type="stuff")
    context = v_store.similarity_search(query, k=3)
    with get_openai_callback() as cb:
        response = chain.invoke({"input_documents": context, "question": query})
        logging.info(cb)
        return response["output_text"]
