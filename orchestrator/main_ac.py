import time
import string
import os

from stt.stt1 import speech_to_text
from agent.agentcore_agent import run_agent
from audio.audio_utils import record_audio, play_audio
from tts.tts_router import run_tts
from config.config import DEFAULT_TTS_PROVIDER, TTS_CONFIG


def run_voice_pipeline():
    stt_model = os.getenv("STT_MODEL", "saarika:v2.5")
    stt_language = os.getenv("STT_LANGUAGE", "en-IN")

    current_tts_provider = os.getenv("TTS_PROVIDER", DEFAULT_TTS_PROVIDER)
    current_voice = TTS_CONFIG[current_tts_provider]["voice"]

    print("Voice assistant started.", flush=True)
    print("Say 'stop' or 'exit' to quit.", flush=True)
    print("Say 'use sarvam voice' or 'use elevenlabs voice' to switch.", flush=True)
    print()

    print(f"[BOOT] TTS Provider -> {current_tts_provider}", flush=True)
    print(f"[BOOT] Voice -> {current_voice}", flush=True)
    print()

    while True:
        pipeline_start = time.perf_counter()

        record_audio(duration=3)

        user_text = speech_to_text(
            model_name=stt_model,
            language_code=stt_language
        )

        if not user_text.strip():
            continue

        normalized = user_text.lower().translate(
            str.maketrans("", "", string.punctuation)
        )

        if normalized in ["stop", "exit", "quit"]:
            print("Exiting voice assistant.", flush=True)
            break

        if "use sarvam voice" in normalized:
            current_tts_provider = "sarvam"
            current_voice = TTS_CONFIG["sarvam"]["voice"]
            print("[TTS] Switched -> Sarvam", flush=True)
            continue

        if "use elevenlabs voice" in normalized:
            current_tts_provider = "elevenlabs"
            current_voice = TTS_CONFIG["elevenlabs"]["voice"]
            print("[TTS] Switched -> ElevenLabs", flush=True)
            continue

        print(f"You said: {user_text}", flush=True)

        response_text = run_agent(user_text)

        if not response_text:
            print("[WARN] Empty AgentCore response. Skipping TTS.", flush=True)
            continue


        print(f"AgentCore response: {response_text}", flush=True)

        audio_path = run_tts(
            response_text,
            provider=current_tts_provider
        )

        play_audio(audio_path)

        total_time = time.perf_counter() - pipeline_start
        print(f"[TIME] Total pipeline time: {total_time:.2f}s", flush=True)
        print("-" * 40, flush=True)


if __name__ == "__main__":
    run_voice_pipeline()
