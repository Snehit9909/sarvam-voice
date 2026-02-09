import assemblyai as aai
from assemblyai.streaming.v3 import StreamingClient, StreamingClientOptions, TurnEvent
from config.config import ASSEMBLYAI_API_KEY

def stream_stt_assembly():
    options = StreamingClientOptions(
        api_key=ASSEMBLYAI_API_KEY,
        sample_rate=16000,
        language_code="en_us", 
        end_of_turn_detection=True,
        end_of_turn_confidence_threshold=0.3 
    )

    client = StreamingClient(options=options)

    try:
        client.connect() 
        
        mic_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        print(" [MIC] AssemblyAI Live. Speak clearly...")

        for event in client.stream(mic_stream):
            # Check for Final Sentences
            if isinstance(event, TurnEvent) and event.transcript:
                yield event.transcript
            
            # Check for partial text to confirm it hears you
            elif hasattr(event, 'text') and event.text:
                # Use a clear terminal overwrite for debugging
                print(f"DEBUG (Partial): {event.text[:60]}...", end="\r")
                
    except Exception as e:
        print(f"[STT] AssemblyAI Error: {e}")
    finally:
        if hasattr(client, 'close'):
            client.close()
