import sounddevice as sd
import numpy as np

DEFAULT_SAMPLE_RATE = 22050
CHANNELS = 1


def play_audio_stream(audio_chunks, samplerate=DEFAULT_SAMPLE_RATE):
    """
    Streaming PCM audio playback using sounddevice (Windows-safe).
    """
    stream = sd.OutputStream(
        samplerate=samplerate,
        channels=CHANNELS,
        dtype="int16"
    )
    stream.start()

    try:
        for chunk in audio_chunks:
            if chunk:
                audio_np = np.frombuffer(chunk, dtype=np.int16)
                stream.write(audio_np)
    finally:
        stream.stop()
        stream.close()
