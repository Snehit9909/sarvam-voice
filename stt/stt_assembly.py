import threading
import queue
from enum import Enum

import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingEvents,
    StreamingSessionParameters,
)
from assemblyai.extras import MicrophoneStream
from config.config import ASSEMBLYAI_API_KEY

# ======================================================
# AssemblyAI model selector
# ======================================================

class AssemblySTTModel(str, Enum):
    UNIVERSAL_2 = "universal_2"
    UNIVERSAL_3_PRO = "universal_3_pro"

# ======================================================
# Runtime state
# ======================================================

mic_gate = threading.Event()
mic_gate.set()

transcript_queue = queue.Queue()

# ======================================================
# Helpers
# ======================================================

def purge_queue():
    while not transcript_queue.empty():
        try:
            transcript_queue.get_nowait()
        except:
            break

def on_turn(client, turn):
    if not mic_gate.is_set():
        return

    # Partial transcript
    if turn.transcript and not turn.end_of_turn:
        print(f"  {turn.transcript}...", end="\r", flush=True)

    # Final transcript
    if turn.transcript and turn.end_of_turn:
        print(f"\n  [AssemblyAI]: {turn.transcript}", flush=True)
        purge_queue()
        transcript_queue.put(turn.transcript)

def on_error(client, error):
    print(f" [AssemblyAI] Error: {error}", flush=True)

# ======================================================
# Streaming STT (Universal-2 / Universal-3 Pro)
# ======================================================

def stream_stt_assembly(
    sample_rate: int = 16000,
    model: AssemblySTTModel = AssemblySTTModel.UNIVERSAL_2,
):
    client = StreamingClient(
        StreamingClientOptions(api_key=ASSEMBLYAI_API_KEY)
    )

    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Error, on_error)

    try:
        if model == AssemblySTTModel.UNIVERSAL_3_PRO:
            session_params = StreamingSessionParameters(
                sample_rate=sample_rate,
                speech_model="universal-streaming", 
                format_turns=True, #
                end_of_turn_confidence_threshold=0.5 # Better for conversational flow
            )
            print(" [AssemblyAI] Universal-3 Pro ACTIVATED", flush=True)

        else:
            session_params = StreamingSessionParameters(
                sample_rate=sample_rate
                # Universal-2 is the default when speech_model is omitted in v3
            )
            print("  [AssemblyAI] Universal-2 ACTIVATED", flush=True)

        client.connect(session_params)
        

        mic_stream = MicrophoneStream(sample_rate=sample_rate)

        def audio_worker():
            try:
                def gated_generator():
                    for chunk in mic_stream:
                        if mic_gate.is_set():
                            yield chunk

                client.stream(gated_generator())
            except Exception as e:
                print(f" [AssemblyAI] Audio thread error: {e}", flush=True)

        threading.Thread(target=audio_worker, daemon=True).start()

        while True:
            text = transcript_queue.get()
            if isinstance(text, str):
                yield text

    except Exception as e:
        print(f" [AssemblyAI] Fatal STT error: {e}", flush=True)

    finally:
        try:
            client.close()
        except Exception:
            pass
