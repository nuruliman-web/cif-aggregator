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
# 4. EKSTRAK M4CU (BASE)
# ============================================================
def extract_m4cu(df):
    result = {}
    
    if df is None or df.empty:
        return result
    
    # MAPPING POSISI KOLOM M4CU (dari header)
    COL_CUCODE = 1      # Customer code
    COL_CUNAME = 2      # Customer Name
    COL_CUADR1 = 4      # Address-1
    COL_CUADR2 = 5      # Address-2
    COL_CUADR3 = 6      # City
    COL_CUFLTY = 31     # Customer type (I/C)
    COL_CUKRJA = 24     # Pekerjaan
    COL_CUJEKL = 25     # Jenis kelamin
    COL_CUDTLH = 26     # Birth date
    COL_CUNKTP = 27     # ID card number
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"]:
            continue
        
        alamat = " ".join([
            str(row[COL_CUADR1]).strip() if len(row) > COL_CUADR1 else "",
            str(row[COL_CUADR2]).strip() if len(row) > COL_CUADR2 else "",
            str(row[COL_CUADR3]).strip() if len(row) > COL_CUADR3 else ""
        ]).strip()
        
        jenis = str(row[COL_CUFLTY]).strip() if len(row) > COL_CUFLTY else ""
        
        result[cif] = {
            "cif": cif,
            "nama": str(row[COL_CUNAME]).strip() if len(row) > COL_CUNAME else "-",
            "jenis_nasabah": jenis if jenis not in ["", "nan"] else "",
            "alamat": alamat if alamat else "-",
            "pekerjaan": str(row[COL_CUKRJA]).strip() if len(row) > COL_CUKRJA and str(row[COL_CUKRJA]).strip() not in ["", "nan"] else "-",
            "jk": str(row[COL_CUJEKL]).strip() if len(row) > COL_CUJEKL and str(row[COL_CUJEKL]).strip() not in ["", "nan"] else "-",
            "tanggal_lahir": str(row[COL_CUDTLH]).strip() if len(row) > COL_CUDTLH and str(row[COL_CUDTLH]).strip() not in ["", "nan"] else "-",
            "nik": str(row[COL_CUNKTP]).strip() if len(row) > COL_CUNKTP and str(row[COL_CUNKTP]).strip() not in ["", "nan"] else "-",
            "tempat_lahir": "-",
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
            "bentuk_badan": "-",
            "kewarganegaraan": "-"
        }
    
    return result

