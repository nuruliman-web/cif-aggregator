# app.py
import streamlit as st
import pandas as pd
import io

# Import file kita
from header import HEADER_MAPPING, get_headers_for_file
from parser import parse_tab_file
from utils import get_best_value

# ============================================================
# 1. KONFIGURASI
# ============================================================
st.set_page_config(page_title="Visual Data Mapper", layout="wide")
st.title("📊 Visual Data Mapper")
st.write("Upload file .tab, pilih kolom yang mau digabung")

# ============================================================
# 2. STATE MANAGEMENT
# ============================================================
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "selected_key" not in st.session_state:
    st.session_state.selected_key = {}
if "selected_cols" not in st.session_state:
    st.session_state.selected_cols = {}
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

# ============================================================
# 3. UI UTAMA
# ============================================================

st.subheader("📁 Upload File Data (.tab)")
data_files = st.file_uploader(
    "Upload file .tab",
    accept_multiple_files=True,
    type=["tab", "txt"],
    key="data_uploader"
)

if data_files:
    with st.spinner("⏳ Membaca file..."):
        for file in data_files:
            raw_name = file.name
            if raw_name.endswith(".tab"):
                raw_name = raw_name[:-4]
            elif raw_name.endswith(".txt"):
                raw_name = raw_name[:-4]
            key = raw_name.upper()
            
            df = parse_tab_file(file)
            if df is not None and not df.empty:
                header_info = get_headers_for_file(key)
                if header_info:
                    if header_info.get("deskripsi") and len(header_info["deskripsi"]) > 0 and not all(h == "" for h in header_info["deskripsi"]):
                        headers = header_info["deskripsi"]
                    else:
                        headers = header_info["kode"]
                    
                    if len(headers) > len(df.columns):
                        headers = headers[:len(df.columns)]
                    elif len(headers) < len(df.columns):
                        headers = headers + [f"Kolom {i}" for i in range(len(headers), len(df.columns))]
                    
                    st.session_state.uploaded_files[key] = {
                        "df": df,
                        "headers": headers,
                        "file_name": file.name,
                        "matched_sheet": key
                    }
                    st.success(f"✅ {file.name}: {len(df)} baris, {len(df.columns)} kolom → Match: {key}")
                else:
                    headers = [f"Kolom {i}" for i in range(len(df.columns))]
                    st.session_state.uploaded_files[key] = {
                        "df": df,
                        "headers": headers,
                        "file_name": file.name,
                        "matched_sheet": None
                    }
                    st.warning(f"⚠️ {file.name}: {len(df)} baris, {len(df.columns)} kolom → Tidak ada header di mapping")
            else:
                st.warning(f"⚠️ {file.name}: Kosong atau tidak terbaca")

# ---- Pilih Kolom Kunci ----
if st.session_state.uploaded_files:
    st.subheader("🔑 Pilih Kolom Kunci (CIF)")
    
    for key, info in st.session_state.uploaded_files.items():
        df = info["df"]
        headers = info["headers"]
        file_name = info["file_name"]
        
        if key not in st.session_state.selected_key:
            st.session_state.selected_key[key] = None
        
        st.write(f"**📋 {file_name}**")
        
        preview_df = df.head(3).copy()
        preview_df.columns = headers[:len(preview_df.columns)]
        st.dataframe(preview_df, use_container_width=True)
        
        col_options = {f"{i}: {h}" : i for i, h in enumerate(headers)}
        
        default_idx = 0
        for i, h in enumerate(headers):
            h_upper = h.upper()
            if "CUCODE" in h_upper or "CUSTOMER CODE" in h_upper or "CIF" in h_upper or "CODE" in h_upper:
                default_idx = i
                break
        
        selected_label = st.selectbox(
            f"Pilih kolom kunci untuk {file_name}",
            options=list(col_options.keys()),
            index=default_idx,
            key=f"key_select_{key}"
        )
        st.session_state.selected_key[key] = col_options[selected_label]
        st.write("---")

