import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide")
st.title("S&P 500 - مقارنة الأداء التراكمي")
st.subheader("بيانات مباشرة من Alpha Vantage باستخدام التحديث التلقائي")

@st.cache_data(ttl=86400)  # تحديث يومي
def load_data():
    API_KEY = "X57FEQ50RF9X5LR5"
    SYMBOL = "SPX"
    FUNCTION = "TIME_SERIES_DAILY_ADJUSTED"
    URL = f"https://www.alphavantage.co/query?function={FUNCTION}&symbol={SYMBOL}&outputsize=full&apikey={API_KEY}"

    r = requests.get(URL)
    data = r.json()

    if "Time Series (Daily)" not in data:
        st.error("فشل في تحميل البيانات من Alpha Vantage.")
        st.stop()

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df = df.rename(columns={"5. adjusted close": "Adj Close"})
    df = df[["Adj Close"]].astype(float)
    df["Date"] = df.index
    df.reset_index(drop=True, inplace=True)

    # تحليل البيانات
    df['Year'] = df['Date'].dt.year
    df['Daily Return'] = df['Adj Close'].pct_change()
    df['Trading Day'] = df.groupby('Year').cumcount() + 1
    df['Cumulative Return'] = df.groupby('Year')['Daily Return'].cumsum()
    df['Cumulative Return'] = (1 + df['Cumulative Return']) - 1

    df = df[df['Year'] >= 2015]
    df['DateStr'] = df['Date'].dt.strftime('%Y-%m-%d')

    df_past = df[df['Year'] < 2025]
    df_2025 = df[df['Year'] == 2025]

    avg = df_past.groupby('Trading Day')['Cumulative Return'].mean().reset_index()
    avg.columns = ['Trading Day', 'Avg Cumulative Return']
    merged = pd.merge(df_2025, avg, on='Trading Day', how='left')

    return merged

# تحميل البيانات
merged = load_data()

# إنشاء الرسم البياني
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Avg Cumulative Return'] * 100,
    mode='lines',
    name='Average YTD Percent Change (2015-2024)',
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Cumulative Return'] * 100,
    mode='lines',
    name='2025 YTD Percent Change',
    line=dict(color='red')
))

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Percent Change (%)',
    legend=dict(x=0, y=1),
    height=500,
    autosize=True
)

st.plotly_chart(fig, use_container_width=True)