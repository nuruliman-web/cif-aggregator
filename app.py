import streamlit as st
import pandas as pd
import io
import re

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(page_title="CIF Data Aggregator", layout="wide")

st.title("📊 CIF Data Aggregator")
st.write("Upload file .tab dari core banking untuk digabung datanya")

# ============================================================
# 2. FUNGSI BACA FILE .tab (TAB-DELIMITED)
# ============================================================
def parse_tab_file(uploaded_file):
    """Baca file .tab yang berformat TAB-delimited"""
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file, 
            sep="\t", 
            encoding="latin-1", 
            on_bad_lines="skip",
            dtype=str
        )
        df = df.replace(r'^\s*$', '', regex=True)
        df = df.replace(r'^nan$', '', regex=True)
        df = df.replace(r'^None$', '', regex=True)
        return df
    except Exception as e:
        return None

# ============================================================
# 3. FUNGSI CARI KOLOM
# ============================================================
def find_column(df, possible_names):
    """Cari kolom di dataframe berdasarkan kemungkinan nama"""
    if df is None or df.empty:
        return None
    for col in df.columns:
        col_clean = col.strip().upper()
        for name in possible_names:
            if col_clean == name.upper():
                return col
            if name.upper() in col_clean:
                return col
    return None

# ============================================================
# 4. FUNGSI GET BEST VALUE
# ============================================================
def get_best_value(values, prefer_text=True):
    """Pilih nilai terbaik dari beberapa sumber"""
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
    else:
        return str(valid[0])

