# from tts.tts_sarvam_stream import stream_tts_sarvam
# from tts.tts_eleven_stream import speak_stream

# def run_tts(provider, text):
#     if provider == "sarvam":
#         return stream_tts_sarvam([text])
#     if provider == "elevenlabs":
#         return speak_stream(text)
#     raise ValueError("Unknown TTS provider")
from tts.tts_sarvam_stream import stream_tts_sarvam
from tts.tts_eleven_stream import speak_stream

def run_tts(provider, text, lang_code="en-IN"): # <--- Add lang_code here
    if provider == "sarvam":
        # Pass the lang_code to the actual streaming function
        return stream_tts_sarvam(text, lang_code=lang_code) 
    
    if provider == "elevenlabs":
        return speak_stream(text)
        
    raise ValueError(f"Unknown TTS provider: {provider}")