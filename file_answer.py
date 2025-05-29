import pickle
import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_answer(thy_question):
    """通过RAG获得答案"""
    load_dotenv()
    model = ChatOpenAI(
        model='gpt-3.5-turbo',
        base_url='https://twapi.openai-hk.com/v1',
        temperature=0
    )
    if st.session_state['is_new_file']:
        loader = TextLoader(f'{st.session_state["session_id"]}.txt', encoding='utf-8')
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=["\n", "。", "！", "？", "，", "、", ""]
        )
        texts = text_splitter.split_documents(docs)
        db = FAISS.from_documents(texts, st.session_state['em_model'])
        st.session_state['db'] = db
        st.session_state['is_new_file'] = False
    if 'db' in st.session_state:
        retriever = st.session_state['db'].as_retriever()
        chain = ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=retriever,
            memory=st.session_state['memory']
        )
        resp = chain.invoke({'chat_history': st.session_state['memory'], 'question': thy_question})
        return resp
    return ''


