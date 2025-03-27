import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("S&P 500 - مقارنة الأداء التراكمي")
st.subheader("بيانات حية من Google Sheets - تحدث تلقائيًا يوميًا")

@st.cache_data(ttl=86400)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSG0n6vJgiLbyUo2hiiLwTr0HOyhZVONxV6W-h1UPs2ba2WLHAl33IHkcxB-sSN2vthoBJDmEnzhQdP/pub?output=csv"
    df = pd.read_csv(url)

    if df.empty or df.shape[1] < 2:
        st.error("البيانات غير صالحة أو الملف فارغ.")
        st.stop()

    # تنظيف التاريخ وتحويله لتاريخ فقط
    df['Date'] = pd.to_datetime(df[df.columns[0]], errors='coerce')
    df = df.dropna(subset=["Date"])
    df = df.rename(columns={df.columns[1]: "Close"})

    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df = df.dropna(subset=["Close"])

    df['Year'] = df['Date'].dt.year
    df['Daily Return'] = df['Close'].pct_change()
    df['Trading Day'] = df.groupby('Year').cumcount() + 1
    df['Cumulative Return'] = df.groupby('Year')['Daily Return'].cumsum()
    df['Cumulative Return'] = (1 + df['Cumulative Return']) - 1

    df_past = df[df['Year'] < 2025]
    df_2025 = df[df['Year'] == 2025]

    avg = df_past.groupby('Trading Day')['Cumulative Return'].mean().reset_index()
    avg.columns = ['Trading Day', 'Avg Cumulative Return']
    merged = pd.merge(df_2025, avg, on='Trading Day', how='left')
    merged['DateStr'] = merged['Date'].dt.strftime('%Y-%m-%d')
    return merged

merged = load_data()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Avg Cumulative Return'] * 100,
    mode='lines',
    name='متوسط التغير التراكمي (2015-2024)',
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Cumulative Return'] * 100,
    mode='lines',
    name='تغير 2025',
    line=dict(color='red')
))

fig.update_layout(
    xaxis_title='التاريخ',
    yaxis_title='نسبة التغير (%)',
    legend=dict(x=0, y=1),
    height=500,
    autosize=True
)

st.plotly_chart(fig, use_container_width=True)