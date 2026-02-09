# tts_open.py
import torchaudio
from chatterbox.tts import ChatterboxTTS
from config.config import OUTPUT_AUDIO_FILE

# Load Chatterbox TTS model
tts_model = ChatterboxTTS.from_pretrained(device="cpu")

def text_to_speech(text):
    print("🔊 Generating speech with Chatterbox...")
    # Generate waveform from text
    wav = tts_model.generate(text)
    # Save to file
    torchaudio.save(OUTPUT_AUDIO_FILE, wav.unsqueeze(0), tts_model.sr)
    print(f"✅ Audio saved to {OUTPUT_AUDIO_FILE}")
