# app.py
import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer   # même import que dans l’image

# — Paramètres Streamlit —
st.set_page_config(page_title="Token Analysis", layout="wide")

# — Chargement des données (mise en cache Streamlit) —
@st.cache_data
def load_data():
    # adapte le chemin si nécessaire
    return pd.read_csv("token_trades_with_onchain_metrics.csv")

df = load_data()

# — Création de l’explorateur Pygwalker —
# Si tu as déjà un spec JSON (par ex. ./spec/token_chart.json), dé-commente la ligne suivante
# pyg_app = StreamlitRenderer(df, spec="./spec/token_chart.json")

# Sinon laisse Pygwalker générer l’interface par défaut
pyg_app = StreamlitRenderer(df)

# — Affichage —
pyg_app.explorer()      # équivalent exact à la ligne 9 de l’image
