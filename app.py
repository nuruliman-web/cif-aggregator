# app.py
import streamlit as st
import pandas as pd
import io
import time

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
if "show_column_selector" not in st.session_state:
    st.session_state.show_column_selector = False

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

# ---- OTOMATIS LOAD DATA KALAU ADA FILE BARU ----
if data_files:
    # Cek apakah ada file baru yang belum di-load
    new_files = False
    for file in data_files:
        raw_name = file.name
        if raw_name.endswith(".tab"):
            raw_name = raw_name[:-4]
        elif raw_name.endswith(".txt"):
            raw_name = raw_name[:-4]
        key = raw_name.upper()
        if key not in st.session_state.uploaded_files:
            new_files = True
            break
    
    if new_files:
        with st.spinner("⏳ Membaca file..."):
            for file in data_files:
                raw_name = file.name
                if raw_name.endswith(".tab"):
                    raw_name = raw_name[:-4]
                elif raw_name.endswith(".txt"):
                    raw_name = raw_name[:-4]
                key = raw_name.upper()
                
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
                    st.session_state.show_column_selector = True

# ---- Tampilkan status file yang sudah di-load ----
if st.session_state.uploaded_files:
    st.info(f"📁 {len(st.session_state.uploaded_files)} file sudah di-load")
    
    # Tampilkan ringkasan file
    for key, info in st.session_state.uploaded_files.items():
        st.write(f"  ✅ {info['file_name']}: {len(info['df'])} baris, {len(info['headers'])} kolom")

# ---- Pilih Kolom Kunci ----
if st.session_state.show_column_selector and st.session_state.uploaded_files:
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
        
        selected_idx = st.selectbox(
            f"Pilih kolom kunci untuk {file_name}",
            options=list(col_options.keys()),
            format_func=lambda x: f"{x}: {col_options[x]}",
            index=default_idx,
            key=f"key_select_{key}"
        )
        st.session_state.selected_key[key] = selected_idx
        st.write("---")

# ---- Pilih Kolom yang Mau Dibawa (pake form biar gak reload tiap klik) ----
if st.session_state.show_column_selector and st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    st.subheader("📋 Pilih Kolom yang Mau Digabung")
    st.caption("💡 Centang kolom yang mau dibawa dari setiap file")
    
    # Gunakan form biar gak reload tiap kali checkbox diclick
    with st.form(key="column_selection_form"):
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
            
            # Render checkbox di columns (4 kolom)
            cols = st.columns(4)
            for i, h in enumerate(headers):
                col_idx = i % 4
                is_checked = i in st.session_state.selected_cols.get(key, [key_col])
                with cols[col_idx]:
                    st.checkbox(
                        f"{i}: {h[:20]}..." if len(h) > 20 else f"{i}: {h}",
                        value=is_checked,
                        key=f"form_{key}_cb_{i}"
                    )
            st.write("---")
        
        # Submit button dengan notifikasi
        submitted = st.form_submit_button("💾 Simpan Pilihan Kolom", use_container_width=True, type="primary")
        
        if submitted:
            try:
                # Simpan pilihan
                for key in st.session_state.uploaded_files.keys():
                    selected = []
                    for i in range(len(st.session_state.uploaded_files[key]["headers"])):
                        if st.session_state.get(f"form_{key}_cb_{i}", False):
                            selected.append(i)
                    st.session_state.selected_cols[key] = selected
                
                st.success("✅ Pilihan kolom berhasil disimpan!")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal menyimpan: {str(e)}")

