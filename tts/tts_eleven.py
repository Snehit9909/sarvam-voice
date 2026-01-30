from elevenlabs import ElevenLabs
from config.config import ELEVENLABS_API_KEY, OUTPUT_AUDIO_FILE

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_MAP = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",  
    "Adam": "pNInz6obpgDQGcFmaJgB"
}

def text_to_speech(text: str, voice: str = "Rachel") -> str:
    """
    Converts text to speech using ElevenLabs TTS.
    Returns path to the generated WAV file.
    """
    try:
        voice_id = VOICE_MAP.get(voice, voice)
        audio = client.text_to_speech.convert(voice_id=voice_id, text=text)

        with open(OUTPUT_AUDIO_FILE, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        return OUTPUT_AUDIO_FILE
    except Exception as e:
        raise RuntimeError(f"ElevenLabs TTS failed: {e}")
