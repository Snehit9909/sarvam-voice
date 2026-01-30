from tts.tts_eleven import text_to_speech as eleven_tts
from tts.tts1 import text_to_speech as sarvam_tts
from config.config import TTS_CONFIG

def run_tts(text: str, provider: str):
    """
    Route TTS based on provider.
    """
    if provider == "elevenlabs":
        print("[TTS] Using ElevenLabs TTS")
        return eleven_tts(text, voice=TTS_CONFIG["elevenlabs"]["voice"])

    if provider == "sarvam":
        print("[TTS] Using Sarvam TTS")
        return sarvam_tts(text, voice=TTS_CONFIG["sarvam"]["voice"])

    raise ValueError(f"Unsupported TTS provider: {provider}")