# ============================================================
# 5. FUNGSI EKSTRAK DATA PER CIF
# ============================================================
def extract_cif_data(all_files):
    """Ekstrak data per CIF dari semua file yang diupload"""
    result = {}
    
    # Debug: tampilkan nama file yang tersedia
    st.write("📁 File yang terdeteksi:", list(all_files.keys()))
    
    # ============================================================
    # 5a. AMBIL BASE DARI M4CU
    # ============================================================
    m4cu = None
    for key in all_files.keys():
        if "M4CU" in key.upper():
            m4cu = all_files[key]
            st.write(f"✅ M4CU ditemukan di key: {key}")
            break
    
    if m4cu is None or m4cu.empty:
        st.error("❌ File M4CU tidak ditemukan!")
        return result
    
    cu_col = find_column(m4cu, ["CUCODE", "CUSTOMER CODE"])
    name_col = find_column(m4cu, ["CUNAME", "CUSTOMER NAME"])
    type_col = find_column(m4cu, ["CUFLTY", "CUSTOMER TYPE"])
    
    addr_cols = []
    for col in m4cu.columns:
        col_clean = col.strip().upper()
        if col_clean.startswith("CUADR") or "ADDRESS" in col_clean:
            addr_cols.append(col)
    
    if cu_col is None:
        st.error("❌ Kolom CUCODE tidak ditemukan di M4CU!")
        st.write("Kolom yang tersedia:", list(m4cu.columns))
        return result
    
    st.write(f"✅ Kolom CUCODE: {cu_col}")
    st.write(f"✅ Kolom CUNAME: {name_col}")
    st.write(f"✅ Kolom CUFLTY: {type_col}")
    
    for _, row in m4cu.iterrows():
        cif = str(row[cu_col]).strip()
        if not cif or cif in ["", "nan", "None"]:
            continue
            
        alamat = " ".join([str(row[c]).strip() for c in addr_cols if str(row[c]).strip() not in ["", "nan"]])
        
        result[cif] = {
            "sources": ["M4CU"],
            "cif": cif,
            "nama": get_best_value([row[name_col]] if name_col else ["-"]),
            "jenis_nasabah": str(row[type_col]).strip() if type_col and str(row[type_col]).strip() not in ["", "nan"] else "",
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
    
    # ============================================================
    # 5b. TAMBAH DATA DARI M4CUI
    # ============================================================
    m4cui = None
    for key in all_files.keys():
        if "M4CUI" in key.upper():
            m4cui = all_files[key]
            break
    
    if m4cui is not None and not m4cui.empty:
        cu_col = find_column(m4cui, ["CUCODE", "CUSTOMER CODE"])
        if cu_col is not None:
            for _, row in m4cui.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
                    continue
                
                for col, field in [
                    ("CUSHOR", "nama"),
                    ("CUPLBR", "tempat_lahir"),
                    ("CUDTLH", "tanggal_lahir"),
                    ("CUIDNO", "nik"),
                    ("CUJEKL", "jk"),
                    ("CUCTZC", "kewarganegaraan"),
                    ("CUMRST", "status_kawin"),
                    ("CUIKRJ", "pekerjaan"),
                    ("CUFRDN", "sumber_dana"),
                    ("CUINCM", "penghasilan"),
                    ("CUTOIC", "tujuan_usaha")
                ]:
                    if col in row:
                        val = str(row[col]).strip()
                        if val not in ["", "nan"]:
                            result[cif][field] = get_best_value([result[cif][field], val])
    
    # ============================================================
    # 5c. TAMBAH DATA DARI M4CUAPU
    # ============================================================
    m4cuapu = None
    for key in all_files.keys():
        if "M4CUAPU" in key.upper():
            m4cuapu = all_files[key]
            break
    
    if m4cuapu is not None and not m4cuapu.empty:
        cu_col = find_column(m4cuapu, ["CUSTOMER CODE", "CUCODE"])
        if cu_col is not None:
            for _, row in m4cuapu.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
                    continue
                
                bo_col = find_column(m4cuapu, ["Beneficiary Owner", "BO"])
                if bo_col is not None:
                    val = str(row[bo_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bo"] = val
                
                sd_col = find_column(m4cuapu, ["Sumber Dana"])
                if sd_col is not None:
                    val = str(row[sd_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["sumber_dana"] = get_best_value([result[cif]["sumber_dana"], val])
                
                tuj_col = find_column(m4cuapu, ["Tujuan Penggunaan Dana", "Tujuan Dana"])
                if tuj_col is not None:
                    val = str(row[tuj_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["tujuan_usaha"] = get_best_value([result[cif]["tujuan_usaha"], val])
                
                ph_col = find_column(m4cuapu, ["Rata-Rata Penghasilan", "Penghasilan"])
                if ph_col is not None:
                    val = str(row[ph_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["penghasilan"] = get_best_value([result[cif]["penghasilan"], val])
                
                bu_col = find_column(m4cuapu, ["Bidang Usaha"])
                if bu_col is not None:
                    val = str(row[bu_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bidang_usaha"] = val
                
                be_col = find_column(m4cuapu, ["Bentuk Usaha"])
                if be_col is not None:
                    val = str(row[be_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bentuk_badan"] = val
                
                izin_col = find_column(m4cuapu, ["No. Izin Usaha", "Nomor Izin Usaha"])
                if izin_col is not None:
                    val = str(row[izin_col]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["no_izin"] = val
    
    # ============================================================
    # 5d. TAMBAH DATA DARI M4CUC
    # ============================================================
    m4cuc = None
    for key in all_files.keys():
        if "M4CUC" in key.upper():
            m4cuc = all_files[key]
            break
    
    if m4cuc is not None and not m4cuc.empty:
        cu_col = find_column(m4cuc, ["CIF", "CUCODE", "CUSTOMER CODE"])
        if cu_col is not None:
            for _, row in m4cuc.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
                    continue
                
                if "Bidang Usaha" in row:
                    val = str(row["Bidang Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bidang_usaha"] = get_best_value([result[cif]["bidang_usaha"], val])
                
                if "Bentuk Usaha" in row:
                    val = str(row["Bentuk Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bentuk_badan"] = get_best_value([result[cif]["bentuk_badan"], val])
                
                if "Nomor Ijin Usaha" in row:
                    val = str(row["Nomor Ijin Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["no_izin"] = get_best_value([result[cif]["no_izin"], val])
                
                if "Tanggal Berdiri" in row:
                    val = str(row["Tanggal Berdiri"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["tanggal_pendirian"] = val
    
    return result

# ============================================================
# 6. FUNGSI GENERATE TEMPLATE
# ============================================================
def generate_template(data):
    """Generate 2 sheet: Perorangan dan Badan Usaha"""
    
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
# 7. FUNGSI DOWNLOAD EXCEL
# ============================================================
def to_excel_download(df1, df2):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Perorangan', index=False)
        df2.to_excel(writer, sheet_name='Badan Usaha', index=False)
    return output.getvalue()

# ============================================================
# 8. UI UTAMA
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
                    # Ambil nama file tanpa ekstensi
                    raw_name = file.name
                    if raw_name.endswith(".tab"):
                        raw_name = raw_name[:-4]
                    elif raw_name.endswith(".txt"):
                        raw_name = raw_name[:-4]
                    key = raw_name.upper()
                    all_files[key] = df
                    st.write(f"✅ {file.name}: {len(df)} baris, {len(df.columns)} kolom")
                else:
                    st.warning(f"⚠️ {file.name}: Kosong atau tidak terbaca")
            except Exception as e:
                st.warning(f"⚠️ Gagal baca {file.name}: {str(e)[:100]}")
                continue
        
        if not all_files:
            st.error("❌ Tidak ada data yang bisa diproses.")
            st.stop()
        
        # Ekstrak data per CIF
        data = extract_cif_data(all_files)
        
        if not data:
            st.error("❌ Tidak ada CIF ditemukan. Pastikan file M4CU ada.")
            st.stop()
        
        # Generate template
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
