import sys
import os
import time
import uuid
import threading

from stt.stt_router import stream_stt
from agent.agentcore_agent import run_agent
from tts.tts_router import run_tts

from audio.audio_utils import (
    play_audio_stream,
    release_mic,
    clear_audio_queue
)

from config.config import DEFAULT_STT_PROVIDER, DEFAULT_TTS_PROVIDER
from stt.stt_assembly import purge_queue, mic_gate


# -------------------------------------------------
# GLOBAL STATE
# -------------------------------------------------
current_tts_thread = None
stop_tts_event = threading.Event()
last_speech_start_time = 0


# -------------------------------------------------
# TTS WORKER (TRUE INTERRUPTIBLE)
# -------------------------------------------------
def tts_worker(audio_stream, stop_event):
    try:
        play_audio_stream(audio_stream, stop_event)
    except Exception as e:
        print(f"[TTS Worker] Error: {e}", flush=True)


# -------------------------------------------------
# INTERRUPTION DETECTION
# -------------------------------------------------
def should_be_interrupted(result):
    if isinstance(result, dict) and result.get('type') == 'events':
        return result.get('data', {}).get('signal_type') == 'START_SPEECH'
    return False


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
def run():
    global current_tts_thread, last_speech_start_time

    session_id = str(uuid.uuid4())

    current_stt = os.getenv("STT_PROVIDER", DEFAULT_STT_PROVIDER).lower()
    current_tts = os.getenv("TTS_PROVIDER", DEFAULT_TTS_PROVIDER).lower()

    print(f"ENGINE READY | STT: {current_stt} | TTS: {current_tts}", flush=True)

    while True:
        try:
            release_mic()
            stt_generator = stream_stt(current_stt)

            for result in stt_generator:

                now = time.time()
                is_speaking = current_tts_thread and current_tts_thread.is_alive()

                raw_text = ""

                # -------------------------------------------------
                # LOG MIC CONTENT
                # -------------------------------------------------
                if isinstance(result, dict) and result.get('type') == 'content':
                    raw_text = result.get('text', '').strip()
                    if raw_text:
                        print(f"\033[93m[Mic Heard]: {raw_text}\033[0m", flush=True)

                elif isinstance(result, str):
                    raw_text = result.strip()
                    print(f"\033[93m[Mic Heard]: {raw_text}\033[0m", flush=True)

                # -------------------------------------------------
                # INTERRUPTION HANDLING (HARD STOP)
                # -------------------------------------------------
                if should_be_interrupted(result):

                    if is_speaking and (now - last_speech_start_time) > 0.2:
                        print("\n[Interrupt] Voice detected! Silencing Assistant...", flush=True)

                        stop_tts_event.set()

                        if current_tts_thread and current_tts_thread.is_alive():
                            current_tts_thread.join(timeout=0.3)

                        clear_audio_queue()

                    continue

                if not raw_text:
                    continue

                # -------------------------------------------------
                # IF STILL SPEAKING, DO NOT PROCESS TEXT
                # -------------------------------------------------
                if is_speaking:
                    stop_tts_event.set()

                    if current_tts_thread and current_tts_thread.is_alive():
                        current_tts_thread.join(timeout=0.3)

                    clear_audio_queue()
                    continue

                # -------------------------------------------------
                # FINAL USER TEXT
                # -------------------------------------------------
                print(f"\033[92mUser said: {raw_text}\033[0m", flush=True)

                if any(cmd in raw_text.lower() for cmd in ["exit", "quit"]):
                    return

                # -------------------------------------------------
                # AGENT RESPONSE
                # -------------------------------------------------
                response_text = run_agent(raw_text, session_id=session_id)

                print(f"Assistant: {response_text}", flush=True)

                # Stop any existing TTS cleanly
                if current_tts_thread and current_tts_thread.is_alive():
                    stop_tts_event.set()
                    current_tts_thread.join(timeout=0.3)

                stop_tts_event.clear()

                audio_stream = run_tts(current_tts, response_text)
                last_speech_start_time = time.time()

                current_tts_thread = threading.Thread(
                    target=tts_worker,
                    args=(audio_stream, stop_tts_event),
                    daemon=True
                )

                current_tts_thread.start()

        except Exception as e:
            print(f"[Main] Loop error: {e}", flush=True)
            time.sleep(1)


if __name__ == "__main__":
    run()