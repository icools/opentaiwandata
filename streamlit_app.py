import streamlit as st
import pandas as pd
import altair as alt
import requests
import json

# 設定頁面配置，隱藏 GitHub 圖標
st.set_page_config(
    page_title="台灣人口指數資料",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 抓取台灣人口指數資料
@st.cache_data(ttl=300)
def fetch_population_data():
    url = "https://nstatdb.dgbas.gov.tw/dgbasall/webMain.aspx?sdmx/a130201010/1+2+3+4+5+6+7+8+9+10+11+12...M.&startTime=2019&endTime=2024-M4"
    response = requests.get(url)
    data = response.json()
    return data

# 讀取本地JSON文件作為備份
def load_local_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 轉換資料格式
def transform_data(data):
    observations = data['data']['dataSets'][0]['series']
    transformed_data = {}
    for key, value in observations.items():
        for idx, obs in value['observations'].items():
            transformed_data.setdefault(idx, []).append(obs[0])
    df = pd.DataFrame.from_dict(transformed_data, orient='index', columns=[
        "土地面積(平方公里)", "鄉鎮市區數", "村里數", "鄰數", "戶數(戶)",
        "人口數(人)", "人口增加率(‰)", "男性人口數(人)", "女性人口數(人)",
        "人口性比例(每百女子所當男子數)", "戶量(人/戶)", "人口密度(人/平方公里)"
    ])
    df.index = pd.date_range(start='2019-01-01', periods=len(df), freq='M')
    return df

# 嘗試抓取網路資料，失敗則使用本地資料
try:
    data = fetch_population_data()
except:
    st.warning("無法抓取網路資料，使用本地備份資料")
    data = load_local_data('/mnt/data/a13020101031210457254.json')

# 轉換資料
df = transform_data(data)

# Streamlit UI
st.title("台灣人口指數資料")

# 顯示資料表
st.write("### 人口指數資料表")
st.write(df)

# 繪製圖表
st.write("### 人口數變化趨勢")
line_chart = alt.Chart(df.reset_index()).mark_line().encode(
    x='index:T',
    y='人口數(人):Q',
    tooltip=['index:T', '人口數(人)']
).properties(
    width=800,
    height=400
)

st.altair_chart(line_chart)

# 男女人口走勢圖
st.write("### 男女人口數變化趨勢")
gender_chart = alt.Chart(df.reset_index()).mark_line().encode(
    x='index:T',
    y='value:Q',
    color='variable:N'
).transform_fold(
    ['男性人口數(人)', '女性人口數(人)'],
    as_=['variable', 'value']
).properties(
    width=800,
    height=400
)

st.altair_chart(gender_chart)

# 人口增加率圖表
st.write("### 人口增加率變化趨勢")
growth_rate_chart = alt.Chart(df.reset_index()).mark_bar().encode(
    x='index:T',
    y='人口增加率(‰):Q',
    tooltip=['index:T', '人口增加率(‰)']
).properties(
    width=800,
    height=400
)

st.altair_chart(growth_rate_chart)
