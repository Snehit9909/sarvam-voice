import time
import string
import threading

from audio.audio_utils import record_audio, play_audio
from agent.voice_agent import run_agent
from stt.stt_router import run_stt
from tts.tts_router import run_tts
from config.config import (
    STT_CONFIG,
    DEFAULT_STT_PROVIDER,
    DEFAULT_TTS_PROVIDER
)

playback_done = threading.Event()
playback_done.set()  

LAST_TTS_TEXT = ""   


def run_voice_pipeline():
    global LAST_TTS_TEXT

    current_stt_provider = DEFAULT_STT_PROVIDER
    current_tts_provider = DEFAULT_TTS_PROVIDER

    print("Voice Assistant Started", flush=True)
    print("Say 'stop' or 'exit' to quit", flush=True)
    print("Say 'use assembly stt' or 'use sarvam stt'", flush=True)
    print("Say 'use sarvam voice' or 'use elevenlabs voice'", flush=True)
    print("-" * 40, flush=True)

    while True:
        playback_done.wait()

        pipeline_start = time.perf_counter()

        record_audio(duration=3)

        # ---------------- STT ----------------
        stt_cfg = STT_CONFIG.get(current_stt_provider, {})
        stt_start = time.perf_counter()

        user_text = run_stt(
            provider=current_stt_provider,
            model=stt_cfg.get("model"),
            language=stt_cfg.get("language")
        )

        stt_time = time.perf_counter() - stt_start
        print(f"[TIME] STT only: {stt_time:.2f}s", flush=True)

        if not user_text.strip():
            continue

        normalized = user_text.lower().translate(
            str.maketrans("", "", string.punctuation)
        )

        if normalized == LAST_TTS_TEXT.lower():
            print("[ECHO] Ignored assistant's own voice", flush=True)
            continue

        if normalized in {"stop", "exit", "quit"}:
            print("Stopping...", flush=True)
            break

        # ---------------- STT SWITCH ----------------
        if "use assembly" in normalized:
            current_stt_provider = "assemblyai"
            print("[STT] Switched to AssemblyAI", flush=True)
            continue

        if "use sarvam " in normalized:
            current_stt_provider = "sarvam"
            print("[STT] Switched to Sarvam", flush=True)
            continue

        # ---------------- TTS SWITCH ----------------
        if "use sarvam voice" in normalized:
            current_tts_provider = "sarvam"
            print("[TTS] Switched to Sarvam", flush=True)
            continue

        if "use elevenlabs voice" in normalized:
            current_tts_provider = "elevenlabs"
            print("[TTS] Switched to ElevenLabs", flush=True)
            continue

        print(f"You said: {user_text}", flush=True)

        # ---------------- AGENT ----------------
        agent_start = time.perf_counter()
        response_text = run_agent(user_text)
        agent_time = time.perf_counter() - agent_start

        print(f"Agent: {response_text}", flush=True)
        print(f"[TIME] Agent only: {agent_time:.2f}s", flush=True)

        LAST_TTS_TEXT = response_text  

        # ---------------- TTS ----------------
        tts_start = time.perf_counter()
        audio_path = run_tts(
            response_text,
            provider=current_tts_provider
        )
        tts_time = time.perf_counter() - tts_start
        print(f"[TIME] TTS only: {tts_time:.2f}s", flush=True)

        def play_and_release():
            play_audio(audio_path)
            time.sleep(0.5)  
            playback_done.set()

        playback_done.clear()
        threading.Thread(
            target=play_and_release,
            daemon=True
        ).start()

        total_time = time.perf_counter() - pipeline_start
        print(f"[TIME] Total processing: {total_time:.2f}s", flush=True)
        print("-" * 40, flush=True)


if __name__ == "__main__":
    run_voice_pipeline()
