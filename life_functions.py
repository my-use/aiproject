import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import plotly.express as px
from openai import OpenAI
import os
import time  # 新增：用于重试机制的延迟
from utils import get_db_connection
import base64  # 用于文件下载


# 初始化数据库表
def init_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # 创建相关表 - 添加自增ID
        c.execute('''CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            date TEXT, 
            plan TEXT, 
            status TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            date TEXT, 
            category TEXT, 
            amount REAL
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            name TEXT, 
            date TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            date TEXT, 
            steps INTEGER, 
            sleep_hours REAL, 
            diet TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS shopping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            date TEXT, 
            item TEXT, 
            amount REAL, 
            status TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS reading (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            date TEXT, 
            book TEXT, 
            pages INTEGER
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, 
            date TEXT, 
            movie TEXT, 
            rating REAL
        )''')

        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"数据库初始化失败: {e}")


# 初始化数据库
init_db()


# 辅助函数：验证用户是否登录
def check_login():
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

    if not st.session_state.logged_in_user:
        st.error("请先登录才能使用此功能")
        return False
    return True


# 辅助函数：将日期转换为字符串
def date_to_str(date):
    return date.strftime('%Y-%m-%d')


# 辅助函数：从字符串转换为日期
def str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


# 辅助函数：获取数据列表
def get_data_list(table_name, columns=None):
    if not check_login():
        return []

    conn = get_db_connection()
    try:
        c = conn.cursor()
        if columns:
            query = f"SELECT {', '.join(columns)} FROM {table_name} WHERE username = ?"
        else:
            query = f"SELECT * FROM {table_name} WHERE username = ?"
        c.execute(query, (st.session_state.logged_in_user,))
        return c.fetchall()
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return []
    finally:
        conn.close()


# 辅助函数：删除数据项
def delete_data_item(table_name, item_id):
    if not check_login():
        return False

    conn = get_db_connection()
    try:
        c = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = ? AND username = ?"
        c.execute(query, (item_id, st.session_state.logged_in_user))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"删除数据失败: {e}")
        return False
    finally:
        conn.close()


# 辅助函数：导入数据
def import_data(table_name, file):
    if not check_login():
        return False

    try:
        # 读取上传的文件
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            st.error("请上传CSV或Excel文件")
            return False

        # 添加用户名
        df['username'] = st.session_state.logged_in_user

        # 写入数据库
        conn = get_db_connection()
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()

        st.success(f"成功导入 {len(df)} 条记录")
        return True
    except Exception as e:
        st.error(f"导入失败: {e}")
        return False


# 辅助函数：导出数据
def export_data(table_name, file_name):
    if not check_login():
        return None

    try:
        # 从数据库获取数据
        conn = get_db_connection()
        df = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE username = ?",
                               conn, params=(st.session_state.logged_in_user,))
        conn.close()

        if df.empty:
            st.warning("没有数据可导出")
            return None

        # 导出为CSV
        csv = df.to_csv(sep='\t', na_rep='nan')
        b64 = base64.b64encode(csv.encode()).decode()

        # 创建下载链接
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}.csv">下载CSV文件</a>'
        return href
    except Exception as e:
        st.error(f"导出失败: {e}")
        return None


