import streamlit as st
import pandas as pd
import io
import re

# ============================================================
# 1. KONFIGURASI
# ============================================================
st.set_page_config(page_title="CIF Data Aggregator", layout="wide")
st.title("📊 CIF Data Aggregator")
st.write("Upload file .tab dari core banking untuk digabung datanya")

# ============================================================
# 2. BACA FILE
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
# 3. GET BEST VALUE
# ============================================================
def get_best_value(values, prefer_text=True):
    valid = []
    for v in values:
        v_str = str(v).strip()
        if v_str and v_str not in ["", "nan", "None", "-", "0", "0000", "NULL"]:
            valid.append(v_str)
    if not valid:
        return "-"
    if prefer_text:
        text_values = [v for v in valid if re.search(r'[A-Za-z]', str(v))]
        if text_values:
            return max(text_values, key=lambda x: len(str(x)))
        else:
            return str(valid[0])
    return str(valid[0])

# ============================================================
# 4. EKSTRAK M4CU
# ============================================================
def extract_m4cu(df):
    result = {}
    
    if df is None or df.empty:
        return result
    
    COL_CUCODE = 1
    COL_CUNAME = 2
    COL_CUFLTY = 31
    COL_ALAMAT = [4, 5, 6]
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"]:
            continue
        
        alamat = " ".join([str(row[i]).strip() for i in COL_ALAMAT if i < len(row) and str(row[i]).strip() not in ["", "nan"]])
        jenis = str(row[COL_CUFLTY]).strip() if len(row) > COL_CUFLTY else ""
        
        result[cif] = {
            "cif": cif,
            "nama": str(row[COL_CUNAME]).strip() if len(row) > COL_CUNAME else "-",
            "jenis_nasabah": jenis if jenis not in ["", "nan"] else "",
            "alamat": alamat if alamat else "-",
            "pekerjaan": "-",
            "tempat_lahir": "-",
            "tanggal_lahir": "-",
            "nik": "-",
            "jk": "-",
            "kewarganegaraan": "-",
            "status_kawin": "-",
            "nama_ibu": "-",
            "bo": "-",
            "sumber_dana": "-",
            "penghasilan": "-",
            "tujuan_usaha": "-",
            "alamat_lain": "-",
            "alamat_kantor": "-",
            "telp_kantor": "-",
            "no_izin": "-",
            "bidang_usaha": "-",
            "tempat_pendirian": "-",
            "tanggal_pendirian": "-",
            "bentuk_badan": "-"
        }
    
    return result

