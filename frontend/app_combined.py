import os
import subprocess
import streamlit as st

from config.config import STT_LANGUAGES

st.set_page_config(
    page_title="Talk Buddy-Voice Engine",
    page_icon="$",
    layout="centered"
)

st.markdown("""
    <style>
    /* Main Dark Canvas */
    .stApp {
        background-color: #05070a;
        color: #e2e8f0;
    }

    /* High Contrast Headers */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        letter-spacing: 2px;
        margin-bottom: 3rem;
        text-transform: uppercase;
    }

    /* Modern Configuration Card */
    .config-box {
        background: #0f172a;
        border: 2px solid #1e293b;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }

    /* Section Labels */
    .section-label {
        color: #00f2fe;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 15px;
        display: block;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* High-Contrast Start Button */
    .stButton > button {
        background: #fbbf24 !important; /* Vivid Amber */
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.2) !important;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(251, 191, 36, 0.5) !important;
        background: #f59e0b !important;
    }

    /* Style Radio and Selectbox */
    div[data-baseweb="radio"] label {
        color: #ffffff !important;
    }
    
    .stSelectbox label p {
        color: #94a3b8 !important;
    }

    /* Terminal/Log Box */
    .stCodeBlock {
        border: 1px solid #00f2fe !important;
        border-radius: 10px !important;
        background-color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Talk Buddy!</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'> AWS Voice Engine</p>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><span class='section-label'>Engine Parameters</span></div>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([0.1, 4, 0.1])
    
    with center_col:
        stt_col, tts_col = st.columns(2, gap="large")

        with stt_col:
            st.markdown("<span class='section-label'> Audio Input(STT)</span>", unsafe_allow_html=True)
            stt_provider = st.radio(
                "STT Provider",
                ["Sarvam", "AssemblyAI"],
                horizontal=True,
                label_visibility="collapsed"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            stt_language_label = st.selectbox(
                "Processing Language",
                list(STT_LANGUAGES.keys())
            )

        with tts_col:
            st.markdown("<span class='section-label'> Voice Output(TTS)</span>", unsafe_allow_html=True)
            tts_provider = st.radio(
                "TTS Provider",
                ["Sarvam", "ElevenLabs"],
                horizontal=True,
                label_visibility="collapsed"
            )
            st.markdown("<div style='margin-top: 45px; padding: 15px; border-radius: 10px; background: rgba(0, 242, 254, 0.05); border-left: 3px solid #00f2fe; color: #94a3b8; font-size: 0.8rem;'>System ready for communication.</div>", unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: #1e293b;'><br>", unsafe_allow_html=True)

_, btn_center, _ = st.columns([1, 2, 1])

with btn_center:
    start_clicked = st.button(
        "START SESSION",
        use_container_width=True
    )

if start_clicked:
    env = os.environ.copy()
    env["STT_PROVIDER"] = stt_provider.lower()
    env["STT_LANGUAGE"] = STT_LANGUAGES[stt_language_label]
    env["TTS_PROVIDER"] = tts_provider.lower()

    if not env.get("AWS_REGION"):
        st.error("SYSTEM ERROR: AWS_REGION UNDEFINED")
        st.stop()

    st.markdown("<div style='text-align: center; color: #fbbf24; font-weight: bold; animation: pulse 2s infinite;'> ENGINE ONLINE - WAIT FOR IT TO START...</div>", unsafe_allow_html=True)

    log_box = st.empty()
    logs = ""

    process = subprocess.Popen(
        ["python", "-u", "-m", "orchestrator.main_assembly"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
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