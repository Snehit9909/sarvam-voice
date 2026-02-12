import sys, io, os, time, signal, uuid, threading
from stt.stt_router import stream_stt
from agent.agentcore_agent import run_agent
from tts.tts_router import run_tts
from audio.audio_utils import play_audio_stream, release_mic, clear_audio_queue
from config.config import DEFAULT_STT_PROVIDER, DEFAULT_TTS_PROVIDER
from stt.stt_assembly import purge_queue, mic_gate

# Global Variables for Interruption Tracking
current_tts_thread = None
stop_tts_event = threading.Event()
last_speech_start_time = 0

def tts_worker(audio_stream, stop_event):
    """Plays audio and listens for the stop signal to allow interruption."""
    try:
        def interruptible_generator(stream):
            for chunk in stream:
                if stop_event.is_set():
                    return 
                yield chunk
        play_audio_stream(interruptible_generator(audio_stream))
    except Exception as e:
        print(f" [TTS Worker] Error: {e}", flush=True)

def should_be_interrupted(result):
    """Detects Sarvam's START_SPEECH event signal."""
    if isinstance(result, dict) and result.get('type') == 'events':
        return result.get('data', {}).get('signal_type') == 'START_SPEECH'
    return False

def run():
    session_id = str(uuid.uuid4())
    current_stt = os.getenv("STT_PROVIDER", DEFAULT_STT_PROVIDER).lower()
    current_tts = os.getenv("TTS_PROVIDER", DEFAULT_TTS_PROVIDER).lower()
    global current_tts_thread, last_speech_start_time

    print(f" ENGINE READY | STT: {current_stt} | TTS: {current_tts}", flush=True)

    while True:
        try:
            release_mic()
            stt_generator = stream_stt(current_stt)

            for result in stt_generator:
                now = time.time()
                is_speaking = current_tts_thread and current_tts_thread.is_alive()

                # 1. LOG CHUNKS IN REAL-TIME (Diagnostics)
                if isinstance(result, dict) and result.get('type') == 'content':
                    raw_text = result.get('text', '').strip()
                    if raw_text:
                        # Print interim text in YELLOW to distinguish from final user commands
                        print(f"\033[93m [Mic Heard]: {raw_text}\033[0m", flush=True)
                elif isinstance(result, str):
                    raw_text = result
                    print(f"\033[93m [Mic Heard]: {raw_text}\033[0m", flush=True)
                else:
                    raw_text = ""

                # 2. INTERRUPTION LOGIC
                if should_be_interrupted(result):
                    if is_speaking and (now - last_speech_start_time) > 0.5:
                        print("\n [Interrupt] Voice detected! Silencing Assistant...", flush=True)
                        stop_tts_event.set()
                        clear_audio_queue()
                    continue

                # 3. ECHO PROTECTION (The Loophole Fix)
                if not raw_text: continue
                
                # If we are currently playing audio, discard whatever text the STT generated
                # because it's 99% likely to be the assistant hearing itself.
                if is_speaking:
                    # We stop the voice but DO NOT send this text to the agent
                    stop_tts_event.set()
                    clear_audio_queue()
                    continue 

                # 4. FINAL PROCESSING
                print(f" \033[92mUser said: {raw_text}\033[0m", flush=True)

                if any(cmd in raw_text.lower() for cmd in ["exit", "quit"]):
                    return

                # 5. AGENT RESPONSE
                response_text = run_agent(raw_text, session_id=session_id)
                print(f" Assistant: {response_text}", flush=True)

                # Reset and Start New TTS
                if current_tts_thread and current_tts_thread.is_alive():
                    stop_tts_event.set()
                    current_tts_thread.join(timeout=0.2)

                stop_tts_event.clear()
                audio_stream = run_tts(current_tts, response_text)
                last_speech_start_time = time.time()
                
                current_tts_thread = threading.Thread(
                    target=tts_worker, args=(audio_stream, stop_tts_event), daemon=True
                )
                current_tts_thread.start()
                
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