# ============================================================
# 5. EKSTRAK M4CUI
# ============================================================
def extract_m4cui(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # MAPPING POSISI KOLOM M4CUI (dari header)
    COL_CUCODE = 1      # Customer code
    COL_CUNAME = 2      # Customer Name
    COL_CUSHOR = 11     # Short name
    COL_CUKRJA = 25     # Pekerjaan
    COL_CUJEKL = 26     # Jenis kelamin
    COL_CUDTLH = 27     # Birth date
    COL_CUNKTP = 28     # ID card number
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"]:
            continue
        
        if cif in existing_data:
            # Nama (prioritas CUNAME, fallback CUSHOR)
            if len(row) > COL_CUNAME:
                val = str(row[COL_CUNAME]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["nama"] = get_best_value([existing_data[cif]["nama"], val])
            
            if len(row) > COL_CUSHOR:
                val = str(row[COL_CUSHOR]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["nama"] = get_best_value([existing_data[cif]["nama"], val])
            
            # Pekerjaan
            if len(row) > COL_CUKRJA:
                val = str(row[COL_CUKRJA]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["pekerjaan"] = get_best_value([existing_data[cif]["pekerjaan"], val])
            
            # Jenis Kelamin
            if len(row) > COL_CUJEKL:
                val = str(row[COL_CUJEKL]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["jk"] = get_best_value([existing_data[cif]["jk"], val])
            
            # Tanggal Lahir
            if len(row) > COL_CUDTLH:
                val = str(row[COL_CUDTLH]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["tanggal_lahir"] = get_best_value([existing_data[cif]["tanggal_lahir"], val])
            
            # NIK
            if len(row) > COL_CUNKTP:
                val = str(row[COL_CUNKTP]).strip()
                if val not in ["", "nan"]:
                    existing_data[cif]["nik"] = get_best_value([existing_data[cif]["nik"], val])
    
    return existing_data

# ============================================================
# 6. EKSTRAK M4CUAPU
# ============================================================
def extract_m4cuapu(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # MAPPING POSISI KOLOM M4CUAPU (dari header)
    COL_CUCODE = 1
    COL_BO = 22
    COL_BONAME = 23
    COL_SUMBER_DANA = 33
    COL_TUJUAN = 35
    COL_JK = 41
    COL_TEMPAT_LAHIR = 43
    COL_TGL_LAHIR = 44
    COL_STATUS_KAWIN = 45
    COL_PENGHASILAN = 48
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"] or cif not in existing_data:
            continue
        
        # BO
        if len(row) > COL_BO:
            val = str(row[COL_BO]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["bo"] = val
        if len(row) > COL_BONAME:
            val = str(row[COL_BONAME]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["bo"] = get_best_value([existing_data[cif]["bo"], val])
        
        # Sumber Dana
        if len(row) > COL_SUMBER_DANA:
            val = str(row[COL_SUMBER_DANA]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["sumber_dana"] = get_best_value([existing_data[cif]["sumber_dana"], val])
        
        # Tujuan
        if len(row) > COL_TUJUAN:
            val = str(row[COL_TUJUAN]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["tujuan_usaha"] = get_best_value([existing_data[cif]["tujuan_usaha"], val])
        
        # JK (prioritas dari M4CUAPU)
        if len(row) > COL_JK:
            val = str(row[COL_JK]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["jk"] = get_best_value([existing_data[cif]["jk"], val])
        
        # Tempat Lahir
        if len(row) > COL_TEMPAT_LAHIR:
            val = str(row[COL_TEMPAT_LAHIR]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["tempat_lahir"] = val
        
        # Tgl Lahir (prioritas dari M4CUAPU)
        if len(row) > COL_TGL_LAHIR:
            val = str(row[COL_TGL_LAHIR]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["tanggal_lahir"] = get_best_value([existing_data[cif]["tanggal_lahir"], val])
        
        # Status Kawin
        if len(row) > COL_STATUS_KAWIN:
            val = str(row[COL_STATUS_KAWIN]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["status_kawin"] = val
        
        # Penghasilan
        if len(row) > COL_PENGHASILAN:
            val = str(row[COL_PENGHASILAN]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["penghasilan"] = get_best_value([existing_data[cif]["penghasilan"], val])
    
    return existing_data

# ============================================================
# 7. EKSTRAK M4CUC (Badan Usaha)
# ============================================================
def extract_m4cuc(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # MAPPING POSISI KOLOM M4CUC (dari header)
    COL_CIF = 0         # CIF
    COL_BENTUK = 1      # Bentuk Usaha
    COL_BIDANG = 2      # Bidang Usaha
    COL_NO_IZIN = 3     # Nomor Ijin Usaha
    COL_TGL_BERDIRI = 5 # Tanggal Berdiri
    COL_TUJUAN = 7      # Tujuan Hub
    COL_SUMBER = 8      # Sumber Dana
    
    for _, row in df.iterrows():
        cif = str(row[COL_CIF]).strip()
        if not cif or cif in ["", "nan", "None"] or cif not in existing_data:
            continue
        
        if len(row) > COL_BENTUK:
            val = str(row[COL_BENTUK]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["bentuk_badan"] = val
        
        if len(row) > COL_BIDANG:
            val = str(row[COL_BIDANG]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["bidang_usaha"] = val
        
        if len(row) > COL_NO_IZIN:
            val = str(row[COL_NO_IZIN]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["no_izin"] = val
        
        if len(row) > COL_TGL_BERDIRI:
            val = str(row[COL_TGL_BERDIRI]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["tanggal_pendirian"] = val
        
        if len(row) > COL_TUJUAN:
            val = str(row[COL_TUJUAN]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["tujuan_usaha"] = get_best_value([existing_data[cif]["tujuan_usaha"], val])
        
        if len(row) > COL_SUMBER:
            val = str(row[COL_SUMBER]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["sumber_dana"] = get_best_value([existing_data[cif]["sumber_dana"], val])
    
    return existing_data

# ============================================================
# 8. GENERATE TEMPLATE
# ============================================================
def generate_template(data):
    perorangan_rows = []
    badan_usaha_rows = []
    
    for cif, d in data.items():
        # Pastikan semua field ada
        default = {
            "nama": "-", "nik": "-", "alamat": "-", "alamat_lain": "-",
            "tempat_lahir": "-", "tanggal_lahir": "-", "kewarganegaraan": "-",
            "pekerjaan": "-", "alamat_kantor": "-", "telp_kantor": "-",
            "jk": "-", "status_kawin": "-", "nama_ibu": "-",
            "bo": "-", "sumber_dana": "-", "penghasilan": "-",
            "tujuan_usaha": "-", "no_izin": "-", "bidang_usaha": "-",
            "tempat_pendirian": "-", "tanggal_pendirian": "-", "bentuk_badan": "-",
            "jenis_nasabah": ""
        }
        
        for key in default:
            if key not in d:
                d[key] = default[key]
        
        jenis = d.get("jenis_nasabah", "").strip().upper()
        
        if jenis == "I":
            # PERORANGAN
            required_fields = ["nama", "nik", "alamat", "tempat_lahir", "tanggal_lahir", 
                              "pekerjaan", "jk", "status_kawin", "nama_ibu"]
            is_lengkap = all(d[f] != "-" for f in required_fields)
            
            row = {
                "Status": "✅ LENGKAP" if is_lengkap else "⚠️ TIDAK LENGKAP",
                "CIF": cif,
                "Nama Lengkap": d["nama"],
                "Nama Alias": "-",
                "No Dokumen Identitas": d["nik"],
                "Alamat Tempat Tinggal": d["alamat"],
                "Alamat Lain": d["alamat_lain"],
                "Tempat Lahir": d["tempat_lahir"],
                "Tanggal Lahir": d["tanggal_lahir"],
                "Kewarganegaraan": d["kewarganegaraan"],
                "Pekerjaan": d["pekerjaan"],
                "Alamat Kantor": d["alamat_kantor"],
                "Telp Kantor": d["telp_kantor"],
                "Jenis Kelamin": d["jk"],
                "Status Perkawinan": d["status_kawin"],
                "Nama Ibu Kandung": d["nama_ibu"],
                "Beneficial Owner": d["bo"],
                "Sumber Dana": d["sumber_dana"],
                "Penghasilan": d["penghasilan"],
                "Tujuan Hubungan Usaha": d["tujuan_usaha"],
                "Keterangan": "LENGKAP" if is_lengkap else "TIDAK LENGKAP"
            }
            
            perorangan_rows.append(row)
            
        else:
            # BADAN USAHA
            required_fields = ["nama", "no_izin", "bidang_usaha", "alamat"]
            is_lengkap = all(d[f] != "-" for f in required_fields)
            
            row = {
                "Status": "✅ LENGKAP" if is_lengkap else "⚠️ TIDAK LENGKAP",
                "CIF": cif,
                "Nama Perusahaan": d["nama"],
                "No Izin": d["no_izin"],
                "Bidang Usaha": d["bidang_usaha"],
                "Alamat": d["alamat"],
                "Tempat Pendirian": d["tempat_pendirian"],
                "Tanggal Pendirian": d["tanggal_pendirian"],
                "Bentuk Badan Hukum": d["bentuk_badan"],
                "Beneficial Owner": d["bo"],
                "Sumber Dana": d["sumber_dana"],
                "Penghasilan": d["penghasilan"],
                "Tujuan Hubungan Usaha": d["tujuan_usaha"],
                "Keterangan": "LENGKAP" if is_lengkap else "TIDAK LENGKAP"
            }
            
            badan_usaha_rows.append(row)
    
    df_perorangan = pd.DataFrame(perorangan_rows)
    df_badan_usaha = pd.DataFrame(badan_usaha_rows)
    
    return df_perorangan, df_badan_usaha

# ============================================================
# 9. DOWNLOAD CSV
# ============================================================
def to_csv_download(df1, df2):
    output = io.BytesIO()
    combined = pd.concat([df1, df2], ignore_index=True)
    combined.to_csv(output, index=False)
    return output.getvalue()

# ============================================================
# 10. UI UTAMA
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
        
        # 1. M4CU (BASE)
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
        csv_data = to_csv_download(df_perorangan, df_badan_usaha)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="CIF_Data_Aggregator.csv",
            mime="text/csv"
        )
