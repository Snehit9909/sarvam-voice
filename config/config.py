import os
# ===== AWS =====
AWS_REGION = "us-east-1"
BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


AGENT_RUNTIME_ARN = os.getenv("arn:aws:bedrock-agentcore:us-east-1:762233739050:runtime/app3-3trSxmCEpL")


# ===== SARVAM =====
SARVAM_API_KEY = "sk_pan06xjq_quAeCvDv57KZWsIyXsXuDc2t"

# ===== ELEVENLABS =====
ELEVENLABS_API_KEY = "sk_9211b1a9d8a6286f34fbc79008bb27e66572825d17fc8a9a"
ELEVENLABS_MODEL = "eleven_monolingual_v1"

# ================= ASSEMBLY AI =================
ASSEMBLYAI_API_KEY = "4d97faf049694691984880eafafa8d20"

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
# ===== STT CONFIG =====
STT_CONFIG = {
    "sarvam": {
        "provider": "sarvam",
        "model": "saarika:v2.5",
        "language": "en-IN"
    },
    "assemblyai": {
        "provider": "assemblyai",
        "models": {
            "universal_2": "universal-2",       
            "universal_3_pro": "universal-3-pro" 
        },
        "default_model": "universal_2"
    }
}

DEFAULT_STT_PROVIDER = os.getenv("STT_PROVIDER", "sarvam")

if DEFAULT_STT_PROVIDER not in STT_CONFIG:
    raise ValueError(f"Invalid STT_PROVIDER: {DEFAULT_STT_PROVIDER}")

# Allowed STT models (Sarvam AI)
STT_MODELS = [
    "saarika:v2.5",
    "saaras:v3",
    "saarika:v1",
    "saarika:v2",
    "saarika:flash"
]

# ===== UPDATED STT LANGUAGES =====
STT_LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Marathi": "mr-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Bengali": "bn-IN",
    "Auto-Detect": "unknown"  # Highly recommended
}

# Add a default language helper
DEFAULT_INPUT_LANGUAGE = os.getenv("INPUT_LANGUAGE", "unknown")

# ElevenLabs voices (for reference, optional)
TTS_VOICES = [
    "Rachel",
    "Adam",
    "Bella",
    "Antoni",
    "Josh",
    "Arnold"
]
