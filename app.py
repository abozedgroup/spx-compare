import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay

st.set_page_config(layout="wide")
st.title("مقارنة الأداء التراكمي للمؤشرات")
st.subheader("2025 مقابل متوسط الأداء من 2015 إلى 2024 حسب يوم التداول")

# روابط المؤشرات من Google Sheets (Published CSV)
symbols = {
    "S&P 500 (SPX)": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSG0n6vJgiLbyUo2hiiLwTr0HOyhZVONxV6W-h1UPs2ba2WLHAl33IHkcxB-sSN2vthoBJDmEnzhQdP/pub?gid=0&single=true&output=csv",
    "Nasdaq 100 (QQQ)": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSG0n6vJgiLbyUo2hiiLwTr0HOyhZVONxV6W-h1UPs2ba2WLHAl33IHkcxB-sSN2vthoBJDmEnzhQdP/pub?gid=1428234309&single=true&output=csv",
    "Dow Jones (DIA)": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSG0n6vJgiLbyUo2hiiLwTr0HOyhZVONxV6W-h1UPs2ba2WLHAl33IHkcxB-sSN2vthoBJDmEnzhQdP/pub?gid=2020634384&single=true&output=csv"
}

# اختيار المؤشر
selected_symbol = st.selectbox("اختر المؤشر:", list(symbols.keys()))
data_url = symbols[selected_symbol]

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

    # تحديد الحد الأدنى المشترك لعدد أيام التداول (مثلاً 251)
    max_days = df_past.groupby('Year')['Trading Day'].max().min()
    df_past = df_past[df_past['Trading Day'] <= max_days]

    avg = df_past.groupby('Trading Day')['Cumulative Return'].mean().reset_index()
    avg.columns = ['Trading Day', 'Avg Cumulative Return']

    return avg, df_2025, max_days

# تحميل البيانات
avg, df_2025, max_days = load_data(data_url)

# توليد تواريخ كاملة بـ max_days تداول تبدأ من أول يوم في 2025
start_date = df_2025['Date'].min()
trading_days_full = pd.date_range(start=start_date, periods=max_days, freq=BDay())

# إعداد التواريخ للمحور (كل 10 أيام تداول)
tickvals = avg['Trading Day'][::10]
ticktext = trading_days_full.strftime('%b %d')[::10]

# رسم البيانات
fig = go.Figure()

# الخط الأزرق: المتوسط التاريخي
fig.add_trace(go.Scatter(
    x=avg['Trading Day'],
    y=avg['Avg Cumulative Return'] * 100,
    mode='lines',
    name='متوسط التغير التراكمي (2015-2024)',
    line=dict(color='blue')
))

# الخط الأحمر: أداء 2025
fig.add_trace(go.Scatter(
    x=df_2025['Trading Day'],
    y=df_2025['Cumulative Return'] * 100,
    mode='lines',
    name='التغير التراكمي 2025',
    line=dict(color='red')
))

# إعدادات الرسم
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
    height=600
)

st.plotly_chart(fig, use_container_width=True)
