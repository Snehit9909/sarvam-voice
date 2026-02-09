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
def is_speech(pcm_bytes, threshold=0.15, samplerate=16000):
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
    release_mic()

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
        stream.stop()
        stream.close()
        
  

# import logging
# import sounddevice as sd
# import soundfile as sf
# import numpy as np
# import torch
# import queue

# # Silence torch noise
# logging.getLogger("torch").setLevel(logging.ERROR)

# DEFAULT_SAMPLE_RATE = 16000
# CHANNELS = 1
# BLOCKSIZE = 512

# # Load Silero VAD
# VAD_MODEL, _ = torch.hub.load(
#     repo_or_dir="snakers4/silero-vad",
#     model="silero_vad",
#     trust_repo=True
# )
# VAD_MODEL.eval()

# # -------------------------------------------------
# # VAD detection (High-Confidence)
# # -------------------------------------------------
# def is_speech(pcm_bytes, threshold=0.45, samplerate=16000):
#     if not pcm_bytes:
#         return False

#     audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    
#     # 🛡️ FIX 2: Ensure we only send exactly 512 samples to the model
#     # If the chunk is bigger or smaller, we slice it or pad it
#     if len(audio) > 512:
#         audio = audio[:512]
#     elif len(audio) < 512:
#         return False # Too small to be meaningful speech

#     with torch.no_grad():
#         conf = VAD_MODEL(torch.from_numpy(audio), samplerate).item()
    
#     return conf > threshold

# # ... (rest of the file remains the same)
# # -------------------------------------------------
# # Mic streaming engine
# # -------------------------------------------------
# _audio_queue = queue.Queue(maxsize=100)
# _stream = None

# def _audio_callback(indata, frames, time, status):
#     if status:
#         return
#     try:
#         _audio_queue.put_nowait(bytes(indata))
#     except queue.Full:
#         try:
#             _audio_queue.get_nowait()
#             _audio_queue.put_nowait(bytes(indata))
#         except:
#             pass

# def open_mic_stream():
#     global _stream
#     if _stream is not None:
#         return
    
#     # Clear queue before starting
#     while not _audio_queue.empty():
#         _audio_queue.get_nowait()

#     _stream = sd.RawInputStream(
#         samplerate=DEFAULT_SAMPLE_RATE,
#         channels=CHANNELS,
#         dtype="int16",
#         blocksize=BLOCKSIZE,
#         callback=_audio_callback
#     )
#     _stream.start()

# def read_audio_frame():
#     try:
#         return _audio_queue.get(timeout=0.1)
#     except queue.Empty:
#         return None

# def close_mic_stream():
#     global _stream
#     if _stream:
#         _stream.stop()
#         _stream.close()
#         _stream = None
#     # Purge queue
#     while not _audio_queue.empty():
#         try:
#             _audio_queue.get_nowait()
#         except:
#             break

# # -------------------------------------------------
# # Logic Helpers (REQUIRED by orchestrator)
# # -------------------------------------------------
# def release_mic():
#     """Stops all active sounddevice activity."""
#     try:
#         sd.stop()
#     except Exception:
#         pass
    
#     #updated

# def play_audio_stream(audio_io):
#     if audio_io is None:
#         return
#     try:
#         data, fs = sf.read(audio_io)
#         sd.play(data, fs)
#         sd.wait() # This blocks until the audio finishes. 
#     except Exception as e:
#         print(f" [Playback Error] {e}")