import streamlit as st

st.title("🔍 DEBUG - Lihat Struktur File .tab")

uploaded_file = st.file_uploader("Upload 1 file .tab", type=["tab", "txt"])

if uploaded_file:
    st.subheader("📄 50 baris pertama file (RAW)")
    
    # Baca sebagai bytes
    raw = uploaded_file.read()
    
    # Coba decode pake beberapa encoding
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            uploaded_file.seek(0)
            text = uploaded_file.read().decode(enc, errors="replace")
            break
        except:
            continue
    
    lines = text.splitlines()
    
    # Tampilkan 50 baris pertama
    for i, line in enumerate(lines[:50]):
        # Ganti karakter aneh biar aman
        clean_line = line.replace("\t", "[TAB]").replace("\r", "")
        st.code(f"{i+1:03d}: {clean_line[:200]}")
    
    st.subheader("📊 Deteksi Format")
    
    # Cek apakah ada pipe |
    has_pipe = any("|" in line for line in lines[:50])
    # Cek apakah ada tab
    has_tab = any("\t" in line for line in lines[:50])
    # Cek apakah ada metadata sheet
    has_metadata = any("metadata.sheet_name" in line for line in lines[:50])
    
    st.write(f"- Ada karakter `|` (pipe): {'✅' if has_pipe else '❌'}")
    st.write(f"- Ada karakter `TAB`: {'✅' if has_tab else '❌'}")
    st.write(f"- Ada `metadata.sheet_name`: {'✅' if has_metadata else '❌'}")
    
    if has_pipe and not has_tab:
        st.info("📌 Format: PIPE (mirip tabel markdown) - ini yang saya dukung")
    elif has_tab and not has_pipe:
        st.info("📌 Format: TAB DELIMITED (file CSV pake tab) - saya perlu sesuaikan")
    elif has_metadata:
        st.info("📌 Format: MULTI-SHEET dengan metadata - saya perlu sesuaikan")
    else:
        st.warning("⚠️ Format gak dikenal, kirim screenshot ke saya")
