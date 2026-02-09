from tts.tts_eleven_stream import stream_tts_eleven
from tts.tts_sarvam_stream import stream_tts_sarvam

def stream_tts(provider, text_stream):
    if provider == "elevenlabs":
        return stream_tts_eleven(text_stream)
    if provider == "sarvam":
        return stream_tts_sarvam(text_stream)

    raise ValueError("Unsupported TTS provider")
