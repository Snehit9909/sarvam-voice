# import os
# import subprocess
# import streamlit as st
# from config.config import STT_LANGUAGES

# st.set_page_config(
#     page_title="Talk Buddy - Streaming Voice Assistant",
#     page_icon="*",
#     layout="centered"
# )

# # -------------------------------
# # Title
# # -------------------------------
# st.markdown("<h1 style='text-align:center;'>Talk Buddy!</h1>", unsafe_allow_html=True)
# st.markdown("<p style='text-align:center;color:#94a3b8;'>Streaming Voice Assistant</p>", unsafe_allow_html=True)

# # -------------------------------
# # Config UI
# # -------------------------------
# stt_provider = st.radio("STT Provider", ["Sarvam", "AssemblyAI"], horizontal=True)
# stt_language_label = st.selectbox("Processing Language", list(STT_LANGUAGES.keys()))
# tts_provider = st.radio("TTS Provider", ["Sarvam", "ElevenLabs"], horizontal=True)

# # -------------------------------
# # Start Button
# # -------------------------------
# start_clicked = st.button("START SESSION", use_container_width=True)

# if start_clicked:
#     env = os.environ.copy()
#     env["STT_PROVIDER"] = stt_provider.lower()
#     env["STT_LANGUAGE"] = STT_LANGUAGES[stt_language_label]
#     env["TTS_PROVIDER"] = tts_provider.lower()

#     st.markdown("<div style='text-align:center;color:#fbbf24;font-weight:bold;'>ONLINE — WAIT FOR IT TO START...</div>", unsafe_allow_html=True)

#     log_box = st.empty()
#     logs = ""

#     process = subprocess.Popen(
#         ["python", "-u", "-m", "orchestrator.main_streaming"],
#         env=env,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True,
#         bufsize=1,
#         encoding="utf-8",
#         errors="replace"
#     )


#     try:
#             while True:
#                 line = process.stdout.readline()
#                 if not line:
#                     break
                
#                 print(line, end="", flush=True)
#                 logs += line
#                 log_display = "\n".join(logs.splitlines()[-15:])
#                 log_box.code(log_display, language="bash")
#     except Exception as e:
#         st.error(f"STREAM ERROR: {e}")
#     finally:
#         process.wait()
#         st.warning("SESSION TERMINATED")

import os
import subprocess
import streamlit as st
from config.config import STT_LANGUAGES

st.set_page_config(
    page_title="Talk Buddy - Streaming Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# -------------------------------
# Title
# -------------------------------
st.markdown("<h1 style='text-align:center;'>Talk Buddy!</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#94a3b8;'>Streaming Voice Assistant</p>",
    unsafe_allow_html=True
)

# -------------------------------
# Config UI
# -------------------------------
stt_provider = st.radio(
    "STT Provider",
    ["Sarvam", "AssemblyAI"],
    horizontal=True
)

# 🔹 AssemblyAI model selector
assembly_model = "Universal-2"
if stt_provider == "AssemblyAI":
    assembly_model = st.radio(
        "AssemblyAI Model",
        ["Universal-2", "Universal-3 Pro"],
        horizontal=True
    )

stt_language_label = st.selectbox(
    "Processing Language",
    list(STT_LANGUAGES.keys())
)

tts_provider = st.radio(
    "TTS Provider",
    ["Sarvam", "ElevenLabs"],
    horizontal=True
)

# -------------------------------
# Start Button
# -------------------------------
start_clicked = st.button(
    "START SESSION",
    use_container_width=True
)

if start_clicked:
    env = os.environ.copy()

    env["STT_PROVIDER"] = stt_provider.lower()
    env["STT_LANGUAGE"] = STT_LANGUAGES[stt_language_label]
    env["TTS_PROVIDER"] = tts_provider.lower()

    # 🔹 Pass AssemblyAI model via env
    if stt_provider == "AssemblyAI":
        env["ASSEMBLY_MODEL"] = (
            "universal_3_pro"
            if assembly_model == "Universal-3 Pro"
            else "universal_2"
        )

    st.markdown(
        "<div style='text-align:center;color:#fbbf24;font-weight:bold;'>"
        "ONLINE — WAIT FOR IT TO START..."
        "</div>",
        unsafe_allow_html=True
    )

    log_box = st.empty()
    logs = ""

    process = subprocess.Popen(
        ["python", "-u", "-m", "orchestrator.main_streaming"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line, end="", flush=True)
            logs += line
            log_display = "\n".join(logs.splitlines()[-15:])
            log_box.code(log_display, language="bash")

    except Exception as e:
        st.error(f"STREAM ERROR: {e}")

    finally:
        process.wait()
        st.warning("SESSION TERMINATED")
