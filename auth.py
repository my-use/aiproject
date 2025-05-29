import streamlit as st
import sqlite3
import bcrypt

def get_db_connection():
    return sqlite3.connect('user_data.db')

def init_db():
    """初始化用户表结构"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def register():
    """用户注册功能"""
    st.subheader("注册新用户")

    new_user = st.text_input("用户名", key="register_username")
    new_password = st.text_input("密码", type='password', key="register_password")
    confirm_password = st.text_input("确认密码", type='password', key="confirm_password")

    if st.button("注册", key="register_button"):
        if not new_user or not new_password:
            st.warning("用户名和密码不能为空")
            return

        if new_password != confirm_password:
            st.error("两次输入的密码不一致")
            return

        conn = get_db_connection()
        c = conn.cursor()

        # 检查用户名是否已存在
        c.execute("SELECT * FROM users WHERE username = ?", (new_user,))
        if c.fetchone():
            st.error("用户名已存在！")
            conn.close()
            return

        # 安全哈希密码
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        try:
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                      (new_user, password_hash.decode('utf-8')))
            conn.commit()
            st.success("注册成功！请登录。")
        except Exception as e:
            st.error(f"注册失败：{e}")
        finally:
            conn.close()

def login():
    """用户登录功能，增加表结构验证"""
    st.subheader("用户登录")

    user = st.text_input("用户名", key="login_username")
    password = st.text_input("密码", type='password', key="login_password")

    if st.button("登录", key="login_button"):
        if not user or not password:
            st.warning("用户名和密码不能为空")
            return

        conn = get_db_connection()
        c = conn.cursor()

        # 检查表结构是否存在 password_hash 列
        c.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in c.fetchall()]
        if 'password_hash' not in columns:
            st.error("数据库表结构错误：users 表缺少 password_hash 列")
            st.write(f"当前表结构: {columns}")
            conn.close()
            return

        # 执行登录查询
        c.execute("SELECT password_hash FROM users WHERE username = ?", (user,))
        result = c.fetchone()

        conn.close()

        if result:
            stored_hash = result[0].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                st.success("登录成功！")
                st.session_state.logged_in_user = user
                st.rerun()
            else:
                st.error("用户名或密码错误！")
        else:
            st.error("用户名或密码错误！")

def logout():
    """用户登出功能"""
    st.session_state.pop('logged_in_user', None)
    st.session_state.pop('chat_history', None)
    st.success("已成功登出")
    st.rerun()