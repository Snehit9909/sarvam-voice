import os
import subprocess
import streamlit as st

from config.config import STT_MODELS, STT_LANGUAGES, TTS_CONFIG

st.set_page_config(
    page_title=" Voice AgentCore",
    layout="centered"
)

st.title(" Talk Buddy!")
st.caption("Voice Assistant powered by AWS Bedrock AgentCore")

st.markdown("## Configuration")


col1, col2 = st.columns(2)

with col1:
    st.markdown("###  Speech-to-Text")
    stt_model = st.selectbox("STT Model", STT_MODELS)
    stt_language_label = st.selectbox(
        "Language",
        list(STT_LANGUAGES.keys())
    )

with col2:
    st.markdown("###  Text-to-Speech")
    tts_provider = st.radio(
        "TTS Provider",
        list(TTS_CONFIG.keys()),
        format_func=lambda x: x.capitalize()
    )

st.markdown("---")


if st.button(" Start Voice Assistant"):
    env = os.environ.copy()

    # STT / TTS configs
    env["STT_MODEL"] = stt_model
    env["STT_LANGUAGE"] = STT_LANGUAGES[stt_language_label]
    env["TTS_PROVIDER"] = tts_provider

    required_vars = [
        "AWS_REGION",
        "AGENT_RUNTIME_ARN",
        "AGENT_QUALIFIER"
    ]

    missing = [v for v in required_vars if not env.get(v)]
    if missing:
        st.error(f"Missing environment variables: {', '.join(missing)}")
        st.stop()

    st.success(" Voice assistant running. Speak into the mic.")

    log_box = st.empty()
    logs = ""

    process = subprocess.Popen(
        ["python", "-u", "-m", "orchestrator.main_ac"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )


    try:
        for line in process.stdout:
            print(line, end="", flush=True)
            logs += line
            log_box.code(logs)

    except Exception as e:
        st.error(f"Error reading logs: {e}")

    finally:
        process.wait()
        st.info(" Voice assistant stopped.")
