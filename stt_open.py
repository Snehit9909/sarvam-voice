# stt_open.py
import whisper
from config.config import INPUT_AUDIO_FILE

# Load whisper model once (tiny or base for speed)
model = whisper.load_model("base")

def speech_to_text():
    print("🔊 Transcribing with Whisper...")
    result = model.transcribe(INPUT_AUDIO_FILE)
    text = result["text"].strip()
    print(f"📝 You said: {text}")
    return text
