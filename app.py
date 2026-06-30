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
# 2. STATE MANAGEMENT (biar gak reload ulang)
# ============================================================
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "selected_key" not in st.session_state:
    st.session_state.selected_key = {}
if "selected_cols" not in st.session_state:
    st.session_state.selected_cols = {}
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "file_headers" not in st.session_state:
    st.session_state.file_headers = {}  # Simpan header biar gak reload
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# ============================================================
# 3. FUNGSI BANTUAN
# ============================================================
def make_unique_headers(headers):
    """Bikin header unik dengan nambahin suffix kalau ada duplikat"""
    seen = {}
    unique_headers = []
    for h in headers:
        h_str = str(h).strip()
        if not h_str or h_str == "":
            h_str = "Kolom"
        if h_str in seen:
            seen[h_str] += 1
            unique_headers.append(f"{h_str}_{seen[h_str]}")
        else:
            seen[h_str] = 1
            unique_headers.append(h_str)
    return unique_headers

def render_checkbox_columns(headers, key_prefix, default_selected):
    """Render kolom pilihan pake checkbox di columns"""
    selected = []
    cols = st.columns(4)  # 4 kolom per baris
    
    for i, h in enumerate(headers):
        col_idx = i % 4
        is_checked = i in default_selected
        with cols[col_idx]:
            if st.checkbox(
                h, 
                value=is_checked, 
                key=f"{key_prefix}_col_{i}"
            ):
                selected.append(i)
    
    return selected

# ============================================================
# 4. UI UTAMA
# ============================================================

st.subheader("📁 Upload File Data (.tab)")
data_files = st.file_uploader(
    "Upload file .tab",
    accept_multiple_files=True,
    type=["tab", "txt"],
    key="data_uploader"
)

# Tombol untuk load data (biar gak auto-load)
col1, col2 = st.columns([1, 4])
with col1:
    load_button = st.button("📥 Load Data", use_container_width=True)

if load_button or st.session_state.data_loaded:
    if data_files:
        st.session_state.data_loaded = True
        with st.spinner("⏳ Membaca file..."):
            for file in data_files:
                raw_name = file.name
                if raw_name.endswith(".tab"):
                    raw_name = raw_name[:-4]
                elif raw_name.endswith(".txt"):
                    raw_name = raw_name[:-4]
                key = raw_name.upper()
                
                # Skip kalau udah di-load
                if key in st.session_state.uploaded_files:
                    continue
                
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
                            for i in range(len(headers), len(df.columns)):
                                headers.append(f"Kolom_{i}")
                        
                        headers = make_unique_headers(headers)
                    else:
                        headers = [f"Kolom_{i}" for i in range(len(df.columns))]
                    
                    st.session_state.uploaded_files[key] = {
                        "df": df,
                        "headers": headers,
                        "file_name": file.name,
                        "matched_sheet": key
                    }
                    st.success(f"✅ {file.name}: {len(df)} baris, {len(df.columns)} kolom → Match: {key}")
                else:
                    st.warning(f"⚠️ {file.name}: Kosong atau tidak terbaca")
        
        st.rerun()

# ---- Tampilkan file yang sudah di-load ----
if st.session_state.uploaded_files:
    st.info(f"📁 {len(st.session_state.uploaded_files)} file sudah di-load")
    
    # ---- Pilih Kolom Kunci ----
    st.subheader("🔑 Pilih Kolom Kunci (CIF)")
    
    for key, info in st.session_state.uploaded_files.items():
        df = info["df"]
        headers = info["headers"]
        file_name = info["file_name"]
        
        if key not in st.session_state.selected_key:
            st.session_state.selected_key[key] = None
        
        st.write(f"**📋 {file_name}**")
        
        # Preview 3 baris
        preview_df = df.head(3).copy()
        preview_headers = headers[:len(preview_df.columns)]
        preview_headers = make_unique_headers(preview_headers)
        preview_df.columns = preview_headers
        st.dataframe(preview_df, use_container_width=True)
        
        col_options = {i: h for i, h in enumerate(headers)}
        
        # Cari default
        default_idx = 0
        for i, h in enumerate(headers):
            h_upper = h.upper()
            if "CUCODE" in h_upper or "CUSTOMER CODE" in h_upper or "CIF" in h_upper:
                default_idx = i
                break
        
        # Pake radio atau selectbox? Tetep pake selectbox tapi kecil
        selected_idx = st.selectbox(
            f"Pilih kolom kunci untuk {file_name}",
            options=list(col_options.keys()),
            format_func=lambda x: f"{x}: {col_options[x]}",
            index=default_idx,
            key=f"key_select_{key}"
        )
        st.session_state.selected_key[key] = selected_idx
        st.write("---")

