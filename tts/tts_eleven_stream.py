from elevenlabs.client import ElevenLabs
from config.config import ELEVENLABS_API_KEY, TTS_CONFIG

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_MAP = {
    "Adam": "pNInz6obpgDQGcFmaJgB"
}

def speak_stream(text: str):
    """
    Streams audio bytes directly from ElevenLabs using the correct Voice ID.
    """
    voice_name = TTS_CONFIG["elevenlabs"]["voice"]
    # Look up the ID; if not found, use the name as fallback
    voice_id = VOICE_MAP.get(voice_name, voice_name)

    # print(f"[TTS] Streaming audio using Voice ID: {voice_id}")

    # Use 'stream' method for low-latency playback
    audio_stream = client.text_to_speech.stream(
        voice_id=voice_id,
        text=text,
        model_id="eleven_turbo_v2_5", # Optimized for speed
        output_format="pcm_22050"      # Matches your play_audio_stream samplerate
    )
    return audio_stream
