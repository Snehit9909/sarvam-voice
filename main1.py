import time
from audio.audio_utils import record_audio, play_audio
from stt.stt1 import speech_to_text
from tts.tts1 import text_to_speech
from agent.voice_agent import call_agent

def main():
    print("🎧 Voice Assistant Started")
    print("Say 'exit' or 'stop' to quit\n")

    while True:
        # 1. Recording Phase
        start_rec = time.perf_counter()
        record_audio(duration=5)
        rec_duration = time.perf_counter() - start_rec
        print(f"✅ Audio recorded ({rec_duration:.2f}s)")

        try:
            # 2. Transcription Phase (STT)
            start_stt = time.perf_counter()
            user_text = speech_to_text() 
            stt_duration = time.perf_counter() - start_stt
            # Note: The time is printed immediately after stt1.py's internal print
            print(f"   ** Transcription Latency: {stt_duration:.2f}s")

            if not user_text.strip():
                response = "I didn't catch that. Please repeat."
            elif any(word in user_text.lower() for word in ["exit", "stop"]):
                response = "Goodbye. Have a great day."
                text_to_speech(response)
                play_audio()
                break
            else:
                # 3. Brain Phase (LLM)
                start_agent = time.perf_counter()
                response = call_agent(user_text)
                agent_duration = time.perf_counter() - start_agent
                print(f"   ** Agent Thinking Time: {agent_duration:.2f}s")


                # 4. Synthesis Phase (TTS)
                start_tts = time.perf_counter()
                text_to_speech(response)
                tts_duration = time.perf_counter() - start_tts
                
                # Calculate Synthesis Rate (Chars per second)
                char_count = len(response)
                rate = char_count / tts_duration if tts_duration > 0 else 0
                
                print(f"   ** Synthesis Latency: {tts_duration:.2f}s [Speed: {rate:.1f} chars/sec]")

            # 5. Output Phase
            play_audio()
            print("-" * 40)

        except Exception as e:
            print(f"❌ Processing Error: {e}")
            continue

if __name__ == "__main__":
    main()
