import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("S&P 500 - مقارنة الأداء التراكمي")
st.subheader("مقارنة بين متوسط الأداء من 2015 إلى 2024 وأداء سنة 2025 حتى الآن")

# تحميل البيانات
merged = pd.read_csv("spx_2025_vs_avg.csv")

# تحويل التاريخ إلى نص فقط بدون وقت
merged['Date'] = pd.to_datetime(merged['Date'])
merged['DateStr'] = merged['Date'].dt.strftime('%Y-%m-%d')

# رسم الخط البياني
fig = go.Figure()

# متوسط السنوات السابقة
fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Avg Cumulative Return'] * 100,
    mode='lines',
    name='Average YTD Percent Change, 2015-2024',
    line=dict(color='blue')
))

# سنة 2025
fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Cumulative Return'] * 100,
    mode='lines',
    name='2025 YTD Percent Change',
    line=dict(color='red')
))

# تنسيق الرسم ليتناسب مع الجوال
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Percent Change (%)',
    legend=dict(x=0, y=1),
    height=500,
    autosize=True
)

st.plotly_chart(fig, use_container_width=True)