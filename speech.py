import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from sarvamai import SarvamAI

SAMPLE_RATE = 16000
RECORD_SECONDS = 5
LANG = "en-IN"  


class SarvamSTT:
    def __init__(self, api_key):
        self.client = SarvamAI(api_subscription_key=api_key)

    def record_audio(self, filename="input.wav"):
        print("🎤 Speak now...")
        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        write(filename, SAMPLE_RATE, audio)
        print("✅ Audio recorded:", filename)

    def transcribe(self, audio_file="input.wav"):
        response = self.client.speech_to_text.transcribe(
            file=open(audio_file, "rb"),
            language_code=LANG
        )
        return response.transcript
