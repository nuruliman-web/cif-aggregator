import streamlit as st
import pandas as pd
import io
import re

# ============================================================
# 1. KONFIGURASI
# ============================================================
st.set_page_config(page_title="Visual Data Mapper", layout="wide")
st.title("📊 Visual Data Mapper")
st.write("Upload file .tab dan pilih kolom yang mau digabung")

# ============================================================
# 2. STATE MANAGEMENT (biar gak hilang pas reload)
# ============================================================
if "header_mapping" not in st.session_state:
    st.session_state.header_mapping = {}  # key: sheet_name, value: list of column names
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}  # key: file_key, value: dataframe
if "selected_key" not in st.session_state:
    st.session_state.selected_key = {}  # key: file_key, value: column_name
if "selected_cols" not in st.session_state:
    st.session_state.selected_cols = {}  # key: file_key, value: list of column names
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

# ============================================================
# 3. BACA FILE .tab (TANPA HEADER)
# ============================================================
def parse_tab_file(uploaded_file):
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file, 
            sep="\t", 
            encoding="latin-1", 
            on_bad_lines="skip",
            dtype=str,
            header=None
        )
        df = df.replace(r'^\s*$', '', regex=True)
        df = df.replace(r'^nan$', '', regex=True)
        df = df.replace(r'^None$', '', regex=True)
        return df
    except Exception as e:
        return None

# ============================================================
# 4. BACA HEADER EXCEL
# ============================================================
def load_header_excel(uploaded_file):
    """Baca semua sheet dari file header Excel"""
    try:
        xl = pd.ExcelFile(uploaded_file)
        mapping = {}
        
        for sheet_name in xl.sheet_names:
            if sheet_name.startswith("metadata.") or sheet_name in ["Sheet1", "Sheet2"]:
                continue
            
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)
            if df.empty:
                continue
            
            # Cari baris yang berisi header (biasanya baris ke-2 atau ke-3)
            header_row = None
            for idx in range(min(5, len(df))):
                row = df.iloc[idx].astype(str).tolist()
                # Cek apakah ada kata kunci seperti "Customer code" atau "CUCODE"
                for cell in row:
                    if isinstance(cell, str) and ("CUCODE" in cell.upper() or "CUSTOMER" in cell.upper() or "CODE" in cell.upper()):
                        header_row = idx
                        break
                if header_row is not None:
                    break
            
            if header_row is None:
                # Fallback: pake baris ke-2
                header_row = 1 if len(df) > 1 else 0
            
            # Ambil header
            headers = df.iloc[header_row].astype(str).tolist()
            # Bersihin
            headers = [str(h).strip() if str(h).strip() not in ["", "nan", "None"] else f"Kolom {i}" for i, h in enumerate(headers)]
            
            mapping[sheet_name.upper()] = headers
        
        return mapping
    except Exception as e:
        st.error(f"❌ Gagal baca header: {str(e)}")
        return {}

# ============================================================
# 5. MATCH FILE .tab DENGAN HEADER
# ============================================================
def match_header(file_key, header_mapping):
    """Cocokkan nama file dengan sheet header"""
    # Coba exact match
    if file_key in header_mapping:
        return file_key
    
    # Coba case insensitive
    for sheet in header_mapping.keys():
        if sheet.upper() == file_key.upper():
            return sheet
    
    # Coba partial match
    for sheet in header_mapping.keys():
        if file_key.upper() in sheet.upper() or sheet.upper() in file_key.upper():
            return sheet
    
    return None

# ============================================================
# 6. UI UTAMA
# ============================================================

# ---- STEP 1: Upload Header ----
st.subheader("📄 Step 1: Upload File Header (Excel)")
header_file = st.file_uploader(
    "Upload file Excel yang berisi semua header",
    type=["xlsx", "xls"],
    key="header_uploader"
)

if header_file:
    with st.spinner("⏳ Membaca header..."):
        header_mapping = load_header_excel(header_file)
        if header_mapping:
            st.session_state.header_mapping = header_mapping
            st.success(f"✅ Header berhasil dimuat! {len(header_mapping)} sheet ditemukan")
            
            # Tampilkan daftar sheet
            st.write("📋 Sheet yang tersedia:")
            for sheet, cols in header_mapping.items():
                st.write(f"  - {sheet}: {len(cols)} kolom")
        else:
            st.error("❌ Gagal membaca header")

