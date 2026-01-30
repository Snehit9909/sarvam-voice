# stt_streaming.py
import os
import tempfile
from sarvamai import SarvamAI
from config.config import SARVAM_API_KEY, STT_LANGUAGE

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

def transcribe_chunk(audio_bytes: bytes) -> str:
    """
    Transcribe a short audio chunk (500ms–1s)
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                model="saarika:v2.5",
                language_code=STT_LANGUAGE
            )
        return response.transcript or ""
    finally:
        os.remove(tmp_path)
