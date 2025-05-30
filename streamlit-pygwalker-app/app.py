import streamlit as st
import pandas as pd
import pygwalker as pyg

st.set_page_config(page_title="Token Analysis", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("token_trades_with_onchain_metrics.csv")

df = load_data()

st.title("Token Trade Analysis with Pygwalker")

pyg_html = pyg.walk(df, return_html=True)
st.components.v1.html(pyg_html, height=1000, scrolling=True)
