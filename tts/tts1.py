from sarvamai import SarvamAI
from config.config import SARVAM_API_KEY, OUTPUT_AUDIO_FILE
import base64

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

def text_to_speech(text: str, voice: str = "anushka") -> str:
   
    try:
        response = client.text_to_speech.convert(
            text=text,
            model="bulbul:v2",   
            target_language_code="en-IN",
            speaker=voice
        )

        if hasattr(response, 'audios') and response.audios:
            audio_base64_string = response.audios[0]
            audio_data = base64.b64decode(audio_base64_string)
            with open(OUTPUT_AUDIO_FILE, "wb") as f:
                f.write(audio_data)
            return OUTPUT_AUDIO_FILE
        else:
            raise RuntimeError("No audio content in TTS response")
    except Exception as e:
        raise RuntimeError(f"TTS failed: {e}")
