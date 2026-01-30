# main2.py
import time
from stt.stt1 import speech_to_text
from tts.tts1 import text_to_speech
from audio.audio_utils import play_audio
from agent.voice_agent import run_agent

def run_voice_pipeline(stt_model, stt_language, tts_voice):
    timings = {}
    pipeline_start = time.perf_counter()

    # STT
    start = time.perf_counter()
    user_text = speech_to_text(model_name=stt_model, language_code=stt_language)
    timings["stt"] = time.perf_counter() - start

    if not user_text.strip():
        return None

    # Agent
    start = time.perf_counter()
    response_text = run_agent(user_text)
    timings["agent"] = time.perf_counter() - start

    # TTS
    start = time.perf_counter()
    audio_path = text_to_speech(response_text, voice=tts_voice)
    timings["tts"] = time.perf_counter() - start

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    timings["total"] = time.perf_counter() - pipeline_start

    print(f"User: {user_text}")
    print(f"Assistant: {response_text}")
    print("Timings:", timings)

    return {
        "user_text": user_text,
        "response_text": response_text,
        "audio_path": audio_path,
        "audio_bytes": audio_bytes,
        "timings": timings
    }

if __name__ == "__main__":
    result = run_voice_pipeline(
        stt_model="saarika:v2.5",
        tts_voice="anushka",
        stt_language="en-IN"
    )

    if result:
        print("User said:", result["user_text"])
        print("Assistant:", result["response_text"])
        print("Audio saved at:", result["audio_path"])
        print("Timings:", result["timings"])
    