# 计划管理
def manage_plans():
    st.subheader("计划管理")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入计划数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("plans", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("plans", "plans_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 获取计划数据
    plans = get_data_list("plans")
    if not plans:
        st.info("暂无计划数据")
    else:
        df = pd.DataFrame([dict(p) for p in plans])

        # 获取所有状态
        statuses = ['全部'] + list(df['status'].unique())

        # 使用下拉菜单选择状态
        selected_status = st.selectbox("选择计划状态", statuses)

        # 根据选择的状态过滤数据
        if selected_status != '全部':
            filtered_plans = df[df['status'] == selected_status]
        else:
            filtered_plans = df

        # 显示过滤后的计划
        if not filtered_plans.empty:
            st.write(f"### {selected_status} 计划")
            for _, plan in filtered_plans.iterrows():
                plan_id = plan["id"]
                plan_date = str_to_date(plan["date"])
                plan_content = plan["plan"]

                with st.expander(f"{plan_date} - {plan_content[:20]}{'...' if len(plan_content) > 20 else ''}"):
                    st.write(f"**日期:** {plan_date}")
                    st.write(f"**内容:** {plan_content}")
                    st.write(f"**状态:** {plan['status']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if plan['status'] != "已完成":
                            if st.button("标记为完成", key=f"complete_{plan_id}"):
                                conn = get_db_connection()
                                try:
                                    c = conn.cursor()
                                    c.execute("UPDATE plans SET status = ? WHERE username = ? AND id = ?",
                                              ("已完成", st.session_state.logged_in_user, plan_id))
                                    conn.commit()
                                    st.success("计划状态已更新！")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"更新失败: {e}")
                                finally:
                                    conn.close()
                    with col2:
                        if st.button("删除", key=f"delete_{plan_id}"):
                            if delete_data_item("plans", plan_id):
                                st.success("计划已删除！")
                                st.rerun()
        else:
            st.info(f"没有找到 {selected_status} 状态的计划")

    # 添加新计划
    st.write("### 添加新计划")
    date = st.date_input("日期", datetime.now().date(), key="new_plan_date")
    plan = st.text_area("计划内容", key="new_plan_content")
    status = st.selectbox("状态", ["未完成", "已完成", "进行中"], key="new_plan_status")

    if st.button("添加计划", key="add_new_plan"):
        if not plan.strip():
            st.warning("计划内容不能为空")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO plans (username, date, plan, status) VALUES (?, ?, ?, ?)",
                (st.session_state.logged_in_user, date_to_str(date), plan, status)
            )
            conn.commit()
            st.success("计划已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()


# 财务数据分析
def analyze_finances():
    st.subheader("财务数据分析")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入财务数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("finances", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("finances", "finances_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 获取财务数据
    finances = get_data_list("finances")
    if not finances:
        st.info("暂无财务数据")
        return

    # 转换为DataFrame进行分析
    df = pd.DataFrame([dict(f) for f in finances])
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    # 总支出
    total_expense = df['amount'].sum()
    st.metric("总支出", f"¥{total_expense:.2f}")

    # 支出分类统计
    st.write("### 支出分类统计")
    category_stats = df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
    category_stats.columns = ['类别', '总金额', '交易次数', '平均金额']
    category_stats['总金额'] = category_stats['总金额'].apply(lambda x: f"¥{x:.2f}")
    category_stats['平均金额'] = category_stats['平均金额'].apply(lambda x: f"¥{x:.2f}")
    st.dataframe(category_stats)

    # 最高和最低支出
    st.write("### 最高和最低支出")
    highest_expense = df.loc[df['amount'].idxmax()]
    lowest_expense = df.loc[df['amount'].idxmin()]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**最高支出**")
        st.markdown(f"- 金额: ¥{highest_expense['amount']:.2f}")
        st.markdown(f"- 类别: {highest_expense['category']}")
        st.markdown(f"- 日期: {highest_expense['date'].strftime('%Y-%m-%d')}")

    with col2:
        st.markdown(f"**最低支出**")
        st.markdown(f"- 金额: ¥{lowest_expense['amount']:.2f}")
        st.markdown(f"- 类别: {lowest_expense['category']}")
        st.markdown(f"- 日期: {lowest_expense['date'].strftime('%Y-%m-%d')}")

    # 近期支出列表
    st.write("### 近期支出列表")
    recent_expenses = df.sort_values('date', ascending=False).head(10)
    recent_expenses['date'] = recent_expenses['date'].dt.strftime('%Y-%m-%d')
    st.dataframe(recent_expenses[['date', 'category', 'amount']])

    # 按日期统计
    st.write("### 按日期统计")
    daily_stats = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_stats.columns = ['日期', '总金额']
    daily_stats['总金额'] = daily_stats['总金额'].apply(lambda x: f"¥{x:.2f}")
    st.dataframe(daily_stats)

    # 按月份统计
    st.write("### 按月份统计")
    monthly_stats = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly_stats.columns = ['月份', '总金额']
    monthly_stats['月份'] = monthly_stats['月份'].astype(str)
    monthly_stats['总金额'] = monthly_stats['总金额'].apply(lambda x: f"¥{x:.2f}")
    st.dataframe(monthly_stats)

    # 添加新财务记录
    st.write("### 添加新财务记录")
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("日期", datetime.now().date())
        category = st.text_input("类别")
    with col2:
        amount = st.number_input("金额", min_value=0.01)

    if st.button("添加记录"):
        if not category.strip():
            st.warning("类别不能为空")
            return

        if amount <= 0:
            st.warning("金额必须大于0")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO finances (username, date, category, amount) VALUES (?, ?, ?, ?)",
                (st.session_state.logged_in_user, date_to_str(date), category, amount)
            )
            conn.commit()
            st.success("记录已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()

# 家人生日管理
def manage_birthdays():
    st.subheader("家人生日管理")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入生日数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("birthdays", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("birthdays", "birthdays_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 显示生日列表
    birthdays = get_data_list("birthdays")
    if birthdays:
        st.write("### 现有生日记录")
        for birthday in birthdays:
            birthday_id = birthday["id"]
            name = birthday["name"]
            date = str_to_date(birthday["date"])

            with st.expander(f"{name} - {date.strftime('%m-%d')}"):
                st.write(f"**姓名:** {name}")
                st.write(f"**生日:** {date.strftime('%Y-%m-%d')}")

                if st.button("删除", key=f"delete_birthday_{birthday_id}"):
                    if delete_data_item("birthdays", birthday_id):
                        st.success("生日记录已删除！")
                        st.rerun()

    # 添加新生日记录
    st.write("### 添加新生日记录")
    name = st.text_input("姓名", key="new_birthday_name")
    date = st.date_input("生日", datetime.now().date(), key="new_birthday_date")

    if st.button("添加记录", key="add_new_birthday"):
        if not name.strip():
            st.warning("姓名不能为空")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO birthdays (username, name, date) VALUES (?, ?, ?)",
                (st.session_state.logged_in_user, name, date_to_str(date))
            )
            conn.commit()
            st.success("生日记录已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()


# 健康数据管理
def manage_health():
    st.subheader("健康数据管理")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入健康数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("health", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("health", "health_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 显示健康数据列表
    health_data = get_data_list("health")
    if health_data:
        st.write("### 现有健康数据")
        for data in health_data:
            data_id = data["id"]
            date = str_to_date(data["date"])
            steps = data["steps"]
            sleep_hours = data["sleep_hours"]
            diet = data["diet"]

            with st.expander(f"{date}"):
                st.write(f"**日期:** {date}")
                st.write(f"**步数:** {steps}")
                st.write(f"**睡眠时间:** {sleep_hours}小时")
                st.write(f"**饮食情况:** {diet}")

                if st.button("删除", key=f"delete_health_{data_id}"):
                    if delete_data_item("health", data_id):
                        st.success("健康数据已删除！")
                        st.rerun()

    # 添加新健康数据
    st.write("### 添加新健康数据")
    date = st.date_input("日期", datetime.now().date(), key="new_health_date")
    steps = st.number_input("步数", min_value=0, key="new_health_steps")
    sleep_hours = st.number_input("睡眠时间", min_value=0.0, key="new_health_sleep")
    diet = st.text_area("饮食情况", key="new_health_diet")

    if st.button("添加记录", key="add_new_health"):
        if not diet.strip():
            st.warning("饮食情况不能为空")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO health (username, date, steps, sleep_hours, diet) VALUES (?, ?, ?, ?, ?)",
                (st.session_state.logged_in_user, date_to_str(date), steps, sleep_hours, diet)
            )
            conn.commit()
            st.success("健康数据已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()


# 购物清单管理
def manage_shopping():
    st.subheader("购物清单管理")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入购物数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("shopping", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("shopping", "shopping_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 获取购物数据
    shopping_list = get_data_list("shopping")
    if not shopping_list:
        st.info("暂无购物数据")
    else:
        df = pd.DataFrame([dict(s) for s in shopping_list])

        # 获取所有状态
        statuses = ['全部'] + list(df['status'].unique())

        # 使用下拉菜单选择状态
        selected_status = st.selectbox("选择购物状态", statuses)

        # 根据选择的状态过滤数据
        if selected_status != '全部':
            filtered_items = df[df['status'] == selected_status]
        else:
            filtered_items = df

        # 显示过滤后的购物清单
        if not filtered_items.empty:
            st.write(f"### {selected_status} 购物清单")
            for _, item in filtered_items.iterrows():
                item_id = item["id"]
                date = str_to_date(item["date"])
                name = item["item"]
                amount = item["amount"]

                with st.expander(f"{date} - {name}"):
                    st.write(f"**日期:** {date}")
                    st.write(f"**物品:** {name}")
                    st.write(f"**金额:** {amount}")
                    st.write(f"**状态:** {item['status']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if item['status'] != "已完成":
                            if st.button("标记为完成", key=f"complete_shopping_{item_id}"):
                                conn = get_db_connection()
                                try:
                                    c = conn.cursor()
                                    c.execute("UPDATE shopping SET status = ? WHERE username = ? AND id = ?",
                                              ("已完成", st.session_state.logged_in_user, item_id))
                                    conn.commit()
                                    st.success("购物清单状态已更新！")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"更新失败: {e}")
                                finally:
                                    conn.close()
                    with col2:
                        if st.button("删除", key=f"delete_shopping_{item_id}"):
                            if delete_data_item("shopping", item_id):
                                st.success("购物清单已删除！")
                                st.rerun()
        else:
            st.info(f"没有找到 {selected_status} 状态的购物清单")

    # 添加新购物清单
    st.write("### 添加新购物清单")
    date = st.date_input("日期", datetime.now().date(), key="new_shopping_date")
    item = st.text_input("物品", key="new_shopping_item")
    amount = st.number_input("金额", min_value=0.01, key="new_shopping_amount")
    status = st.selectbox("状态", ["未完成", "已完成"], key="new_shopping_status")

    if st.button("添加记录", key="add_new_shopping"):
        if not item.strip():
            st.warning("物品名称不能为空")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO shopping (username, date, item, amount, status) VALUES (?, ?, ?, ?, ?)",
                (st.session_state.logged_in_user, date_to_str(date), item, amount, status)
            )
            conn.commit()
            st.success("购物清单已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()


# 阅读记录管理
def manage_reading():
    st.subheader("阅读记录管理")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入阅读数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("reading", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("reading", "reading_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 显示阅读记录
    reading_records = get_data_list("reading")
    if reading_records:
        st.write("### 现有阅读记录")
        for record in reading_records:
            record_id = record["id"]
            date = str_to_date(record["date"])
            book = record["book"]
            pages = record["pages"]

            with st.expander(f"{date} - {book}"):
                st.write(f"**日期:** {date}")
                st.write(f"**书籍:** {book}")
                st.write(f"**页数:** {pages}")

                if st.button("删除", key=f"delete_reading_{record_id}"):
                    if delete_data_item("reading", record_id):
                        st.success("阅读记录已删除！")
                        st.rerun()

    # 添加新阅读记录
    st.write("### 添加新阅读记录")
    date = st.date_input("日期", datetime.now().date(), key="new_reading_date")
    book = st.text_input("书籍", key="new_reading_book")
    pages = st.number_input("页数", min_value=0, key="new_reading_pages")

    if st.button("添加记录", key="add_new_reading"):
        if not book.strip():
            st.warning("书籍名称不能为空")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO reading (username, date, book, pages) VALUES (?, ?, ?, ?)",
                (st.session_state.logged_in_user, date_to_str(date), book, pages)
            )
            conn.commit()
            st.success("阅读记录已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()


# 电影观看记录管理
def manage_movies():
    st.subheader("电影观看记录管理")

    # 文件导入导出
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("导入电影数据", type=['csv', 'xlsx'])
        if uploaded_file:
            if import_data("movies", uploaded_file):
                st.rerun()

    with col2:
        download_link = export_data("movies", "movies_data")
        if download_link:
            st.markdown(download_link, unsafe_allow_html=True)

    # 显示电影观看记录
    movie_records = get_data_list("movies")
    if movie_records:
        st.write("### 现有电影观看记录")
        for record in movie_records:
            record_id = record["id"]
            date = str_to_date(record["date"])
            movie = record["movie"]
            rating = record["rating"]

            with st.expander(f"{date} - {movie}"):
                st.write(f"**日期:** {date}")
                st.write(f"**电影:** {movie}")
                st.write(f"**评分:** {rating}")

                if st.button("删除", key=f"delete_movie_{record_id}"):
                    if delete_data_item("movies", record_id):
                        st.success("电影观看记录已删除！")
                        st.rerun()

    # 添加新电影观看记录
    st.write("### 添加新电影观看记录")
    date = st.date_input("日期", datetime.now().date(), key="new_movie_date")
    movie = st.text_input("电影", key="new_movie_name")
    rating = st.number_input("评分", min_value=0.0, max_value=10.0, step=0.1, key="new_movie_rating")

    if st.button("添加记录", key="add_new_movie"):
        if not movie.strip():
            st.warning("电影名称不能为空")
            return

        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO movies (username, date, movie, rating) VALUES (?, ?, ?, ?)",
                (st.session_state.logged_in_user, date_to_str(date), movie, rating)
            )
            conn.commit()
            st.success("电影观看记录已添加！")
            st.rerun()
        except Exception as e:
            st.error(f"添加失败：{e}")
        finally:
            conn.close()


def life_functions():
    st.header("生活数据管理")

    if not check_login():
        return

    # 主要功能选项
    function_options = [
        "计划管理", "财务数据分析", "家人生日管理",
        "健康数据管理", "购物清单管理", "阅读记录管理",
        "电影观看记录管理"
    ]

    selected_function = st.sidebar.selectbox("选择功能", function_options)

    # 根据选择显示相应功能
    if selected_function == "计划管理":
        manage_plans()
    elif selected_function == "财务数据分析":
        analyze_finances()
    elif selected_function == "家人生日管理":
        manage_birthdays()
    elif selected_function == "健康数据管理":
        manage_health()
    elif selected_function == "购物清单管理":
        manage_shopping()
    elif selected_function == "阅读记录管理":
        manage_reading()
    elif selected_function == "电影观看记录管理":
        manage_movies()
