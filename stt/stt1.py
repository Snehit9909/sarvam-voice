from sarvamai import SarvamAI
from config.config import SARVAM_API_KEY, INPUT_AUDIO_FILE

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

def speech_to_text(model_name="saarika:v2.5", language_code="en-IN"):
    try:
        with open(INPUT_AUDIO_FILE, "rb") as audio_file:
            response = client.speech_to_text.transcribe(
                file=audio_file,
                model=model_name,
                language_code=language_code
            )
        text = response.transcript
        print(f"You said: {text}")
        return text
    except Exception as e:
        raise RuntimeError(f"STT failed: {e}")
