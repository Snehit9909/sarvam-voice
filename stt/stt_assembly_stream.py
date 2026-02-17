# import assemblyai as aai
# from assemblyai.streaming.v3 import StreamingClient, StreamingClientOptions, TurnEvent
# from config.config import ASSEMBLYAI_API_KEY

# def stream_stt_assembly():
#     options = StreamingClientOptions(
#         api_key=ASSEMBLYAI_API_KEY,
#         sample_rate=16000,
#         language_code="en_us", 
#         end_of_turn_detection=True,
#         end_of_turn_confidence_threshold=0.3 
#     )

#     client = StreamingClient(options=options)

#     try:
#         client.connect() 
        
#         mic_stream = aai.extras.MicrophoneStream(sample_rate=16000)
#         print(" [MIC] AssemblyAI Live. Speak clearly...")

#         for event in client.stream(mic_stream):
#             # Check for Final Sentences
#             if isinstance(event, TurnEvent) and event.transcript:
#                 yield event.transcript
            
#             # Check for partial text to confirm it hears you
#             elif hasattr(event, 'text') and event.text:
#                 # Use a clear terminal overwrite for debugging
#                 print(f"DEBUG (Partial): {event.text[:60]}...", end="\r")
                
#     except Exception as e:
#         print(f"[STT] AssemblyAI Error: {e}")
#     finally:
#         if hasattr(client, 'close'):
#             client.close()

import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingEvents,
    StreamingParameters,
    TerminationEvent,
    TurnEvent,
    StreamingError,
)
from config.config import ASSEMBLYAI_API_KEY


def stream_stt_assembly():

    interruption_sent = False

    # -------------------------
    # Event Handlers
    # -------------------------

    def on_begin(self, event: BeginEvent):
        print(f"[AssemblyAI] ✅ Session started: {event.id}")

    def on_turn(self, event: TurnEvent):
        nonlocal interruption_sent

        transcript = (event.transcript or "").strip()

        # -----------------------------
        # 🔥 INTERRUPTION DETECTION
        # -----------------------------
        # If assistant is speaking and user starts speaking again,
        # your main loop will stop TTS when it receives START_SPEECH

        if transcript and not event.end_of_turn:
            if not interruption_sent:
                interruption_sent = True
                yield_queue.append({
                    "type": "events",
                    "data": {"signal_type": "START_SPEECH"}
                })

        # -----------------------------
        # 📝 FINAL TRANSCRIPT
        # -----------------------------
        if transcript and event.end_of_turn:
            yield_queue.append({
                "type": "content",
                "text": transcript
            })
            interruption_sent = False

    def on_terminated(self, event: TerminationEvent):
        print(f"[AssemblyAI] 🛑 Session terminated")

    def on_error(self, self_client, error: StreamingError):
        print(f"[AssemblyAI] ❌ Error: {error}")

    # -------------------------
    # Setup Client
    # -------------------------

    client = StreamingClient(
        StreamingClientOptions(
            api_key=ASSEMBLYAI_API_KEY,
            api_host="streaming.assemblyai.com",
        )
    )

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    # -------------------------
    # Generator Bridge
    # -------------------------

    yield_queue = []

    try:
        client.connect(
            StreamingParameters(
                sample_rate=16000,
                format_turns=True,
            )
        )

        print("[AssemblyAI] 🎙 Streaming Active...")

        mic_stream = aai.extras.MicrophoneStream(sample_rate=16000)

        # Start streaming (non-blocking)
        client.stream(mic_stream)

        # Infinite generator loop
        while True:
            if yield_queue:
                yield yield_queue.pop(0)

    except Exception as e:
        print(f"[STT] AssemblyAI Error: {e}")

    finally:
        client.disconnect(terminate=True)
