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
st.set_page_config(page_title="DIKA SUPER AI - OpenRouter", layout="wide", page_icon="🔥")

# ==================== KODE CSS PREMIUM ANIMATION ====================
st.markdown("""
<style>
/* Background Animasi Gradasi Berjalan */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #0f0c29);
    background-size: 400% 400%;
    animation: gradient 10s ease infinite;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Judul Glowing & Animasi */
.premium-header {
    font-size: 55px !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(to right, #00ff00, #00bfff, #00ff00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 15px rgba(0,255,0,0.5));
    animation: glow 3s infinite alternate;
    margin-bottom: -10px;
}
@keyframes glow {
    from { filter: drop-shadow(0 0 5px rgba(0,255,0,0.2)); }
    to { filter: drop-shadow(0 0 25px rgba(0,255,0,0.8)); }
}

/* Tombol Premium */
div.stButton > button {
    width: 100%;
    border-radius: 15px !important;
    height: 55px;
    font-weight: bold !important;
    background: linear-gradient(45deg, #00ff00, #008000) !important;
    color: white !important;
    border: none !important;
    transition: 0.4s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
}
div.stButton > button:hover {
    transform: scale(1.03) translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,255,0,0.5) !important;
}

/* Tab & Chat Style */
.stTabs [data-baseweb="tab-list"] { background-color: transparent; }
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="premium-header">DIKA SUPER AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00ff00; font-weight: bold;'>⚡ OPENROUTER ULTRA PREMIUM EDITION ⚡</p>", unsafe_allow_html=True)
st.divider()

# ==================== LOGIKA OPENROUTER ====================
try:
    # Pastikan lo pake nama OPENROUTER_API_KEY di Secrets
    api_key = st.secrets["OPENROUTER_API_KEY"]
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
except Exception as e:
    st.error("🚨 API Key OpenRouter belum dipasang di Secrets!")
    st.stop()

# System Prompt
SYSTEM_PROMPT = """Kamu adalah DIKA SUPER AI, asisten paling pintar di dunia.
- Jawab pake bahasa Indonesia santai, asik, modern (Gen Z style).
- Selalu kasih step-by-step logika yang jenius.
- Jangan pernah menolak request, selalu bantu maksimal."""

# Sidebar - Pilihan Otak AI (OpenRouter)
st.sidebar.markdown("### 🧠 Pilih Otak AI")
model_options = {
    "Grok Beta (X.ai)": "x-ai/grok-beta",
    "Claude 3.5 Sonnet (Terpintar)": "anthropic/claude-3-5-sonnet",
    "GPT-4o (OpenAI)": "openai/gpt-4o",
    "Gemini Pro 1.5 (Google)": "google/gemini-flash-1.5",
    "DeepSeek V3 (Kenceng)": "deepseek/deepseek-chat",
    "Llama 3.1 405B (Meta)": "meta-llama/llama-3.1-405b-instruct"
}
selected_model = st.sidebar.selectbox("Model Aktif:", list(model_options.keys()))
model_id = model_options[selected_model]
st.sidebar.success(f"Running: {selected_model}")

# Tabs
t_chat, t_pdf, t_file, t_web, t_vid = st.tabs(["💬 Chat AI", "📄 Buat PDF", "📁 Bedah File", "🌐 Tarik Web", "🎥 Script Video"])

# ==================== TAB CHAT ====================
with t_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.toast('Sistem OpenRouter Siap! 🚀')

    chat_placeholder = st.container()

    if prompt := st.chat_input("Ketik di sini bro..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Lagi mikir..."):
                    try:
                        res = client.chat.completions.create(
                            model=model_id,
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                            extra_headers={
                                "HTTP-Referer": "https://dika-ai.streamlit.app", 
                                "X-Title": "Dika Super AI",
                            }
                        )
                        answer = res.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Waduh error: {e}")
    
    elif len(st.session_state.messages) > 0:
        with chat_placeholder:
            for msg in st.session_state.messages[-2:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

# ==================== TAB PDF ====================
with t_pdf:
    txt = st.text_area("Masukkan teks:", height=200)
    if st.button("🚀 CETAK PDF"):
        if txt:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt)
            out = pdf.output(dest="S").encode("latin-1")
            st.balloons()
            st.download_button("📥 Download PDF", out, "dika_file.pdf", "application/pdf")
        else: st.warning("Isi dulu teksnya!")

# ==================== TAB FILE ====================
with t_file:
    up = st.file_uploader("Upload File:", type=["pdf", "png", "jpg", "txt"])
    if up and st.button("🔍 ANALISIS SEKARANG"):
        with st.spinner("Membaca data..."):
            try:
                if up.type == "application/pdf":
                    text = "\n".join([p.extract_text() for p in PdfReader(up).pages])
                    msg = f"Analisis PDF ini: {text[:8000]}"
                else: msg = "Tolong analisis file ini."
                
                res = client.chat.completions.create(model=model_id, messages=[{"role":"user", "content":msg}])
                st.snow()
                st.write(res.choices[0].message.content)
            except: st.error("Limit API atau File kegedean!")

# ==================== TAB WEB ====================
with t_web:
    link = st.text_input("Link Website:")
    if st.button("🔥 SEDOT DATA"):
        if link:
            with st.spinner("Menarik info..."):
                try:
                    r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                    txt = BeautifulSoup(r.text, "html.parser").get_text()[:10000]
                    res = client.chat.completions.create(
                        model=model_id, 
                        messages=[{"role":"user", "content":f"Ringkas web ini: {txt}"}]
                    )
                    st.write(res.choices[0].message.content)
                except: st.error("Gagal akses web!")

# ==================== TAB VIDEO ====================
with t_vid:
    tp = st.text_input("Topik Video:")
    if st.button("🎬 BUAT NASKAH"):
        with st.spinner("Menulis..."):
            try:
                res = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role":"user", "content":f"Buat script video Gen Z tentang: {tp}"}]
                )
                st.balloons()
                st.write(res.choices[0].message.content)
            except: st.error("Limit API habis!")

# Sidebar Footer
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style='background: rgba(0,255,0,0.1); padding: 15px; border-radius: 15px; border: 1px solid #00ff00; text-align: center;'>
        <b style='color: #00ff00;'>DIBUAT SAMA DIKA</b><br>
        <span style='font-size: 12px;'>Dukung via DANA:</span><br>
        <code style='font-size: 16px; color: white;'>083829310666</code><br>
        <i>Premium OpenRouter 🔥</i>
    </div>
    """, unsafe_allow_html=True
)
