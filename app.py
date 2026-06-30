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
# 2. FUNGSI BACA FILE .tab (dengan fallback encoding)
# ============================================================
def parse_tab_file(uploaded_file):
    """Baca file .tab yang berisi multiple sheet (mirip file Excel)"""
    data = {}
    
    # Coba berbagai encoding
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    content = None
    
    for enc in encodings:
        try:
            uploaded_file.seek(0)  # Reset ke awal
            content = uploaded_file.read().decode(enc, errors="replace")
            break
        except:
            continue
    
    if content is None:
        # Fallback: baca sebagai bytes dan ganti karakter bermasalah
        uploaded_file.seek(0)
        raw = uploaded_file.read()
        content = raw.decode("utf-8", errors="ignore")
    
    lines = content.splitlines()
    
    current_sheet = None
    sheet_data = []
    is_header = False
    header_cols = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Deteksi sheet baru (format: [metadata.sheet_name: NAMA])
        if line.startswith("> metadata.sheet_name:"):
            # Simpan sheet sebelumnya
            if current_sheet and sheet_data:
                try:
                    if header_cols and len(header_cols) > 0:
                        # Bersihin header
                        clean_header = [c.replace("_", " ").strip() for c in header_cols]
                        # Buat dataframe dengan header
                        df = pd.DataFrame(sheet_data)
                        if len(df.columns) >= len(clean_header):
                            df.columns = clean_header[:len(df.columns)]
                        # Hapus baris yang semua nilainya kosong
                        df = df.replace(r'^\s*$', '', regex=True)
                        df = df.replace(r'^nan$', '', regex=True)
                        df = df.dropna(how='all')
                        if not df.empty:
                            data[current_sheet] = df
                except Exception as e:
                    # Kalau error, simpan raw dulu
                    pass
            # Mulai sheet baru
            current_sheet = line.split(":")[1].strip()
            sheet_data = []
            header_cols = []
            is_header = True
            continue
            
        # Deteksi header kolom (baris pertama setelah sheet name)
        if is_header and current_sheet:
            if line.startswith("|") and "|" in line:
                cols = [c.strip() for c in line.split("|")[1:-1]]
                cols = [c for c in cols if c and not c.startswith("metadata")]
                if cols:
                    header_cols = cols
                    is_header = False
            continue
            
        # Data baris (diawali pipe)
        if line.startswith("|") and current_sheet and header_cols:
            row = [c.strip() for c in line.split("|")[1:-1]]
            if row:
                # Potong atau tambah biar sesuai header
                while len(row) < len(header_cols):
                    row.append("")
                sheet_data.append(row)
    
    # Simpan sheet terakhir
    if current_sheet and sheet_data and header_cols:
        try:
            clean_header = [c.replace("_", " ").strip() for c in header_cols]
            df = pd.DataFrame(sheet_data)
            if len(df.columns) >= len(clean_header):
                df.columns = clean_header[:len(df.columns)]
            df = df.replace(r'^\s*$', '', regex=True)
            df = df.replace(r'^nan$', '', regex=True)
            df = df.dropna(how='all')
            if not df.empty:
                data[current_sheet] = df
        except:
            pass
    
    return data

# ============================================================
# 3. FUNGSI EKSTRAK DATA PER CIF
# ============================================================
def get_best_value(values, prefer_text=True):
    """
    Pilih nilai terbaik dari beberapa sumber
    - prefer_text=True: pilih yang ada huruf (teks), kalau semua angka, pilih angka
    - prefer_text=False: pilih nilai pertama yang gak kosong
    """
    # Filter nilai kosong
    valid = []
    for v in values:
        v_str = str(v).strip()
        if v_str and v_str not in ["", "nan", "None", "-", "0", "0000", "NULL"]:
            valid.append(v_str)
    
    if not valid:
        return "-"
    
    if prefer_text:
        # Cari yang mengandung huruf (teks)
        text_values = [v for v in valid if re.search(r'[A-Za-z]', str(v))]
        if text_values:
            # Pilih yang paling panjang (paling lengkap)
            return max(text_values, key=lambda x: len(str(x)))
        else:
            # Semua angka, pilih angka pertama
            return str(valid[0])
    else:
        return str(valid[0])

