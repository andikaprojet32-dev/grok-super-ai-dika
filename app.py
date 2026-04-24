import streamlit as st
from openai import OpenAI
import base64
from fpdf import FPDF
from pypdf import PdfReader
from PIL import Image
import requests
from bs4 import BeautifulSoup
import io

# Konfigurasi Halaman Utama
st.set_page_config(page_title="DIKA SUPER AI", layout="wide", page_icon="⚡")

# ==================== CSS UNTUK TAMPILAN CLEAN PREMIUM ====================
st.markdown("""
<style>
.main-title {
    font-size: 45px !important;
    font-weight: 900 !important;
    background: -webkit-linear-gradient(45deg, #2193b0, #6dd5ed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: -10px;
}
.sub-title {
    text-align: center;
    color: #555555;
    font-size: 18px;
    margin-bottom: 30px;
    font-weight: 500;
}
div.stButton > button {
    border-radius: 10px !important;
    border: 2px solid #2193b0 !important;
    background-color: transparent !important;
    color: #2193b0 !important;
    font-weight: bold !important;
    transition: 0.3s;
    width: 100%;
}
div.stButton > button:hover {
    background-color: #2193b0 !important;
    color: white !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(33, 147, 176, 0.4) !important;
}
[data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 15px;
    background-color: rgba(33, 147, 176, 0.05);
    border: 1px solid rgba(33, 147, 176, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">DIKA SUPER AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">⚡ Asisten Pintar Masa Depan ⚡</p>', unsafe_allow_html=True)
st.divider()

# ==================== KONEKSI API KEY ====================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("🚨 API Key belum dipasang di Secrets Streamlit Cloud!")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """Kamu adalah DIKA SUPER AI.
- Jawab dengan bahasa Indonesia santai, asik, modern, dan sopan.
- Selalu berikan logika step-by-step.
- Berikan solusi yang akurat dan ringkas."""

# Sidebar Pengaturan
st.sidebar.markdown("### ⚙️ Engine AI")
model_options = {
    "GPT-4o Mini (Cepat)": "gpt-4o-mini",
    "GPT-4o (Pintar)": "gpt-4o"
}
selected = st.sidebar.selectbox("Pilih Server:", list(model_options.keys()))
model = model_options[selected]
st.sidebar.success(f"Sistem siap: {selected} ✅")

# Menu Tab
t_chat, t_pdf, t_file, t_web, t_vid = st.tabs(["💬 Chat", "📄 Buat PDF", "📁 Analisis File", "🌐 Tarik Web", "🎥 Ide Video"])

# ==================== TAB CHAT ====================
with t_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.toast('Sistem siap bantu, ketik aja! ⚡')

    chat_box = st.container()

    if prompt := st.chat_input("Tanya apa aja..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_box:
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Mikir bentar..."):
                    try:
                        res = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                            temperature=0.7
                        )
                        answer = res.choices[0].message.content
                        st.write(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        if "AuthenticationError" in str(type(e)):
                            st.error("🚨 API Key lo MATI/DIBLOKIR sama OpenAI karena bocor di internet. Ganti key baru!")
                        elif "RateLimitError" in str(type(e)):
                            st.warning("⚠️ Kuota API habis atau akun belum diisi saldo ($).")
                        else:
                            st.error(f"Error sistem: {e}")
                            
    elif len(st.session_state.messages) > 0:
        with chat_box:
            for msg in st.session_state.messages[-2:]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

# ==================== TAB PDF ====================
with t_pdf:
    teks = st.text_area("Teks untuk PDF:", height=150)
    nama = st.text_input("Nama file:", "Dika_Dokumen.pdf")
    if st.button("Buat PDF"):
        if teks:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, teks)
            out = pdf.output(dest="S").encode("latin-1")
            st.download_button("📥 Download File", out, nama, "application/pdf")
        else:
            st.warning("Isi teksnya dulu!")

# ==================== TAB FILE ====================
with t_file:
    up = st.file_uploader("Upload Dokumen/Gambar:", type=["pdf", "png", "jpg", "txt"])
    if up and st.button("Bedah File"):
        with st.spinner("Menganalisis..."):
            try:
                msg = "Tolong analisis file ini."
                if up.type == "application/pdf":
                    txt = "\n".join([p.extract_text() for p in PdfReader(up).pages])
                    msg = f"Ringkas PDF ini: {txt[:5000]}"
                
                res = client.chat.completions.create(model=model, messages=[{"role":"user", "content":msg}])
                st.write(res.choices[0].message.content)
            except:
                st.error("Gagal baca file. Pastikan API key aktif.")

# ==================== TAB WEB ====================
with t_web:
    url = st.text_input("Link (https://...):")
    if st.button("Tarik Data"):
        if url:
            with st.spinner("Menyedot..."):
                try:
                    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                    txt = BeautifulSoup(r.text, "html.parser").get_text()[:8000]
                    res = client.chat.completions.create(
                        model=model, 
                        messages=[{"role":"user", "content":f"Ringkas info web ini: {txt}"}]
                    )
                    st.success("Berhasil!")
                    st.write(res.choices[0].message.content)
                except:
                    st.error("Gagal akses web / Limit API.")

# ==================== TAB VIDEO ====================
with t_vid:
    topik = st.text_input("Ide Konten:")
    if st.button("Buat Naskah"):
        with st.spinner("Nulis naskah..."):
            try:
                res = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user", "content":f"Buat naskah video pendek YouTube/TikTok tentang: {topik}"}]
                )
                st.write(res.choices[0].message.content)
            except:
                st.error("Gagal. Cek API Key lo.")

# Footer
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #555; font-size: 14px;'>
        <b>DIKA SUPER AI</b><br>
        <span style='font-size: 12px;'>Support & Donasi DANA:</span><br>
        <b style='color: #2193b0; font-size: 16px;'>+62 83829310666</b>
    </div>
    """, unsafe_allow_html=True
)
