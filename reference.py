# reference.py
# ============================================================
# SEMUA REFERENSI DARI FILE MASTER "Kode 012 017 (2).xls"
# ============================================================
import re

# ============================================================
# 1. KODE CABANG
# ============================================================
CABANG_MAP = {
    "1": "KPO",
    "2": "Tangerang",
    "3": "Depok",
    "5": "Bekasi",
    "6": "Kelapa Gading",
    "7": "Bogor",
    "9": "Jambi",
    "10": "Pekanbaru",
    "11": "Pangkalan Kerinci",
    "12": "Pontianak",
    "13": "Siantan",
}

# ============================================================
# 2. KODE PEKERJAAN
# ============================================================
PEKERJAAN_MAP = {
    "0": "LAIN-LAIN",
    "1": "PEGAWAI NEGERI SIPIL/PNS",
    "2": "TNI/POLRI",
    "3": "PEGAWAI SWASTA",
    "4": "DOKTER",
    "5": "WIRASWASTA",
    "6": "PEJABAT NEGARA",
    "7": "PENGACARA/ADVOKAT",
    "8": "MAHASISWA/PELAJAR",
    "9": "PENSIUNAN",
    "10": "IBU RUMAH TANGGA",
    "11": "PELAJAR/MAHASISWA",
    "12": "WIRASWASTA",
    "13": "POLISI",
    "14": "PETANI",
    "15": "NELAYAN",
    "16": "PETERNAK",
    "17": "DOKTER",
    "18": "TENAGA MEDIS",
    "19": "HUKUM",
    "20": "PERHOTELAN",
    "21": "PENELITI",
    "22": "DESAINER",
    "32": "BURUH",
    "33": "KOMISARIS PERUSAHAAN SWASTA",
    "34": "IRT",
    "35": "PEKERJA INFORMAL",
    "36": "SPV PERUSAHAAN SWASTA",
    "37": "PEGAWAI PEMERINTAH",
    "38": "KEPALA OPERASIONAL",
    "41": "PEGAWAI HONORER",
    "42": "ADMINISTRASI",
    "54": "NOTARIS/PPAT",
    "62": "DOSEN/GURU",
    "9999": "LAIN-LAIN",
}

# ============================================================
# 3. STATUS PERKAWINAN
# ============================================================
STATUS_KAWIN_MAP = {
    "1": "Menikah",
    "2": "Belum Menikah",
    "3": "Pernah Menikah",
}

# ============================================================
# 4. BENTUK BADAN USAHA
# ============================================================
BENTUK_USAHA_MAP = {
    "A": "PT",
    "B": "CV",
    "D": "Yayasan",
    "E": "Persero",
    "H": "Perusahaan Daerah",
    "J": "Usaha Dagang",
    "K": "Persekutuan Perdata",
    "S": "Koperasi",
    "T": "Koperasi Unit Desa",
    "X": "Lainnya Badan Usaha",
}

# ============================================================
# 5. PENGHASILAN
# ============================================================
PENGHASILAN_MAP = {
    "1": "0 - 2,5 Juta",
    "2": "2,5 - 5 Juta",
    "3": "5 - 10 Juta",
    "4": "10 - 50 Juta",
    "5": "> 50 Juta",
}

# ============================================================
# 6. KRITERIA TKM
# ============================================================
KRITERIA_TKM_MAP = {
    "01": "Nasabah Profil Resiko Tinggi",
    "02": "Nasabah Red Flag",
    "03": "Nasabah PEP",
    "04": "Nasabah Memiliki Kesamaan Nama Dengan DTTOT",
    "05": "Transaksi Tidak Sesuai Profil Nasabah",
    "06": "Transaksi Debet/Kredit 100 Juta Keatas",
    "07": "Transaksi Debet/Kredit 500 Juta Keatas",
}