# ---- Pilih Kolom yang Mau Dibawa (pake checkbox) ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    st.subheader("📋 Pilih Kolom yang Mau Digabung (Checkbox)")
    st.caption("💡 Centang kolom yang mau dibawa dari setiap file")
    
    # Cek apakah ada perubahan di selected_cols
    for key, info in st.session_state.uploaded_files.items():
        headers = info["headers"]
        file_name = info["file_name"]
        key_col = st.session_state.selected_key[key]
        
        st.write(f"**📋 {file_name}** (Kunci: {headers[key_col] if key_col < len(headers) else f'Kolom {key_col}'})")
        
        # Default: pilih key + 2 kolom pertama
        if key not in st.session_state.selected_cols:
            default_cols = [key_col]
            count = 0
            for i in range(len(headers)):
                if i != key_col and count < 2:
                    default_cols.append(i)
                    count += 1
            st.session_state.selected_cols[key] = default_cols
        
        # Render checkbox di columns
        selected = render_checkbox_columns(
            headers=headers,
            key_prefix=f"col_{key}",
            default_selected=st.session_state.selected_cols.get(key, [key_col])
        )
        st.session_state.selected_cols[key] = selected
        st.write("---")

# ---- Proses Gabung (dengan tombol) ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    # Cek apakah ada pilihan kolom yang dipilih
    has_selection = False
    for key in st.session_state.uploaded_files.keys():
        if key in st.session_state.selected_cols and len(st.session_state.selected_cols[key]) > 0:
            has_selection = True
            break
    
    if has_selection:
        if st.button("🚀 Gabungkan Data", use_container_width=True):
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
                    
                    # Ambil CIF dari file pertama (hanya 1 kolom CIF)
                    cif_col_name = "CIF"
                    result_headers.append(cif_col_name)
                    result_data[cif_col_name] = first_df[first_key_col].tolist()
                    
                    # Ambil kolom lain dari file pertama (kecuali CIF)
                    for col_idx in first_selected_cols:
                        if col_idx == first_key_col:
                            continue  # Skip CIF, udah diambil di atas
                        col_name = first_headers[col_idx] if col_idx < len(first_headers) else f"Kolom_{col_idx}"
                        final_name = f"{first_info['file_name']}_{col_name}"
                        result_headers.append(final_name)
                        result_data[final_name] = first_df[col_idx].tolist()
                    
                    # Tambah dari file lain (tanpa CIF)
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
                            if col_idx == key_col:
                                continue  # Skip CIF dari file lain
                            col_name = headers[col_idx] if col_idx < len(headers) else f"Kolom_{col_idx}"
                            final_name = f"{info['file_name']}_{col_name}"
                            result_headers.append(final_name)
                            other_data[final_name] = df[col_idx].tolist()
                        
                        result_keys = result_data[cif_col_name]
                        
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
    else:
        st.warning("⚠️ Pilih minimal 1 kolom dari setiap file untuk digabung")

# ---- Preview & Download ----
if st.session_state.processed_data is not None:
    st.subheader("📊 Preview Hasil Gabungan")
    st.dataframe(st.session_state.processed_data, use_container_width=True)
    st.caption(f"Total: {len(st.session_state.processed_data)} baris, {len(st.session_state.processed_data.columns)} kolom")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = io.BytesIO()
        st.session_state.processed_data.to_csv(csv_data, index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data.getvalue(),
            file_name="hasil_gabungan.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        try:
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                st.session_state.processed_data.to_excel(writer, sheet_name='Hasil', index=False)
            st.download_button(
                label="📥 Download Excel",
                data=excel_data.getvalue(),
                file_name="hasil_gabungan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except:
            st.info("Excel download tidak tersedia, gunakan CSV")

# ---- Reset ----
if st.button("🔄 Reset Semua", use_container_width=True):
    for key in list(st.session_state.keys()):
        st.session_state[key] = {} if key in ["uploaded_files", "selected_key", "selected_cols", "file_headers"] else None
    st.session_state.processed_data = None
    st.session_state.data_loaded = False
    st.rerun()
