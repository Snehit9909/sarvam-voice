import os
import subprocess
import streamlit as st
from config.config import STT_MODELS, STT_LANGUAGES, TTS_CONFIG

st.set_page_config(page_title="Voice Assistant", layout="centered")
st.title(" Talk Buddy!")

st.markdown("## Configuration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### STT")
    stt_model = st.selectbox("STT Model", STT_MODELS)
    stt_language = st.selectbox("Language", list(STT_LANGUAGES.keys()))

with col2:
    st.markdown("### TTS")
    tts_provider = st.radio(
        "TTS Provider",
        list(TTS_CONFIG.keys()),
        format_func=lambda x: x.capitalize()
    )

st.markdown("---")

if st.button(" Start Voice Assistant"):
    env = os.environ.copy()
    env["STT_MODEL"] = stt_model
    env["STT_LANGUAGE"] = STT_LANGUAGES[stt_language]
    env["TTS_PROVIDER"] = tts_provider

    st.success("Voice assistant running. Speak into the mic.")

    log_box = st.empty()
    logs = ""

    process = subprocess.Popen(
        ["python", "-u", "-m", "orchestrator.main_unified"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1 
    )

    for line in process.stdout:
        # 1. Print to terminal window
        print(line, end="", flush=True) 
        
        # 2. Update the Streamlit UI
        logs += line
        log_box.code(logs)

    process.wait()