# ---- Proses Gabung dengan Progress Bar ----
if st.session_state.show_column_selector and st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    # Cek apakah ada pilihan kolom yang dipilih
    has_selection = False
    for key in st.session_state.uploaded_files.keys():
        if key in st.session_state.selected_cols and len(st.session_state.selected_cols[key]) > 0:
            has_selection = True
            break
    
    if has_selection:
        if st.button("🚀 Gabungkan Data", use_container_width=True, type="primary"):
            try:
                # --- PROGRESS BAR ---
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                first_key = list(st.session_state.uploaded_files.keys())[0]
                first_info = st.session_state.uploaded_files[first_key]
                first_df = first_info["df"]
                first_key_col = st.session_state.selected_key[first_key]
                first_selected_cols = st.session_state.selected_cols[first_key]
                first_headers = first_info["headers"]
                
                status_text.text("🔄 Membuat data awal...")
                progress_bar.progress(10)
                time.sleep(0.2)
                
                result_data = {}
                result_headers = []
                
                # Ambil CIF dari file pertama (hanya 1 kolom CIF)
                cif_col_name = "CIF"
                result_headers.append(cif_col_name)
                result_data[cif_col_name] = first_df[first_key_col].tolist()
                
                # Ambil kolom lain dari file pertama (kecuali CIF)
                for col_idx in first_selected_cols:
                    if col_idx == first_key_col:
                        continue
                    col_name = first_headers[col_idx] if col_idx < len(first_headers) else f"Kolom_{col_idx}"
                    final_name = f"{first_info['file_name']}_{col_name}"
                    result_headers.append(final_name)
                    result_data[final_name] = first_df[col_idx].tolist()
                
                status_text.text("🔄 Menambahkan data dari file lain...")
                progress_bar.progress(30)
                time.sleep(0.2)
                
                # Tambah dari file lain (tanpa CIF)
                other_files = [k for k in st.session_state.uploaded_files.keys() if k != first_key]
                total_other = len(other_files)
                
                for idx, key in enumerate(other_files):
                    info = st.session_state.uploaded_files[key]
                    df = info["df"]
                    key_col = st.session_state.selected_key[key]
                    selected_cols = st.session_state.selected_cols[key]
                    headers = info["headers"]
                    
                    status_text.text(f"🔄 Memproses {info['file_name']}... ({idx+1}/{total_other})")
                    progress_bar.progress(30 + int((idx + 1) / total_other * 50))
                    
                    other_keys = df[key_col].tolist()
                    other_data = {}
                    
                    for col_idx in selected_cols:
                        if col_idx == key_col:
                            continue
                        col_name = headers[col_idx] if col_idx < len(headers) else f"Kolom_{col_idx}"
                        final_name = f"{info['file_name']}_{col_name}"
                        result_headers.append(final_name)
                        other_data[final_name] = df[col_idx].tolist()
                    
                    result_keys = result_data[cif_col_name]
                    
                    # Match data
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
                    
                    time.sleep(0.1)
                
                status_text.text("🔄 Membuat DataFrame akhir...")
                progress_bar.progress(90)
                time.sleep(0.2)
                
                result_df = pd.DataFrame(result_data)
                st.session_state.processed_data = result_df
                
                progress_bar.progress(100)
                status_text.text("✅ Selesai!")
                time.sleep(0.3)
                
                st.success(f"✅ Data berhasil digabung! {len(result_df)} baris, {len(result_df.columns)} kolom")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Pilih minimal 1 kolom dari setiap file untuk digabung")

# ---- Preview & Download ----
if st.session_state.processed_data is not None:
    st.subheader("📊 Preview Hasil Gabungan")
    
    # Bersihin header hasil gabungan pake alias
    from utils import clean_headers
    cleaned_columns = clean_headers(st.session_state.processed_data.columns.tolist())
    st.session_state.processed_data.columns = cleaned_columns
    
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
        except Exception as e:
            st.info("💡 Excel download tidak tersedia, gunakan CSV")


# ---- Reset ----
if st.button("🔄 Reset Semua", use_container_width=True):
    for key in list(st.session_state.keys()):
        if key not in ["header_mapping"]:
            st.session_state[key] = {} if key in ["uploaded_files", "selected_key", "selected_cols"] else None
    st.session_state.processed_data = None
    st.session_state.show_column_selector = False
    st.rerun()
