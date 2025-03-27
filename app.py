import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("S&P 500 - مقارنة الأداء التراكمي")
st.subheader("بيانات حية من Google Sheets - تحدث تلقائيًا يوميًا")

@st.cache_data(ttl=86400)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSG0n6vJgiLbyUo2hiiLwTr0HOyhZVONxV6W-h1UPs2ba2WLHAl33IHkcxB-sSN2vthoBJDmEnzhQdP/pub?output=csv"
    df_raw = pd.read_csv(url)

    if df_raw.empty or df_raw.shape[1] < 2:
        st.error("البيانات غير كافية.")
        st.stop()

    # معاينة مبدئية
    st.write("أول 5 صفوف من البيانات الأصلية:")
    st.dataframe(df_raw.head())

    # فرض أسماء الأعمدة
    df_raw.columns = ["RawDate", "RawClose"]

    # إزالة الصفوف اللي تاريخها ما يمكن تحويله
    df_raw["Date"] = pd.to_datetime(df_raw["RawDate"], errors="coerce")
    df_raw = df_raw.dropna(subset=["Date"])

    # تحويل الإغلاق إلى رقم
    df_raw["Close"] = pd.to_numeric(df_raw["RawClose"], errors="coerce")
    df = df_raw.dropna(subset=["Close"]).copy()

    df['Year'] = df['Date'].dt.year
    df['Daily Return'] = df['Close'].pct_change()
    df['Trading Day'] = df.groupby('Year').cumcount() + 1
    df['Cumulative Return'] = df.groupby('Year')['Daily Return'].cumsum()
    df['Cumulative Return'] = (1 + df['Cumulative Return']) - 1

    df_past = df[df['Year'] < 2025]
    df_2025 = df[df['Year'] == 2025]

    if df_past.empty or df_2025.empty:
        st.error("لا توجد بيانات كافية لعرض الرسم.")
        st.dataframe(df.head(10))
        st.stop()

    avg = df_past.groupby('Trading Day')['Cumulative Return'].mean().reset_index()
    avg.columns = ['Trading Day', 'Avg Cumulative Return']

    merged = pd.merge(df_2025, avg, on='Trading Day', how='left')
    merged['DateStr'] = merged['Date'].dt.strftime('%Y-%m-%d')

    if merged.empty or 'Avg Cumulative Return' not in merged.columns:
        st.error("فشل في تجهيز البيانات للعرض.")
        st.dataframe(merged.head(10))
        st.stop()

    return merged

merged = load_data()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Avg Cumulative Return'] * 100,
    mode='lines',
    name='متوسط الأداء (2015-2024)',
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=merged['DateStr'],
    y=merged['Cumulative Return'] * 100,
    mode='lines',
    name='أداء 2025',
    line=dict(color='red')
))

fig.update_layout(
    xaxis_title='التاريخ',
    yaxis_title='نسبة التغير (%)',
    legend=dict(x=0, y=1),
    height=500
)

st.plotly_chart(fig, use_container_width=True)