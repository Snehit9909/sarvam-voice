from tts.tts_eleven import text_to_speech

if __name__ == "__main__":
    audio_path = text_to_speech(
        "Hello! This is a test of ElevenLabs text to speech.",
        voice="Rachel"
    )
    print("Audio generated at:", audio_path)
