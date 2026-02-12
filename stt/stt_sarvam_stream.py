import io
import time
import threading
import queue
import numpy as np
import soundfile as sf

from sarvamai import SarvamAI
from audio.audio_utils import (
    open_mic_stream,
    close_mic_stream,
    read_audio_frame,
    is_speech
)
from config.config import SARVAM_API_KEY

client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

mic_gate = threading.Event()
mic_gate.set()

transcript_queue = queue.Queue()

SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 0.8  # Increased slightly to avoid cutting off natural pauses

def stream_stt_sarvam():
    print(" [Sarvam] Listening (sentence-level STT)", flush=True)
    open_mic_stream()

    pcm_buffer = bytearray()
    last_voice_time = None
    in_speech = False

    try:
        while True:
            frame = read_audio_frame()
            
            # --- CRITICAL FIX: Flush everything if mic is gated ---
            if not mic_gate.is_set():
                pcm_buffer.clear()
                in_speech = False
                # Drain the queue so main thread doesn't get old text
                while not transcript_queue.empty():
                    try:
                        transcript_queue.get_nowait()
                    except queue.Empty:
                        break
                continue

            if is_speech(frame):
                if not in_speech:
                    # EMIT START_SPEECH SIGNAL
                    yield {
                        "type": "events", 
                        "data": {"signal_type": "START_SPEECH"}
                    }
                    pcm_buffer.clear()
                    in_speech = True
                
                pcm_buffer.extend(frame)
                last_voice_time = time.time()
           
            elif in_speech:
                if time.time() - last_voice_time > SILENCE_TIMEOUT:
                    pcm_bytes = bytes(pcm_buffer)
                    audio_np = np.frombuffer(pcm_bytes, dtype=np.int16)

                    wav_io = io.BytesIO()
                    sf.write(wav_io, audio_np, SAMPLE_RATE, format="WAV", subtype="PCM_16")
                    wav_io.seek(0)

                    try:
                        # Brevity reinforcement: append instruction to prompt if API supports it
                        response = client.speech_to_text.transcribe(
                            file=("speech.wav", wav_io, "audio/wav"),
                            model="saarika:v2.5",
                            language_code="en-IN"
                        )
                        text = response.transcript.strip()
                        # Only queue if text exists
                        if text:
                            transcript_queue.put(text)
                    except Exception as e:
                        print(f" [Sarvam] STT error: {e}", flush=True)

                    pcm_buffer.clear()
                    in_speech = False

            while not transcript_queue.empty():
                yield {"type": "content", "text": transcript_queue.get()}

    finally:
        close_mic_stream()
