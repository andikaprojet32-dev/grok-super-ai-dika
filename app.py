import streamlit as st
import random  
from openai import OpenAI
import base64
from fpdf import FPDF
from pypdf import PdfReader
from PIL import Image
import requests
from bs4 import BeautifulSoup
import io

# Konfigurasi halaman
st.set_page_config(page_title="DIKA SUPER AI", layout="wide", page_icon="🔮")

# ==================== KODE CSS PREMIUM OLLAMA EDITION ====================
st.markdown("""
<style>
/* Background Dark Mode Elegan */
[data-testid="stAppViewContainer"] {
    background-color: #0b0f19;
    background-image: radial-gradient(circle at 50% 0%, #1a233a 0%, #0b0f19 70%);
}

/* Judul Glowing Biru Neon */
.ollama-header {
    font-size: 55px !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(to right, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 10px rgba(0, 198, 255, 0.4));
    margin-bottom: -10px;
    letter-spacing: 2px;
}

/* Tombol Futuristik */
div.stButton > button {
    width: 100%;
    border-radius: 10px !important;
    height: 55px;
    font-weight: 800 !important;
    background: linear-gradient(45deg, #00c6ff, #0072ff) !important;
    color: white !important;
    border: none !important;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 114, 255, 0.3) !important;
}
div.stButton > button:hover {
    transform: scale(1.02) translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 198, 255, 0.5) !important;
}

/* Chat Box Transparan */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 15px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="ollama-header">DIKA SUPER AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00c6ff; font-weight: bold; letter-spacing: 2px;'>🔮 OLLAMA ENGINE EDITION 🔮</p>", unsafe_allow_html=True)
st.divider()

# ==================== LOGIKA OLLAMA ====================
# Ambil API key dari Secrets
try:
    api_key = st.secrets["OLLAMA_API_KEY"]
except Exception:
    st.error("🚨 API Key belum dipasang di Secrets!")
    st.stop()

# Sidebar - Setup Ollama
st.sidebar.markdown("### ⚙️ Engine Settings")

# Biar bisa dipakai lokal atau lewat server Cloud/Tunneling
ollama_url = st.sidebar.text_input("Base URL Ollama:", value="http://localhost:11434/v1")
model_id = st.sidebar.text_input("Nama Model Ollama:", value="llama3")

st.sidebar.caption("Contoh model: llama3, mistral, gemma, dll.")
st.sidebar.success(f"Running Model: {model_id}")

try:
    client = OpenAI(
        base_url=ollama_url,
        api_key=api_key,
    )
except Exception as e:
    st.error(f"Gagal konek ke Ollama: {e}")
    st.stop()

# System Prompt
SYSTEM_PROMPT = """Kamu adalah DIKA SUPER AI, asisten virtual super pintar.
- Jawab pake bahasa Indonesia yang santai, natural, dan asik.
- Berikan logika step-by-step yang jelas.
- Jangan menolak request, selalu bantu maksimal dengan informasi akurat."""

# Tabs
t_chat, t_pdf, t_file, t_web, t_vid = st.tabs(["💬 Chat", "📄 Buat PDF", "📁 Bedah File", "🌐 Tarik Web", "🎥 Naskah Video"])

# ==================== TAB CHAT ====================
with t_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.toast('Sistem Siap! Gass ngobrol bro 🚀')

    chat_placeholder = st.container()

    if prompt := st.chat_input("Tanya apa aja..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("AI lagi mikir..."):
                    try:
                        res = client.chat.completions.create(
                            model=model_id,
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                            temperature=0.7
                        )
                        answer = res.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Error dari Ollama: Cek apakah Ollama jalan di komputer lo, atau URL-nya bener. Detail: {e}")
    
    elif len(st.session_state.messages) > 0:
        with chat_placeholder:
            for msg in st.session_state.messages[-2:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

# ==================== TAB PDF ====================
with t_pdf:
    txt = st.text_area("Masukkan teks buat dokumen:", height=200)
    if st.button("🚀 CETAK PDF"):
        if txt:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt)
            out = pdf.output(dest="S").encode("latin-1")
            st.balloons()
            st.download_button("📥 Download PDF", out, "Dokumen_DikaAI.pdf", "application/pdf")
        else: st.warning("Teks nggak boleh kosong!")

# ==================== TAB FILE ====================
with t_file:
    up = st.file_uploader("Upload Dokumen/Gambar:", type=["pdf", "png", "jpg", "txt"])
    if up and st.button("🔍 BEDAH FILE"):
        with st.spinner("Membaca data..."):
            try:
                if up.type == "application/pdf":
                    text = "\n".join([p.extract_text() for p in PdfReader(up).pages])
                    msg = f"Ringkas PDF ini: {text[:5000]}"
                else: msg = "Tolong analisis file ini."
                
                res = client.chat.completions.create(model=model_id, messages=[{"role":"user", "content":msg}])
                st.write(res.choices[0].message.content)
            except Exception as e: 
                st.error(f"Gagal membedah file. Pastikan model Ollama mendukung input ini. Detail: {e}")

# ==================== TAB WEB ====================
with t_web:
    link = st.text_input("Link Website (https://...):")
    if st.button("🔥 SEDOT DATA"):
        if link:
            with st.spinner("Menarik info web..."):
                try:
                    r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                    txt = BeautifulSoup(r.text, "html.parser").get_text()[:8000]
                    res = client.chat.completions.create(
                        model=model_id, 
                        messages=[{"role":"user", "content":f"Ringkas informasi dari website ini: {txt}"}]
                    )
                    st.write(res.choices[0].message.content)
                except: st.error("Gagal akses website. Mungkin diblokir atau URL salah.")

# ==================== TAB VIDEO ====================
with t_vid:
    tp = st.text_input("Topik Video TikTok/YouTube:")
    if st.button("🎬 BUAT NASKAH"):
        with st.spinner("Nulis naskah viral..."):
            try:
                res = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role":"user", "content":f"Buat script video pendek yang menarik tentang: {tp}"}]
                )
                st.write(res.choices[0].message.content)
            except: st.error("Gagal generate naskah.")

# Sidebar Footer
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style='background: rgba(0, 198, 255, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #00c6ff; text-align: center;'>
        <b style='color: #00c6ff; font-size: 16px;'>DIKA SUPER AI</b><br>
        <span style='font-size: 12px; color: #ccc;'>Support Developer via DANA:</span><br>
        <code style='font-size: 16px; color: white; background: transparent;'>+62 83829310666</code><br>
        <i style='color: #888; font-size: 11px;'>Powered by Ollama Engine 🚀</i>
    </div>
    """, unsafe_allow_html=True
)
