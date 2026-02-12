import logging
import sounddevice as sd
import soundfile as sf
import numpy as np
import torch
import queue

# -------------------------------------------------
# Silence torch noise
# -------------------------------------------------
logging.getLogger("torch").setLevel(logging.ERROR)
logging.getLogger("torch.hub").setLevel(logging.ERROR)

DEFAULT_SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1024

# -------------------------------------------------
# Load Silero VAD
# -------------------------------------------------
VAD_MODEL, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    trust_repo=True
)
VAD_MODEL.eval()
VAD_MODEL.to(torch.device("cpu"))

# -------------------------------------------------
# VAD detection (RAW PCM)
# -------------------------------------------------
def is_speech(pcm_bytes, threshold=0.5, samplerate=16000):
    if not pcm_bytes:
        return False

    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    window = 512

    for i in range(0, len(audio) - window, window):
        chunk = audio[i:i + window]
        with torch.no_grad():
            conf = VAD_MODEL(
                torch.from_numpy(chunk),
                samplerate
            ).item()
        if conf > threshold:
            return True
    return False

# -------------------------------------------------
# Mic streaming engine
# -------------------------------------------------
_audio_queue = queue.Queue()
_stream = None

def _audio_callback(indata, frames, time, status):
    if status:
        return
    _audio_queue.put(bytes(indata))

def open_mic_stream():
    global _stream
    if _stream is not None:
        return

    _stream = sd.RawInputStream(
        samplerate=DEFAULT_SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=BLOCKSIZE,
        callback=_audio_callback
    )
    _stream.start()

def read_audio_frame():
    return _audio_queue.get()

def close_mic_stream():
    global _stream
    if _stream:
        _stream.stop()
        _stream.close()
        _stream = None
    while not _audio_queue.empty():
        _audio_queue.get_nowait()

# -------------------------------------------------
# Legacy helpers (REQUIRED by orchestrator)
# -------------------------------------------------
def release_mic():
    try:
        sd.stop()
    except Exception:
        pass
    
def clear_audio_queue():
    """Completely empties the audio queue to prevent processing old sounds."""
    while not _audio_queue.empty():
        try:
            _audio_queue.get_nowait()
        except queue.Empty:
            break

def play_audio_stream(audio_chunks, samplerate=22050):
    """
    Plays TTS audio chunks (int16 PCM).
    """
    stream = sd.RawOutputStream(
        samplerate=samplerate,
        channels=CHANNELS,
        dtype="int16",
        blocksize=1024
    )

    try:
        stream.start()
        for chunk in audio_chunks:
            if chunk:
                stream.write(np.frombuffer(chunk, dtype=np.int16))
    finally:
        # abort() stops playback immediately without waiting for buffer to drain
        stream.abort() 
        stream.close()
