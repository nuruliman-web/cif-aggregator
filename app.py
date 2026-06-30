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
# 2. FUNGSI BACA FILE .tab (semua sheet)
# ============================================================
def parse_tab_file(uploaded_file):
    """Baca file .tab yang berisi multiple sheet (mirip file Excel)"""
    data = {}
    content = uploaded_file.read().decode("utf-8")
    lines = content.splitlines()
    
    current_sheet = None
    sheet_data = []
    is_header = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Deteksi sheet baru (format: [metadata.sheet_name: NAMA])
        if line.startswith("> metadata.sheet_name:"):
            # Simpan sheet sebelumnya
            if current_sheet and sheet_data:
                data[current_sheet] = pd.DataFrame(sheet_data)
            # Mulai sheet baru
            current_sheet = line.split(":")[1].strip()
            sheet_data = []
            is_header = True
            continue
            
        # Deteksi header kolom (baris pertama setelah sheet name)
        if is_header and current_sheet:
            # Header biasanya diawali "| A | B | C | ..."
            if line.startswith("|") and "|" in line:
                # Ambil semua kolom dari header
                cols = [c.strip() for c in line.split("|")[1:-1]]
                # Filter kolom yang gak kosong
                cols = [c for c in cols if c and not c.startswith("metadata")]
                if cols:
                    sheet_data.append(cols)
                is_header = False
            continue
            
        # Data baris (diawali pipe)
        if line.startswith("|") and current_sheet:
            row = [c.strip() for c in line.split("|")[1:-1]]
            if row:
                sheet_data.append(row)
    
    # Simpan sheet terakhir
    if current_sheet and sheet_data:
        # Pastikan semua baris punya panjang yang sama
        max_cols = max(len(row) for row in sheet_data)
        for row in sheet_data:
            while len(row) < max_cols:
                row.append("")
        data[current_sheet] = pd.DataFrame(sheet_data[1:], columns=sheet_data[0] if len(sheet_data) > 1 else None)
    
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
    valid = [v for v in values if v and str(v).strip() and str(v).strip() != "-"]
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
            if col_clean in ["CUCODE", "CUSTOMER CODE"]:
                cu_col = col
            elif col_clean in ["CUNAME", "CUSTOMER NAME"]:
                name_col = col
            elif col_clean in ["CUFLTY", "CUSTOMER TYPE"]:
                type_col = col
            elif col_clean.startswith("CUADR"):
                addr_cols.append(col)
        
        if cu_col is not None:
            for _, row in m4cu.iterrows():
                cif = str(row[cu_col]).strip()
                if not cif or cif == "nan":
                    continue
                    
                result[cif] = {
                    "sources": ["M4CU"],
                    "cif": cif,
                    "nama": get_best_value([row[name_col]] if name_col else ["-"]),
                    "jenis_nasabah": str(row[type_col]).strip() if type_col else "",
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
    # 3b. TAMBAH DATA DARI M4CUI
    # ============================================================
    m4cui = sheets.get("M4CUI")
    if m4cui is not None and not m4cui.empty:
        for col in m4cui.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CUCODE", "CUSTOMER CODE"]:
                cu_col = col
                break
        else:
            cu_col = None
        
        if cu_col is not None:
            for _, row in m4cui.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
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
                    if val_list and str(val_list[0]).strip() not in ["", "nan", "-"]:
                        current = result[cif].get(key, "-")
                        if current == "-" or len(str(val_list[0])) > len(str(current)):
                            result[cif][key] = get_best_value(val_list)
    
    # ============================================================
    # 3c. TAMBAH DATA DARI M4CUGE (ibu kandung, dll)
    # ============================================================
    m4cuge = sheets.get("M4CUGE")
    if m4cuge is not None and not m4cuge.empty:
        for col in m4cuge.columns:
            if col.strip().upper() in ["CUCODE", "CUSTOMER CODE"]:
                cu_col = col
                break
        else:
            cu_col = None
        
        if cu_col is not None:
            for _, row in m4cuge.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
                    continue
                
                if row.get("CUIBUN"):
                    result[cif]["nama_ibu"] = get_best_value([row.get("CUIBUN", "-")])
                if row.get("CUNAME2"):
                    result[cif]["nama"] = get_best_value([result[cif]["nama"], row.get("CUNAME2", "-")])
    
    # ============================================================
    # 3d. TAMBAH DATA DARI M4CUAPPU (BO, sumber dana, tujuan)
    # ============================================================
    m4cuappu = sheets.get("M4CUAPPU")
    if m4cuappu is not None and not m4cuappu.empty:
        for col in m4cuappu.columns:
            col_clean = col.strip().upper()
            if col_clean in ["CUSTOMER CODE", "CUCODE"]:
                cu_col = col
                break
        else:
            cu_col = None
        
        if cu_col is not None:
            for _, row in m4cuappu.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
                    continue
                
                if row.get("Beneficiary Owner"):
                    result[cif]["bo"] = get_best_value([row.get("Beneficiary Owner", "-"), row.get("Beneficiary Owner Name", "-")])
                if row.get("Sumber Dana"):
                    result[cif]["sumber_dana"] = get_best_value([result[cif]["sumber_dana"], row.get("Sumber Dana", "-")])
                if row.get("Tujuan Penggunaan Dana"):
                    result[cif]["tujuan_usaha"] = get_best_value([result[cif]["tujuan_usaha"], row.get("Tujuan Penggunaan Dana", "-")])
                if row.get("Rata-Rata Penghasilan"):
                    result[cif]["penghasilan"] = get_best_value([result[cif]["penghasilan"], row.get("Rata-Rata Penghasilan", "-")])
                if row.get("Bidang Usaha"):
                    result[cif]["bidang_usaha"] = row.get("Bidang Usaha", "-")
                if row.get("Bentuk Usaha"):
                    result[cif]["bentuk_badan"] = row.get("Bentuk Usaha", "-")
                if row.get("No. Izin Usaha"):
                    result[cif]["no_izin"] = row.get("No. Izin Usaha", "-")
    
    # ============================================================
    # 3e. TAMBAH DATA DARI M4CUC (badan usaha)
    # ============================================================
    m4cuc = sheets.get("M4CUC")
    if m4cuc is not None and not m4cuc.empty:
        for col in m4cuc.columns:
            if col.strip().upper() in ["CIF", "CUCODE", "CUSTOMER CODE"]:
                cu_col = col
                break
        else:
            cu_col = None
        
        if cu_col is not None:
            for _, row in m4cuc.iterrows():
                cif = str(row[cu_col]).strip()
                if cif not in result:
                    continue
                
                if row.get("Bidang Usaha"):
                    result[cif]["bidang_usaha"] = get_best_value([result[cif]["bidang_usaha"], row.get("Bidang Usaha", "-")])
                if row.get("Bentuk Usaha"):
                    result[cif]["bentuk_badan"] = get_best_value([result[cif]["bentuk_badan"], row.get("Bentuk Usaha", "-")])
                if row.get("Nomor Ijin Usaha"):
                    result[cif]["no_izin"] = get_best_value([result[cif]["no_izin"], row.get("Nomor Ijin Usaha", "-")])
                if row.get("Tanggal Berdiri"):
                    result[cif]["tanggal_pendirian"] = row.get("Tanggal Berdiri", "-")
    
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
    type=["tab"]
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file berhasil diupload!")
    
    with st.spinner("⏳ Memproses data..."):
        all_sheets = {}
        for file in uploaded_files:
            sheets = parse_tab_file(file)
            for sheet_name, df in sheets.items():
                if sheet_name not in all_sheets:
                    all_sheets[sheet_name] = df
                else:
                    all_sheets[sheet_name] = pd.concat([all_sheets[sheet_name], df], ignore_index=True)
        
        # Ekstrak data per CIF
        data = extract_cif_data(all_sheets)
        
        # Generate template
        df_perorangan, df_badan_usaha = generate_template(data)
    
    st.success(f"✅ Data berhasil diproses! {len(data)} CIF ditemukan")
    
    # Tampilkan preview
    tab1, tab2 = st.tabs(["👤 Perorangan", "🏢 Badan Usaha"])
    
    with tab1:
        st.dataframe(df_perorangan, use_container_width=True)
    
    with tab2:
        st.dataframe(df_badan_usaha, use_container_width=True)
    
    # Tombol download
    excel_data = to_excel_download(df_perorangan, df_badan_usaha)
    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="CIF_Data_Aggregator.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
