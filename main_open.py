import time
from audio_utils import record_audio, play_audio
from stt_open import speech_to_text
from tts_open import text_to_speech
from agent.voice_agent import run_agent  # keep your Strands agent

def voice_loop():
    print("⚡ Open-Source Voice Assistant Started")

    while True:
        # 1. Record
        record_audio(duration=3)

        start_total = time.perf_counter()

        # 2. STT
        start = time.perf_counter()
        user_text = speech_to_text()
        stt_time = time.perf_counter() - start
        print(f"   ** STT: {stt_time:.2f}s")

        if not user_text.strip():
            continue
        if any(w in user_text.lower() for w in ["exit", "stop"]):
            print("👋 Exiting voice loop")
            break

        # 3. Agent
        start = time.perf_counter()
        response_text = run_agent(user_text)
        agent_time = time.perf_counter() - start
        print(f"   ** Agent: {agent_time:.2f}s")
        print(f"🤖 Response: {response_text}")

        # 4. TTS
        start = time.perf_counter()
        text_to_speech(response_text)
        tts_time = time.perf_counter() - start
        print(f"   ** TTS: {tts_time:.2f}s")

        # 5. Playback
        play_audio()

        total = time.perf_counter() - start_total
        print(f"🌐 Total Latency: {total:.2f}s")
        print("-" * 35)

if __name__ == "__main__":
    voice_loop()
