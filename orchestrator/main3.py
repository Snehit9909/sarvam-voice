# main3.py
import time
import string
from stt.stt1 import speech_to_text
from tts.tts_eleven import text_to_speech
from agent.voice_agent import run_agent
from audio.audio_utils import record_audio, play_audio

def run_voice_pipeline(stt_model="saarika:v2.5", stt_language="en-IN", tts_voice="Adam"):
    print("Voice assistant started. Say 'stop' or 'exit' to quit.\n")
    
    while True:
        timings = {}
        pipeline_start = time.perf_counter()

        # ------------------- RECORD & STT -------------------
        start = time.perf_counter()
        record_audio(duration=3)
        user_text = speech_to_text(model_name=stt_model, language_code=stt_language)
        timings["stt"] = time.perf_counter() - start

        if not user_text.strip():
            print("No speech detected. Try again.")
            continue

        # ------------------- NORMALIZE INPUT -------------------
        normalized_text = user_text.strip().lower().translate(str.maketrans("", "", string.punctuation))
        if normalized_text in ["stop", "exit", "quit"]:
            print("Exiting voice assistant. Goodbye!")
            break

        print("You said:", user_text)

        # ------------------- AGENT -------------------
        start = time.perf_counter()
        response_text = run_agent(user_text)
        timings["agent"] = time.perf_counter() - start
        print("Agent response:", response_text)

        # ------------------- TTS -------------------
        start = time.perf_counter()
        audio_path = text_to_speech(response_text, voice=tts_voice)
        timings["tts"] = time.perf_counter() - start
        print("Audio generated at:", audio_path)

        # ------------------- PLAY AUDIO -------------------
        play_audio(audio_path)

        # ------------------- TIMINGS -------------------
        timings["total"] = time.perf_counter() - pipeline_start
        print("Timings (seconds):", {k: round(v,2) for k,v in timings.items()})
        print("-"*40)

if __name__ == "__main__":
    run_voice_pipeline()
