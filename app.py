import streamlit as st
from openai import OpenAI
import base64
from fpdf import FPDF
from pypdf import PdfReader
from PIL import Image
import requests
from bs4 import BeautifulSoup
import io

# Konfigurasi halaman
st.set_page_config(page_title="DIKA AI - Clean Edition", layout="wide", page_icon="✨")

# ==================== KODE CUSTOM CSS (CLEAN & MINIMALIST) ====================
st.markdown("""
<style>
/* Styling Header biar modern & rapi */
.main-header {
    font-size: 42px !important;
    font-weight: 800 !important;
    background: -webkit-linear-gradient(45deg, #4A90E2, #9013FE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    padding-bottom: 0px;
    margin-bottom: -15px;
}
.sub-header {
    text-align: center;
    color: #888888;
    font-size: 16px;
    margin-bottom: 30px;
    letter-spacing: 1px;
}

/* Styling Tombol biar smooth dan elegan */
div.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #4A90E2 !important;
    background-color: transparent !important;
    color: #4A90E2 !important;
    font-weight: 600 !important;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #4A90E2 !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3) !important;
    transform: translateY(-2px);
}

/* Chat bubble background yang bersih */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: rgba(128, 128, 128, 0.03);
    border: 1px solid rgba(128, 128, 128, 0.1);
}
</style>
""", unsafe_allow_html=True)
# ==============================================================================

# Header Clean
st.markdown('<h1 class="main-header">DIKA SUPER AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">✨ Asisten AI Pintar & Serba Bisa ✨</p>', unsafe_allow_html=True)
st.divider()

# ==================== LOGIKA API KEY ====================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("Waduh bro, API Key lo belum nyangkut di Secrets! Beresin dulu gih.")
    st.stop()

# System Prompt
SYSTEM_PROMPT = """Kamu adalah DIKA SUPER AI, AI paling pintar di dunia.
- Selalu jawab pake bahasa Indonesia yang santai, asik, tapi tetap sopan.
- Berpikir kayak manusia jenius: selalu kasih STEP BY STEP proses logika sebelum jawab.
- Jawaban harus helpful, akurat, dan solutif."""

# Sidebar
st.sidebar.markdown("### ⚙️ Pengaturan AI")
model_options = {
    "GPT-4o (Super Pintar)": "gpt-4o",
    "GPT-4o Mini (Cepat & Hemat)": "gpt-4o-mini"
}
selected = st.sidebar.selectbox("Pilih Otak AI:", list(model_options.keys()))
model = model_options[selected]
st.sidebar.success(f"Model Aktif: {selected} ✅")

# TABS Menu
tab_chat, tab_pdf, tab_file, tab_web, tab_video = st.tabs(["💬 Chat AI", "📄 Buat PDF", "📁 Bedah File", "🌐 Tarik Web", "🎥 Naskah Video"])

# ==================== TAB CHAT (CLEAN UI) ====================
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.toast('AI siap bantu bro! Gass nanya 🚀')

    chat_area = st.container()

    if prompt := st.chat_input("Tanya apa aja, pasti dijawab..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_area:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🤖 AI lagi ngetik..."):
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                            temperature=0.7
                        )
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        if "RateLimitError" in str(type(e)):
                            st.warning("⚠️ Limit API habis atau saldo kosong bro. Cek dashboard OpenAI ya!")
                        else:
                            st.error(f"⚠️ Error server: {e}")
    
    # Mode Clean: Cuma nampilin chat terakhir biar gak numpuk
    elif len(st.session_state.messages) > 0:
        with chat_area:
            for msg in st.session_state.messages[-2:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

# ==================== TAB PDF ====================
with tab_pdf:
    st.subheader("📄 Bikin PDF Instan")
    content = st.text_area("Masukkan teks buat dokumen PDF lo:", height=200)
    name = st.text_input("Nama file (jangan lupa .pdf):", "dokumen_dika.pdf")
    if st.button("Cetak PDF"):
        if content:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, content)
            out = pdf.output(dest="S").encode("latin-1")
            st.download_button("📥 Simpan File", out, name, "application/pdf")
        else: st.warning("Isi teksnya dulu bro, masa kosong!")

# ==================== TAB FILE ====================
with tab_file:
    st.subheader("📁 Bedah Isi File")
    up = st.file_uploader("Upload PDF, TXT, atau Gambar:", type=["txt", "pdf", "png", "jpg", "jpeg"])
    if up and st.button("Analisis Dokumen"):
        with st.spinner("Membaca file..."):
            try:
                if up.type == "application/pdf":
                    text = "\n".join([p.extract_text() for p in PdfReader(up).pages])
                    msg = f"Tolong ringkas dan analisis dokumen PDF ini: {text[:10000]}"
                else:
                    msg = "Tolong analisis isi file ini."
                
                res = client.chat.completions.create(model=model, messages=[{"role":"user", "content":msg}])
                st.markdown(res.choices[0].message.content)
            except Exception as e:
                st.warning("⚠️ Gagal baca file. Pastikan format bener atau cek saldo API lo.")

# ==================== TAB WEB ====================
with tab_web:
    st.subheader("🌐 Tarik Data Website")
    url = st.text_input("Link Website (harus https://...):")
    if st.button("Tarik Info"):
        if url:
            with st.spinner("Mengakses server web..."):
                try:
                    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                    txt = BeautifulSoup(r.text, "html.parser").get_text()[:15000]
                    res = client.chat.completions.create(
                        model=model, 
                        messages=[{"role":"user", "content":f"Buat ringkasan dari isi website ini secara detail: {txt}"}]
                    )
                    st.success("Web berhasil ditarik!")
                    st.write(res.choices[0].message.content)
                except: st.error("Web diblokir dari luar atau saldo API limit bro!")

# ==================== TAB VIDEO ====================
with tab_video:
    st.subheader("🎥 Bikin Naskah Video Auto-Viral")
    topic = st.text_input("Ide Video:")
    if st.button("Tulis Naskah"):
        with st.spinner("Merangkai kata-kata..."):
            try:
                res = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user", "content":f"Buat naskah video pendek yang menarik buat sosmed tentang: {topic}"}]
                )
                st.write(res.choices[0].message.content)
            except:
                st.warning("⚠️ Limit API nyangkut bro!")

# Sidebar Footer
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 14px;'>
        <b>DIKA SUPER AI</b><br>
        <i>Clean & Minimalist Edition</i><br>
        <br>
        Dukung developer via DANA:<br>
        <b style='color: #4A90E2; font-size: 16px;'>+62 83829310666</b>
    </div>
    """, unsafe_allow_html=True
)
