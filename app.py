import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay

st.set_page_config(layout="wide")
st.title("مقارنة الأداء التراكمي للمؤشرات")
st.subheader("2025 مقابل متوسط الأداء من 2015 إلى 2024 حسب يوم التداول")

# قائمة المؤشرات وروابطها
symbols = {
    "S&P 500 (SPX)": "0",
    "Nasdaq 100 (QQQ)": "1428234309",
    "Dow Jones (DIA)": "2020634384"
}

# اختيار المؤشر
selected_symbol = st.selectbox("اختر المؤشر:", list(symbols.keys()))
gid = symbols[selected_symbol]

# رابط الملف العام
base_url = "https://docs.google.com/spreadsheets/d/1-0RoT4BK96Mn9V36RtoHFH0Ibwun9pVi0tuZuqpCGEA/export?format=csv&gid="

@st.cache_data(ttl=86400)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = ["Date", "Close"]
    df['Date'] = pd.to_datetime(df['Date'], errors="coerce")
    df['Close'] = pd.to_numeric(df['Close'], errors="coerce")
    df = df.dropna(subset=["Date", "Close"])

    df['Year'] = df['Date'].dt.year
    df['Daily Return'] = df['Close'].pct_change()
    df['Trading Day'] = df.groupby('Year').cumcount() + 1
    df['Cumulative Return'] = df.groupby('Year')['Daily Return'].cumsum()
    df['Cumulative Return'] = (1 + df['Cumulative Return']) - 1

    df_past = df[df['Year'] < 2025]
    df_2025 = df[df['Year'] == 2025].copy()

    avg = df_past.groupby('Trading Day')['Cumulative Return'].mean().reset_index()
    avg.columns = ['Trading Day', 'Avg Cumulative Return']

    return avg, df_2025

# تحميل البيانات
data_url = base_url + gid
avg, df_2025 = load_data(data_url)

# توليد تواريخ كاملة لـ 252 يوم تداول تبدأ من أول يوم في 2025
start_date = df_2025['Date'].min()
trading_days_full = pd.date_range(start=start_date, periods=252, freq=BDay())
trading_days_full = trading_days_full[:avg['Trading Day'].max()]

# إعداد التواريخ للمحور (كل 10 أيام تداول)
tickvals = avg['Trading Day'][::10]
ticktext = trading_days_full.strftime('%b %d')[::10]

# رسم البيانات
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=avg['Trading Day'],
    y=avg['Avg Cumulative Return'] * 100,
    mode='lines',
    name='متوسط التغير التراكمي (2015-2024)',
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=df_2025['Trading Day'],
    y=df_2025['Cumulative Return'] * 100,
    mode='lines',
    name='التغير التراكمي 2025',
    line=dict(color='red')
))

fig.update_layout(
    xaxis=dict(
        title='التاريخ (حسب يوم التداول)',
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        tickangle=-45,
        tickfont=dict(size=10),
    ),
    yaxis=dict(title='نسبة التغير التراكمي (%)'),
    legend=dict(x=0, y=1),
    height=500
)

st.plotly_chart(fig, use_container_width=True)