# ============================================================
# 7. KODE AO
# ============================================================
AO_MAP = {
    "AA": "JEKKY SIMAMORA",
    "AB": "SUWARDI",
    "AC": "AGUNG SETIAWAN",
    "AD": "EKA SEPTA SIREGAR",
    "AE": "ROBERT SAUT SARDION SIMATUPANG",
    "AF": "SUWANDI MANULANG",
    "AG": "DHIYAH TRI RESMIATI",
    "AH": "DESI MEGASARI",
    "AI": "SURONO ANOM",
    "AJ": "ANJAR IRAWAN",
    "AK": "AGUN SUDRAJAT",
    "AL": "YESSE FREDDY ARITONANG",
    "AM": "MARUSAHA NABABAN",
    "AN": "BANGUN SIBORO",
    "AO": "HADI WIJAYA",
    "AP": "DASUM",
    "AQ": "SUBLI BIN REJE",
    "AR": "KHAIRUL RAMDANI",
    "AS": "AHMAD IRWANSYAHPUTRA",
    "AT": "ANJU BONA SIBORO",
    "AU": "NANA PRIATNA",
    "AV": "MUHAMAD ICHWAN",
    "AW": "RIKO ALAMANDA",
    "AX": "JIMMY NOPEN PASARIBU",
    "AY": "SURATNO",
    "AZ": "HENDRA F. LUMINTANG",
    "BA": "YOPIE NASUTION",
    "BB": "DEDE AHMADI",
    "BC": "ENDANG KUSUMA TAHIR",
    "BD": "PUTRANIA",
    "BE": "HARRIS PRIHASTOMO",
    "BF": "YURI SETYAWAN",
    "BG": "ENDRO DWI PRASETIYO",
    "BH": "DEDEF HARDIMAN",
    "BI": "UJANG SUPRIADI",
    "BJ": "NANA SUPRIATNA",
    "BK": "ANDIKHA AGUNG",
    "BL": "FADLI ANUGRAH",
    "BM": "ADE FRANGKY",
    "BN": "HENDRO SUSANTO",
    "BO": "TENGKOH SEMBIRING",
    "BP": "HANA MAULANA YUSUP",
    "BQ": "IRWANTO PANGABEAN",
    "BR": "CAHYONO AGUNG NUGROHO",
    "BS": "EMIL MAULANA",
    "BT": "AL SUPRIANTA PERANGIN ANGIN",
    "BU": "RICHARD MANURUNG",
    "BV": "SUGIARTO",
    "BW": "KIKI AFRISON",
    "BX": "HENGKY HERLAMBANG",
    "BY": "AFRIANSYAH",
    "BZ": "BODMAN LUMBANTORUAN",
    "CA": "DENIS BUTAR BUTAR",
    "CB": "SANTOSO",
    "CC": "FADLY HARRISON SIMAMORA",
    "CD": "SAID MUBAROK",
    "CE": "MULYA PUJIANTO",
    "CF": "DOA RIO OKTO RAHARJO",
    "CG": "FRANSISCO J. SIMARMATA",
    "CH": "ALVINO SITUNGKIR",
    "CI": "AGUS FAIZIN",
    "CJ": "ANDRI ISWAHYUDI",
    "CK": "DIDIK SUTOPO",
    "CL": "DEWANTO",
    "CM": "IRIANA WIGUNA",
    "CN": "TRIO HARSILO",
    "CO": "ARFIYANTO WIBOWO",
    "CP": "SUBAGIA",
    "CQ": "VALERIANUS HOSANA OLA DATON",
    "CR": "MARINA",
    "CS": "JAYA BURHANUDDIN",
    "CT": "SANDY PERMANA",
    "CU": "NARES HENDRA",
    "CV": "VERONICA",
    "CW": "FITBERLAN PRAMUDYA HERSAN",
    "CX": "YAHYA SENJAYA",
    "CY": "WARSAN MAULANA",
    "CZ": "RAHMAT HIDAYAT",
    "DA": "MUHAMMAD ALI MAHDI",
    "DB": "SUPARYO",
    "DC": "ARIYANTO",
    "DD": "RULLY HEDIYANTO",
    "DE": "RICKY PERMANA",
    "DF": "DADANG SARIPUDIN",
    "DG": "TOTO",
    "DH": "YOHANES MAXKY HARTONO",
    "DI": "MUHAMMAD AGUNG FIRDAUS",
    "DJ": "PRAHARSIWI DIAN CHRISTIANTO",
    "DK": "NUR INDAH SARI",
    "DL": "JUWARI",
    "DM": "HARTAWAN",
    "DN": "BASUKI",
    "DO": "DONNY RADJALABIS",
    "DP": "JASINAR TAMPUBOLON",
    "DQ": "DINELIA RAFA SARI",
    "DR": "YOYON KOESWOYO",
    "DS": "YURIS ARDIANTO",
    "DT": "DWI ANGGRAINI",
    "DU": "MOCHAMAD FEBI HABIBIE",
    "DV": "RAFY ABHIGAMIKA",
    "DW": "MARIAH YESY SUCI",
    "DX": "RANIKA BR GINTING",
    "DY": "AJENG WORO SETYANINGRUM",
    "DZ": "ANDREAS RADITYA AMANDA",
    "EA": "MURI RITAMZAH",
    "EB": "NUGROHO AGUNG SETIAWAN",
    "EC": "ERICK EDUARDO",
    "ED": "MARIN MAULANA",
    "EE": "TISYA NUR RIZKIA",
    "EF": "ALI AMSAH",
    "EG": "RIYAN AFRIYANA",
    "EH": "RIZKY MULYANA",
    "EI": "TURZANDI",
    "EJ": "HARYOKO",
    "EK": "RAYMOND SARAGIH",
    "EL": "DODI GURUH",
    "EM": "ADI SUSANTO",
    "EN": "PRANATA DMT NAINGGOLAN",
    "EO": "BAYU SELA AJI",
    "EP": "JURISMAN WARUWU",
    "EQ": "AZMUAZI FHEBRIZAL",
    "ER": "ILHAM AKBAR",
    "ES": "FAJAR IHSAN FATHURROHMAN",
    "ET": "HENDRIK CIPTO BORISMAN",
    "EU": "ELGA RIZKY PRATAMA",
    "EV": "BINTANG PRABOWO TASTY",
    "EW": "MARINA",
    "EX": "HENDRA PURBA",
    "EY": "JOSWA ARITONANG",
    "EZ": "ARIEF WIGUNA",
    "FA": "APRIZAL LUMOWA",
    "FB": "ASTRI KUSHANDAYANI",
    "FC": "DEDIH",
    "FD": "HENDRI SULAIMAN",
    "FE": "HERI SISWANTO",
    "FF": "RIKKA ELEKSI",
    "FG": "WULANDARI",
    "FH": "ABDUL QAHAR MUDZAKKIR",
    "FI": "MELLIANTHY ANDIYANI",
    "FJ": "AGNES HASYIM",
    "FK": "LIDYA CHRISNAWATY E",
    "FL": "MORRI ZAKI",
    "FM": "RIZTQI FEBY MULYADI",
    "FN": "HARRY RIZA NUGRAHA",
    "FO": "DANI RAMDANI",
    "FP": "KANTOR PUSAT CIPANAS",
    "FQ": "ASEP MULYANA",
    "FR": "FIRMANSYAH",
    "FS": "DAOS TRIANA",
    "FT": "FEBY ARDIANSYAH",
    "FU": "KANTOR CABANG SUKABUMI",
    "FV": "YUSUF ADIWIJAYA",
    "FW": "IWAN BURHANUDIN",
    "FX": "YUDHI RACAHARDJO",
    "FY": "RAYMON SIBORO",
    "FZ": "ENANG RUSLIANA",
    "GA": "BIMO PUTRA DIANATA",
    "GB": "IWAN BURHANUDIN",
    "GC": "RUTH ANGELINA SANJAYA",
    "GD": "HENDRI PERDANA",
    "GE": "FAJAR AKBAR",
    "GF": "DESTIARA DITA",
    "GG": "SUHARTO",
    "GH": "SASONGKO MILOEREDJO",
    "GI": "ANDIKA PRIMANDESERA",
    "GJ": "ACHMAD MIRZA FAHLEVI",
    "GK": "YUNITA ROSALINA SIMANJUNTAK",
    "GL": "ANDREAS FERNANDO BRAHMANA",
    "GM": "ADES MULYAWAN",
    "GN": "ANIS RAHMATIKA",
    "GO": "VICA PRATIWI",
    "GP": "ANISA TRI ANDINI",
    "GQ": "MUHAMMAD BILL FIQIH",
    "GR": "SAIFUL BAHRI",
    "GS": "MARIO SOEDJONO",
    "GT": "ARDIFU BANGKIT",
    "GU": "ROY BASTIAN NAPITUPULU",
    "GV": "ARDIE SEPTIAN",
    "GY": "TAUFIK HIDAYAT",
    "GZ": "ZAENAL",
    "HA": "EKO MIHARDJA",
    "HB": "RAFI DELFIAN WIBOWO",
    "HC": "SALSABILA MAULIDYA",
    "HD": "MEGALENSI KHOLBUNIAH",
    "HE": "KEZIA GEOFANY MAHODIM",
    "HF": "ERBA RAFSANJANI F",
    "HG": "KATRINA SAFEREN",
    "HH": "FADELA INTAN",
    "HI": "HANDRISZA PRIADANA",
    "HJ": "YAN SAMUEL",
    "HK": "SUGENG PRAYITNO",
    "HL": "SYAM IRVAN RANGKUTI",
    "HM": "INTAN HERDIANA",
    "HN": "DITA ANGGRAENI",
    "HO": "FIRLI YOGA PRADIPTA",
    "HP": "SOLEHUDIN",
    "HQ": "TULUS BOYLE NAIBAHO",
    "HR": "DITA ANGGRAENI",
    "HS": "AULIA ANDHIKA SHALNA",
    "HT": "HENRY KURNIADI HARTAWAN",
    "HU": "AANG WAHYUDI",
    "HV": "PUTRI ARIYANTI",
    "HW": "MUSTIKA AGFIYANTI",
    "HX": "OULA FALAHIYAH",
    "HY": "FAJRIN ARDIANSYAH",
    "HZ": "HERI APRIYANTO",
    "IA": "HERYANDI",
    "IB": "MUHAMAD RIZKILAH",
    "IC": "SANDRA LASTIYANI",
    "ID": "WIRDA HAYATUN NUPUS",
    "IE": "VICKY SUCI DWILINGGA",
    "IF": "INDRA PANCA PUTRA",
    "IG": "M AZIZUN GHAFUR",
    "IH": "BRIYANDO WESLEY",
    "II": "BIANCA CAROLINA",
    "IJ": "MELLIANTHY ANDIYANI",
    "IK": "HELEN GUSTIKA",
    "IL": "FADHYAL MUBDIARTO",
    "IM": "UGIN GUNAWAN",
    "IN": "ADBULLAH GOZALI",
    "IO": "TESSALONIKA VANIA CHRISTY",
    "IP": "ADI WISNU SUMAATMAJA",
    "IQ": "MUHAMMAD REZA",
    "IR": "EDDY PURNOMO KURNIAWAN",
    "IS": "MOHAMMAD YAZID AKBAR",
    "IT": "MOHAMMAD YAZID AKBAR",  # SEMENTARA - TOLONG KASIH TAU NAMA YANG BENAR
    "IU": "ANDI FAJJAR RIFAI",
    "IV": "ANDREAS DIWAN ADITYA",
    "IW": "JOSSIE MARGARETHA N",
    "IX": "JUPI SUPRIATNA",
    "IY": "LAILATUL PITRIYAH",
    "IZ": "M HAEKAL HARIZ",
    "JA": "MAHESA MUHAMMAD",
    "JB": "NOVALISA PUTRI",
    "JC": "REGINA SAKO WURDELA PUTRI",
    "JD": "REGINALD MOZETTA JANUARDY",
    "JE": "RIFMA ISTIFARIANA",
    "JF": "VINSENSIA ELZANORA SIMBOLON",
    "JG": "YUDO HIDAYATULLOH",
    "JH": "MARTEN HENDRA",
    "JI": "YUNIAR LESTARI",
    "JJ": "RIMA SILVIANA AZIZAH",
    "JK": "PRIMA HARTANTO",
    "JL": "HAFILDA ZEIN HAYATUN NUFUS",
    "JM": "INE NURIDA",
    "JN": "JESSLYN EMILY",
    "JO": "CHRISTINA SRI ARIYANTI",
    "JP": "NABILA SYAFIRA ADLY",
    "JQ": "JEQUIN GIJSBERTHA HUN",
    "JR": "FAWWAZATHA AHMAD MUFLIH",
    "JS": "KLARA NOVI SARI",
    "JT": "REGAN LAURENT",
    "JU": "AGIL MUSTAQIM",
    "JV": "SERENA KARTIKASARI",
    "JW": "MEDITA AISYAH PUTRI",
    "JX": "NICHOLAS BIMO",
    "JY": "MUHAMMAD AULIA DANISWARA",
    "JZ": "ZEDEKIAN ZHEN",
    "K0": "KANTOR KALBAR",
    "K1": "ACHMAD RIDWAN",
    "K2": "CLARA SANTA ANGKAMOR",
    "K3": "JENIFER",
    "K4": "OLIVA RHEA NERISSA ARVIANA",
    "K5": "SUSI",
    "K6": "TAN ERZAL JULIANDI",
    "K7": "ALBERTA ELDA PARERA",
    "K8": "NABILA WIDYA ANDITA",
    "K9": "KANTOR CABANG SIANTAN",
    "KA": "ABDUL WAHAB",
    "KB": "AJENG ASTRI KUSUMA INDRANITYAS",
    "KC": "AKBAR MAULANA",
    "KD": "APOLONIA",
    "KE": "ANIZA APRIYANTI",
    "KF": "JESIKA DWI HARNI",
    "KG": "NOVITA ANGGRAENI",
    "KH": "REZA JUNIZARPUTRA",
    "KI": "YOSNOTO",
    "KJ": "MARIA ELAWATI",
    "KL": "KHOSIN",
    "KM": "STEVANIA NADA WILANDA",
    "KN": "ESTHER PUTRI WIDYAWATI",
    "KO": "JULIO PRATAMA PUTRA",
    "KP": "SANNY YUNITA ROHANA PANDIANGAN",
    "KQ": "STEFEN PRATAMA",
    "KR": "YUDHA PRAWIRA ISKANDAR",
    "KS": "HARIS FADILLAH",
    "KT": "RIO PRATAMA",
    "KU": "MUHAMMAD ARVIN",
    "KV": "M FITRAH",
    "KW": "DANIEL ROVALDI RAJAGUGUK",
    "KX": "FARHAN LANDI",
    "KY": "ARI SAPUTRA",
    "KZ": "PRISKA SENJA AFRENI",
    "LA": "AGUNG PURWOWIJI HARTONO",
    "LB": "MERINDA DWI SAPUTRI",
    "LC": "DONI STEPANUS SILAEN",
    "LD": "ROBY SAPUTRA PARSAULIAN T",
    "LE": "FAUZIAH RAHMAH",
    "LF": "M ARKAN MULTAHADI",
    "LG": "STEFANUS DAPID",
    "LH": "YUSTINUS WIWIL",
    "LI": "OKTAPRIYANTO PAKPAHAN",
    "LJ": "DANY VILES",
    "LK": "SYARRAH RANGGA PUTRI",
    "LL": "IRMA CHRISTINE FENELLA LAOWO",
    "LM": "JANIES ADITYA PUTRA",
    "RA": "PT. BPR UNIVERSAL",
    "RB": "EKO SAPUTRA",
    "RC": "ROCKY SILVISTER",
    "RD": "ADAM M. NUGRAHA",
    "RE": "RICO SIBORO",
    "RF": "HERMAN",
    "RG": "MANONDANG SIMARMATA",
    "RH": "RIKA AYU WULANDARI",
    "RI": "NENNY SAFITRI EDWARD",
    "RJ": "WILLIAMAN SAGALA",
    "RK": "ADINDA JULYANA",
    "RL": "HAPSARI DYAH KUSUMANINGTYAS",
    "SA": "KC JAMBI",
    "SB": "NANDO",
    "SC": "RIZKI WENDIKA",
    "SD": "ROBY SAPUTRA",
    "SE": "RIO SINURAT",
    "SF": "DWI SUSILO",
    "SG": "RIKI RIYANTO",
    "SH": "ROBBY ANDY PUTRA",
    "SI": "ARI SUHENDAR",
    "SJ": "RENDY PURBA",
    "SK": "SURYA YUDATAMA",
    "SL": "NAJMI HABIBI",
    "SM": "BUDI SANTOSO",
    "SN": "SYAHRIZAL ADLI",
    "SV": "SPV FRONT LINER KP EMERALD",
    "TF": "FINTECH",
    "TR": "TREASURY KP PUSAT EMERALD",  # SEMENTARA - TOLONG KASIH TAU NAMA YANG BENAR
    "YY": "KANTOR",
    "ZZ": "CUSTOMER SERVICE",
}

