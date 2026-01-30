import os
# ===== AWS =====
AWS_REGION = "us-east-1"
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# ===== SARVAM =====
SARVAM_API_KEY = "sk_pan06xjq_quAeCvDv57KZWsIyXsXuDc2t"

# ===== ELEVENLABS =====
ELEVENLABS_API_KEY = "e3b94ccdcb3196fd6b15665d0404205de84322437a9ba76e296936a033dea3e4"
ELEVENLABS_MODEL = "eleven_monolingual_v1"

# ===== TTS PROVIDERS (fixed voice per provider) =====
TTS_CONFIG = {
    "elevenlabs": {
        "provider": "elevenlabs",
        "voice": "Adam"
    },
    "sarvam": {
        "provider": "sarvam",
        "voice": "anushka"
    }
}

# Read from environment
DEFAULT_TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs")

if DEFAULT_TTS_PROVIDER not in TTS_CONFIG:
    raise ValueError(
        f"Invalid TTS_PROVIDER env value: {DEFAULT_TTS_PROVIDER}"
    )

# ===== AUDIO FILES =====
INPUT_AUDIO_FILE = "input.wav"
OUTPUT_AUDIO_FILE = "output.wav"
# Allowed STT models (Sarvam AI)
STT_MODELS = [
    "saarika:v2.5",
    "saaras:v3",
    "saarika:v1",
    "saarika:v2",
    "saarika:flash"
]

# STT languages
STT_LANGUAGES = {
    "English (India)": "en-IN",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Telugu": "te-IN"
}

# ElevenLabs voices (for reference, optional)
TTS_VOICES = [
    "Rachel",
    "Adam",
    "Bella",
    "Antoni",
    "Josh",
    "Arnold"
]
