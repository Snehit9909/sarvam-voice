import base64
from sarvamai import SarvamAI

LANG = "en-IN"


class SarvamTTS:
    def __init__(self, api_key):
        self.client = SarvamAI(api_subscription_key=api_key)

    def synthesize(self, text, output_file="output.wav"):
        response = self.client.text_to_speech.convert(
            text=text,
            target_language_code=LANG
        )

        audio_base64 = response.audios[0]
        audio_bytes = base64.b64decode(audio_base64)

        with open(output_file, "wb") as f:
            f.write(audio_bytes)

        print("🔊 Audio generated:", output_file)