# ============================================================
# 5. EKSTRAK M4CUI - VERSI DENGAN DEBUG
# ============================================================
def extract_m4cui(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # TAMPILKAN DEBUG: 5 baris pertama + semua kolom
    st.write("🔍 DEBUG M4CUI:")
    st.write(f"Total baris: {len(df)}, Total kolom: {len(df.columns)}")
    
    # Tampilkan 3 baris pertama dari kolom yang penting
    sample_cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 19, 20, 30, 31, 44, 45, 46]
    sample_data = {}
    for col in sample_cols:
        if col < len(df.columns):
            sample_data[f"Kolom {col}"] = df[col].head(3).tolist()
    
    st.write("📌 Sample 3 baris pertama dari kolom penting:")
    st.json(sample_data)
    
    # Sekarang kita coba mapping berdasarkan data yang terlihat
    # Dari debug sebelumnya, kita tahu:
    # Kolom 1 = CUCODE
    # Kolom 2 = Nama (CUSHOR/CUNAME)
    # Kolom 5 = Tempat Lahir (CUPLBR)
    # Kolom 6 = Tanggal Lahir (CUDTLH)
    # Kolom 19 = NIK (CUIDNO)
    # Kolom 3 = JK (CUJEKL)
    # Kolom 7 = Status Kawin (CUMRST)
    # Kolom 45 = Sumber Dana (CUFRDN)
    # Kolom 44 = Penghasilan (CUINCM)
    # Kolom 46 = Tujuan (CUTOIC)
    
    COL_CUCODE = 1
    COL_CUSHOR = 2
    COL_CUPLBR = 5
    COL_CUDTLH = 6
    COL_CUIDNO = 19
    COL_CUJEKL = 3
    COL_CUMRST = 7
    COL_CUFRDN = 45
    COL_CUINCM = 44
    COL_CUTOIC = 46
    
    total_processed = 0
    total_found = 0
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"]:
            continue
        
        total_processed += 1
        
        if cif in existing_data:
            total_found += 1
            
            if len(row) > COL_CUSHOR:
                val = str(row[COL_CUSHOR]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["nama"] = get_best_value([existing_data[cif]["nama"], val])
            
            if len(row) > COL_CUPLBR:
                val = str(row[COL_CUPLBR]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["tempat_lahir"] = val
            
            if len(row) > COL_CUDTLH:
                val = str(row[COL_CUDTLH]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["tanggal_lahir"] = val
            
            if len(row) > COL_CUIDNO:
                val = str(row[COL_CUIDNO]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["nik"] = val
            
            if len(row) > COL_CUJEKL:
                val = str(row[COL_CUJEKL]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["jk"] = val
            
            if len(row) > COL_CUMRST:
                val = str(row[COL_CUMRST]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["status_kawin"] = val
            
            if len(row) > COL_CUFRDN:
                val = str(row[COL_CUFRDN]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["sumber_dana"] = val
            
            if len(row) > COL_CUINCM:
                val = str(row[COL_CUINCM]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["penghasilan"] = val
            
            if len(row) > COL_CUTOIC:
                val = str(row[COL_CUTOIC]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["tujuan_usaha"] = val
    
    st.write(f"✅ M4CUI: {total_processed} CIF diproses, {total_found} ditemukan di M4CU")
    
    return existing_data

# ============================================================
# 6. EKSTRAK M4CUAPU
# ============================================================
def extract_m4cuapu(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    cu_col = None
    for col in df.columns:
        col_clean = str(col).strip().upper()
        if col_clean in ["CUSTOMER CODE", "CUCODE"]:
            cu_col = col
            break
    
    if cu_col is None:
        return existing_data
    
    for _, row in df.iterrows():
        cif = str(row[cu_col]).strip()
        if not cif or cif in ["", "nan", "None"] or cif not in existing_data:
            continue
        
        for col in df.columns:
            col_clean = str(col).strip().upper()
            val = str(row[col]).strip()
            if val in ["", "nan"]:
                continue
            
            if "BENEFICIAL" in col_clean or "BO" in col_clean:
                existing_data[cif]["bo"] = val
            elif "SUMBER DANA" in col_clean:
                existing_data[cif]["sumber_dana"] = get_best_value([existing_data[cif]["sumber_dana"], val])
            elif "TUJUAN" in col_clean:
                existing_data[cif]["tujuan_usaha"] = get_best_value([existing_data[cif]["tujuan_usaha"], val])
            elif "PENGHASILAN" in col_clean or "RATA" in col_clean:
                existing_data[cif]["penghasilan"] = get_best_value([existing_data[cif]["penghasilan"], val])
            elif "BIDANG USAHA" in col_clean:
                existing_data[cif]["bidang_usaha"] = val
            elif "BENTUK USAHA" in col_clean:
                existing_data[cif]["bentuk_badan"] = val
            elif "IZIN" in col_clean or "IJIN" in col_clean:
                existing_data[cif]["no_izin"] = val
    
    return existing_data

# ============================================================
# 7. EKSTRAK M4CUC
# ============================================================
def extract_m4cuc(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    cu_col = None
    for col in df.columns:
        col_clean = str(col).strip().upper()
        if col_clean in ["CIF", "CUCODE", "CUSTOMER CODE"]:
            cu_col = col
            break
    
    if cu_col is None:
        return existing_data
    
    for _, row in df.iterrows():
        cif = str(row[cu_col]).strip()
        if not cif or cif in ["", "nan", "None"] or cif not in existing_data:
            continue
        
        for col in df.columns:
            col_clean = str(col).strip().upper()
            val = str(row[col]).strip()
            if val in ["", "nan"]:
                continue
            
            if "BIDANG USAHA" in col_clean:
                existing_data[cif]["bidang_usaha"] = get_best_value([existing_data[cif]["bidang_usaha"], val])
            elif "BENTUK USAHA" in col_clean:
                existing_data[cif]["bentuk_badan"] = get_best_value([existing_data[cif]["bentuk_badan"], val])
            elif "IZIN" in col_clean or "IJIN" in col_clean:
                existing_data[cif]["no_izin"] = get_best_value([existing_data[cif]["no_izin"], val])
            elif "TANGGAL BERDIRI" in col_clean:
                existing_data[cif]["tanggal_pendirian"] = val
    
    return existing_data

# ============================================================
# 8. GENERATE TEMPLATE
# ============================================================
def generate_template(data):
    perorangan_rows = []
    badan_usaha_rows = []
    
    for cif, d in data.items():
        jenis = d.get("jenis_nasabah", "").strip().upper()
        
        if jenis == "I":
            required_fields = ["nama", "nik", "alamat", "tempat_lahir", "tanggal_lahir", 
                              "pekerjaan", "jk", "status_kawin", "nama_ibu"]
            is_lengkap = all(d[f] != "-" for f in required_fields)
            
            row = {
                "Status": "✅ LENGKAP" if is_lengkap else "⚠️ TIDAK LENGKAP",
                "CIF": cif,
                "Nama Lengkap + Alias": d["nama"],
                "No Dokumen Identitas": d["nik"],
                "Alamat Tempat Tinggal (KTP)": d["alamat"],
                "Alamat Tempat Tinggal Lain": d["alamat_lain"],
                "Tempat dan Tanggal Lahir": f"{d['tempat_lahir']}, {d['tanggal_lahir']}".strip(", "),
                "Kewarganegaraan": d["kewarganegaraan"],
                "Pekerjaan": d["pekerjaan"],
                "Alamat & Telp Kantor": f"{d['alamat_kantor']}, {d['telp_kantor']}".strip(", "),
                "Jenis Kelamin": d["jk"],
                "Status Perkawinan": d["status_kawin"],
                "Nama Gadis Ibu Kandung": d["nama_ibu"],
                "Beneficial Owner": d["bo"],
                "Sumber Dana": d["sumber_dana"],
                "Penghasilan/Net Worth": d["penghasilan"],
                "Tujuan Hubungan Usaha": d["tujuan_usaha"],
                "Keterangan": "LENGKAP" if is_lengkap else "TIDAK LENGKAP"
            }
            
            fields = ["Nama", "NIK", "Alamat", "TTL", "Pekerjaan", "JK", "Status Kawin", "Nama Ibu", "BO", "Sumber Dana", "Penghasilan", "Tujuan"]
            field_values = [d["nama"], d["nik"], d["alamat"], f"{d['tempat_lahir']}{d['tanggal_lahir']}", 
                           d["pekerjaan"], d["jk"], d["status_kawin"], d["nama_ibu"], 
                           d["bo"], d["sumber_dana"], d["penghasilan"], d["tujuan_usaha"]]
            
            for f, v in zip(fields, field_values):
                row[f"✅ {f}"] = "✅" if v != "-" else "❌"
            
            perorangan_rows.append(row)
            
        else:
            required_fields = ["nama", "no_izin", "bidang_usaha", "alamat"]
            is_lengkap = all(d[f] != "-" for f in required_fields)
            
            row = {
                "Status": "✅ LENGKAP" if is_lengkap else "⚠️ TIDAK LENGKAP",
                "CIF": cif,
                "Nama Perusahaan": d["nama"],
                "No Izin Instansi": d["no_izin"],
                "Bidang Usaha": d["bidang_usaha"],
                "Alamat Kedudukan": d["alamat"],
                "Tempat & Tgl Pendirian": f"{d['tempat_pendirian']}, {d['tanggal_pendirian']}".strip(", "),
                "Bentuk Badan Hukum": d["bentuk_badan"],
                "Beneficial Owner": d["bo"],
                "Sumber Dana": d["sumber_dana"],
                "Penghasilan/Net Worth": d["penghasilan"],
                "Tujuan Hubungan Usaha": d["tujuan_usaha"],
                "Keterangan": "LENGKAP" if is_lengkap else "TIDAK LENGKAP"
            }
            
            fields = ["Nama Perush", "No Izin", "Bidang Usaha", "Alamat", "Tgl Pendirian", "Bentuk Hukum", "BO", "Sumber Dana", "Penghasilan", "Tujuan"]
            field_values = [d["nama"], d["no_izin"], d["bidang_usaha"], d["alamat"], 
                           f"{d['tempat_pendirian']}{d['tanggal_pendirian']}", d["bentuk_badan"], 
                           d["bo"], d["sumber_dana"], d["penghasilan"], d["tujuan_usaha"]]
            
            for f, v in zip(fields, field_values):
                row[f"✅ {f}"] = "✅" if v != "-" else "❌"
            
            badan_usaha_rows.append(row)
    
    df_perorangan = pd.DataFrame(perorangan_rows)
    df_badan_usaha = pd.DataFrame(badan_usaha_rows)
    
    return df_perorangan, df_badan_usaha

# ============================================================
# 9. DOWNLOAD EXCEL
# ============================================================
def to_excel_download(df1, df2):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Perorangan', index=False)
        df2.to_excel(writer, sheet_name='Badan Usaha', index=False)
    return output.getvalue()

# ============================================================
# 10. UI
# ============================================================
uploaded_files = st.file_uploader(
    "Upload file .tab", 
    accept_multiple_files=True, 
    type=["tab", "txt"]
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file berhasil diupload!")
    
    with st.spinner("⏳ Memproses data..."):
        all_files = {}
        
        for file in uploaded_files:
            try:
                df = parse_tab_file(file)
                if df is not None and not df.empty:
                    raw_name = file.name
                    if raw_name.endswith(".tab"):
                        raw_name = raw_name[:-4]
                    elif raw_name.endswith(".txt"):
                        raw_name = raw_name[:-4]
                    key = raw_name.upper()
                    if key in all_files:
                        counter = 2
                        while f"{key}_{counter}" in all_files:
                            counter += 1
                        key = f"{key}_{counter}"
                    all_files[key] = df
                    st.write(f"✅ {file.name}: {len(df)} baris, {len(df.columns)} kolom → key: {key}")
                else:
                    st.warning(f"⚠️ {file.name}: Kosong atau tidak terbaca")
            except Exception as e:
                st.warning(f"⚠️ Gagal baca {file.name}: {str(e)[:100]}")
                continue
        
        if not all_files:
            st.error("❌ Tidak ada data yang bisa diproses.")
            st.stop()
        
        st.write("📁 File keys:", list(all_files.keys()))
        
        data = {}
        
        # 1. M4CU
        m4cu_key = None
        for key in all_files.keys():
            if key == "M4CU":
                m4cu_key = key
                break
        if m4cu_key is None:
            for key in all_files.keys():
                if "M4CU" in key and "APU" not in key and "UI" not in key and "C" not in key and "G" not in key:
                    m4cu_key = key
                    break
        
        if m4cu_key:
            st.write(f"✅ Menggunakan M4CU dari key: {m4cu_key}")
            data = extract_m4cu(all_files[m4cu_key])
        else:
            st.error("❌ File M4CU tidak ditemukan!")
            st.stop()
        
        # 2. M4CUI
        for key in all_files.keys():
            if "M4CUI" in key:
                st.write(f"✅ Menambahkan data dari: {key}")
                data = extract_m4cui(all_files[key], data)
                break
        
        # 3. M4CUAPU
        for key in all_files.keys():
            if "M4CUAPU" in key:
                st.write(f"✅ Menambahkan data dari: {key}")
                data = extract_m4cuapu(all_files[key], data)
                break
        
        # 4. M4CUC
        for key in all_files.keys():
            if "M4CUC" in key:
                st.write(f"✅ Menambahkan data dari: {key}")
                data = extract_m4cuc(all_files[key], data)
                break
        
        if not data:
            st.error("❌ Tidak ada CIF ditemukan.")
            st.stop()
        
        df_perorangan, df_badan_usaha = generate_template(data)
    
    st.success(f"✅ Data berhasil diproses! {len(data)} CIF ditemukan")
    
    tab1, tab2 = st.tabs(["👤 Perorangan", "🏢 Badan Usaha"])
    
    with tab1:
        if not df_perorangan.empty:
            st.dataframe(df_perorangan, use_container_width=True)
            st.caption(f"Total Perorangan: {len(df_perorangan)}")
        else:
            st.info("Tidak ada data Perorangan")
    
    with tab2:
        if not df_badan_usaha.empty:
            st.dataframe(df_badan_usaha, use_container_width=True)
            st.caption(f"Total Badan Usaha: {len(df_badan_usaha)}")
        else:
            st.info("Tidak ada data Badan Usaha")
    
    if not df_perorangan.empty or not df_badan_usaha.empty:
        excel_data = to_excel_download(df_perorangan, df_badan_usaha)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="CIF_Data_Aggregator.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
