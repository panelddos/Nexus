import streamlit as st
import time
from google import genai
from google.genai import types

# --- CONFIG & STYLE ---
st.set_page_config(page_title="AI Nexus Ultra", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0d11; color: white; }
    .stButton>button { border-radius: 10px; background: linear-gradient(45deg, #2e7bcf, #15ecec); color: white; border: none; width: 100%; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- KEY MANAGER ---
API_KEYS = [
    "AIzaSyBV2T2mYx8bHsTnXVi_9NZQu-HLNdkF_bE",
    "AIzaSyCIfu8DRXiOoNkiXYXmVZMQqFxdeK4RPaA",
    "AIzaSyC6bDV2KPfMPyMFyygZHFWBC7iheQtj9ts"
]

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

def get_next_client():
    """Beralih ke API Key berikutnya jika yang sekarang limit."""
    st.session_state.key_index = (st.session_state.key_index + 1) % len(API_KEYS)
    new_key = API_KEYS[st.session_state.key_index]
    return genai.Client(api_key=new_key)

# Inisialisasi awal
current_client = genai.Client(api_key=API_KEYS[st.session_state.key_index])
SYS_PROMPT = "Jawab singkat, padat, dan langsung ke inti."

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌐 AI NEXUS")
    st.write(f"🔑 Memakai Key ke-{st.session_state.key_index + 1}")
    menu = st.radio("Menu", ["Chat Assistant", "Image Studio (Unlimited)", "Video Engine (Veo)"])
    if st.button("🔄 Paksa Ganti Key"):
        current_client = get_next_client()
        st.rerun()

# --- CHAT ASSISTANT ---
if menu == "Chat Assistant":
    st.header("💬 Smart Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Tanya sesuatu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                resp = current_client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(system_instruction=SYS_PROMPT),
                    contents=prompt
                )
                st.markdown(resp.text)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e:
                if "429" in str(e):
                    st.warning("Key limit! Mencoba key cadangan... silakan kirim ulang pesan.")
                    current_client = get_next_client()
                else:
                    st.error(f"Error: {e}")

# --- IMAGE STUDIO ---
elif menu == "Image Studio (Unlimited)":
    st.header("🎨 Visual Studio")
    p_img = st.text_input("Deskripsikan gambar:")
    if st.button("Generate Image"):
        if p_img:
            with st.spinner("Rendering..."):
                url = f"https://image.pollinations.ai/prompt/{p_img.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
                st.image(url, use_container_width=True)

# --- VIDEO ENGINE (DENGAN AUTO-SWITCH) ---
elif menu == "Video Engine (Veo)":
    st.header("🎬 Video Engine (Veo 3.1)")
    p_vid = st.text_area("Deskripsi Video:")
    
    if st.button("Generate Video"):
        success = False
        attempts = 0
        
        while not success and attempts < len(API_KEYS):
            try:
                with st.status(f"Mencoba dengan Key ke-{st.session_state.key_index + 1}...") as s:
                    op = current_client.models.generate_videos(
                        model="veo-3.1-fast-generate-preview",
                        prompt=p_vid,
                        config=types.GenerateVideosConfig(aspect_ratio="16:9")
                    )
                    while not op.done:
                        time.sleep(10)
                        op = current_client.operations.get(op)
                    
                    st.video(op.response.generated_videos[0].video)
                    s.update(label="Selesai!", state="complete")
                    success = True
            except Exception as e:
                if "429" in str(e):
                    st.warning(f"Key ke-{st.session_state.key_index + 1} limit. Mencoba key berikutnya...")
                    current_client = get_next_client()
                    attempts += 1
                else:
                    st.error(f"Gagal: {e}")
                    break
        
        if not success:
            st.error("❌ Semua API Key kamu sudah habis kuotanya untuk saat ini. Coba lagi dalam 1 jam.")
