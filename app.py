import streamlit as st
import pandas as pd
import io
import re

# ============================================================
# 1. KONFIGURASI
# ============================================================
st.set_page_config(page_title="Visual Data Mapper", layout="wide")
st.title("📊 Visual Data Mapper")
st.write("Upload file .tab, pilih kolom yang mau digabung")

# ============================================================
# 2. HARDCODE HEADER (SEMUA SHEET DARI EXCEL LO)
# ============================================================

# Format: "NAMA_SHEET": [header_kode, header_deskripsi]
# - header_kode: baris pertama (kode kolom)
# - header_deskripsi: baris kedua (penjelasan) - bisa sama dengan kode kalau cuma 1 baris

HEADER_MAPPING = {
    "M5RE": {
        "kode": ["RESTAT", "RECODE", "RENAME", "RETELP", "RECUCO", "RECYCO", "REBRCO", "REOWCO", "REATCO", "REFSTA", "REDTOD", "REODRT", "REAECO", "REFIFL", "REBCBL", "REBLBL", "RECLBL", "RELDBL", "REHLBL", "REK1BL", "REK2BL", "REMIBL", "REITCO", "REDIST", "RELPGA", "REDYAS", "REDTLA", "REDTNA", "REDTLT", "REDTBG", "REDTEN", "REAACO", "REFAST", "REFSUB", "REFSAC", "REFBLD", "REFBLC", "REFRFD", "REFRFC", "REFPAD", "REFPAC", "REDTSC", "REDTLC", "REKIOS", "RDITCO", "RDISDR", "RDDYIS", "RDFPIN", "RDDTAI", "RDCALD", "RDPAMT", "RDDTBP", "RDDTEP", "RDOWCO", "RDDNUM", "RDFACO", "RDLOCO", "RDECCO", "RDCOCO", "RDDTLC", "RCITCO", "RCISCR", "RCDYIS", "RCFPIN", "RCDTAI", "RCCALD", "RCCNUM", "RCBSTX", "RCDTLC"],
        "deskripsi": ["Status record", "A/C Number", "A/C Name", "Phone Number", "Customer code", "Currency Code", "Branch", "Golongan pemilik", "A/C type", "Account Status", "O/D rate value date", "Overdraft Rate Code", "Alternate Address Code", "Flag-2 biaya", "Begin.Clear Balance", "Saldo Akhir Rek.Koran", "Clear Balance", "Ledger Balance", "Hold Balance", "Kliring Balance 1", "Kliring Balance 2", "Minimum Balance", "User Group", "Distribution Code", "Last Page Account Stmt", "Account Statement Day", "Date Last A/C Stmt Print", "Date Next A/C Stmt Print", "Date Last Tran by Cust.", "Date Acc. Opened", "Date Acc. Closed", "Alternate Address Code", "Freq.Account Statement-M/L", "Sub. data Y/N", "Stop Accrual Y/N", "Block Debit", "Block Credit", "Refer Debit", "Refer Credit", "Print Advice", "Print Advice", "Date last entry S/C", "Tanggal diubah", "Kiosk", "Interest Type Code", "Interest Sub-Type", "Interest Statem. Day Debit", "Print Interest Statement Dr.", "Available Date Int.Sub-Type", "Calc.Days", "Plafond Amount", "Start Date Plafond", "Finish Date Plafond", "Golongan pemilik", "Debit Account No", "Facility Code", "Location Code", "Economical Sector Code", "Collectibility Code", "Tanggal diubah", "Interest Type Code", "Interest Sub-Type", "Interest Statem. Day Credit", "Print Interest Statement Cr.", "Available Date Int.Sub-Type", "Calc.Days", "Credit Account No", "Base Rate Tax", "Tanggal diubah"]
    },
    "H8PO": {
        "kode": ["POSTAT", "PORECO", "PODTVL", "POREFN", "PODTPO", "POTRCO", "PODESC", "POAMNT", "POFPRS", "PODPCO", "POFSTA", "PODTLC", "POOVRT", "POOVER", "POREIF", "POCYCO", "POBRCO", "POBRCA", "POUSER", "POTECN", "POBCHN", "PODISP", "POAUTU", "PODTEY", "POTIME", "POPROG", "POMODU", "POCUCO"],
        "deskripsi": ["Status record", "A/C Number", "Value Date", "No. Referensi", "Posting Date", "Transaction Code", "Transaction Description", "Transaction Amount", "Print in statement Y/N", "Department Code", "0=Not yet, 1=Printed", "Tanggal diubah", "Override Type", "Override Supervisor Id", "Account Number Information", "Currency Code", "Branch Code Trans.", "Branch Code Account", "User ID", "Counter", "Batch", "Display ID", "Authorizer", "Entry date", "Entry time", "Program", "Module", "Customer code"]
    },
    "D5DO": {
        "kode": ["DOSTAT", "DONUMB", "DONAME", "DODECO", "DOTYPE", "DOCYCO", "DOBRCO", "DOCUCO", "DOAECO", "DOWAKT", "DOJEWA", "DOFREQ", "DOROLI", "DOFLRV", "DOFLRP", "DOFLBA", "DOFLPJ", "DORATE", "DORTBF", "DOFARO", "DOPAJK", "DODTBG", "DODTVL", "DODTEP", "DODTPB", "DODTPI", "DODTCL", "DODTPP", "DODTRC", "DODTRB", "DOCALD", "DOERT1", "DOERT2", "DOCLBL", "DOTBUA", "DOTBUC", "DOTBUB", "DOBUCD", "DOBUCH", "DOBUCL", "DOBUAJ", "DOFLBK", "DOFLST", "DOPNRL", "DOINRL", "DOSNRD", "DOSNRC", "DOSIRC", "DODTIL", "DODTF1", "DODTF2", "DOAMF1", "DOAMF2", "DODTLC", "DOISCO", "DOACNO", "DOBANK", "DOFLNI", "DODES1", "DODES2", "DODES3"],
        "deskripsi": ["Status record", "Nomor Deposito", "Nama Pemegang Deposito", "Deposit Code", "1=T/D,2=Doc,3=C/D", "Currency Code", "Branch", "Customer code", "Alternate Address Code", "Jangka Waktu", "1=harian,2=bulanan", "Payment Frequence", "RollOver Indicator", "Flag Pembatalan", "Flag Restitusi Pajak", "Flag Bayar Pokok", "", "Rate bunga", "Spread Rate Bunga", "Flag Rate ARO", "Base Rate Pajak", "Tanggal Dimasukkan", "Tanggal Berlaku", "Tanggal Pokok Jatuh Tempo", "Tanggal (hari) Pembayaran", "Tanggal Bunga Jatuh Tempo", "Tanggal Tutup Deposito", "Tanggal Bayar Pokok", "Bayar Bunga Terakhir", "", "360 365 366 12", "", "", "Nilai Nominal Deposito", "Akumulasi Bunga Jatuh Tempo", "Akumulasi Cadangan Bunga", "Akumulasi Bunga Dibayar", "Cad. Bunga Sampai Sekarang", "Cad. Bunga Sampai Kemarin", "Bunga Belum Dibayarkan", "Adjustment Bunga", "Flag Blokir", "Flag Cetak Bilyet", "Akumulasi Pajak Bunga", "Pajak Bunga Belum Dibayarkan", "Rekening Penempatan", "Rekening Settlement Pokok", "Rekening Settlement Bunga", "Tanggal Bunga Terakhir", "Tanggal", "Tanggal", "Tanggal", "Tanggal", "Tanggal diubah", "Interest Sub-Type", "Nomor Account", "Nama Bank Penerima", "1=Nm,2=It,3=Nm+It", "Keter./Narasi-1", "Keter./Narasi-2", "Keter./Narasi-3"]
    },
    "M4CUAPPU": {
        "kode": ["Status record", "Customer code", "Customer Name", "Risk Factor", "Deskripsi Risk Factor", "Domisili 1", "Domisili 2", "Domisili 3", "Domisili 4", "Flag PPT", "Red Flag", "No.KIMS/KITAP", "Kode Pekerjaan", "Sumber Dana", "Deskripsi Sumber Dana", "Tujuan Penggunaan Dana", "Deskripsi Tujuan Dana", "Job Type Relation", "Nama Pengurus 1", "Nama Pengurus 2", "Nama Pengurus 3", "Nama Pengurus 4", "Nama Pengurus 5", "Kode Pengurus 1", "Kode Pengurus 2", "Kode Pengurus 3", "Kode Pengurus 4", "Kode Pengurus 5", "Beneficiary Owner", "Beneficiary Owner Name", "Alamat ID 1", "Alamat ID 2", "Kelurahan", "Kecamatan", "Kota", "Propinsi", "Kode Pos", "Domisili BO 1", "Domisili BO 2", "Domisili BO 3", "Domisili BO 4", "Kode Area", "Telephon", "Handphone", "Jenis Kelamin", "Agama", "Tempat Lahir", "Tgl Lahir", "Status Perkawinan", "Sumber Dana BO", "Deskripsi Sumber Dana BO", "Tujuan Dana BO", "Deskripsi Tujuan Dana BO", "Rata-Rata Penghasilan", "Informasi BO", "No. Izin Usaha", "Bentuk Usaha", "Bidang Usaha", "Identitas Nasabah", "Lokasi Usaha", "Profil Nasabah", "Jumlah Transaksi", "Kegiatan Usaha", "Struktur Kepemilikan", "Informasi Lain", "Resume Akhir", "Branch", "Beginning Date Customer", "Date Input", "Time Input", "User Input", "User Otor", "Time Otor", "Date Last Update"],
        "deskripsi": []  # Langsung pake kode sebagai deskripsi
    },
    "M4CU": {
        "kode": ["CUSTAT", "CUCODE", "CUNAME", "CUTITL", "CUADR1", "CUADR2", "CUADR3", "CUTELP", "CUTEL2", "CUFAXN", "CUINCO", "CUSHOR", "CUBRCO", "CUFPAR", "CUCPAR", "CUAOCO", "CUIDCO", "CUARCO", "CUNPWP", "CUDTBG", "CUAUTU", "CUUSER", "CUDTLC", "CUAGAM", "CUKRJA", "CUJEKL", "CUDTLH", "CUNKTP", "CUDTID", "CUNECO", "CUPERS", "CUFLTY", "CUFLPP", "CUOWCO"],
        "deskripsi": ["Status record", "Customer code", "Customer Name", "Titel", "Address-1", "Address-2", "City", "Phone Number 1", "Phone Number 2", "Fax Number", "Institution Code", "Short name", "Branch", "Flag Parent Cust. 0=Yes;1=No", "Parent No.", "A/O code", "Industry Code", "Area Code", "NPWP Nasabah", "Beginning Date Customer", "Authorizer", "Operator-Id", "Tanggal diubah", "Agama", "Pekerjaan", "Jenis kelamin", "Birth date", "ID card number", "ID expire date", "Country", "Contact person", "Customer type", "P.P.H type", "Golongan pemilik"]
    },
    "M4CUI": {
        "kode": ["CUCODE", "CUTITL", "CUSHOR", "CUJEKL", "CUAGAM", "CUPLBR", "CUDTLH", "CUMRST", "CUHOBI", "CUNSPO", "CUNCHL", "CUNPRT", "CURSDS", "CUYRSD", "CUMRSD", "CUEDUC", "CUCTFL", "CUCTZC", "CUIDTY", "CUIDNO", "CUDTPB", "CUDTID", "CUCC01", "CUCL01", "CUCC02", "CUCL02", "CUATM1", "CUATM2", "CUIKRJ", "CUPSTN", "CUCPN1", "CUTCP1", "CUADP1", "CUADP2", "CUCITP", "CUZIPP", "CUPPA1", "CUPPN1", "CUEXT1", "CUPPA2", "CUPPN2", "CUEXT2", "CUPFXA", "CUPFXN", "CUINCM", "CUFRIC", "CUFRDN", "CUTOIC", "CUIDIN", "CUITIN", "CUIUIN", "CUIUOT", "CUITOT", "CUIDLT"],
        "deskripsi": ["Customer code", "Titel", "Short name", "Jenis kelamin", "Agama", "Place Birth", "Birth date", "Marital Status", "Hobbies", "Numbers Wife", "Numbers Child", "Numbers Parents", "Phone#1", "Lama Tahun menempati", "Lama Bln Menempati", "Education Code", "CitizenShip Flag", "Citizenship Code", "ID Type", "ID Number", "Publish Date", "ID expire date", "Credit Card #1", "Credit Limited #1", "Credit Card #2", "Credit Limited", "ATM #1", "ATM #2", "Job Type", "Position Job", "Company Name", "Type Company", "Address #1", "Address #2", "City", "Zip Code", "Kode Area", "Phone #1", "Ext #1", "Kode Area", "Phone #2", "Ext #2", "Fax Area", "Facsimile", "Income per Month", "Sumber Penghasilan", "Sumber Dana", "Tujuan Penggunaan", "Date Input", "Time Input", "User Input", "User Otor", "Time Otor", "Date Last Update"]
    },
    "M4CUG": {
        "kode": ["CUSTAT", "CUCODE", "CUNAME", "CUADR1", "CUADR2", "CUADR3", "CUADR4", "CUADR5", "CUZIPC", "CUADR6", "CUPHA1", "CUPHN1", "CUPHA2", "CUPHN2", "CUMBLN", "CUFAXA", "CUFAXN", "CUMAIL", "CUNPWP", "CUDSRT", "CURLFL", "CUFLTY", "CUFPAR", "CUAOCO", "CURSKF", "CUFLPP", "CUPRMF", "CUREDF", "CUBRCO", "CUDTBG", "CUWICO", "CUGDIN", "CUGTIN", "CUGUIN", "CUGUOT", "CUGTOT", "CUGDLT"],
        "deskripsi": ["Status record", "Customer code", "Customer Name", "Address-1", "Address-2", "Address #3", "Address #4", "City", "Zip Code", "Province", "Area Code Phone#1", "Phone#1", "Area Code Phone#2", "Phone#2", "Seluler #", "Area Code Fax", "Fax No", "Email Address", "NPWP #", "Desrert/Non Desert", "Relation Flag", "Customer Type", "Flag Parent Customer", "A/O code", "Risk Factor", "P.P.H type", "Prime Customer", "Red Flag", "Branch", "Beginning Date", "Kode Wilayah", "Date Input", "Time Input", "User Input", "User Otor", "Time Otor", "Date Last Update"]
    },
    "M4CUGE": {
        "kode": ["CUSTAT", "CUCODE", "CUNAME", "CUNAME2", "CUNAME3", "CUNAME4", "CUADR1", "CUADR2", "CUADR1A", "CUADR2A", "CUADR3", "CUADR4", "CUADR5", "CUZIPC", "CUADR6", "CUADR7", "CUPHA1", "CUPHN1", "CUPHA2", "CUPHN2", "CUPHA3", "CUPHN3", "CUMBLN", "CUMBLN2", "CUMBLN3", "CUFAXA", "CUFAXN", "CUFAXA2", "CUFAXN2", "CUFAXA3", "CUFAXN3", "CUFRICH", "CUFRDNH", "CUTOICH", "CUIBUN", "CUNMPS", "CUPLPS", "CUDTPS", "CUIDPS", "CUINPS", "CUKRPS", "CUADPS1", "CUADPS2", "CUCIPS", "CUNMPJ", "CUADPJ1", "CUADPJ2", "CUCIPJ", "CUPHPJ", "CURLPJ", "CUGDIN", "CUGTIN", "CUGUIN", "CUGUOT", "CUGTOT", "CUGDLT"],
        "deskripsi": ["Status record", "Customer code", "NAME #1", "NAME #2", "NAME #3", "NAME #4", "Address-1", "Address-2", "ADDRESS #1 EXT", "ADDRESS #2 EXT", "Address #3", "Address #4", "City", "Zip Code", "Province", "RT / RW", "Area Code Phone#1", "Phone#1", "Area Code Phone#2", "Phone#2", "Area Code Phone#3", "Phone#3", "Seluler #1", "Seluler #2", "Seluler #3", "Area Code Fax #1", "Fax No #1", "Area Code Fax #2", "Fax No #2", "Area Code Fax#3", "Fax No #3", "SUMBER PENGHASILAN", "SUMBER DANA", "TUJUAN PNG DANA", "NAMA IBU KANDUNG", "NAMA PASANGAN", "TEMPAT LAHIR", "TANGGAL LAHIR", "NO ID", "SUMBER PENGHASILAN", "PEKERJAAN", "ALAMAT", "ALAMAT #2", "KOTA", "NAMA PENJAMIN", "ALAMAT", "ALAMAT #2", "KOTA", "PHONE", "HUBUNGAN DEBITUR", "Date Input", "Time Input", "User Input", "User Otor", "Time Otor", "Date Last Update"]
    },
    "M4CU1D": {
        "kode": ["CDSTAT", "CDCODE", "CDSTDB", "CDKTST", "CDGLDB", "CDDATI", "CDTEMP", "CDNOAK", "CDTAAK", "CDNGIK", "CDGRID", "CDNMGR", "CDGBMK", "CDPBMK", "CDRATE", "CDLBRT", "CDGOPB", "CDDIN", "CDIDDB", "CDCRDT", "CDCRTT", "CDCRUS", "CDUPDT"],
        "deskripsi": ["Status Data", "Customer Code", "Status Debitur", "Keterangan Status", "Golongan Debitur", "Dati2 Debitur", "Tempat Akte Awal Dikeluarkan", "No. Akte Akhir", "Tgl Akte Akhir", "Nama Gadis Ibu Kandung", "Group ID", "Nama Group", "Melanggar BMPK Y/T", "Melampaui BMPK Y/T", "Rating Debitur", "Lembaga Rating", "Go Public Y/T", "Debtor Ident Number", "ID Debitur", "Creation Date", "Creation Time", "Create User", "Update Date"]
    },
    "LLOAN": {
        "kode": ["L0STAT", "L0STAD", "L0BRCA", "L0BRCD", "L0CSNO", "L0FCTY", "L0FCSQ", "L0FISN", "L0FITY", "L0FISQ", "L0LNCS", "L0CSPR", "L0LNNO", "L0LNPR", "L0LNTY", "L0CYCD", "L0NAME", "L0TNGI", "L0ALTN", "L0ECON", "L0INDS", "L0LOCL", "L0TYUS", "L0COLE", "L0COLI", "L0COLS", "L0OWNC", "L0ACOF", "L0NARR", "L0STDT", "L0MTDT", "L0FBRA", "L0FBRC", "L0FLKU", "L0IAFL", "L0PAFL", "L0BWFL", "L0DURA", "L0CALM", "L0BSCD", "L0SPRT", "L0CIRT", "L0DIRT", "L0ADRT", "L0MRRT", "L0MRFL", "L0LNRT", "L0FCRT", "L0FCMT", "L0SSTL", "L0RSTL", "L0ISTL", "L0RASF", "L0IASF", "L0RPTY", "L0RPDT", "L0RPFR", "L0RPDY", "L0RPAM", "L0STPD", "L0NXRP", "L0LSRP", "L0RSFL", "L0IPDT", "L0IPFR", "L0IPDY", "L0IPAM", "L0NXIP", "L0LSIP", "L0IPFL", "L0PNRT", "L0MPMT", "L0PAMO", "L0TDMT", "L0IBVD", "L0PBVD", "L0DVFL", "L0SADT", "L0AJMT", "L0DAMT", "L0ACDT", "L0ACMT", "L0PADT", "L0PAMT", "L0CADT", "L0CAMT", "L0ACTR", "L0DUPI", "L0DUIN", "L0DUPN", "L0PAPI", "L0PAIN", "L0PAPT", "L0PAFE", "L0WOPI", "L0WOIN", "L0WOPN", "L0APPI", "L0APIN", "L0APPT", "L0APFE", "L0AWPI", "L0AWIN", "L0AWPN", "L0PDPI", "L0SDIN", "L0LPPI", "L0LPIN", "L0LPPT", "L0LPFE", "L0WPDT", "L0WIDT", "L0SDDT", "L0WNDT", "L0NOPN", "L0OVFL", "L0OVUS", "L0FJDE", "L0USID", "L0DEPT", "L0LSDA", "L0LJDA", "L0LSTA", "L0AUUS", "L0WSID"],
        "deskripsi": ["Status record", "Status Data", "Wilayah", "Branch", "Customer code", "Facility Type", "Fac. Seq. No", "Cust.No Facilitas", "Fac Type Facilitas", "Fac Seqn Facilitas", "Loan Cust No", "Cust.Parent No", "Loan Number", "Loan Processing", "Loan Type", "Loan Ccy Code", "Loan Holder", "Tangible/ Intangible", "Alternate N/A", "Economical Sector Code", "Industry Code", "Location Code", "Type of Use", "Collectibility External", "Collectibility Internal", "Collectibility System", "Owner Clasf.", "A/O code", "Narrative", "Start Date", "Tanggal", "From Area Code", "From Branch Code", "KUK/Non KUK", "Stop Int.Accr /Amrt", "Stop Penalty Accr.", "Write Off", "Duration", "Calc.Meth (12/360/365-6)", "Base Rate code", "Spread /Rate", "Total/Current Int.Rate", "Dummy Int. Rate", "Int Rate For Advise", "Margin Rate", "Margin Indicator", "Loan Exch Rate", "Fac. Exch Rate", "Facility Amount - Orig", "DrawDwn/Start Settl. A/C", "Repay/Princp. Settl. A/C", "Interest Settl. A/C", "Repay. Auto Sett.Flag", "Int. Auto Sett.Flag", "Repayment Type", "Repayment Date", "Frequency", "Repayment Day No", "Repayment Amount", "StartDate Pric.Deduction", "Next Repayment Date", "Last Repayment Date", "Repayment Sched.Flag", "Int.Payment Date", "Int.Payment Frequency", "Int.Payment Day No", "Interest Amount", "Next Int.Payment Date", "Last Int.Payment Date", "Int.Pay. Revolv. Flag", "Penalty Rate", "Minimum Penalty Amount", "Principle Amount Orig.", "Total Discount Int.Amt.", "Int.Back Value Date", "Princ.Back Value Date", "Div Factor for Accrual", "Stop Int Acc.Date", "Accrue Adj Manual", "Accrue Adj by System", "Last Date Accrued", "Next Amt.Posted Org Ccy", "Last Date Acc.Posted", "Next Amt.Cap. Org Ccy", "Last Date Capitalized", "Tot.Capitalized Org Ccy", "Accrual Days Counter", "Due Principle Amt", "Due Interest Amt", "Due Penalty Amt", "Principle Paid Amount", "Interest Paid Amount", "Penalty Paid Amount", "Fee Paid Amount", "Write Off Principle", "Write Off Interest", "Write Off Penalty", "Principle Paid Unaut.Amt", "Interest Paid Unauth.Amt", "Penalty Paid Unauth.Amt.", "Fee Paid Unauth.Amount", "Unaut.Write Of Principle", "Unaut.Write Off Interest", "Unaut.Write Off Penalty", "Pri/Repay Due Str. Date", "Interest Due Start Date", "Last Principle Pay.Date", "Last Interest Pay. Date", "Last Penalty Pay. Date", "Last Fee Payment Date", "Date Last Write Off Pri.", "Date Last Write Off Int.", "Start Calc Penalty Date", "Date Last Write Off Pnt.", "No. of Penalty", "Override Flag", "Override by", "1st Job Date Entry", "User ID", "Department Code", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Authorize By", "Display ID"]
    },
    "LHPDU": {
        "kode": ["HDSTAT", "HDSTAD", "HDBRCA", "HDBRCD", "HDLNNO", "HDLNPR", "HDCYCD", "HDDTVL", "HDDTEY", "HDSTDT", "HDENDT", "HDREFN", "HDDPMT", "HDDIMT", "HDDNMT", "HDPPMT", "HDPIMT", "HDPNMT", "HDWPMT", "HDWIMT", "HDWNMT", "HDPNRT", "HDSRFL", "HDC1FL", "HDRASF", "HDIASF", "HDRSTL", "HDISTL", "HDACKY", "HDTRCD", "HDSRCE", "HDRSSQ", "HDUSID", "HDAUUS", "HDWSID"],
        "deskripsi": ["Status record", "Status Data", "Wilayah", "Branch", "Loan Number", "Loan Processing", "Loan Ccy Code", "Value Date", "Entry Date", "Start Date", "End Date", "No. Referensi", "Past Due Princ. Amount", "Past Due Intrs. Amount", "Past Due Penal. Amount", "Paid Principle Amt", "Paid Interest Amt", "Paid Penalty Amt", "Write Off Principle Amt", "Write Off Interest Amt", "Write Off Penalty Amt", "Pinalty Rate", "Source Flag", "Clsf-1 Flag", "Rpy.Auto Sett.Flag", "Int.Auto Sett.Flag", "Repay.Sett Account", "Int.Sett Account", "Account Keys", "Transaction Code", "Source Trans", "Repay.Sch. Seqn.", "User ID", "Authorize By", "Display ID"]
    },
    "LHLON": {
        "kode": ["HLSTAT", "HLSTAD", "HLSEQN", "HLCNTR", "HLBRCA", "HLBRCD", "HLLNNO", "HLLNPR", "HLLNTY", "HLCSNO", "HLCYCD", "HLDTVL", "HLDTEY", "HLREFN", "HLDESC", "HLORMT", "HLBQMT", "HLOPMT", "HLOIMT", "HLEXRT", "HLFEXR", "HLLERT", "HLBSCD", "HLCALM", "HLFEEC", "HLSETL", "HLAMTY", "HLRTFL", "HLFTRT", "HLGLFL", "HLFTGL", "HLLNFL", "HLFAFL", "HLPRFL", "HLSRFL", "HLSRCE", "HLC1FL", "HLC2FL", "HLPAFL", "HLBWFL", "HLACKY", "HLCOLC", "HLTRCD", "HLCNFF", "HLSTDT", "HLENDT", "HLOVUS", "HLOVFL", "HLFBRA", "HLFBRC", "HLUSID", "HLDEPT", "HLLSDA", "HLLJDA", "HLLSTA", "HLAUUS", "HLAUDT", "HLAUTM", "HLAUWS", "HLAUFL", "HLWSID"],
        "deskripsi": ["Status record", "Status Data", "Sequence No", "Counter Seq.No.", "Wilayah", "Branch", "Loan Number", "Loan Processing", "Loan Type", "Customer code", "Loan Ccy Code", "Value Date", "Entry Date", "No. Referensi", "Title", "Original Amount", "Base Eqv. Amount", "O/S Principle Amount", "O/S Interest Amount", "Rate", "Fac. Exchange Rate", "Last Exchange Rate", "Base Rate code", "Calc. days", "Fee Code", "Settlement Account", "Amend Type", "Retail Flag", "Flag having Retail Trans", "G/L Flag", "Flag having G/L Trans", "Loan Flag", "Fac Flag", "Process Manual/System", "Source Flag", "Source Trans", "Clsf-1 Flag", "Clsf-2 Flag", "Paid Flag", "Write Off", "Account Keys", "Collectibility", "Transaction Code", "Confirmasi Flag", "Start Date", "End Date", "Override by", "Override Flag", "From Branch Area", "From Branch Code", "User ID", "Department Code", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Authorize By", "Authorize Date", "Authorize Time", "Authorize From", "Auth. Flag Y/N/", "Display ID"]
    },
    "LCOMN": {
        "kode": ["CMSTAT", "CMSTAD", "CMBRCA", "CMBRCD", "CMCSNO", "CMFCTY", "CMFCSQ", "CMSEQN", "CMCLCD", "CMCOTY", "CMCYCD", "CMNRDT", "CMLRDT", "CMMTAS", "CMREFR", "CMDAYN", "CMSTDT", "CMMTDT", "CMFQTY", "CMAMNT", "CMAMIK", "CMAMTC", "CMAMIB", "CMGIVB", "CMNARR", "CMLCSQ", "CMTCSQ", "CMFCOC", "CMFBRC", "CMPGIK", "CMASRC", "CMDEPN", "CMBLDF", "CMFJDE", "CMUSID", "CMWSID", "CMLSDA", "CMLJDA", "CMLSTA", "CMAUUS", "CMLOCA"],
        "deskripsi": ["Status record", "Status Data", "Wilayah", "Branch", "Cust.No Fac.", "Facility Type", "Sequence No", "Sequence No", "Collateral Code", "Coll.Group", "Loan Ccy Code", "Next Review Date", "Last Review Date", "Maturity Assuransi", "Review Freq", "Review Day No", "Start Date", "Maturity Date", "Quantity", "Amount (Orig. CCY)", "Legal.Amt in Orgi-Ccy", "Amount (Base CCY)", "Legal.Amt in Base-Ccy", "Given By", "Narrative", "Last Coll Seq.No", "Total Coll Seq.No", "From Area Code", "From Branch Code", "Kode Pengikatan", "Asuransi", "Deposito Number", "Bloked Deposito", "1st Job Date Entry", "User ID", "Display ID", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Authorize By", "Coll.Location"]
    },
    "LCOMD": {
        "kode": ["CDCSNO", "CDFCTY", "CDFCSQ", "CDSEQN", "CDPRCD", "CDNAMA", "CDADRR", "CDDTII", "CDAGBN", "CDPLNM", "CDAGPL", "CDPRPS", "CDCRDT", "CDCRUS", "CDUPDT", "CDUPUS", "CDIDDB"],
        "deskripsi": ["Customer Code", "Facilitas Type", "Fasilitas Seq", "Sequence #", "Peringkat Surat Bhrg", "Nama Pemilik", "Alamat Pemilik", "Dati II Code", "Agunan Bank", "Penilai Indenpenden", "Agunan Pemilik", "Paripasu %", "Creation Date", "Create User", "Update Date", "Update User", "ID Debitur"]
    },
    "LCOMNE": {
        "kode": ["COSTAT", "COSTAD", "COBRCA", "COBRCD", "COCSNO", "COFCTY", "COFCSQ", "COSEQN", "COCONO", "COCLCD", "COCOTY", "CODTCO", "COMA01", "COMA02", "COMA03", "COMA04", "COMA05", "COMA06", "COMA07", "COMA08", "COMA09", "COMA10", "COMB01", "COMB02", "COMB03", "COMB04", "COMB05", "COMB06", "COMB07", "COMB08", "COMB09", "COMB10", "COMC01", "COMC02", "COMC03", "COMC04", "COMC05", "COMC06", "COMC07", "COMC08", "COMC09", "COMC10", "CORSV1", "CORSV2", "CORSV3", "CORSV4", "CORSV5", "CORSV6", "CORSV7", "CORSV8", "CORSV9", "CORSV0", "CORSVA", "CORSVB", "CORSVC", "CORSVD", "CORSVE", "CORSVF", "CORSVG", "CORSVH"],
        "deskripsi": ["Status record", "Status Data", "Wilayah", "Branch", "Cust.No Fac.", "Facility Type", "Sequence No", "Sequence No", "Nomor Jaminan", "Collateral Code", "Collateral Type", "Kode Detail", "Field01A", "Field02A", "Field03A", "Field04A", "Field05A", "Field06A", "Field07A", "Field08A", "Field09A", "Field10A", "Field01B", "Field02B", "Field03B", "Field04B", "Field05B", "Field06B", "Field07B", "Field08B", "Field09B", "Field10B", "Field01C", "Field02C", "Field03C", "Field04C", "Field 05C", "Field 06C", "Field 07C", "Field 08C", "Field 09C", "Field 10C", "Reserve Field1", "Reserve Field2", "Reserve Field3", "Reserve Field4", "Reserve Field5", "Reserve Field6", "Reserve Field 7", "Reserve Field 8", "Reserve Field 10", "Reserve Field 11", "Reserve Field 12", "Reserve Field 13", "Reserve Field 14", "Reserve Field 15", "Reserve Field 16", "Reserve Field 17", "Reserve Field 18", "Reserve Field 19"]
    },
    "LCOLN": {
        "kode": ["CMSTAT", "CMSTAD", "CMBRCA", "CMBRCD", "CMCONO", "CMCLCD", "CMCYCD", "CMNRDT", "CMLRDT", "CMMTAS", "CMREFR", "CMDAYN", "CMSTDT", "CMMTDT", "CMFQTY", "CMAMNT", "CMAMIK", "CMMVAL", "CMAMTC", "CMAMIB", "CMAMMA", "CMCUNO", "CMGIVB", "CMNARR", "CMLCSQ", "CMTCSQ", "CMFCOC", "CMFBRC", "CMDEPN", "CMBLDF", "CMRECO", "CMPGIK", "CMLOCA", "CMPAPR", "CMDTCO", "CMMA01", "CMMA02", "CMMA03", "CMMA04", "CMMA05", "CMMA06", "CMMA07", "CMMA08", "CMMA09", "CMMA10", "CMMB01", "CMMB02", "CMMB03", "CMMB04", "CMMB05", "CMMB06", "CMMB07", "CMMB08", "CMMB09", "CMMB10", "CMMC01", "CMMC02", "CMMC03", "CMMC04", "CMMC05", "CMMC06", "CMMC07", "CMMC08", "CMMC09", "CMMC10", "CMRSV1", "CMRSV2", "CMRSV3", "CMRSV4", "CMRSV5", "CMRSV6", "CMRSV7", "CMRSV8", "CMRSV9", "CMRSV0", "CMRSVA", "CMRSVB", "CMRSVC", "CMRSVD", "CMRSVE", "CMRSVF", "CMRSVG", "CMRSVH", "CMFJUS", "CMFJWS", "CMFSDA", "CMFJDE", "CMFSTA", "CMLJUS", "CMLJWS", "CMLSDA", "CMLJDA", "CMLSTA", "CMAUUS", "CMAUWS", "CMAULS", "CMAULJ"],
        "deskripsi": ["Status record", "Status Data", "Wilayah", "Branch", "Nomor Jaminan", "Collateral Code", "Loan Ccy Code", "Next Review Date", "Last Review Date", "Maturity Assuransi", "Review Freq", "Review Day No", "Start Date", "Maturity Date", "Quantity", "Amount (Orig. CCY)", "Legal.Amt in Orgi-Ccy", "Market.Val in Orgi-Ccy", "Amount (Base CCY)", "Legal.Amt in Base-Ccy", "Market.Val in Orgi-Ccy", "Customer Code", "Given By", "Narrative", "Last Coll Seq.No", "Total Coll Seq.No", "From Area Code", "From Branch Code", "Deposito Number", "Bloked Deposito", "A/C Number", "Kode Pengikatan", "Coll.Location", "Persentase Paripasu", "Kode Detail", "Field 01A", "Field 02A", "Field 03A", "Field 04A", "Field 05A", "Field 06A", "Field 07A", "Field 08A", "Field 09A", "Field 10A", "Field 01B", "Field 02B", "Field 03B", "Field 04B", "Field 05B", "Field 06B", "Field 07B", "Field 08B", "Field 09B", "Field 10B", "Field 01C", "Field 02C", "Field 03C", "Field 04C", "Field 05C", "Field 06C", "Field 07C", "Field 08C", "Field 09C", "Field 10C", "Reserve Field 01", "Reserve Field 02", "Reserve Field 03", "Reserve Field 04", "Reserve Field 05", "Reserve Field 06", "Reserve Field 07", "Reserve Field 08", "Reserve Field 10", "Reserve Field 11", "Reserve Field 12", "Reserve Field 13", "Reserve Field 14", "Reserve Field 15", "Reserve Field 16", "Reserve Field 17", "Reserve Field 18", "Reserve Field 19", "1st Job User Entry", "1st Job Display Entry", "1st Sys Date Entry", "1st Job Date Entry", "1st Time Entry", "Last Job User Amend", "Last Job Display Amend", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Authorize By", "Auth. Display", "Last Sys Date Auth.", "Last Job Date Auth."]
    },
    "LNDGRH": {
        "kode": ["GRHSTA", "GRHWIL", "GRHBRC", "GRHGRP", "GRHDES", "GRHNAM", "GRHAD1", "GRHAD2", "GRHAD3", "GRHTL1", "GRHTL2", "GRHACC", "GRHIDT", "GRHITM", "GRHIUS", "GRHCDT", "GRHCTM", "GRHCUS", "GRHODT", "GRHOTM", "GRHOUS", "GRHF01", "GRHF02", "GRHF03", "GRHF04", "GRHF05", "GRHF06", "GRHF07", "GRHF08", "GRHF09", "GRHF10"],
        "deskripsi": ["Status", "Kode Wilayah", "Kode Cabang", "Kode Group Bendahara", "Keterangan Bendahara", "Nama Pen.Jawab", "Alamat-1", "Alamat-2", "Alamat-3", "Telpon-1", "Seluler-1", "Rekening Bendahara", "Input Date", "Input Time", "Input By User", "Change Date", "Change Time", "Change By User", "Otor Date", "Otor Time", "Otor By User", "Reserve Field-01", "Reserve Field-02", "Reserve Field-03", "Reserve Field-04", "Reserve Field-05", "Reserve Field-06", "Reserve Field-07", "Reserve Field-08", "Reserve Field-09", "Reserve Field-10"]
    },
    "UBRME": {
        "kode": ["LBSTAT", "LBCODE", "LBCOD1", "LBCOD2", "LBDESC", "LBDESL", "LBRSV1", "LBRSV2", "LBRSV3", "LBRSV4", "LBRSV5", "LBOTHE", "LBAUTH", "LBUSR1", "LBBDTE", "LBDSP1", "LBUSR2", "LBDSP2"],
        "deskripsi": ["STATUS", "TABLE CODE", "SID CODE", "LBU CODE", "DESCRIPTION", "DESCRIPTION", "RESERVE 1", "RESERVE 2", "RESERVE 3", "RESERVE 4", "RESERVE 5", "RESERVED", "AUTH.", "USER TX", "LAST CHANGE", "W.S ID", "USER OT", "W.S ID"]
    },
    "M5KSE": {
        "kode": ["KSESTS", "KSETYP", "KSEACC", "KSEBRC", "KSECKS", "KSERSV", "KSEUSR", "KSEDAT", "KSETIM"],
        "deskripsi": ["Status", "Tipe D/L/R", "Account#", "Branch", "Kios Cd.", "Reserve 01", "User Entry", "Entry Date", "Entry Time"]
    },
    "LNDGRD": {
        "kode": ["GRDSTA", "GRDGRP", "GRDWIL", "GRDBRC", "GRDSEQ", "GRDSGR", "GRDNAM", "GRDACC", "GRDTL1", "GRDTL2", "GRDIDT", "GRDITM", "GRDIUS", "GRDCDT", "GRDCTM", "GRDCUS", "GRDODT", "GRDOTM", "GRDOUS", "GRDF01", "GRDF02", "GRDF03", "GRDF04", "GRDF05", "GRDF06", "GRDF07", "GRDF08", "GRDF09", "GRDF10"],
        "deskripsi": ["Status", "Kode Group Bendahara", "Wilayah", "Branch Code", "Sequence", "Sub Group Bendahara", "Nama Pen.Jawab", "Rek.Sub Group", "Telpon-1", "Seluler-1", "Input Date", "Input Time", "Input By User", "Change Date", "Change Time", "Change By User", "Otor Date", "Otor Time", "Otor By User", "Reserve Field-01", "Reserve Field-02", "Reserve Field-03", "Reserve Field-04", "Reserve Field-05", "Reserve Field-06", "Reserve Field-07", "Reserve Field-08", "Reserve Field-09", "Reserve Field-10"]
    },
    "LFSBI": {
        "kode": ["FSSTAT", "FSSTAD", "FSBRCA", "FSBRCD", "FSCSNO", "FSFCTY", "FSFCSQ", "FSECON", "FSINDS", "FSLOCL", "FSTYUS", "FSCOLC", "FSOWNC", "FSSIFT", "FSGOKR", "FSLOK2", "FSGOPJ", "FSBADJ", "FSKOPI", "FSFJDE", "FSFTME", "FSUSID", "FSDEPT", "FSLSDA", "FSLJDA", "FSLSTA", "FSWSID", "FSAUUS"],
        "deskripsi": ["Status record", "Status Data", "Wilayah", "Branch", "Customer code", "Facility Type", "Fac. Seq. No", "Economical Sector Code", "Industry Code", "Location Code", "Type of Use", "Collectibility", "Owner Clasf.", "Sifat", "Golongan Kredit", "Lokasi 2", "Golongan Penjamin", "Bagian yg Dijamin", "Kode Pengikatan", "1st Job Date Entry", "1st Entry Time", "User ID", "Department Code", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Display ID", "Authorize By"]
    },
    "D8PJ201503": {
        "kode": ["PJNUMB", "PJNAME", "PJBRCO", "PJCYCO", "PJCUCO", "PJAECO", "PJTYPE", "PJDTVB", "PJDTJB", "PJCLBL", "PJBUCL", "PJPAJB", "PJAMNT", "PJREFN", "PJAMBU"],
        "deskripsi": ["Nomor Deposito", "Nama Pemegang Deposito", "Branch", "Currency Code", "Customer code", "Alternate Address Code", "1=T/D,2=Doc,3=C/D", "TGL.AWAL PERIODE", "TGL.AKHIR PERIODE", "NILAI NOMINAL", "NILAI BUNGA", "PAJAK ATAS BUNGA", "NILAI PAJAK", "No. Referensi", "NILAI BUNGA NETTO"]
    },
    "B8P1201503": {
        "kode": ["P1STAT", "P1BRCO", "P1DTVL", "P1NUMB", "P1REFN", "P1RECO", "P1REIF", "P1CYCO", "P1TRDR", "P1TRCR", "P1AMNT", "P1ACCR", "P1DESC", "P1USER", "P1DTPO", "P1FSAL", "P1FLAG", "P1MAXA", "P1MSCO"],
        "deskripsi": ["Status record", "Cabang Rekening Debet", "Value Date", "No.Instruksi", "No. Referensi", "Rekening Pembebanan", "Rekening Bunga", "Currency Code", "Trans.Code Debet", "Trans.Code Credit", "Nilai Bunga/Adjustment", "Nilai Accruel Interest", "Keterangan voucher", "User ID", "Posting Date", "Balance short flag", "Posting flag", "Maximum balance", "Message code"]
    },
    "M6IB": {
        "kode": ["IBRECO", "IBDTPD", "IBDTPC", "IBDTLD", "IBDTLC", "IBAMDI", "IBAMCI", "IBAMOI", "IBAMDG", "IBAMCG", "IBAMOG", "IBAMDA", "IBAMCA", "IBAMOA", "IBAMD1", "IBAMC1", "IBAMO1", "IBAMD2", "IBAMC2", "IBAMO2", "IBRATE"],
        "deskripsi": ["A/C Number", "Date prev. deb. int. accr.", "Date prev. cre. int. accr.", "Date last. deb. int. accr.", "Date last. cre. int. accr.", "Deb. int. accr.", "Cre. int. accr.", "Ovd. int. accr.", "Deb. G/L int. accr.", "Cre. G/L int. accr.", "Ovd. G/L int. accr.", "Deb. adj int. accr.", "Cre. adj int. accr.", "Ovd. adj int. accr.", "Prev. deb. int. accr.", "Prev. cre. int. accr.", "Prev. ovd. int. accr.", "Last. deb. int. accr.", "Last. cre. int. accr.", "Last. ovd. int. accr.", "Rate % 999.9999"]
    },
    "GLBAL": {
        "kode": ["GASTAT", "GAWICO", "GABRCO", "GAGLCO", "GACYCO", "GACOST", "GADAYS", "GAYYMM", "GAAMBL", "GAAMDR", "GAAMCR", "GAAMBA", "GAAMBE", "GAAMDE", "GAAMCE", "GAAMEA", "GAAMBD", "GAAMBC", "GAAMED", "GAAMEC", "GASQDR", "GASQCR"],
        "deskripsi": ["Status record", "Wilayah", "Branch", "G/L code", "Currency Code", "Cost center", "Day only", "Tahun bulan", "Agregate balance", "DR movement", "CR movement", "Agregate balance", "Agregate balance", "DR movement eq.", "CR movement eq.", "Agregate balance", "DR movement", "CR movement", "DR movement eq.", "CR movement eq.", "DR item", "CR item"]
    },
    "GLHST": {
        "kode": ["GHSTAT", "GHSEQN", "GHWICO", "GHBRCO", "GHGLCO", "GHCYCO", "GHCOST", "GHDTPO", "GHDTVL", "GHREFN", "GHDESC", "GHDEPT", "GHAMNT", "GHAMEQ", "GHPROG", "GHMODU", "GHUSER"],
        "deskripsi": ["Status record", "Sequence", "Wilayah", "Branch", "G/L code", "Currency Code", "Cost center", "Tanggal posting", "Tanggal berlaku", "No. Referensi", "Nama", "Department Code", "Amount", "Nilai base equivalent", "Program", "Module", "User ID"]
    },
    "GLTRN": {
        "kode": ["GTSTAT", "GTSEQN", "GTWICO", "GTBRCO", "GTGLCO", "GTCYCO", "GTCOST", "GTDTPO", "GTDTVL", "GTREFN", "GTDESC", "GTDEPT", "GTAMNT", "GTAMEQ", "GTPROG", "GTMODU", "GTUSER", "GTDISP", "GTDTEY", "GTTIME", "GTCUCO", "GTPRCO"],
        "deskripsi": ["Status record", "Sequence", "Wilayah", "Branch", "G/L code", "Currency Code", "Cost center", "Tanggal posting", "Tanggal berlaku", "No. Referensi", "Nama", "Department Code", "Amount", "Nilai base equivalent", "Program", "Module", "User ID", "Display ID", "Tanggal dikey-in", "Time", "Customer code", "Produk"]
    },
    "A1GL": {
        "kode": ["GLSTAT", "GLCODE", "GLNAME", "GLACGR", "GLACTY", "GLFLG1", "GLFLG2", "GLSTSA", "GLGLIN", "GLSORT", "GLFLGC", "GLDTLC"],
        "deskripsi": ["Status record", "G/L code", "GL Name", "Accounting group", "Accounting type", "Flag B/S-P/L", "Flag D / C", "Status access", "G/L induk", "Sort number", "Flag Cost Center", "Tanggal diubah"]
    },
    "LBUDPD": {
        "kode": ["BUNUMB", "BUAMBL", "BUBTBA", "BUJMLH", "BUREV1", "BUREV2", "BUREV3", "BUREV4", "BUREV5", "BUREV6", "BUREV7", "BUREV8", "BUREV9", "BUREV10"],
        "deskripsi": ["Nomer Deposito", "Nominal Diblokir", "Biaya Trx Amortisasi", "Nominal - Biaya", "Reserved 1", "Reserved 2", "Reserved 3", "Reserved 4", "Reserved 5", "Reserved 6", "Reserved 7", "Reserved 8", "Reserved 9", "Reserved 10"]
    },
    "LBIDPD": {
        "kode": ["BIBRCO", "BICYCO", "BIDECO", "BIJENIS", "BICUCO", "BIOWCO", "BIHUBU", "BINUMB", "BILOCL", "BIBULA", "BIHARI", "BINAME", "BIDTVL", "BIDTEP", "BIBUNG", "BISALD", "BIFLAG"],
        "deskripsi": ["Branch Code", "Currency", "Deposit Code", "Sandi Rekening", "Customer Code", "Owner Code", "Hub.Nasabah", "Nomer Deposito", "Lokasi", "Jangka Waktu Bulan", "Jangka Waktu Hari", "Nama Pemegang Depo", "Tanggal Berlaku", "Tgl Pokok Jth Tempo", "Suku Bunga", "Nilai Nominal", "Flag Grouping"]
    },
    "LBURTD": {
        "kode": ["BURECO", "BUJENIS", "BUATCO", "BUJWST", "BUJWMT", "BUAMBL", "BUBTBA", "BUJMLH", "BUREV1", "BUREV2", "BUREV3", "BUREV4", "BUREV5", "BUREV6", "BUREV7", "BUREV8", "BUREV9", "BUREV10"],
        "deskripsi": ["No.Rekening", "Jenis Rek Berjangka", "Produk Type", "JW Mulai", "JW Jatuh Tempo", "Nominal Diblokir", "Biaya Trx Amortisasi", "Nominal - Biaya", "Reserved 1", "Reserved 2", "Reserved 3", "Reserved 4", "Reserved 5", "Reserved 6", "Reserved 7", "Reserved 8", "Reserved 9", "Reserved 10"]
    },
    "LBIRTD": {
        "kode": ["BIBRCO", "BICYCO", "BIATCO", "BIJENIS", "BIRECO", "BICSNO", "BINAME", "BIINRT", "BIINRR", "BIAMNT", "BIOWCO", "BIHUBU", "BILOCL", "BIFLAG"],
        "deskripsi": ["Branch Code", "Currency", "Jenis Rekening", "Sandi Rekening", "No.Rekening", "No.Cust", "Nama Debitur", "Bunga", "Bunga Terendah", "Saldo", "Owner Code", "Hub.Nasabah", "Lokasi", "Flag Grouping"]
    },
    "LBULND": {
        "kode": ["BUCSNO", "BUFCTY", "BUFCSQ", "BUCODE", "BULNTY", "BUPRPAP", "BUPRPAB", "BULATGP", "BULATGB", "BUSANB", "BUNPAP", "BURVDT", "BULOTR", "BUPRAM", "BUBIAM", "BUPBDR", "BUCKRR", "BUBDNT", "BUPPAR", "BUPBDP", "BUREV1", "BUREV2", "BUREV3", "BUREV4", "BUREV5", "BUREV6", "BUREV7", "BUREV8", "BUREV9", "BUREV10"],
        "deskripsi": ["Cust.Fac.No", "Fac.Type", "Fac.Seq", "No.Rekening", "Loan Type", "Period Pmbyrn Pokok", "Period Pmbyrn Bunga", "Lama Tnggakn Pokok", "Lama Tnggakn Bunga", "Sandi Bank", "Nilai PPAP", "Tgl Review Agunan", "Longgar Tarik", "Prov Blum Diamrtsasi", "Biay Trx Blum Diamor", "Pndp Bunga Rstruktur", "Cad Krugian Rstrktr", "Baki Debet Netto", "PPAP Restuktur", "Pdnpt Bng dlm Pnylsn", "Reserved 1", "Reserved 2", "Reserved 3", "Reserved 4", "Reserved 5", "Reserved 6", "Reserved 7", "Reserved 8", "Reserved 9", "Reserved 10"]
    },
    "LBILND": {
        "kode": ["BITYPE", "BITNGI", "BIBRCO", "BICYCO", "BICYFL", "BICSNO", "BIFCTY", "BIFCSQ", "BICODE", "BILNTY", "BINAME", "BIREFN", "BINARR", "BINMON", "BINDAY", "BIINRT", "BIINRR", "BIFCMT", "BIPLAF", "BIAVMT", "BISIFT", "BITYUS", "BICOLC", "BIOWNC", "BIGOKR", "BIECON", "BILOCL", "BIGOPJ", "BIBADJ", "BIHUBU", "BIPPAP", "BIBULA", "BIANGU", "BISIF1", "BIMYST", "BIMYDU", "BIODDT", "BIFLAG"],
        "deskripsi": ["2-Loan,3-Non PRK CER", "Direct/Indirect", "Branch Code", "Currency Kredit", "Currency Fasilitas", "Cust.Fac.No", "Fac.Type", "Fac.Seq", "No.Rekening", "Loan Type", "Nama Debitur", "Fac.Ref", "Fac.Narrative", "Month", "Day", "Interest Rate", "Interest Rate Low", "Plafond", "Baki Debet", "Longgar Tarik", "Orient.Pengg", "Type of Use", "Collectibility", "Owner Code", "Gol.Kredit", "Economic Sect.", "Location", "Gol.Penjamin", "Bagian Dijamin", "Hub.Bank", "PPAP", "Bulan Lalu", "Agunan", "Sifat", "Start Date", "End Date", "OD Date", "Flag Grouping"]
    },
    "LCFEE": {
        "kode": ["FOSTAT", "FOSTAD", "FOBRCA", "FOBRCD", "FOCSNO", "FOFCTY", "FOFCSQ", "FOCFPR", "FOCFTY", "FOCYCD", "FOCALM", "FOSAFL", "FOSTDT", "FOENDT", "FONXDT", "FOFREQ", "FODAYN", "FOCFRT", "FONFRT", "FONFDT", "FOSETL", "FOASTF", "FONARR", "FOREFN", "FODAMT", "FOACDT", "FOACMT", "FOPADT", "FOPAMT", "FOCADT", "FOCAMT", "FOOVUS", "FOOVFL", "FOFJDE", "FOFTME", "FOUSID", "FODEPT", "FOLSDA", "FOLJDA", "FOLSTA", "FOWSID", "FOAUUS", "FOFSEQ"],
        "deskripsi": ["Status record", "Status Data", "Branch Area Code", "Branch Code", "Cust. No Fac.", "Facility Type", "Fac. Seq. No", "C&O Fee Processing", "C&O Fee Type", "Loan Ccy Code", "Calc. days", "Stop Accrual C&O (0/1/2)", "Start Date", "End Date", "Next Date", "Frequency", "Day only", "Fee Rate", "Next.Fee Rate", "Next.Eff.Rate Date", "Settlement Account", "Auto Sett.Flag", "Narrative", "Reference No.", "Accrue Amt.Today Org Ccy", "Last Date Accrued", "Next Amt.Posted Org Ccy", "Last Date Acc.Posted", "Next Amt.Cap. Org Ccy", "Last Date Capitalized", "Tot.Capitalized Org Ccy", "Override by", "Override Flag", "1st Job Date Entry", "1st Entry Time", "User ID", "User Dept Code", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Display ID", "Authorize By", "Fee Seqn No"]
    },
    "LCEXP": {
        "kode": ["EXSTAT", "EXSTAD", "EXBRCA", "EXBRCD", "EXCSNO", "EXFCTY", "EXFCSQ", "EXCFPR", "EXCFTY", "EXCYCD", "EXCALM", "EXSAFL", "EXSTDT", "EXENDT", "EXNXDT", "EXFREQ", "EXDAYN", "EXCFRT", "EXNFRT", "EXNFDT", "EXSETL", "EXASTF", "EXNARR", "EXREFN", "EXDAMT", "EXACDT", "EXACMT", "EXPADT", "EXPAMT", "EXCADT", "EXCAMT", "EXOVUS", "EXOVFL", "EXFJDE", "EXFTME", "EXUSID", "EXDEPT", "EXLSDA", "EXLJDA", "EXLSTA", "EXWSID", "EXAUUS", "EXFSEQ"],
        "deskripsi": ["Status record", "Status Data", "Branch Area Code", "Branch Code", "Cust. No Fac.", "Facility Type", "Fac. Seq. No", "C&O Fee Processing", "C&O Fee Type", "Loan Ccy Code", "Calc. days", "Stop Accrual C&O (0/1/2)", "Start Date", "End Date", "Next Date", "Frequency", "Day only", "Fee Rate", "Next.Fee Rate", "Next.Eff.Rate Date", "Settlement Account", "Auto Sett.Flag", "Narrative", "Reference No.", "Accrue Amt.Today Org Ccy", "Last Date Accrued", "Next Amt.Posted Org Ccy", "Last Date Acc.Posted", "Next Amt.Cap. Org Ccy", "Last Date Capitalized", "Tot.Capitalized Org Ccy", "Override by", "Override Flag", "1st Job Date Entry", "1st Entry Time", "User ID", "User Dept Code", "Last Sys Date Amend", "Last Job Date Amend", "Last Time Amend", "Display ID", "Authorize By", "Fee Seqn No"]
    },
    "M4CUBI": {
        "kode": ["CUCODE", "CUINCO", "CUOWCO", "CUIDCO", "CUBDIN", "CUBTIN", "CUBUIN", "CUBUOT", "CUBTOT", "CUBDLT"],
        "deskripsi": ["Customer code", "Institution Code", "Golongan pemilik", "Industry Code", "Date Input", "Time Input", "User Input", "User Otor", "Time Otor", "Date Last Update"]
    },
    "T6APPU": {
        "kode": ["Status", "Nomor Rekening", "Cabang Transaksi", "Nomor CIF Nasabah", "Nama Nasabah", "Kode Transaksi", "Nomor Referensi", "Nilai Transaksi", "Kode Alert/Peringatan", "Alamat 1", "Alamat 2", "Kelurahan", "Kabupaten", "Provinsi", "Nomor Identitas Nasabah", "Kode Program", "Tanggal Transaksi", "Jam Transaksi", "User Teller ID", "Nomor Batch", "Nomor Counter", "Flag Otorisasi", "User Otorisasi", "User Override", "Keterangan/Catatan Transaksi", "RESERVE 1", "RESERVE 2", "RESERVE 3", "RESERVE 4", "RESERVE 5", "RESERVE 6", "RESERVE 7", "RESERVE 8", "RESERVE 9"],
        "deskripsi": []  # Langsung pake kode sebagai deskripsi
    },
    "M4CUC": {
        "kode": ["CIF", "Bentuk Usaha", "Bidang Usaha", "Nomor Ijin Usaha", "Nomor Akta", "Tanggal Berdiri", "Penghasilan Per-tahun", "Tujuan Hub", "Sumber Dana", "Kepemilikan Modal", "Column11", "Column12", "Column13", "Column14", "Column15", "Column16", "Column17", "Column18", "Column19", "Column20", "Column21"],
        "deskripsi": []  # Langsung pake kode sebagai deskripsi
    }
}

# ============================================================
# 3. BACA FILE .tab
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
# 4. MATCH FILE DENGAN HEADER
# ============================================================
def get_headers_for_file(file_key):
    """Cari header untuk file berdasarkan nama"""
    for sheet_name in HEADER_MAPPING.keys():
        if sheet_name.upper() == file_key.upper():
            return HEADER_MAPPING[sheet_name]
        if file_key.upper() in sheet_name.upper() or sheet_name.upper() in file_key.upper():
            return HEADER_MAPPING[sheet_name]
    return None

# ============================================================
# 5. STATE MANAGEMENT
# ============================================================
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "selected_key" not in st.session_state:
    st.session_state.selected_key = {}
if "selected_cols" not in st.session_state:
    st.session_state.selected_cols = {}
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

# ============================================================
# 6. UI UTAMA
# ============================================================

st.subheader("📁 Upload File Data (.tab)")
data_files = st.file_uploader(
    "Upload file .tab",
    accept_multiple_files=True,
    type=["tab", "txt"],
    key="data_uploader"
)

if data_files:
    with st.spinner("⏳ Membaca file..."):
        for file in data_files:
            raw_name = file.name
            if raw_name.endswith(".tab"):
                raw_name = raw_name[:-4]
            elif raw_name.endswith(".txt"):
                raw_name = raw_name[:-4]
            key = raw_name.upper()
            
            df = parse_tab_file(file)
            if df is not None and not df.empty:
                # Cari header
                header_info = get_headers_for_file(key)
                if header_info:
                    # Ada 2 kemungkinan: pake kode atau deskripsi
                    if header_info.get("deskripsi") and len(header_info["deskripsi"]) > 0:
                        # Pake deskripsi sebagai header (lebih jelas)
                        headers = header_info["deskripsi"]
                        # Tapi kalau deskripsi kosong, pake kode
                        if len(headers) == 0 or all(h == "" for h in headers):
                            headers = header_info["kode"]
                    else:
                        headers = header_info["kode"]
                    
                    # Potong atau tambah header sesuai jumlah kolom
                    if len(headers) > len(df.columns):
                        headers = headers[:len(df.columns)]
                    elif len(headers) < len(df.columns):
                        headers = headers + [f"Kolom {i}" for i in range(len(headers), len(df.columns))]
                    
                    st.session_state.uploaded_files[key] = {
                        "df": df,
                        "headers": headers,
                        "file_name": file.name,
                        "matched_sheet": key
                    }
                    st.success(f"✅ {file.name}: {len(df)} baris, {len(df.columns)} kolom → Match: {key}")
                else:
                    # Tidak ada header, pake default
                    headers = [f"Kolom {i}" for i in range(len(df.columns))]
                    st.session_state.uploaded_files[key] = {
                        "df": df,
                        "headers": headers,
                        "file_name": file.name,
                        "matched_sheet": None
                    }
                    st.warning(f"⚠️ {file.name}: {len(df)} baris, {len(df.columns)} kolom → Tidak ada header di mapping")
            else:
                st.warning(f"⚠️ {file.name}: Kosong atau tidak terbaca")

# ---- Pilih Kolom Kunci ----
if st.session_state.uploaded_files:
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
        preview_df.columns = headers[:len(preview_df.columns)]
        st.dataframe(preview_df, use_container_width=True)
        
        col_options = {f"{i}: {h}" : i for i, h in enumerate(headers)}
        
        # Cari default: kolom yang mengandung CIF/CUCODE/CODE
        default_idx = 0
        for i, h in enumerate(headers):
            h_upper = h.upper()
            if "CUCODE" in h_upper or "CUSTOMER CODE" in h_upper or "CIF" in h_upper or "CODE" in h_upper:
                default_idx = i
                break
        
        selected_label = st.selectbox(
            f"Pilih kolom kunci untuk {file_name}",
            options=list(col_options.keys()),
            index=default_idx,
            key=f"key_select_{key}"
        )
        st.session_state.selected_key[key] = col_options[selected_label]
        st.write("---")

# ---- Pilih Kolom yang Mau Dibawa ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    st.subheader("📋 Pilih Kolom yang Mau Digabung")
    
    for key, info in st.session_state.uploaded_files.items():
        df = info["df"]
        headers = info["headers"]
        file_name = info["file_name"]
        key_col = st.session_state.selected_key[key]
        
        st.write(f"**📋 {file_name}** (Kunci: {headers[key_col] if key_col < len(headers) else f'Kolom {key_col}'})")
        
        if key not in st.session_state.selected_cols:
            st.session_state.selected_cols[key] = [key_col]
            # Tambahkan 2 kolom pertama yang bukan key
            count = 0
            for i in range(len(headers)):
                if i != key_col and count < 2:
                    st.session_state.selected_cols[key].append(i)
                    count += 1
        
        col_options = {i: f"{i}: {h}" for i, h in enumerate(headers)}
        
        selected = st.multiselect(
            f"Pilih kolom dari {file_name}",
            options=list(col_options.keys()),
            format_func=lambda x: col_options[x],
            default=st.session_state.selected_cols.get(key, [key_col]),
            key=f"col_select_{key}"
        )
        st.session_state.selected_cols[key] = selected
        st.write("---")

# ---- Proses Gabung ----
if st.session_state.uploaded_files and all(v is not None for v in st.session_state.selected_key.values()):
    if st.button("🚀 Gabungkan Data"):
        with st.spinner("⏳ Memproses..."):
            try:
                first_key = list(st.session_state.uploaded_files.keys())[0]
                first_info = st.session_state.uploaded_files[first_key]
                first_df = first_info["df"]
                first_key_col = st.session_state.selected_key[first_key]
                first_selected_cols = st.session_state.selected_cols[first_key]
                first_headers = first_info["headers"]
                
                # Hasil dari file pertama
                result_data = {}
                result_headers = []
                
                for col_idx in first_selected_cols:
                    col_name = first_headers[col_idx] if col_idx < len(first_headers) else f"Kolom {col_idx}"
                    result_headers.append(col_name)
                    result_data[col_name] = first_df[col_idx].tolist()
                
                # Tambah dari file lain
                for key, info in st.session_state.uploaded_files.items():
                    if key == first_key:
                        continue
                    
                    df = info["df"]
                    key_col = st.session_state.selected_key[key]
                    selected_cols = st.session_state.selected_cols[key]
                    headers = info["headers"]
                    
                    other_keys = df[key_col].tolist()
                    other_data = {}
                    
                    for col_idx in selected_cols:
                        col_name = headers[col_idx] if col_idx < len(headers) else f"Kolom {col_idx}"
                        final_name = f"{info['file_name']}_{col_name}"
                        result_headers.append(final_name)
                        other_data[final_name] = df[col_idx].tolist()
                    
                    result_keys = result_data[result_headers[0]]
                    
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
                
                result_df = pd.DataFrame(result_data)
                st.session_state.processed_data = result_df
                st.success(f"✅ Data berhasil digabung! {len(result_df)} baris, {len(result_df.columns)} kolom")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ---- Preview & Download ----
if st.session_state.processed_data is not None:
    st.subheader("📊 Preview Hasil Gabungan")
    st.dataframe(st.session_state.processed_data, use_container_width=True)
    st.caption(f"Total: {len(st.session_state.processed_data)} baris, {len(st.session_state.processed_data.columns)} kolom")
    
    csv_data = io.BytesIO()
    st.session_state.processed_data.to_csv(csv_data, index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data.getvalue(),
        file_name="hasil_gabungan.csv",
        mime="text/csv"
    )
    
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
    except:
        pass

# ---- Reset ----
if st.button("🔄 Reset Semua"):
    for key in list(st.session_state.keys()):
        if key != "header_mapping":
            st.session_state[key] = None if key not in ["header_mapping"] else st.session_state.get(key, {})
    st.rerun()
