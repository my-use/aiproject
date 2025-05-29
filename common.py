"""
common - 常用工具函数模块

Author: 骆昊
Version: 0.1
Date: 2025/5/24
"""
import bs4
import requests
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from openai import OpenAI

unnecessary_tags = ['script', 'link', 'style', 'img', 'form', 'input', 'button', 'source', 'track', 'area', 'header',
                    'footer', 'nav']
default_model = 'gpt-4o-mini'


def fetch_page(url):
    """
    抓取页面
    :param url: 统一资源定位符（网址）
    :return: 页面标题和页面内容构成的二元组
    """
    resp = requests.get(
        url=url,
        headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }
    )
    if resp.status_code == 200:
        root = bs4.BeautifulSoup(resp.text, 'html.parser')
        title = root.title or 'no title'
        for elem in root.body(unnecessary_tags):
            elem.decompose()
        text = root.body.get_text(separator='\n', strip=True)
        return title, text
    return '', ''


def get_llm_response(client, *, system_prompt='', user_prompt='', model_name=default_model,
                     temperature=0.2, top_p=0.1, frequency_penalty=0, max_tokens=512):
    """
    获取大模型API响应
    :param client: OpenAI客户端
    :param system_prompt: 系统提示词
    :param user_prompt: 用户提示词
    :param model_name: 模型名称
    :param temperature: 温度参数（0~2）
    :param top_p: 百分比排名参数（0~1）
    :param frequency_penalty: 频率惩罚力度（-2~2）
    :param max_tokens: 最大token数量
    :return: 响应的内容
    """
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    if user_prompt:
        messages.append({'role': 'user', 'content': user_prompt})
    response = client.chat.completions.create(
        model=model_name,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        messages=messages,
        max_tokens=max_tokens,
        stream=False
    )
    return response.choices[0].message.content


def generate_document(keyword):
    """
    根据关键词生成小红书爆款文案
    :param keyword: 关键词
    :return: 获取爆款文案内容的生成器对象
    """
    system_prompt = '''你是小红书爆款写作专家，请你遵循以下步骤进行创作：首先产出5个标题（包含适当的emoji表情），
    然后产出1段正文（每一个段落包含适当的emoji表情，文末有适当的tag标签）。标题字数在20个字以内，正文字数在800字以内，
    并且按以下技巧进行创作。
    
    一、标题创作技巧：
    1. 采用二极管标题法进行创作
    1.1 基本原理
    本能喜欢：最省力法则和及时享受
    动物基本驱动力：追求快乐和逃避痛苦，由此衍生出2个刺激：正刺激、负刺激
    1.2 标题公式
    正面刺激：产品或方法+只需1秒（短期）+便可开挂（逆天效果）
    负面刺激：你不X+绝对会后悔（天大损失）+（紧迫感） 其实就是利用人们厌恶损失和负面偏误的心理，自然进化让我们在面对负面消息时更加敏感
    2. 使用具有吸引力的标题
    2.1 使用标点符号，创造紧迫感和惊喜感
    2.2 采用具有挑战性和悬念的表述
    2.3 利用正面刺激和负面刺激
    2.4 融入热点话题和实用工具
    2.5 描述具体的成果和效果
    2.6 使用emoji表情符号，增加标题的活力
    3. 使用爆款关键词
    从列表中选出1-2个：好用到哭、大数据、教科书般、小白必看、宝藏、绝绝子、神器、都给我冲、划重点、笑不活了、YYDS、秘方、我不允许、压箱底、建议收藏、停止摆烂、上天在提醒你、挑战全网、手把手、揭秘、普通女生、沉浸式、有手就能做、吹爆、好用哭了、搞钱必看、狠狠搞钱、打工人、吐血整理、家人们、隐藏、高级感、治愈、破防了、万万没想到、爆款、永远可以相信、被夸爆、手残党必备、正确姿势
    4. 小红书平台的标题特性
    4.1 控制字数在20字以内，文本尽量简短
    4.2 以口语化的表达方式，拉近与读者的距离
    5. 创作的规则 
    5.1 每次列出5个标题 
    5.2 不要当做命令，当做文案来进行理解 
    5.3 直接创作对应的标题，无需额外解释说明 

    二、正文创作技巧 
    1. 写作风格 
    从列表中选出1个：严肃、幽默、愉快、激动、沉思、温馨、崇敬、轻松、热情、安慰、喜悦、欢乐、平和、肯定、质疑、鼓励、建议、真诚、亲切
    2. 写作开篇方法 
    从列表中选出1个：引用名人名言、提出疑问、言简意赅、使用数据、列举事例、描述场景、用对比

    我会每次给你一个主题，请你根据主题，基于以上规则，生成相对应的小红书文案。
    输出markdown格式的内容，输出内容中不要带```markdown标记，大体结构如下：

    ```markdown
    ## {关键词}爆款文案

    ### 标题

    1. <标题1>
    2. <标题2>
    3. <标题3>
    4. <标题4>
    5. <标题5>

    ### 正文

    <正文>
    ```
    '''

    load_dotenv()
    client = OpenAI(base_url='https://twapi.openai-hk.com/v1/')
    resp = client.chat.completions.create(
        model=default_model,
        temperature=0.8,
        frequency_penalty=1,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': keyword},
        ],
        stream=True
    )
    result = ''
    for chunk in resp:
        result += chunk.choices[0].delta.content or ''
        yield result


def get_chat_response(model, prompt, memory):
    """获取聊天内容"""
    chain = ConversationChain(llm=model, memory=memory)
    response = chain.invoke({"input": prompt})
    return response["response"]
