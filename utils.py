# utils.py
import re

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
    return str(valid[0])

# ============================================================
# MAPPING ALIAS HEADER (KODE → NAMA USER FRIENDLY)
# ============================================================
HEADER_ALIAS = {
    # M4CU / M4CUI
    "CUCODE": "CIF",
    "Customer code": "CIF",
    "CIF": "CIF",
    "CUNAME": "Nama Nasabah",
    "Customer Name": "Nama Nasabah",
    "Nama": "Nama Nasabah",
    "CUSHOR": "Nama Alias",
    "Short name": "Nama Alias",
    "CUIDNO": "No KTP/NIK",
    "ID Number": "No KTP/NIK",
    "CUPLBR": "Tempat Lahir",
    "Place Birth": "Tempat Lahir",
    "CUDTLH": "Tanggal Lahir",
    "Birth date": "Tanggal Lahir",
    "CUJEKL": "Jenis Kelamin",
    "Jenis kelamin": "Jenis Kelamin",
    "CUMRST": "Status Perkawinan",
    "Marital Status": "Status Perkawinan",
    "CUADR1": "Alamat 1",
    "Address-1": "Alamat 1",
    "CUADR2": "Alamat 2",
    "Address-2": "Alamat 2",
    "CUADR3": "Kota",
    "City": "Kota",
    "CUADP1": "Alamat Kantor",
    "Address #1": "Alamat Kantor",
    "CUPPN1": "No Telp Kantor",
    "Phone #1": "No Telp Kantor",
    "CUINCM": "Penghasilan/bulan",
    "Income per Month": "Penghasilan/bulan",
    "CUFRDN": "Sumber Dana",
    "Sumber Dana": "Sumber Dana",
    "CUTOIC": "Tujuan Penggunaan",
    "Tujuan Penggunaan": "Tujuan Penggunaan",
    "CUOWCO": "Golongan Pemilik",
    "Golongan pemilik": "Golongan Pemilik",
    "CUKRJA": "Pekerjaan",
    "Pekerjaan": "Pekerjaan",
    "CUNECO": "Kewarganegaraan",
    "Country": "Kewarganegaraan",
    "CUNKTP": "No KTP/NIK",
    "ID card number": "No KTP/NIK",
    "CUAGAM": "Agama",
    "Agama": "Agama",
    "CUHOBI": "Hobi",
    "Hobbies": "Hobi",
    "CUNSPO": "Jml Istri/Suami",
    "Numbers Wife": "Jml Istri/Suami",
    "CUNCHL": "Jml Anak",
    "Numbers Child": "Jml Anak",
    "CUSTAT": "Status Record",
    "Status record": "Status Record",
    
    # M4CUC
    "Bentuk Usaha": "Bentuk Usaha",
    "Bidang Usaha": "Bidang Usaha",
    "Nomor Ijin Usaha": "No Izin Usaha",
    "Tanggal Berdiri": "Tanggal Berdiri",
    "Penghasilan Per-tahun": "Penghasilan/tahun",
    "Tujuan Hub": "Tujuan Hubungan",
    "Kepemilikan Modal": "Kepemilikan Modal",
    
    # M4CUAPPU
    "Domisili 1": "Domisili 1",
    "Domisili 2": "Domisili 2",
    "Beneficiary Owner": "Beneficial Owner",
    "Beneficiary Owner Name": "Nama BO",
    "Rata-Rata Penghasilan": "Rata-rata Penghasilan",
    "No. Izin Usaha": "No Izin Usaha",
    
    # T6APPU
    "Status": "Status",
    "Nomor Rekening": "No Rekening",
    "Cabang Transaksi": "Cabang",
    "Nomor CIF Nasabah": "CIF",
    "Nama Nasabah": "Nama Nasabah",
    "Kode Transaksi": "Kode Transaksi",
    "Nomor Referensi": "No Referensi",
    "Nilai Transaksi": "Nilai Transaksi",
    "Tanggal Transaksi": "Tgl Transaksi",
    "Jam Transaksi": "Jam Transaksi",
    
    # Kolom default
    "CIF": "CIF",
    "Nama": "Nama",
    "Alamat": "Alamat",
}

def get_alias(header_name):
    """Convert header name ke user-friendly alias"""
    if not header_name:
        return header_name
    
    # Cek exact match
    if header_name in HEADER_ALIAS:
        return HEADER_ALIAS[header_name]
    
    # Cek case insensitive
    for key, value in HEADER_ALIAS.items():
        if key.upper() == header_name.upper():
            return value
    
    # Cek partial match
    for key, value in HEADER_ALIAS.items():
        if key.upper() in header_name.upper() or header_name.upper() in key.upper():
            return value
    
    # Kalo gak ada, balikin asli
    return header_name

def clean_headers(headers):
    """
    Bersihin header jadi user friendly dan PASTIKAN UNIK
    """
    cleaned = []
    seen = {}
    
    for h in headers:
        # Dapatkan alias
        alias = get_alias(h)
        
        # Hapus prefix file name yang mungkin kelebihan
        if "_" in alias:
            parts = alias.split("_")
            if len(parts) > 1 and parts[-1] in HEADER_ALIAS.values():
                alias = parts[-1]
        
        # Pastikan unik
        if alias in seen:
            seen[alias] += 1
            alias = f"{alias}_{seen[alias]}"
        else:
            seen[alias] = 1
        
        cleaned.append(alias)
    
    return cleaned
