import sys
import io
import os
import time 
import signal
import uuid
from stt.stt_router import stream_stt
from agent.agentcore_agent import run_agent
from tts.tts_router import run_tts
from audio.audio_utils import play_audio_stream, release_mic, clear_audio_queue
from config.config import DEFAULT_STT_PROVIDER, DEFAULT_TTS_PROVIDER
from stt.stt_assembly import purge_queue, mic_gate, transcript_queue

# Windows UTF-8 safety
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ------------------------------------
# Signal handling
# ------------------------------------
def shutdown_handler(sig, frame):
    print("\n Engine shutting down", flush=True)
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# ------------------------------------
# Provider modes
# ------------------------------------
MIC_GATED_STT = {"sarvam"}
PROVIDER_STREAMING_STT = {"assemblyai"}

# ------------------------------------
# Main Engine
# ------------------------------------
def run():
    session_id = str(uuid.uuid4())
    current_stt = os.getenv("STT_PROVIDER", DEFAULT_STT_PROVIDER).lower()
    current_tts = os.getenv("TTS_PROVIDER", DEFAULT_TTS_PROVIDER).lower()
    assembly_model = os.getenv("ASSEMBLY_MODEL", "universal_3_pro")

    print(" STARTING STREAMING VOICE ASSISTANT", flush=True)
    print(f" STT: {current_stt} |  TTS: {current_tts}", flush=True)

    print(" ENGINE READY — SPEAK INTO YOUR MICROPHONE", flush=True)

    # -------------------------------------------------
    # MODE 1: TRUE STREAMING (AssemblyAI)
    # -------------------------------------------------
    if current_stt in PROVIDER_STREAMING_STT:
        mic_gate.set()
        print(" Listening...\n", flush=True)

        for user_text in stream_stt(current_stt):
            if not mic_gate.is_set():
                purge_queue()
                continue

            text_clean = "".join(c for c in user_text if ord(c) < 128).lower().strip()
            
            if len(text_clean.split()) < 3:
                continue

            print(f"\n User said: {user_text}", flush=True)

            if any(cmd in text_clean for cmd in ["exit", "quit"]):
                print(" Goodbye", flush=True)
                return

            response_text = run_agent(text_clean, session_id=session_id)
            audio_stream = run_tts(current_tts, response_text)

            mic_gate.clear() # STOP LISTENING
            try:
                play_audio_stream(audio_stream)
                time.sleep(1.2) # Wait for room to go silent
            finally:
                purge_queue()
                clear_audio_queue()
                mic_gate.set() # START LISTENING
                print(" [MIC] Listening...\n", flush=True)

    # -------------------------------------------------
    # MODE 2: MIC-GATED (Sarvam)
    # -------------------------------------------------
    else:
        mic_gate.set()
        print(" Listening (mic-gated mode)...\n", flush=True)

        while True:
            try:
                release_mic()
                stt_generator = stream_stt(current_stt)

                for user_text in stt_generator:
                    if not isinstance(user_text, str) or not mic_gate.is_set():
                        continue

                    text_clean = "".join(c for c in user_text if ord(c) < 128).lower().strip()
                    
                    # REPETITION FILTER: Ignore noise/echoes shorter than 1 words
                    if len(text_clean.split()) < 1:
                        continue

                    print(f" User said: {user_text}", flush=True)

                    if any(cmd in text_clean for cmd in ["exit", "quit", "goodbye"]):
                        print(" Goodbye", flush=True)
                        return

                    response_text = run_agent(f"{text_clean} (Answer briefly)", session_id=session_id)
                    print(f" Assistant: {response_text}", flush=True)

                    # --- TTS & Playback ---
                    audio_stream = run_tts(current_tts, response_text)

                    def ttfb_wrapper(stream):
                        nonlocal tts_start
                        first = True
                        for chunk in stream:
                            if first:
                                print(f" TTS Started playing", flush=True)
                                first = False
                            yield chunk

                    mic_gate.clear() # MUTE MIC
                    print(" [MIC] Muted (Assistant Speaking)", flush=True)

                    try:
                        tts_start = time.time()
                        play_audio_stream(ttfb_wrapper(audio_stream))
                        
                        # --- ENHANCED POST-PLAYBACK DRAIN ---
                        time.sleep(1.2) # Allow 1.2s for echo to clear
                        
                        while not transcript_queue.empty():
                            try:
                                discarded = transcript_queue.get_nowait()
                                print(f" [DEBUG] Discarded echo: '{discarded}'", flush=True)
                            except:
                                break
                    finally:
                        clear_audio_queue()
                        mic_gate.set() # OPEN MIC
                        print(" [MIC] Listening...\n", flush=True)

            except Exception as e:
                print(f" [Main] Loop error: {e}", flush=True)
                time.sleep(1)

