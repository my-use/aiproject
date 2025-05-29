import pickle
import uuid
from addition import addition_function
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from auth import register, login, logout
from common import get_llm_response
from life_functions import life_functions
from data_analysis import data_analysis
from shuju import create_chart

import os
from concurrent.futures import ThreadPoolExecutor
# from file_answer import get_answer
# 导入LangChain相关依赖
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from utils import dataframe_agent
from file_answer import get_answer

# 配置文件路径
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# 初始化会话状态
def init_session_state():
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'general_memory' not in st.session_state:
        st.session_state.general_memory = ConversationBufferMemory(return_messages=True)
    if 'doc_memory' not in st.session_state:
        st.session_state.doc_memory = ConversationBufferMemory(return_messages=True)

# 文件解析相关配置
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
EMBEDDINGS = OpenAIEmbeddings() if os.getenv("OPENAI_API_KEY") else None
VECTOR_STORE = None
FILE_HANDLED = False
executor = ThreadPoolExecutor(max_workers=4)




# 问答界面
def ask_question():
    mode = st.radio("选择问答模式", ["直接提问 💬", "文件提问 📁","数据处理 📁"])
    if mode == "文件提问 📁":
        st.subheader("📁 文件上传")
        if 'session_id' not in st.session_state:
            st.session_state['memory'] = ConversationBufferMemory(
                return_messages=True,
                memory_key='chat_history',
                output_key='answer'
            )
            st.session_state['session_id'] = uuid.uuid4().hex
            st.session_state['is_new_file'] = False
            with open('em.pkl', 'rb') as file_obj:
                em_model = pickle.load(file_obj)
                st.session_state['em_model'] = em_model

        uploaded_file = st.file_uploader('上传你的文本文件：', type="txt")
        question = st.text_input('请输入你的问题', disabled=not uploaded_file)

        if uploaded_file:
            st.session_state['is_new_file'] = True
            with open(f'{st.session_state["session_id"]}.txt', 'w', encoding='utf-8') as temp_file:
                temp_file.write(uploaded_file.read().decode('utf-8'))

        if uploaded_file and question:
            response = get_answer(question)
            st.write('### 答案')
            st.write(response['answer'])
            st.session_state['chat_history'] = response['chat_history']

        if 'chat_history' in st.session_state:
            with st.expander("历史消息"):
                for i in range(0, len(st.session_state["chat_history"]), 2):
                    human_message = st.session_state["chat_history"][i]
                    ai_message = st.session_state["chat_history"][i + 1]
                    st.write(human_message.content)
                    st.write(ai_message.content)
                    if i < len(st.session_state["chat_history"]) - 2:
                        st.divider()
    if mode == "数据处理 📁":
        option = st.radio("请选择数据文件类型:", ("Excel", "CSV"))
        file_type = "xlsx" if option == "Excel" else "csv"
        data = st.file_uploader(f"上传你的{option}数据文件", type=file_type)
        if data:
            if file_type == "xlsx":
                st.session_state["df"] = pd.read_excel(data, sheet_name='data')
            else:
                st.session_state["df"] = pd.read_csv(data)
            with st.expander("原始数据"):
                st.dataframe(st.session_state["df"])

        query = st.text_area(
            "请输入你关于以上数据集的问题或数据可视化需求：",
            disabled="df" not in st.session_state
        )
        button = st.button("生成回答")

        if button and "df" not in st.session_state:
            st.info("请先上传数据文件")
            st.stop()
        if query:
            with st.spinner("AI正在思考中，请稍等..."):
                result = dataframe_agent(st.session_state["df"], query)
                if "answer" in result:
                    st.write(result["answer"])
                if "table" in result:
                    st.table(pd.DataFrame(result["table"]["data"],
                                          columns=result["table"]["columns"]))
                if "bar" in result:
                    create_chart(result["bar"], "bar")
                if "line" in result:
                    create_chart(result["line"], "line")
    if mode == "直接提问 💬":
        def get_ai_response(user_prompt):
            model = ChatOpenAI(
                model='gpt-4o-mini',
                base_url='https://twapi.openai-hk.com/v1'
            )
            chain = ConversationChain(llm=model, memory=st.session_state['memory'])
            return chain.invoke({'input': user_prompt})['response']

        if 'messages' not in st.session_state:
            st.session_state['messages'] = [{'role': 'ai', 'content': '你好主人，我是你的智能问答助手，很高兴为你服务'}]
            st.session_state['memory'] = ConversationBufferMemory(return_message=True)

        for message in st.session_state['messages']:
            role, content = message['role'], message['content']
            st.chat_message(role).write(content)

        user_input = st.chat_input()
        if user_input:
            st.chat_message('human').write(user_input)
            st.session_state['messages'].append({'role': 'human', 'content': user_input})
            with st.spinner('AI正在思考，请等待……'):
                resp_from_ai = get_ai_response(user_input)
                st.session_state['history'] = resp_from_ai
                st.chat_message('ai').write(resp_from_ai)
                st.session_state['messages'].append({'role': 'ai', 'content': resp_from_ai})

# 主函数
def main():
    init_session_state()
    # 居中主标题（H1）
    st.markdown("<h1 style='text-align: center;'>智能体生活管家 ✨</h1>", unsafe_allow_html=True)

    # 侧边栏
    if st.session_state.get('logged_in_user'):
        st.sidebar.write(f"👋 欢迎, {st.session_state.logged_in_user}")
        if st.sidebar.button("登出 🔒", key="logout_button"):
            logout()

    # 登录/注册界面
    if st.session_state.get('logged_in_user') is None:
        # 使用span标签自定义样式显示提示文本
        st.markdown("<span style='text-align: left; font-size: 1em; font-weight: normal;'>欢迎使用智能体生活管家！请先注册或登录。</span>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["登录 🔑","注册 📝"])
        with tab1:
            login()
        with tab2:
            register()
    else:
        main_function = st.sidebar.selectbox(
            "选择功能",
            ["智能问答助手 💡", "生活数据管理 🏠", "数据分析 📊","其他功能 ⭐"]
        )
        if main_function == "智能问答助手 💡":
            ask_question()
        elif main_function == "生活数据管理 🏠":
            life_functions()
        elif main_function == "数据分析 📊":
            data_analysis()
        elif main_function == "其他功能 ⭐":
            addition_function()

if __name__ == "__main__":
    main()