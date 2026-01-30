import sounddevice as sd
import soundfile as sf
from config.config import INPUT_AUDIO_FILE, OUTPUT_AUDIO_FILE

def record_audio(duration=3, samplerate=44100):
    """
    Records audio from microphone and saves it to INPUT_AUDIO_FILE.
    """
    print(f"Recording {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(INPUT_AUDIO_FILE, audio, samplerate)
    print(f"Recording saved to {INPUT_AUDIO_FILE}")

def play_audio(path):
    """
    Plays a WAV audio file.
    """
    data, samplerate = sf.read(path)
    sd.play(data, samplerate)
    sd.wait()
