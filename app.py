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
    COL_CUIDCO = 16     # Pekerjaan (Industry Code)  ✅ dari lo
    COL_CUJEKL = 25     # Jenis kelamin
    COL_CUDTLH = 26     # Birth date
    COL_CUNKTP = 27     # ID card number
    COL_CUNECO = 29     # Kewarganegaraan (Country) ✅ dari lo
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"]:
            continue
        
        alamat = " ".join([
            str(row[COL_CUADR1]).strip() if len(row) > COL_CUADR1 and str(row[COL_CUADR1]).strip() not in ["", "nan"] else "",
            str(row[COL_CUADR2]).strip() if len(row) > COL_CUADR2 and str(row[COL_CUADR2]).strip() not in ["", "nan"] else "",
            str(row[COL_CUADR3]).strip() if len(row) > COL_CUADR3 and str(row[COL_CUADR3]).strip() not in ["", "nan"] else ""
        ]).strip()
        
        jenis = str(row[COL_CUFLTY]).strip() if len(row) > COL_CUFLTY else ""
        
        result[cif] = {
            "cif": cif,
            "nama_m4cu": str(row[COL_CUNAME]).strip() if len(row) > COL_CUNAME and str(row[COL_CUNAME]).strip() not in ["", "nan"] else "-",
            "alamat_m4cu": alamat if alamat else "-",
            "pekerjaan_m4cu": str(row[COL_CUIDCO]).strip() if len(row) > COL_CUIDCO and str(row[COL_CUIDCO]).strip() not in ["", "nan"] else "-",
            "kewarganegaraan_m4cu": str(row[COL_CUNECO]).strip() if len(row) > COL_CUNECO and str(row[COL_CUNECO]).strip() not in ["", "nan"] else "-",
            "jk_m4cu": str(row[COL_CUJEKL]).strip() if len(row) > COL_CUJEKL and str(row[COL_CUJEKL]).strip() not in ["", "nan"] else "-",
            "tanggal_lahir_m4cu": str(row[COL_CUDTLH]).strip() if len(row) > COL_CUDTLH and str(row[COL_CUDTLH]).strip() not in ["", "nan"] else "-",
            "nik_m4cu": str(row[COL_CUNKTP]).strip() if len(row) > COL_CUNKTP and str(row[COL_CUNKTP]).strip() not in ["", "nan"] else "-",
            "jenis_nasabah": jenis if jenis not in ["", "nan"] else "",
            # Default values
            "nama": "-",
            "alamat": "-",
            "pekerjaan": "-",
            "kewarganegaraan": "-",
            "jk": "-",
            "tanggal_lahir": "-",
            "nik": "-",
            "tempat_lahir": "-",
            "status_kawin": "-",
            "nama_ibu": "-",
            "bo": "-",
            "sumber_dana": "-",
            "penghasilan": "-",
            "tujuan_usaha": "-",
            "alamat_kantor": "-",
            "telp_kantor": "-",
            "no_izin": "-",
            "bidang_usaha": "-",
            "tempat_pendirian": "-",
            "tanggal_pendirian": "-",
            "bentuk_badan": "-",
            "alamat_lain": "-"
        }
    
    return result

