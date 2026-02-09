import base64
from sarvamai import SarvamAI
from config.config import SARVAM_API_KEY

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

def stream_tts_sarvam(text_stream, lang_code="None"):
    buffer = ""
    for token in text_stream:
        buffer += token
        if buffer.strip().endswith((".", "!", "?")):
            response = client.text_to_speech.convert(
                text=buffer,
                model="bulbul:v2",
                target_language_code="en-IN",
                speaker="anushka" 
            )
           
            audio_b64 = response.audios[0]
            audio_bytes = base64.b64decode(audio_b64)
            yield audio_bytes

            buffer = ""
# import base64
# import io
# from sarvamai import SarvamAI
# from config.config import SARVAM_API_KEY

# client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

# import base64
# import io
# from sarvamai import SarvamAI
# from config.config import SARVAM_API_KEY

# client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

# def stream_tts_sarvam(text, lang_code="en-IN"):
#     try:
#         if not text or not text.strip():
#             return None

#         response = client.text_to_speech.convert(
#             text=text,                      # ✅ FIXED
#             model="bulbul:v2",
#             target_language_code=lang_code,
#             speaker="anushka"
#         )

#         audio_bytes = bytearray()

#         # Sarvam returns base64 audio
#         if hasattr(response, "audio"):
#             audio_bytes.extend(base64.b64decode(response.audio))
#         elif hasattr(response, "audios"):
#             for chunk in response.audios:
#                 audio_bytes.extend(base64.b64decode(chunk))

#         if not audio_bytes:
#             print(" [Sarvam TTS] Empty audio returned")
#             return None

#         return io.BytesIO(audio_bytes)

#     except Exception as e:
#         print(f" [Sarvam TTS Error] {e}")
#         return None