# ---- Pilih Kolom yang Mau Dibawa ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    st.subheader("📋 Pilih Kolom yang Mau Digabung")
    
    for key, info in st.session_state.uploaded_files.items():
        df = info["df"]
        headers = info["headers"]
        file_name = info["file_name"]
        key_col = st.session_state.selected_key[key]
        
        st.write(f"**📋 {file_name}** (Kunci: {headers[key_col] if key_col < len(headers) else f'Kolom {key_col}'})")
        
        if key not in st.session_state.selected_cols:
            st.session_state.selected_cols[key] = [key_col]
            count = 0
            for i in range(len(headers)):
                if i != key_col and count < 2:
                    st.session_state.selected_cols[key].append(i)
                    count += 1
        
        col_options = {i: f"{i}: {h}" for i, h in enumerate(headers)}
        
        selected = st.multiselect(
            f"Pilih kolom dari {file_name}",
            options=list(col_options.keys()),
            format_func=lambda x: col_options[x],
            default=st.session_state.selected_cols.get(key, [key_col]),
            key=f"col_select_{key}"
        )
        st.session_state.selected_cols[key] = selected
        st.write("---")

# ---- Proses Gabung ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    if st.button("🚀 Gabungkan Data"):
        with st.spinner("⏳ Memproses..."):
            try:
                first_key = list(st.session_state.uploaded_files.keys())[0]
                first_info = st.session_state.uploaded_files[first_key]
                first_df = first_info["df"]
                first_key_col = st.session_state.selected_key[first_key]
                first_selected_cols = st.session_state.selected_cols[first_key]
                first_headers = first_info["headers"]
                
                result_data = {}
                result_headers = []
                
                for col_idx in first_selected_cols:
                    col_name = first_headers[col_idx] if col_idx < len(first_headers) else f"Kolom {col_idx}"
                    result_headers.append(col_name)
                    result_data[col_name] = first_df[col_idx].tolist()
                
                for key, info in st.session_state.uploaded_files.items():
                    if key == first_key:
                        continue
                    
                    df = info["df"]
                    key_col = st.session_state.selected_key[key]
                    selected_cols = st.session_state.selected_cols[key]
                    headers = info["headers"]
                    
                    other_keys = df[key_col].tolist()
                    other_data = {}
                    
                    for col_idx in selected_cols:
                        col_name = headers[col_idx] if col_idx < len(headers) else f"Kolom {col_idx}"
                        final_name = f"{info['file_name']}_{col_name}"
                        result_headers.append(final_name)
                        other_data[final_name] = df[col_idx].tolist()
                    
                    result_keys = result_data[result_headers[0]]
                    
                    for i, row_key in enumerate(result_keys):
                        for j, other_key in enumerate(other_keys):
                            if str(row_key).strip() == str(other_key).strip():
                                for col_name, col_data in other_data.items():
                                    if col_name not in result_data:
                                        result_data[col_name] = []
                                    while len(result_data[col_name]) < i:
                                        result_data[col_name].append("-")
                                    result_data[col_name].append(col_data[j])
                                break
                        for col_name in other_data.keys():
                            if col_name not in result_data:
                                result_data[col_name] = []
                            while len(result_data[col_name]) < i + 1:
                                result_data[col_name].append("-")
                
                result_df = pd.DataFrame(result_data)
                st.session_state.processed_data = result_df
                st.success(f"✅ Data berhasil digabung! {len(result_df)} baris, {len(result_df.columns)} kolom")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ---- Preview & Download ----
if st.session_state.processed_data is not None:
    st.subheader("📊 Preview Hasil Gabungan")
    st.dataframe(st.session_state.processed_data, use_container_width=True)
    st.caption(f"Total: {len(st.session_state.processed_data)} baris, {len(st.session_state.processed_data.columns)} kolom")
    
    csv_data = io.BytesIO()
    st.session_state.processed_data.to_csv(csv_data, index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data.getvalue(),
        file_name="hasil_gabungan.csv",
        mime="text/csv"
    )
    
    try:
        excel_data = io.BytesIO()
        with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
            st.session_state.processed_data.to_excel(writer, sheet_name='Hasil', index=False)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data.getvalue(),
            file_name="hasil_gabungan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except:
        pass

# ---- Reset ----
if st.button("🔄 Reset Semua"):
    for key in list(st.session_state.keys()):
        if key != "header_mapping":
            st.session_state[key] = None if key not in ["header_mapping"] else st.session_state.get(key, {})
    st.rerun()