# ============================================================
# 5. EKSTRAK M4CUI (PELENGKAP)
# ============================================================
def extract_m4cui(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # MAPPING POSISI KOLOM M4CUI (dari header)
    # CUCODE di kolom 0, CUSHOR di 2, CUPLBR di 5, CUDTLH di 6, CUMRST di 7,
    # CUIDNO di 19, CUINCM di 44, CUFRDN di 46,
    # Alamat kantor: CUADP1(33), CUADP2(34), CUCITP(35), CUZIPP(36), CUPPA1(37)
    # Telp kantor: CUPPN1(38), CUEXT1(39), CUPPA2(40), CUPPN2(41), CUEXT2(42)
    
    COL_CUCODE = 0      # Customer code
    COL_CUSHOR = 2      # Short name (alias)
    COL_CUPLBR = 5      # Place Birth (Tempat Lahir)
    COL_CUDTLH = 6      # Birth date
    COL_CUMRST = 7      # Marital Status (Status Kawin) ✅ dari lo
    COL_CUIDNO = 19     # ID Number (NIK)
    COL_CUINCM = 44     # Income per Month (Penghasilan) ✅ dari lo
    COL_CUFRDN = 46     # Sumber Dana ✅ dari lo
    
    # Alamat Kantor
    COL_CUADP1 = 33
    COL_CUADP2 = 34
    COL_CUCITP = 35
    COL_CUZIPP = 36
    COL_CUPPA1 = 37
    
    # Telp Kantor
    COL_CUPPN1 = 38
    COL_CUEXT1 = 39
    COL_CUPPA2 = 40
    COL_CUPPN2 = 41
    COL_CUEXT2 = 42
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"] or cif not in existing_data:
            continue
        
        # === KUMPULKAN DATA DARI M4CUI ===
        alias = str(row[COL_CUSHOR]).strip() if len(row) > COL_CUSHOR and str(row[COL_CUSHOR]).strip() not in ["", "nan"] else "-"
        tempat_lahir = str(row[COL_CUPLBR]).strip() if len(row) > COL_CUPLBR and str(row[COL_CUPLBR]).strip() not in ["", "nan"] else "-"
        tgl_lahir = str(row[COL_CUDTLH]).strip() if len(row) > COL_CUDTLH and str(row[COL_CUDTLH]).strip() not in ["", "nan"] else "-"
        status_kawin = str(row[COL_CUMRST]).strip() if len(row) > COL_CUMRST and str(row[COL_CUMRST]).strip() not in ["", "nan"] else "-"
        nik = str(row[COL_CUIDNO]).strip() if len(row) > COL_CUIDNO and str(row[COL_CUIDNO]).strip() not in ["", "nan"] else "-"
        penghasilan = str(row[COL_CUINCM]).strip() if len(row) > COL_CUINCM and str(row[COL_CUINCM]).strip() not in ["", "nan"] else "-"
        sumber_dana = str(row[COL_CUFRDN]).strip() if len(row) > COL_CUFRDN and str(row[COL_CUFRDN]).strip() not in ["", "nan"] else "-"
        
        # Alamat Kantor
        alamat_kantor_parts = []
        if len(row) > COL_CUADP1:
            val = str(row[COL_CUADP1]).strip()
            if val not in ["", "nan"]:
                alamat_kantor_parts.append(val)
        if len(row) > COL_CUADP2:
            val = str(row[COL_CUADP2]).strip()
            if val not in ["", "nan"]:
                alamat_kantor_parts.append(val)
        if len(row) > COL_CUCITP:
            val = str(row[COL_CUCITP]).strip()
            if val not in ["", "nan"]:
                alamat_kantor_parts.append(val)
        if len(row) > COL_CUZIPP:
            val = str(row[COL_CUZIPP]).strip()
            if val not in ["", "nan"]:
                alamat_kantor_parts.append(val)
        if len(row) > COL_CUPPA1:
            val = str(row[COL_CUPPA1]).strip()
            if val not in ["", "nan"]:
                alamat_kantor_parts.append(val)
        alamat_kantor = " ".join(alamat_kantor_parts) if alamat_kantor_parts else "-"
        
        # Telp Kantor
        telp_kantor_parts = []
        if len(row) > COL_CUPPN1:
            val = str(row[COL_CUPPN1]).strip()
            if val not in ["", "nan"]:
                telp_kantor_parts.append(val)
        if len(row) > COL_CUEXT1:
            val = str(row[COL_CUEXT1]).strip()
            if val not in ["", "nan"]:
                telp_kantor_parts.append(val)
        if len(row) > COL_CUPPA2:
            val = str(row[COL_CUPPA2]).strip()
            if val not in ["", "nan"]:
                telp_kantor_parts.append(val)
        if len(row) > COL_CUPPN2:
            val = str(row[COL_CUPPN2]).strip()
            if val not in ["", "nan"]:
                telp_kantor_parts.append(val)
        if len(row) > COL_CUEXT2:
            val = str(row[COL_CUEXT2]).strip()
            if val not in ["", "nan"]:
                telp_kantor_parts.append(val)
        telp_kantor = " ".join(telp_kantor_parts) if telp_kantor_parts else "-"
        
        # === GABUNG DENGAN PRIORITAS (M4CU > M4CUI) ===
        
        # Nama: M4CU dulu, kalau kosong pakai alias
        if existing_data[cif]["nama_m4cu"] != "-":
            existing_data[cif]["nama"] = existing_data[cif]["nama_m4cu"]
        elif alias != "-":
            existing_data[cif]["nama"] = alias
        
        # Alamat: M4CU dulu
        if existing_data[cif]["alamat_m4cu"] != "-":
            existing_data[cif]["alamat"] = existing_data[cif]["alamat_m4cu"]
        
        # Pekerjaan: M4CU dulu
        if existing_data[cif]["pekerjaan_m4cu"] != "-":
            existing_data[cif]["pekerjaan"] = existing_data[cif]["pekerjaan_m4cu"]
        
        # Kewarganegaraan: M4CU dulu
        if existing_data[cif]["kewarganegaraan_m4cu"] != "-":
            existing_data[cif]["kewarganegaraan"] = existing_data[cif]["kewarganegaraan_m4cu"]
        
        # Tempat Lahir: dari M4CUI
        if tempat_lahir != "-":
            existing_data[cif]["tempat_lahir"] = tempat_lahir
        
        # Tanggal Lahir: M4CU dulu, kalau kosong pakai M4CUI
        if existing_data[cif]["tanggal_lahir_m4cu"] != "-":
            existing_data[cif]["tanggal_lahir"] = existing_data[cif]["tanggal_lahir_m4cu"]
        elif tgl_lahir != "-":
            existing_data[cif]["tanggal_lahir"] = tgl_lahir
        
        # NIK: M4CU dulu, kalau kosong pakai M4CUI
        if existing_data[cif]["nik_m4cu"] != "-":
            existing_data[cif]["nik"] = existing_data[cif]["nik_m4cu"]
        elif nik != "-":
            existing_data[cif]["nik"] = nik
        
        # JK: M4CU dulu
        if existing_data[cif]["jk_m4cu"] != "-":
            existing_data[cif]["jk"] = existing_data[cif]["jk_m4cu"]
        
        # Status Kawin: dari M4CUI
        if status_kawin != "-":
            existing_data[cif]["status_kawin"] = status_kawin
        
        # Sumber Dana: dari M4CUI
        if sumber_dana != "-":
            existing_data[cif]["sumber_dana"] = sumber_dana
        
        # Penghasilan: dari M4CUI
        if penghasilan != "-":
            existing_data[cif]["penghasilan"] = penghasilan
        
        # Alamat Kantor: dari M4CUI
        if alamat_kantor != "-":
            existing_data[cif]["alamat_kantor"] = alamat_kantor
        
        # Telp Kantor: dari M4CUI
        if telp_kantor != "-":
            existing_data[cif]["telp_kantor"] = telp_kantor
    
    return existing_data

# ============================================================
# 6. EKSTRAK M4CUAPU (BO)
# ============================================================
def extract_m4cuapu(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # MAPPING POSISI KOLOM M4CUAPU
    # Customer code di kolom 1, Beneficiary Owner Name di kolom 23
    COL_CUCODE = 1
    COL_BONAME = 23
    
    for _, row in df.iterrows():
        cif = str(row[COL_CUCODE]).strip()
        if not cif or cif in ["", "nan", "None"] or cif not in existing_data:
            continue
        
        # BO Name
        if len(row) > COL_BONAME:
            val = str(row[COL_BONAME]).strip()
            if val not in ["", "nan"]:
                existing_data[cif]["bo"] = val
    
    return existing_data

# ============================================================
# 7. EKSTRAK M4CUG (Nama Ibu - nanti)
# ============================================================
def extract_m4cug(df, existing_data):
    if df is None or df.empty:
        return existing_data
    
    # Belum ada mapping untuk Nama Ibu
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
            if key not in d or d[key] in ["", "nan", "None"]:
                d[key] = default[key]
        
        for key in d:
            if d[key] in ["nan", "None", ""]:
                d[key] = "-"
        
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
        
        # 2. M4CUI (PELENGKAP)
        for key in all_files.keys():
            if "M4CUI" in key:
                st.write(f"✅ Menambahkan data dari: {key}")
                data = extract_m4cui(all_files[key], data)
                break
        
        # 3. M4CUAPU (BO)
        for key in all_files.keys():
            if "M4CUAPU" in key:
                st.write(f"✅ Menambahkan data dari: {key}")
                data = extract_m4cuapu(all_files[key], data)
                break
        
        # 4. M4CUG (Nama Ibu - belum)
        for key in all_files.keys():
            if "M4CUG" in key:
                st.write(f"✅ Menambahkan data dari: {key}")
                data = extract_m4cug(all_files[key], data)
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
