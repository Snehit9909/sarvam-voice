from scipy.io.wavfile import read
import sounddevice as sd

from speech import SarvamSTT
from text import SarvamTTS

API_KEY = "sk_pan06xjq_quAeCvDv57KZWsIyXsXuDc2t"


def play_audio(filename):
    rate, data = read(filename)
    sd.play(data, rate)
    sd.wait()


def main():
    stt = SarvamSTT(API_KEY)
    tts = SarvamTTS(API_KEY)

    # Step 1: Record + STT
    stt.record_audio()
    text = stt.transcribe()
    print("📝 You said:", text)

    # Step 2: Process text
    reply = f"You said: {text}"

    # Step 3: TTS + playback
    tts.synthesize(reply)
    play_audio("output.wav")


if __name__ == "__main__":
    main()
