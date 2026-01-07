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
    .stTextInput>div>div>input { background-color: #1e2129; color: white; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- API SETUP ---
API_KEY = "AIzaSyBV2T2mYx8bHsTnXVi_9NZQu-HLNdkF_bE"
client = genai.Client(api_key=API_KEY)
SYS_PROMPT = "Jawab instruksi user dengan sangat singkat dan langsung ke inti. Jika user meminta gambar/video, ingatkan mereka untuk menggunakan menu yang sesuai di sidebar."

# --- SIDEBAR NAV ---
with st.sidebar:
    st.title("🌐 AI NEXUS")
    menu = st.radio("Menu", ["Chat Assistant", "Image Generator", "Video (Veo)"])
    st.divider()
    st.caption("Status: Active")

# --- CHAT ASSISTANT ---
if menu == "Chat Assistant":
    st.header("💬 Smart Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Apa yang ingin kamu selesaikan?"):
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
                if resp.text:
                    st.markdown(resp.text)
                    st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e:
                st.error("⚠️ Maaf, permintaan ini tidak bisa diproses di sini. Jika kamu ingin membuat gambar, gunakan menu 'Image Generator'.")

# --- IMAGE GENERATOR ---
elif menu == "Image Generator":
    st.header("🎨 Visual Studio")
    p_img = st.text_input("Deskripsikan gambar (misal: 'Anak kecil bermain di taman'):")
    if st.button("Generate Image"):
        if p_img:
            with st.spinner("Menciptakan karya seni..."):
                url = f"https://image.pollinations.ai/prompt/{p_img.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
                st.image(url, caption="Hasil AI", use_container_width=True)
        else:
            st.error("Isi deskripsi dulu!")

# --- VIDEO GENERATOR (VEO) ---
elif menu == "Video (Veo)":
    st.header("🎬 Video Engine")
    p_vid = st.text_area("Deskripsi Video:")
    if st.button("Generate Video"):
        if p_vid:
            try:
                with st.status("Veo sedang bekerja...") as s:
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
                st.error(f"Error: {e}")