# ============================================================
# 8. FUNGSI TRANSLATE
# ============================================================

def translate_cabang(kode):
    """Translate kode cabang ke nama cabang (support 1 atau 001)"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    
    val = str(kode).strip()
    
    if val in CABANG_MAP:
        return CABANG_MAP[val]
    
    val_clean = val.lstrip('0') or '0'
    if val_clean in CABANG_MAP:
        return CABANG_MAP[val_clean]
    
    return val

def translate_pekerjaan(kode):
    """Translate kode pekerjaan ke nama pekerjaan"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    val = str(kode).strip()
    return PEKERJAAN_MAP.get(val, val)

def translate_status_kawin(kode):
    """Translate kode status kawin ke keterangan"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    val = str(kode).strip()
    return STATUS_KAWIN_MAP.get(val, val)

def translate_bentuk_usaha(kode):
    """Translate kode bentuk usaha ke nama"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    val = str(kode).strip().upper()
    return BENTUK_USAHA_MAP.get(val, val)

def translate_penghasilan(kode):
    """Translate kode penghasilan ke range (support 1 atau 01)"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    
    val = str(kode).strip()
    
    if val in PENGHASILAN_MAP:
        return PENGHASILAN_MAP[val]
    
    val_clean = val.lstrip('0') or '0'
    if val_clean in PENGHASILAN_MAP:
        return PENGHASILAN_MAP[val_clean]
    
    return val

def translate_kriteria_tkm(kode):
    """Translate kode kriteria TKM ke deskripsi"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    val = str(kode).strip()
    return KRITERIA_TKM_MAP.get(val, val)

