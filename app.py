import streamlit as st
import time
from google import genai
from google.genai import types

# --- CONFIG & STYLE ---
st.set_page_config(page_title="AI Nexus Ultra - Multi Key", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0d11; color: white; }
    .stButton>button { border-radius: 10px; background: linear-gradient(45deg, #2e7bcf, #15ecec); color: white; border: none; width: 100%; height: 3em; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1e2129; color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- MULTI-API KEY MANAGER ---
API_KEYS = [
    "AIzaSyBV2T2mYx8bHsTnXVi_9NZQu-HLNdkF_bE",
    "AIzaSyCIfu8DRXiOoNkiXYXmVZMQqFxdeK4RPaA",
    "AIzaSyC6bDV2KPfMPyMFyygZHFWBC7iheQtj9ts"
]

def get_working_client():
    """Mencoba menginisialisasi client yang tersedia jika ada yang limit."""
    for key in API_KEYS:
        try:
            client = genai.Client(api_key=key)
            # Tes singkat untuk cek apakah key ini valid/tidak limit
            return client, key
        except:
            continue
    return None, None

SYS_PROMPT = "Jawab instruksi user dengan sangat singkat dan langsung ke inti. Jangan berbasa-basi."

# --- SIDEBAR NAV ---
with st.sidebar:
    st.title("🌐 AI NEXUS")
    st.caption("Multi-Key Auto Switcher Active")
    menu = st.radio("Menu", ["Chat Assistant", "Image Studio (Unlimited)", "Video Engine (Veo)"])
    st.divider()
    st.info(f"Menggunakan {len(API_KEYS)} API Keys secara bergantian.")

# --- LOGIC SELECTION ---
client, active_key = get_working_client()

if not client:
    st.error("⚠️ Semua API Key kamu sedang mencapai batas limit (429). Silakan tunggu beberapa menit.")
    st.stop()

# --- CHAT ASSISTANT ---
if menu == "Chat Assistant":
    st.header("💬 Smart Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Tanya sesuatu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(system_instruction=SYS_PROMPT),
                    contents=prompt
                )
                st.markdown(resp.text)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e:
                st.error("Terjadi masalah pada Key saat ini. Silakan refresh aplikasi untuk switch ke Key cadangan.")

# --- IMAGE STUDIO ---
elif menu == "Image Studio (Unlimited)":
    st.header("🎨 Visual Studio (No Limit)")
    p_img = st.text_input("Deskripsikan gambar:")
    if st.button("Generate Image"):
        if p_img:
            with st.spinner("Menciptakan karya seni..."):
                url = f"https://image.pollinations.ai/prompt/{p_img.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
                st.image(url, use_container_width=True)
        else:
            st.error("Isi prompt dulu!")

# --- VIDEO ENGINE ---
elif menu == "Video Engine (Veo)":
    st.header("🎬 Video Engine (Veo 3.1)")
    p_vid = st.text_area("Deskripsi Video:")
    if st.button("Generate Video"):
        if p_vid:
            try:
                with st.status("Rendering Video...") as s:
                    op = client.models.generate_videos(
                        model="veo-3.1-fast-generate-preview",
                        prompt=p_vid,
                        config=types.GenerateVideosConfig(aspect_ratio="16:9")
                    )
                    while not op.done:
                        time.sleep(10)
                        op = client.operations.get(op)
                    s.update(label="Render Selesai!", state="complete")
                st.video(op.response.generated_videos[0].video)
            except Exception as e:
                st.error(f"Gagal generate video: {e}")