if __name__ == "__main__":
    run()

    
# import sys
# import io
# import os
# import time
# import signal

# from stt.stt_router import stream_stt
# from agent.agentcore_agent import run_agent
# from tts.tts_router import run_tts
# from audio.audio_utils import play_audio_stream, release_mic
# from config.config import DEFAULT_STT_PROVIDER, DEFAULT_TTS_PROVIDER
# from stt.stt_assembly import purge_queue, mic_gate, transcript_queue

# # ------------------------------------
# # Windows UTF-8 safety
# # ------------------------------------
# if sys.platform == "win32":
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
#     sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# # ------------------------------------
# # Signal handling
# # ------------------------------------
# def shutdown_handler(sig, frame):
#     print("\n Engine shutting down", flush=True)
#     sys.exit(0)

# signal.signal(signal.SIGINT, shutdown_handler)
# signal.signal(signal.SIGTERM, shutdown_handler)

# # ------------------------------------
# # Provider modes
# # ------------------------------------
# MIC_GATED_STT = {"sarvam"}
# PROVIDER_STREAMING_STT = {"assemblyai"}

# # ------------------------------------
# # Main Engine
# # ------------------------------------
# # ... (Keep imports same) ...

# def run():
#     current_stt = os.getenv("STT_PROVIDER", DEFAULT_STT_PROVIDER).lower()
#     current_tts = os.getenv("TTS_PROVIDER", DEFAULT_TTS_PROVIDER).lower()
    
#     print("\n STARTING MULTILINGUAL STREAMING VOICE ASSISTANT", flush=True)
#     mic_gate.set()

#     while True:
#         try:
#             release_mic()
#             stt_generator = stream_stt(current_stt)

#             for result in stt_generator:
#                 # Unpack text and language
#                 user_text, lang_code = result if isinstance(result, tuple) else (result, "en-IN")

#                 if not mic_gate.is_set() or len(user_text.strip()) < 1:
#                     continue

#                 print(f"\n User said: {user_text} (Detected: {lang_code})", flush=True)

#                 if any(word in user_text.lower() for word in ["exit", "quit"]):
#                     print(" Goodbye")
#                     return

#                 # --- 1. Agent Core ---
#                 agent_start = time.time()
#                 response_text = run_agent(f"User speaking {lang_code}: {user_text}")
#                 agent_latency = (time.time() - agent_start) * 1000
#                 print(f" Assistant: {response_text}", flush=True)

#                 # ... (After Agent response) ...
#                 print(f" Assistant: {response_text}", flush=True)

#                 # 1. Generate Audio
#                 tts_start = time.time()
#                 audio_buffer = run_tts(current_tts, response_text, lang_code=lang_code)
                
#                 if audio_buffer:
#                     # 2. Latency Logging
#                     ttfb = (time.time() - tts_start) * 1000
#                     print(f" [Latency] Agent: {agent_latency:.0f}ms | TTS: {ttfb:.0f}ms")

#                     # 3. Mute Mic and Play
#                     mic_gate.clear() 
#                     try:
#                         audio_buffer.seek(0)
#                         play_audio_stream(audio_buffer)
#                     except Exception as play_err:
#                         print(f" [Playback Error] {play_err}")
#                     finally:
#                         time.sleep(0.4) # Small pause
#                         mic_gate.set()
#                         print(" [MIC] Listening...", flush=True)
#                 else:
#                     print(" [Error] TTS failed to generate audio.")

#         except Exception as e:
#             print(f" Engine error: {e}")
#             mic_gate.set()
#             time.sleep(1)

# if __name__ == "__main__":
#     run()