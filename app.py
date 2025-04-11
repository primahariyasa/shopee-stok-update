import streamlit as st
import pandas as pd

st.title("Cek Upload File CSV & Excel")

uploaded_file = st.file_uploader("Upload file (.csv / .xlsx)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success("File berhasil dibaca!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
