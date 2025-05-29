import streamlit as st
import requests
import webbrowser

# 设置页面配置,包括页面标题、图标和布局
st.set_page_config(
    page_title="智能体生活管家",
    page_icon="🌟",
    layout="wide"
)

# 初始化会话状态,用于记录当前功能
if "current_function" not in st.session_state:
    st.session_state.current_function = None

# VIP视频功能
def watch_tv():
    # 设置页面标题和说明
    st.header("VIP视频解析")
    # 创建文本输入框，用于输入视频网址
    st.markdown("输入视频链接，选择解析平台观看VIP视频")
    video_url = st.text_input("请输入视频网址", placeholder="https://www.iqiyi.com/v_xxxxxx.html")
    #创建4个按钮，按钮实现4个功能，点击按钮后实现跳转
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("爱奇艺", key="iqiyi"):
            webbrowser.open(f"https://www.iqiyi.com")
    with col2:
        if st.button("腾讯视频", key="tencent"):
            webbrowser.open("https://v.qq.com")
    with col3:
        if st.button("优酷", key="youku"):
            webbrowser.open("https://www.youku.com/")
    with col4:
        if st.button("解析", key="parse"):
            webbrowser.open('https://jx.xmflv.cc/?url=' + video_url)

# BFR体脂率计算
def BFR():
    st.header("BFR体脂率计算器")
    st.markdown("输入身高、体重和年龄，计算您的体脂率")

    # 创建三个列，分别放置身高、体重和年龄的输入框
    col1, col2, col3 = st.columns(3)
    with col1:
        height = st.number_input("身高(cm)", min_value=50, max_value=250, step=1, value=170, format="%d")  # 整数类型
    with col2:
        weight = st.number_input("体重(kg)", min_value=10.0, max_value=300.0, step=0.1, value=65.0)  # 浮点类型
    with col3:
        age = st.number_input("年龄", min_value=5, max_value=120, step=1, value=30, format="%d")  # 整数类型

    if st.button("计算体脂率", key="calculate_bfr"):
        if height and weight and age:
            with st.spinner("计算中..."):
                try:
                    #发送请求
                    url = "https://apis.tianapi.com/bfrsum/index"
                    params = {
                        'key': '02a2c9f6ee2b318d97236cbcd317e6de',
                        'height': int(height),  # 显式转换为整数
                        'weight': float(weight),  # 显式转换为浮点数
                        'age': int(age)  # 显式转换为整数
                    }
                    resp = requests.get(url, params=params)
                    #判断请求状态
                    if resp.status_code == 200:
                        data = resp.json()
                        if data['code'] == 200:
                            result = data['result']
                            #显示结果
                            st.subheader("计算结果")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("体脂率", f"{result['bfr']}")
                                st.metric("正常体脂率范围", f"{result['normbfr']}")
                                st.metric("理想体重", result['idealweight'])
                            with col2:
                                st.metric("正常体重", result['normweight'])
                                st.metric("健康状态", result['healthy'])
                            st.info(f"**健康建议**: {result['tip']}")
                        else:
                            st.error(f"API错误: {data['msg']}")
                    else:
                        st.error(f"请求失败，状态码: {resp.status_code}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
        else:
            st.warning("请填写完整的身高、体重和年龄信息")

# 健康知识问答
def jiankangzhishi():
    st.header("健康知识问答")
    st.markdown("输入您关心的健康问题，获取专业解答")

    question = st.text_input("请输入您的问题", placeholder="例如：高血压的饮食注意事项")

    if st.button("获取答案", key="get_health_answer"):
        if question:
            with st.spinner("查询中..."):
                try:
                    resp = requests.get(
                        url='https://apis.tianapi.com/healthskill/index',
                        params={
                            'key': 'f9a6a0b06e1cec7c38fa0a6fc0b675d2',
                            'word': question,
                            'len': 3
                        }
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        if data['code'] == 200:
                            results = data['result']['list']

                            if results:
                                for i, item in enumerate(results, 1):
                                    st.subheader(f"回答 {i}")
                                    st.write(item['content'])
                                    st.markdown("---")
                            else:
                                st.info("未找到相关回答，请尝试其他关键词")
                        else:
                            st.error("请输入正确关键词如流鼻涕")
                    else:
                        st.error(f"请求失败，状态码: {resp.status_code}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
        else:
            st.warning("请输入您的问题")

# 诗经查询助手
def shijing():
    st.header("诗经查询助手")
    st.markdown("输入《诗经》篇目名称，获取详细内容及注释")

    poem_name = st.text_input("请输入篇目名称", placeholder="例如：关雎、蒹葭")

    if st.button("查询", key="search_shijing"):
        if poem_name:
            with st.spinner("查询中..."):
                try:
                    resp = requests.get(
                        url='https://apis.tianapi.com/shijing/index',
                        params={
                            'key': 'f9a6a0b06e1cec7c38fa0a6fc0b675d2',
                            'word': poem_name,
                            'len': 1
                        }
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        if data['code'] == 200:
                            poem = data['result']['list'][0]

                            st.title(poem['name'])
                            st.markdown(f"**{poem['author']}**")
                            st.divider()

                            st.subheader("原文")
                            st.code(poem['content'], language="text")

                            st.subheader("注释")
                            st.info(poem['note'])

                            # 分享和收藏功能
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("👍 喜欢", key="like_poem"):
                                    st.success("已记录您的喜爱！")
                            with col2:
                                if st.button("⭐ 收藏", key="save_poem"):
                                    st.success(f"已收藏《{poem['name']}》")
                        else:
                            st.error(f"API错误: {data['msg']}")
                    else:
                        st.error(f"请求失败，状态码: {resp.status_code}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
        else:
            st.warning("请输入篇目名称")


# 油价查询
def youjia():
    st.header("各省份油价数据")
    st.markdown("查询国内各省份最新油价信息")

    province = st.selectbox(
        "请选择省份",
        ["北京", "上海", "天津", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
         "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
         "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古",
         "广西", "西藏", "宁夏", "新疆"]
    )

    if st.button("查询油价", key="search_oil_price"):
        with st.spinner("查询中..."):
            try:
                resp = requests.get(
                    url='https://apis.tianapi.com/oilprice/index',
                    params={
                        'key': 'f9a6a0b06e1cec7c38fa0a6fc0b675d2',
                        'prov': province,
                        'len': 1
                    }
                )

                if resp.status_code == 200:
                    data = resp.json()
                    if data['code'] == 200:
                        result = data['result']

                        st.success(f"{result['prov']} 最新油价（更新时间：{result['time'][:16]}）")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("柴油(0#)", f"¥{float(result['p0']):.2f}")
                        with col2:
                            st.metric("汽油(92#)", f"¥{float(result['p92']):.2f}")
                        with col3:
                            st.metric("汽油(95#)", f"¥{float(result['p95']):.2f}")
                        with col4:
                            st.metric("汽油(98#)",
                                      f"¥{float(result['p98']):.2f}" if result['p98'] != "0.00" else "暂无数据")
                    else:
                        st.error(f"API错误: {data['msg']}")
                else:
                    st.error(f"请求失败，状态码: {resp.status_code}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")


# 百科知识题库
def baike():
    st.header("百科知识题库")
    st.markdown("查询各类百科知识题目及答案")

    keyword = st.text_input("请输入关键词", placeholder="例如：历史、科技、文化")

    if st.button("搜索题目", key="search_baike"):
        if keyword:
            with st.spinner("搜索中..."):
                try:
                    resp = requests.get(
                        url='https://apis.tianapi.com/baiketiku/index',
                        params={
                            'key': 'f9a6a0b06e1cec7c38fa0a6fc0b675d2',
                            'word': keyword,
                            'len': 1
                        }
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        if data['code'] == 200:
                            result = data['result']

                            st.subheader(result['title'])

                            st.markdown("**选项:**")
                            st.write(f"A. {result['answerA']}")
                            st.write(f"B. {result['answerB']}")
                            st.write(f"C. {result['answerC']}")
                            st.write(f"D. {result['answerD']}")

                            with st.expander("查看答案与解析"):
                                st.success(f"**正确答案**: {result['answer']}")
                                st.info(result['analytic'])

                            # 分享和收藏功能
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📤 分享题目", key="share_question"):
                                    st.success("题目链接已复制到剪贴板！")
                            with col2:
                                if st.button("⭐ 收藏题目", key="save_question"):
                                    st.success("题目已收藏！")
                        else:
                            st.error(f"API错误: {data['msg']}")
                    else:
                        st.error(f"请求失败，状态码: {resp.status_code}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
        else:
            st.warning("请输入关键词")
def addition_function():
    # 主要功能选项
    function_options = [
        "vip视频", "健康知识问答",
        "BFR体脂率计算", "诗经查询助手",
        "各省份油价数据","百科知识题库"
    ]

    selected_function = st.sidebar.selectbox("选择功能", function_options)
    # 根据选择显示相应功能
    if selected_function == "vip视频":
        watch_tv()
    elif selected_function == "健康知识问答":
        jiankangzhishi()
    elif selected_function == "BFR体脂率计算":
        BFR()
    elif selected_function == "诗经查询助手":
        shijing()
    elif selected_function == "各省份油价数据":
        youjia()
    elif selected_function == "百科知识题库":
        baike()