import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CIF Data Aggregator", layout="wide")

st.title("📊 CIF Data Aggregator")
st.write("Upload file .tab dari core banking untuk digabung datanya")

uploaded_files = st.file_uploader(
    "Upload file .tab", 
    accept_multiple_files=True, 
    type=["tab"]
)

if uploaded_files:
    # Di sini nanti kode parsing data dari file .tab
    st.success(f"✅ {len(uploaded_files)} file berhasil diupload!")
    
    # Nanti di sini: proses data → tampilkan preview → tombol download