def extract_cif_data(sheets):
    """Ekstrak data per CIF dari semua sheet"""
    result = {}
    
    # ============================================================
    # 3a. AMBIL BASE DARI M4CU (Customer code = CIF)
    # ============================================================
    m4cu = sheets.get("M4CU")
    if m4cu is not None and not m4cu.empty:
        # Cari kolom CUCODE (Customer code)
        cu_col = None
        name_col = None
        type_col = None
        addr_cols = []
        
        for col in m4cu.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CUCODE", "CUSTOMER CODE", "CUSTAT"]:
                cu_col = col
            elif col_clean in ["CUNAME", "CUSTOMER NAME"]:
                name_col = col
            elif col_clean in ["CUFLTY", "CUSTOMER TYPE"]:
                type_col = col
            elif col_clean.startswith("CUADR") or "ADDRESS" in col_clean:
                addr_cols.append(col)
        
        if cu_col is not None:
            for _, row in m4cu.iterrows():
                cif = str(row[cu_col]).strip()
                if not cif or cif in ["", "nan", "None"]:
                    continue
                    
                result[cif] = {
                    "sources": ["M4CU"],
                    "cif": cif,
                    "nama": get_best_value([row[name_col]] if name_col else ["-"]),
                    "jenis_nasabah": str(row[type_col]).strip() if type_col and str(row[type_col]).strip() not in ["", "nan"] else "",
                    "alamat": " ".join([str(row[c]).strip() for c in addr_cols if str(row[c]).strip() not in ["", "nan"]]),
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
    # 3b. TAMBAH DATA DARI M4CUI (atau M4CU1)
    # ============================================================
    m4cui = sheets.get("M4CUI")
    if m4cui is None or m4cui.empty:
        m4cui = sheets.get("M4CU1")  # Coba alternatif nama
    
    if m4cui is not None and not m4cui.empty:
        cu_col = None
        for col in m4cui.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CUCODE", "CUSTOMER CODE"]:
                cu_col = col
                break
        
        if cu_col is not None:
            for _, row in m4cui.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result or cif in ["", "nan"]:
                    continue
                
                # Kumpulkan nilai dari berbagai kolom
                vals = {
                    "nama": [row.get("CUSHOR", "-"), row.get("CUNAME", "-")],
                    "tempat_lahir": [row.get("CUPLBR", "-")],
                    "tanggal_lahir": [row.get("CUDTLH", "-")],
                    "nik": [row.get("CUIDNO", "-")],
                    "jk": [row.get("CUJEKL", "-")],
                    "kewarganegaraan": [row.get("CUCTZC", "-")],
                    "status_kawin": [row.get("CUMRST", "-")],
                    "pekerjaan": [row.get("CUIKRJ", "-")],
                    "sumber_dana": [row.get("CUFRDN", "-")],
                    "penghasilan": [row.get("CUINCM", "-")],
                    "tujuan_usaha": [row.get("CUTOIC", "-")],
                    "alamat_lain": [f"{row.get('CUADP1','')} {row.get('CUADP2','')}".strip()],
                    "alamat_kantor": [row.get("CUADP1", "-")],
                    "telp_kantor": [row.get("CUPPN1", "-")]
                }
                
                for key, val_list in vals.items():
                    if val_list:
                        current = result[cif].get(key, "-")
                        new_val = get_best_value(val_list)
                        if new_val != "-":
                            if current == "-" or len(str(new_val)) > len(str(current)):
                                result[cif][key] = new_val
    
    # ============================================================
    # 3c. TAMBAH DATA DARI M4CU.G (atau M4CUGE)
    # ============================================================
    m4cuge = sheets.get("M4CU.G")
    if m4cuge is None or m4cuge.empty:
        m4cuge = sheets.get("M4CUGE")
    
    if m4cuge is not None and not m4cuge.empty:
        cu_col = None
        for col in m4cuge.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CUCODE", "CUSTOMER CODE"]:
                cu_col = col
                break
        
        if cu_col is not None:
            for _, row in m4cuge.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result or cif in ["", "nan"]:
                    continue
                
                if "CUIBUN" in row and str(row["CUIBUN"]).strip() not in ["", "nan"]:
                    result[cif]["nama_ibu"] = get_best_value([result[cif]["nama_ibu"], row.get("CUIBUN", "-")])
                if "CUNAME2" in row and str(row["CUNAME2"]).strip() not in ["", "nan"]:
                    result[cif]["nama"] = get_best_value([result[cif]["nama"], row.get("CUNAME2", "-")])
    
    # ============================================================
    # 3d. TAMBAH DATA DARI M4CUAPU (atau M4CUAPPU)
    # ============================================================
    m4cuappu = sheets.get("M4CUAPU")
    if m4cuappu is None or m4cuappu.empty:
        m4cuappu = sheets.get("M4CUAPPU")
    
    if m4cuappu is not None and not m4cuappu.empty:
        cu_col = None
        for col in m4cuappu.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CUSTOMER CODE", "CUCODE"]:
                cu_col = col
                break
        
        if cu_col is not None:
            for _, row in m4cuappu.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result or cif in ["", "nan"]:
                    continue
                
                if "Beneficiary Owner" in row:
                    bo_val = get_best_value([row.get("Beneficiary Owner", "-"), row.get("Beneficiary Owner Name", "-")])
                    if bo_val != "-":
                        result[cif]["bo"] = bo_val
                if "Sumber Dana" in row:
                    val = str(row["Sumber Dana"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["sumber_dana"] = get_best_value([result[cif]["sumber_dana"], val])
                if "Tujuan Penggunaan Dana" in row:
                    val = str(row["Tujuan Penggunaan Dana"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["tujuan_usaha"] = get_best_value([result[cif]["tujuan_usaha"], val])
                if "Rata-Rata Penghasilan" in row:
                    val = str(row["Rata-Rata Penghasilan"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["penghasilan"] = get_best_value([result[cif]["penghasilan"], val])
                if "Bidang Usaha" in row:
                    val = str(row["Bidang Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bidang_usaha"] = val
                if "Bentuk Usaha" in row:
                    val = str(row["Bentuk Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bentuk_badan"] = val
                if "No. Izin Usaha" in row:
                    val = str(row["No. Izin Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["no_izin"] = val
    
    # ============================================================
    # 3e. TAMBAH DATA DARI M4CU.C
    # ============================================================
    m4cuc = sheets.get("M4CU.C")
    if m4cuc is not None and not m4cuc.empty:
        cu_col = None
        for col in m4cuc.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CIF", "CUCODE", "CUSTOMER CODE"]:
                cu_col = col
                break
        
        if cu_col is not None:
            for _, row in m4cuc.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result or cif in ["", "nan"]:
                    continue
                
                if "Bidang Usaha" in row:
                    val = str(row["Bidang Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bidang_usaha"] = get_best_value([result[cif]["bidang_usaha"], val])
                if "Bentuk Usaha" in row:
                    val = str(row["Bentuk Usaha"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["bentuk_badan"] = get_best_value([result[cif]["bentuk_badan"], val])
                if "Nomor Ijin Usaha" in row or "Nomor Izin Usaha" in row:
                    col_name = "Nomor Ijin Usaha" if "Nomor Ijin Usaha" in row else "Nomor Izin Usaha"
                    val = str(row[col_name]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["no_izin"] = get_best_value([result[cif]["no_izin"], val])
                if "Tanggal Berdiri" in row:
                    val = str(row["Tanggal Berdiri"]).strip()
                    if val not in ["", "nan"]:
                        result[cif]["tanggal_pendirian"] = val
    
    return result

# ============================================================
# 4. FUNGSI GENERATE TEMPLATE
# ============================================================
def generate_template(data):
    """Generate 2 sheet: Perorangan dan Badan Usaha"""
    
    perorangan_rows = []
    badan_usaha_rows = []
    
    for cif, d in data.items():
        # Tentukan jenis nasabah
        jenis = d.get("jenis_nasabah", "").strip().upper()
        if jenis == "I":
            # Perorangan
            row = {
                "Status": "✅ LENGKAP" if all(v != "-" for v in [
                    d["nama"], d["nik"], d["alamat"], d["tempat_lahir"], 
                    d["tanggal_lahir"], d["pekerjaan"], d["jk"], 
                    d["status_kawin"], d["nama_ibu"]
                ]) else "⚠️ TIDAK LENGKAP",
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
                "Keterangan": "LENGKAP" if all(v != "-" for v in [
                    d["nama"], d["nik"], d["alamat"], d["tempat_lahir"], 
                    d["tanggal_lahir"], d["pekerjaan"], d["jk"], 
                    d["status_kawin"], d["nama_ibu"]
                ]) else "TIDAK LENGKAP"
            }
            
            # Tambah kolom ceklis
            fields = ["Nama", "NIK", "Alamat", "TTL", "Pekerjaan", "JK", "Status Kawin", "Nama Ibu", "BO", "Sumber Dana", "Penghasilan", "Tujuan"]
            field_values = [d["nama"], d["nik"], d["alamat"], f"{d['tempat_lahir']}{d['tanggal_lahir']}", 
                           d["pekerjaan"], d["jk"], d["status_kawin"], d["nama_ibu"], 
                           d["bo"], d["sumber_dana"], d["penghasilan"], d["tujuan_usaha"]]
            
            for f, v in zip(fields, field_values):
                row[f"✅ {f}"] = "✅" if v != "-" else "❌"
            
            perorangan_rows.append(row)
            
        else:
            # Badan Usaha (C atau kosong)
            row = {
                "Status": "✅ LENGKAP" if all(v != "-" for v in [
                    d["nama"], d["no_izin"], d["bidang_usaha"], d["alamat"]
                ]) else "⚠️ TIDAK LENGKAP",
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
                "Keterangan": "LENGKAP" if all(v != "-" for v in [
                    d["nama"], d["no_izin"], d["bidang_usaha"], d["alamat"]
                ]) else "TIDAK LENGKAP"
            }
            
            # Tambah kolom ceklis
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
# 5. FUNGSI DOWNLOAD EXCEL
# ============================================================
def to_excel_download(df1, df2):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='Perorangan', index=False)
        df2.to_excel(writer, sheet_name='Badan Usaha', index=False)
    return output.getvalue()

# ============================================================
# 6. UI UTAMA
# ============================================================
uploaded_files = st.file_uploader(
    "Upload file .tab", 
    accept_multiple_files=True, 
    type=["tab", "txt"]
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file berhasil diupload!")
    
    with st.spinner("⏳ Memproses data..."):
        all_sheets = {}
        for file in uploaded_files:
            try:
                sheets = parse_tab_file(file)
                for sheet_name, df in sheets.items():
                    if sheet_name not in all_sheets:
                        all_sheets[sheet_name] = df
                    else:
                        all_sheets[sheet_name] = pd.concat([all_sheets[sheet_name], df], ignore_index=True)
            except Exception as e:
                st.warning(f"⚠️ Gagal baca file {file.name}: {str(e)[:100]}")
                continue
        
        if not all_sheets:
            st.error("❌ Tidak ada data yang bisa diproses. Pastikan file .tab berisi data.")
            st.stop()
        
        # Ekstrak data per CIF
        data = extract_cif_data(all_sheets)
        
        if not data:
            st.error("❌ Tidak ada CIF ditemukan. Pastikan file M4CU ada.")
            st.stop()
        
        # Generate template
        df_perorangan, df_badan_usaha = generate_template(data)
    
    st.success(f"✅ Data berhasil diproses! {len(data)} CIF ditemukan")
    
    # Tampilkan preview
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
    
    # Tombol download
    if not df_perorangan.empty or not df_badan_usaha.empty:
        excel_data = to_excel_download(df_perorangan, df_badan_usaha)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="CIF_Data_Aggregator.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
