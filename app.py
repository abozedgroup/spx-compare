import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

st.set_page_config(layout="wide")

st.title("S&P 500 - مقارنة الأداء التراكمي")
st.subheader("تحديث تلقائي لبيانات S&P 500 من 2015 حتى 2025")

@st.cache_data(ttl=86400)  # يتم تحديث البيانات كل 24 ساعة
def load_data():
    spx = yf.download('^GSPC', start='2015-01-01')

    # التحقق من الأعمدة قبل المعالجة
    if 'Date' not in spx.columns or 'Adj Close' not in spx.columns:
        st.error("فشل تحميل بيانات SPX من yfinance. حاول لاحقًا.")
        st.stop()

    spx.reset_index(inplace=True)
    spx = spx[['Date', 'Adj Close']]
    spx['Year'] = spx['Date'].dt.year
    spx['Daily Return'] = spx['Adj Close'].pct_change()
    spx['Trading Day'] = spx.groupby('Year').cumcount() + 1
    spx['Cumulative Return'] = spx.groupby('Year')['Daily Return'].cumsum()
    spx['Cumulative Return'] = (1 + spx['Cumulative Return']) - 1

    # فصل السنوات
    spx_past = spx[spx['Year'] < 2025]
    spx_2025 = spx[spx['Year'] == 2025]

    avg_cumulative = spx_past.groupby('Trading Day')['Cumulative Return'].mean().reset_index()
    avg_cumulative.columns = ['Trading Day', 'Avg Cumulative Return']

    merged = pd.merge(spx_2025, avg_cumulative, on='Trading Day', how='left')
    merged['DateStr'] = merged['Date'].dt.strftime('%Y-%m-%d')
    return merged

merged = load_data()

# إنشاء الرسم البياني
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Avg Cumulative Return'] * 100,
    mode='lines',
    name='Average YTD Percent Change, 2015-2024',
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