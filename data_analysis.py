import streamlit as st
import pandas as pd
import plotly.express as px
from life_functions import get_db_connection, check_login, import_data, export_data

def financial_analysis():
    st.subheader("财务数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT date, category, amount FROM finances WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 数据概览
            st.write("### 财务数据概览")
            st.dataframe(df)

            # 月度支出趋势
            st.write("### 月度支出趋势")
            monthly_data = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
            monthly_data['date'] = monthly_data['date'].astype(str)
            fig = px.line(monthly_data, x='date', y='amount', title="每月支出趋势")
            st.plotly_chart(fig)

            # 支出类别分析
            st.write("### 支出类别分析")
            category_data = df.groupby('category')['amount'].sum().reset_index()
            fig = px.pie(category_data, values='amount', names='category', title="支出类别分布")
            st.plotly_chart(fig)

            # 支出统计信息
            st.write("### 支出统计信息")
            stats = df['amount'].describe().round(2)
            st.dataframe(stats)

            # 增加可视化图形
            st.write("### 支出类别分布（柱状图）")
            fig_bar = px.bar(category_data, x='category', y='amount', title="支出类别分布")
            st.plotly_chart(fig_bar)

            st.write("### 每日支出趋势（折线图）")
            daily_expense = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
            fig_line = px.line(daily_expense, x='date', y='amount', title="每日支出趋势")
            st.plotly_chart(fig_line)

            st.write("### 支出金额箱线图")
            fig_box = px.box(df, y='amount', title="支出金额箱线图")
            st.plotly_chart(fig_box)

            st.write("### 支出金额散点图（按日期）")
            fig_scatter = px.scatter(df, x='date', y='amount', title="支出金额散点图（按日期）")
            st.plotly_chart(fig_scatter)

            st.write("### 支出类别累计分布（面积图）")
            fig_area = px.area(df, x='date', y='amount', color='category', title="支出类别累计分布")
            st.plotly_chart(fig_area)

            # 导出数据
            if st.button("导出财务数据"):
                download_link = export_data("finances", "financial_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何财务数据。请先录入数据。")

    except Exception as e:
        st.error(f"财务数据分析失败：{e}")

def plan_analysis():
    st.subheader("计划数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT date, plan, status FROM plans WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 数据概览
            st.write("### 计划数据概览")
            st.dataframe(df)

            # 计划完成情况
            st.write("### 计划完成情况")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['状态', '数量']
            fig = px.bar(status_counts, x='状态', y='数量', title="计划完成情况统计")
            st.plotly_chart(fig)

            # 按日期分组的计划数量
            st.write("### 每日计划数量")
            daily_plans = df.groupby(df['date'].dt.date)['plan'].count().reset_index()
            daily_plans.columns = ['日期', '计划数量']
            fig = px.line(daily_plans, x='日期', y='计划数量', title="每日计划数量趋势")
            st.plotly_chart(fig)

            # 增加可视化图形
            st.write("### 计划状态分布（饼图）")
            fig_pie = px.pie(status_counts, values='数量', names='状态', title="计划状态分布")
            st.plotly_chart(fig_pie)

            st.write("### 每日计划数量箱线图")
            fig_box = px.box(daily_plans, y='计划数量', title="每日计划数量箱线图")
            st.plotly_chart(fig_box)

            st.write("### 计划数量散点图（按日期）")
            fig_scatter = px.scatter(daily_plans, x='日期', y='计划数量', title="计划数量散点图（按日期）")
            st.plotly_chart(fig_scatter)

            # st.write("### 计划状态累计分布（面积图）")
            # fig_area = px.area(df, x='date', y=1, color='status', title="计划状态累计分布")
            # st.plotly_chart(fig_area)

            # 导出数据
            if st.button("导出计划数据"):
                download_link = export_data("plans", "plan_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何计划。请先录入计划。")

    except Exception as e:
        st.error(f"计划数据分析失败：{e}")

def birthday_analysis():
    st.subheader("生日数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name, date FROM birthdays WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 提取月份信息用于分析
            df['month'] = df['date'].dt.month

            # 数据概览
            st.write("### 生日数据概览")
            st.dataframe(df[['name', 'date']])

            # 月份分布
            st.write("### 生日月份分布")
            month_counts = df['month'].value_counts().sort_index().reset_index()
            month_counts.columns = ['月份', '人数']
            fig = px.bar(month_counts, x='月份', y='人数', title="生日月份分布")
            st.plotly_chart(fig)

            # 即将到来的生日
            today = pd.Timestamp.today()
            df['this_year_birthday'] = df['date'].apply(lambda x: pd.Timestamp(today.year, x.month, x.day))
            df['days_until'] = (df['this_year_birthday'] - today).dt.days
            df.loc[df['days_until'] < 0, 'days_until'] += 365  # 处理已经过去的生日
            upcoming_birthdays = df.sort_values('days_until').head(3)

            st.write("### 即将到来的生日")
            for _, row in upcoming_birthdays.iterrows():
                st.write(f"- {row['name']}: 还有 {int(row['days_until'])} 天 ({row['date'].strftime('%m-%d')})")

            # 增加可视化图形
            st.write("### 生日月份分布（饼图）")
            fig_pie = px.pie(month_counts, values='人数', names='月份', title="生日月份分布")
            st.plotly_chart(fig_pie)

            st.write("### 生日月份分布（箱线图）")
            fig_box = px.box(month_counts, y='人数', title="生日月份分布箱线图")
            st.plotly_chart(fig_box)

            st.write("### 生日月份分布（散点图）")
            fig_scatter = px.scatter(month_counts, x='月份', y='人数', title="生日月份分布散点图")
            st.plotly_chart(fig_scatter)

            st.write("### 生日月份累计分布（面积图）")
            fig_area = px.area(month_counts, x='月份', y='人数', title="生日月份累计分布")
            st.plotly_chart(fig_area)

            # 导出数据
            if st.button("导出生日数据"):
                download_link = export_data("birthdays", "birthday_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何家人生日。请先录入数据。")

    except Exception as e:
        st.error(f"生日数据分析失败：{e}")

def health_analysis():
    st.subheader("健康数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT date, steps, sleep_hours, diet FROM health WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 数据概览
            st.write("### 健康数据概览")
            st.dataframe(df)

            # 运动步数趋势
            st.write("### 运动步数趋势")
            fig = px.line(df, x='date', y='steps', title="每日运动步数")
            st.plotly_chart(fig)

            # 睡眠时间趋势
            st.write("### 睡眠时间趋势")
            fig = px.line(df, x='date', y='sleep_hours', title="每日睡眠时间")
            st.plotly_chart(fig)

            # 步数与睡眠时间关系
            st.write("### 步数与睡眠时间关系")
            fig = px.scatter(df, x='steps', y='sleep_hours',
                             hover_data=['date', 'diet'],
                             title="步数与睡眠时间关系")
            st.plotly_chart(fig)

            # 健康统计数据
            st.write("### 健康统计数据")
            stats = {
                "平均每日步数": df['steps'].mean(),
                "平均睡眠时间": df['sleep_hours'].mean(),
                "最高步数": df['steps'].max(),
                "最长睡眠时间": df['sleep_hours'].max()
            }
            st.dataframe(pd.DataFrame(list(stats.items()), columns=['指标', '值']))

            # 增加可视化图形
            st.write("### 运动步数箱线图")
            fig_box_steps = px.box(df, y='steps', title="运动步数箱线图")
            st.plotly_chart(fig_box_steps)

            st.write("### 睡眠时间箱线图")
            fig_box_sleep = px.box(df, y='sleep_hours', title="睡眠时间箱线图")
            st.plotly_chart(fig_box_sleep)

            st.write("### 运动步数分布直方图")
            fig_hist_steps = px.histogram(df, x='steps', nbins=20, title="运动步数分布直方图")
            st.plotly_chart(fig_hist_steps)

            st.write("### 睡眠时间分布直方图")
            fig_hist_sleep = px.histogram(df, x='sleep_hours', nbins=20, title="睡眠时间分布直方图")
            st.plotly_chart(fig_hist_sleep)

            st.write("### 步数与睡眠时间关系（三维散点图）")
            fig_scatter_3d = px.scatter_3d(df, x='date', y='steps', z='sleep_hours',
                                           hover_data=['diet'], title="步数与睡眠时间关系（三维散点图）")
            st.plotly_chart(fig_scatter_3d)

            # 导出数据
            if st.button("导出健康数据"):
                download_link = export_data("health", "health_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何健康数据。请先录入数据。")

    except Exception as e:
        st.error(f"健康数据分析失败：{e}")

def shopping_analysis():
    st.subheader("购物数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT date, item, amount, status FROM shopping WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 数据概览
            st.write("### 购物数据概览")
            st.dataframe(df)

            # 购物状态分布
            st.write("### 购物状态分布")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['状态', '数量']
            fig = px.pie(status_counts, values='数量', names='状态', title="购物状态分布")
            st.plotly_chart(fig)

            # 购物金额趋势
            st.write("### 购物金额趋势")
            daily_amount = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
            daily_amount.columns = ['日期', '金额']
            fig = px.line(daily_amount, x='日期', y='金额', title="每日购物金额")
            st.plotly_chart(fig)

            # 已完成和未完成的购物金额对比
            st.write("### 已完成和未完成的购物金额对比")
            status_amount = df.groupby('status')['amount'].sum().reset_index()
            fig = px.bar(status_amount, x='status', y='amount', title="购物金额对比")
            st.plotly_chart(fig)

            # 增加可视化图形
            st.write("### 购物状态分布（柱状图）")
            fig_bar = px.bar(status_counts, x='状态', y='数量', title="购物状态分布")
            st.plotly_chart(fig_bar)

            st.write("### 购物金额箱线图")
            fig_box = px.box(df, y='amount', title="购物金额箱线图")
            st.plotly_chart(fig_box)

            st.write("### 购物金额散点图（按日期）")
            fig_scatter = px.scatter(df, x='date', y='amount', title="购物金额散点图（按日期）")
            st.plotly_chart(fig_scatter)

            st.write("### 购物金额累计分布（面积图）")
            fig_area = px.area(df, x='date', y='amount', color='status', title="购物金额累计分布")
            st.plotly_chart(fig_area)

            # 导出数据
            if st.button("导出购物数据"):
                download_link = export_data("shopping", "shopping_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何购物数据。请先录入数据。")

    except Exception as e:
        st.error(f"购物数据分析失败：{e}")

def reading_analysis():
    st.subheader("阅读数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT date, book, pages FROM reading WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 数据概览
            st.write("### 阅读数据概览")
            st.dataframe(df)

            # 阅读页数趋势
            st.write("### 阅读页数趋势")
            daily_pages = df.groupby(df['date'].dt.date)['pages'].sum().reset_index()
            daily_pages.columns = ['日期', '页数']
            fig = px.line(daily_pages, x='日期', y='页数', title="每日阅读页数")
            st.plotly_chart(fig)

            # 阅读量最大的书籍
            st.write("### 阅读量最大的书籍")
            book_pages = df.groupby('book')['pages'].sum().reset_index().sort_values('pages', ascending=False)
            fig = px.bar(book_pages, x='book', y='pages', title="每本书的总阅读页数")
            st.plotly_chart(fig)

            # 月度阅读统计
            st.write("### 月度阅读统计")
            monthly_data = df.groupby(df['date'].dt.to_period('M'))['pages'].sum().reset_index()
            monthly_data.columns = ['月份', '页数']
            monthly_data['月份'] = monthly_data['月份'].astype(str)
            fig = px.bar(monthly_data, x='月份', y='页数', title="每月阅读页数")
            st.plotly_chart(fig)

            # 增加可视化图形
            st.write("### 阅读页数箱线图")
            fig_box = px.box(df, y='pages', title="阅读页数箱线图")
            st.plotly_chart(fig_box)

            st.write("### 阅读页数分布直方图")
            fig_hist = px.histogram(df, x='pages', nbins=20, title="阅读页数分布直方图")
            st.plotly_chart(fig_hist)

            st.write("### 阅读页数散点图（按日期）")
            fig_scatter = px.scatter(df, x='date', y='pages', title="阅读页数散点图（按日期）")
            st.plotly_chart(fig_scatter)

            st.write("### 阅读页数累计分布（面积图）")
            fig_area = px.area(df, x='date', y='pages', title="阅读页数累计分布")
            st.plotly_chart(fig_area)

            # 导出数据
            if st.button("导出阅读数据"):
                download_link = export_data("reading", "reading_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何阅读数据。请先录入数据。")

    except Exception as e:
        st.error(f"阅读数据分析失败：{e}")

def movie_analysis():
    st.subheader("电影观看数据分析")

    if not check_login():
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT date, movie, rating FROM movies WHERE username = ?",
                  (st.session_state.logged_in_user,))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame([dict(row) for row in data])
            df['date'] = pd.to_datetime(df['date'])

            # 数据概览
            st.write("### 电影观看数据概览")
            st.dataframe(df)

            # 评分分布
            st.write("### 电影评分分布")
            fig = px.histogram(df, x='rating', nbins=10, title="电影评分分布")
            st.plotly_chart(fig)

            # 观看趋势
            st.write("### 电影观看趋势")
            monthly_count = df.groupby(df['date'].dt.to_period('M'))['movie'].count().reset_index()
            monthly_count.columns = ['月份', '数量']
            monthly_count['月份'] = monthly_count['月份'].astype(str)
            fig = px.line(monthly_count, x='月份', y='数量', title="每月观看电影数量")
            st.plotly_chart(fig)

            # 高分电影
            st.write("### 高分电影推荐")
            top_movies = df.sort_values('rating', ascending=False).head(3)
            for _, row in top_movies.iterrows():
                st.write(f"- **{row['movie']}** (评分: {row['rating']}) - {row['date'].strftime('%Y-%m-%d')}")

            # 增加可视化图形
            st.write("### 电影评分箱线图")
            fig_box = px.box(df, y='rating', title="电影评分箱线图")
            st.plotly_chart(fig_box)

            st.write("### 电影评分散点图（按日期）")
            fig_scatter = px.scatter(df, x='date', y='rating', title="电影评分散点图（按日期）")
            st.plotly_chart(fig_scatter)

            st.write("### 电影评分分布（小提琴图）")
            fig_violin = px.violin(df, y='rating', title="电影评分分布（小提琴图）")
            st.plotly_chart(fig_violin)

            st.write("### 电影评分累计分布（ECDF图）")
            fig_ecdf = px.ecdf(df, x='rating', title="电影评分累计分布")
            st.plotly_chart(fig_ecdf)

            # 导出数据
            if st.button("导出电影数据"):
                download_link = export_data("movies", "movie_data")
                if download_link:
                    st.markdown(download_link, unsafe_allow_html=True)

        else:
            st.warning("您还没有录入任何电影观看数据。请先录入数据。")

    except Exception as e:
        st.error(f"电影观看数据分析失败：{e}")

def data_analysis():
    st.header("数据分析界面")

    if not check_login():
        return

    # 数据分析选项
    analysis_options = [
        "财务数据分析", "计划数据分析", "家人生日分析",
        "健康数据分析", "购物数据分析", "阅读数据分析",
        "电影观看数据分析"
    ]

    selected_analysis = st.sidebar.selectbox("选择分析类型", analysis_options)

    # 根据选择显示相应分析
    if selected_analysis == "财务数据分析":
        financial_analysis()
    elif selected_analysis == "计划数据分析":
        plan_analysis()
    elif selected_analysis == "家人生日分析":
        birthday_analysis()
    elif selected_analysis == "健康数据分析":
        health_analysis()
    elif selected_analysis == "购物数据分析":
        shopping_analysis()
    elif selected_analysis == "阅读数据分析":
        reading_analysis()
    elif selected_analysis == "电影观看数据分析":
        movie_analysis()