# ---- STEP 2: Upload Data ----
if st.session_state.header_mapping:
    st.subheader("📁 Step 2: Upload File Data (.tab)")
    data_files = st.file_uploader(
        "Upload file .tab",
        accept_multiple_files=True,
        type=["tab", "txt"],
        key="data_uploader"
    )
    
    if data_files:
        with st.spinner("⏳ Membaca file data..."):
            for file in data_files:
                raw_name = file.name
                if raw_name.endswith(".tab"):
                    raw_name = raw_name[:-4]
                elif raw_name.endswith(".txt"):
                    raw_name = raw_name[:-4]
                key = raw_name.upper()
                
                df = parse_tab_file(file)
                if df is not None and not df.empty:
                    # Match dengan header
                    matched_sheet = match_header(key, st.session_state.header_mapping)
                    
                    if matched_sheet:
                        headers = st.session_state.header_mapping[matched_sheet]
                        # Potong atau tambah header sesuai jumlah kolom
                        if len(headers) > len(df.columns):
                            headers = headers[:len(df.columns)]
                        elif len(headers) < len(df.columns):
                            headers = headers + [f"Kolom {i}" for i in range(len(headers), len(df.columns))]
                        
                        st.session_state.uploaded_files[key] = {
                            "df": df,
                            "headers": headers,
                            "matched_sheet": matched_sheet,
                            "file_name": file.name
                        }
                    else:
                        # Tidak match, pake header default
                        headers = [f"Kolom {i}" for i in range(len(df.columns))]
                        st.session_state.uploaded_files[key] = {
                            "df": df,
                            "headers": headers,
                            "matched_sheet": None,
                            "file_name": file.name
                        }
                    st.success(f"✅ {file.name}: {len(df)} baris, {len(df.columns)} kolom → Match: {matched_sheet or 'Tidak ada'}")
                else:
                    st.warning(f"⚠️ {file.name}: Kosong atau tidak terbaca")

# ---- STEP 3: Pilih Kolom ----
if st.session_state.uploaded_files:
    st.subheader("🔑 Step 3: Pilih Kolom Kunci (CIF)")
    st.info("💡 Pilih 1 kolom yang berisi CIF/Nomor Nasabah untuk setiap file")
    
    # Pilih key untuk setiap file
    for key, info in st.session_state.uploaded_files.items():
        df = info["df"]
        headers = info["headers"]
        file_name = info["file_name"]
        
        # Inisialisasi key jika belum ada
        if key not in st.session_state.selected_key:
            st.session_state.selected_key[key] = None
        
        st.write(f"**📋 {file_name}** ({len(headers)} kolom)")
        
        # Tampilkan preview 3 baris pertama
        preview_df = df.head(3).copy()
        # Ganti header sementara
        preview_df.columns = headers[:len(preview_df.columns)]
        st.dataframe(preview_df, use_container_width=True)
        
        # Pilih kolom key
        col_options = {f"{i}: {h}" : i for i, h in enumerate(headers)}
        default_idx = None
        for i, h in enumerate(headers):
            if "CUCODE" in h.upper() or "CUSTOMER CODE" in h.upper() or "CIF" in h.upper():
                default_idx = i
                break
        
        selected_label = st.selectbox(
            f"Pilih kolom kunci untuk {file_name}",
            options=list(col_options.keys()),
            index=default_idx if default_idx is not None else 0,
            key=f"key_select_{key}"
        )
        st.session_state.selected_key[key] = col_options[selected_label]
        
        st.write("---")

# ---- STEP 4: Pilih Kolom yang Mau Dibawa ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    st.subheader("📋 Step 4: Pilih Kolom yang Mau Digabung")
    st.info("💡 Pilih kolom mana aja yang mau dibawa dari setiap file")
    
    for key, info in st.session_state.uploaded_files.items():
        df = info["df"]
        headers = info["headers"]
        file_name = info["file_name"]
        key_col = st.session_state.selected_key[key]
        key_header = headers[key_col] if key_col < len(headers) else f"Kolom {key_col}"
        
        st.write(f"**📋 {file_name}** (Kunci: {key_header})")
        
        # Inisialisasi selected_cols
        if key not in st.session_state.selected_cols:
            # Default: pilih key + 3 kolom pertama
            st.session_state.selected_cols[key] = [key_col]
            # Tambahkan 3 kolom pertama yang bukan key
            count = 0
            for i in range(len(headers)):
                if i != key_col and count < 3:
                    st.session_state.selected_cols[key].append(i)
                    count += 1
        
        # Multi-select untuk kolom
        col_options = {i: f"{i}: {h}" for i, h in enumerate(headers)}
        default_selected = st.session_state.selected_cols.get(key, [key_col])
        
        selected = st.multiselect(
            f"Pilih kolom dari {file_name}",
            options=list(col_options.keys()),
            format_func=lambda x: col_options[x],
            default=default_selected,
            key=f"col_select_{key}"
        )
        st.session_state.selected_cols[key] = selected
        
        st.write("---")

