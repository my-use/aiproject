
"""
main.py - 自助式数据分析（数据分析智能体）

Author: 骆昊
Version: 0.1
"""
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils import dataframe_agent


def create_chart(input_data, chart_type):
    """生成统计图表"""
    df_data = pd.DataFrame(
        data={
            "x": input_data["columns"],
            "y": input_data["data"]
        }
    )
    df_data.set_index("x", inplace=True)
    if chart_type == "bar":
        st.bar_chart(df_data)
    elif chart_type == "line":
        plt.plot(df_data.index, df_data["y"], marker="o", linestyle="--")
        plt.ylim(0, df_data["y"].max() * 1.1)
        plt.title("xxxxxxxxxxx")
        st.pyplot(plt.gcf())