def translate_ao(kode):
    """Translate kode AO ke nama lengkap"""
    if kode is None or kode == "-" or kode == "":
        return "-"
    val = str(kode).strip().upper()
    return AO_MAP.get(val, val)

# ============================================================
# 9. FUNGSI TRANSLATE OTOMATIS (berdasarkan nama kolom)
# ============================================================

def translate_value(column_name, value):
    """Translate value berdasarkan nama kolom (support prefix apapun)"""
    # Handle nilai kosong - FIX NAN
    if value is None or value == "-" or value == "" or str(value).upper() in ["NAN", "NULL", "NONE"]:
        return "-"
    
    val_str = str(value).strip()
    
    # Bersihin nama kolom dari prefix (M4CU.tab_, M4CUI.tab_, dll)
    col_clean = re.sub(r'^[A-Z0-9]+\.tab_', '', column_name)
    col_clean = col_clean.upper()
    
    # === CABANG / BRANCH ===
    if "BRANCH" in col_clean or "CABANG" in col_clean or "CUBRCO" in col_clean or "BRCODE" in col_clean:
        return translate_cabang(val_str)
    
    # === PEKERJAAN ===
    if "PEKERJAAN" in col_clean or "CUKRJA" in col_clean or "JOB" in col_clean or "PROFESI" in col_clean:
        return translate_pekerjaan(val_str)
    
    # === STATUS KAWIN ===
    if "STATUS KAWIN" in col_clean or "CUMRST" in col_clean or "MARITAL" in col_clean:
        return translate_status_kawin(val_str)
    
    # === BENTUK USAHA ===
    if "BENTUK USAHA" in col_clean or "BENTUK BADAN" in col_clean:
        return translate_bentuk_usaha(val_str)
    
    # === PENGHASILAN ===
    if "PENGHASILAN" in col_clean or "INCOME" in col_clean or "CUINCM" in col_clean:
        return translate_penghasilan(val_str)
    
    # === AO ===
    if "AO" in col_clean or "ACCOUNT OFFICER" in col_clean or "CUAOCO" in col_clean or "A/O" in col_clean:
        return translate_ao(val_str)
    
    # === KRITERIA TKM ===
    if "KRITERIA" in col_clean or "TKM" in col_clean:
        return translate_kriteria_tkm(val_str)
    
    # Tidak ada mapping, return value asli
    return val_str