# ---- STEP 5: Proses Gabung ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    if st.button("🚀 Gabungkan Data"):
        with st.spinner("⏳ Memproses..."):
            try:
                # Ambil key dari file pertama sebagai base
                first_key = list(st.session_state.uploaded_files.keys())[0]
                first_info = st.session_state.uploaded_files[first_key]
                first_df = first_info["df"]
                first_key_col = st.session_state.selected_key[first_key]
                first_selected_cols = st.session_state.selected_cols[first_key]
                first_headers = first_info["headers"]
                
                # Buat dataframe hasil dari file pertama
                result_data = {}
                result_headers = []
                
                # Ambil data dari file pertama
                for col_idx in first_selected_cols:
                    col_name = first_headers[col_idx] if col_idx < len(first_headers) else f"Kolom {col_idx}"
                    result_headers.append(col_name)
                    result_data[col_name] = first_df[col_idx].tolist()
                
                # Tambahkan data dari file lain
                for key, info in st.session_state.uploaded_files.items():
                    if key == first_key:
                        continue
                    
                    df = info["df"]
                    key_col = st.session_state.selected_key[key]
                    selected_cols = st.session_state.selected_cols[key]
                    headers = info["headers"]
                    
                    # Buat mapping key dari file lain
                    other_keys = df[key_col].tolist()
                    # Buat dictionary untuk quick lookup
                    other_data = {}
                    for col_idx in selected_cols:
                        col_name = headers[col_idx] if col_idx < len(headers) else f"Kolom {col_idx}"
                        # Pastikan nama kolom unik (tambah prefix)
                        final_name = f"{info['file_name']}_{col_name}"
                        result_headers.append(final_name)
                        other_data[final_name] = df[col_idx].tolist()
                    
                    # Gabung dengan hasil (match berdasarkan key)
                    # Ambil key dari result
                    result_keys = result_data[result_headers[0]]  # Key dari file pertama
                    # Buat mapping key → data
                    for i, row_key in enumerate(result_keys):
                        # Cari di file lain
                        for j, other_key in enumerate(other_keys):
                            if str(row_key).strip() == str(other_key).strip():
                                for col_name, col_data in other_data.items():
                                    if col_name not in result_data:
                                        result_data[col_name] = []
                                    # Tambahkan data di posisi i
                                    while len(result_data[col_name]) < i:
                                        result_data[col_name].append("-")
                                    result_data[col_name].append(col_data[j])
                                break
                        # Kalau gak ketemu, isi dengan "-"
                        for col_name in other_data.keys():
                            if col_name not in result_data:
                                result_data[col_name] = []
                            while len(result_data[col_name]) < i + 1:
                                result_data[col_name].append("-")
                
                # Buat dataframe
                result_df = pd.DataFrame(result_data)
                st.session_state.processed_data = result_df
                
                st.success(f"✅ Data berhasil digabung! {len(result_df)} baris, {len(result_df.columns)} kolom")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ---- STEP 6: Preview & Download ----
if st.session_state.processed_data is not None:
    st.subheader("📊 Preview Hasil Gabungan")
    st.dataframe(st.session_state.processed_data, use_container_width=True)
    st.caption(f"Total: {len(st.session_state.processed_data)} baris, {len(st.session_state.processed_data.columns)} kolom")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download CSV
        csv_data = io.BytesIO()
        st.session_state.processed_data.to_csv(csv_data, index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data.getvalue(),
            file_name="hasil_gabungan.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download Excel (coba pake xlsxwriter)
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
        except Exception as e:
            st.warning(f"Excel download tidak tersedia (xlsxwriter error), gunakan CSV")

# ---- Reset ----
if st.button("🔄 Reset Semua"):
    for key in list(st.session_state.keys()):
        st.session_state[key] = None if key not in ["header_mapping"] else st.session_state.header_mapping
    st.rerun()
