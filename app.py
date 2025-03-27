import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("تحقق من بيانات Google Sheets")

@st.cache_data(ttl=86400)
def load_raw_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSG0n6vJgiLbyUo2hiiLwTr0HOyhZVONxV6W-h1UPs2ba2WLHAl33IHkcxB-sSN2vthoBJDmEnzhQdP/pub?output=csv"
    return pd.read_csv(url)

df = load_raw_data()

st.write("أسماء الأعمدة:")
st.write(df.columns.tolist())

st.write("أول 20 صف:")
st.dataframe(df.head(20))