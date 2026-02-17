import logging
from typing import Type
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    TerminationEvent,
    TurnEvent,
)

# 🔑 Use environment variable in production
api_key = "4d97faf049694691984880eafafa8d20"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------
# STATE FLAGS
# -----------------------
is_user_speaking = False
is_assistant_speaking = False
last_turn_order = None


# -----------------------
# TTS CONTROL (Replace with your real TTS stop/play)
# -----------------------
def stop_tts():
    global is_assistant_speaking
    print("🛑 STOPPING TTS (INTERRUPTION)")
    is_assistant_speaking = False


def play_tts(text):
    global is_assistant_speaking
    print(f"🤖 Assistant speaking: {text}")
    is_assistant_speaking = True


def call_llm(user_text):
    # Replace with your real LLM call
    return f"You said: {user_text}"


# -----------------------
# EVENT HANDLERS
# -----------------------

def on_begin(self: Type[StreamingClient], event: BeginEvent):
    print(f"\n✅ Session started: {event.id}")


def on_turn(self: Type[StreamingClient], event: TurnEvent):
    global is_user_speaking
    global is_assistant_speaking
    global last_turn_order

    transcript = event.transcript.strip()

    # Ignore empty transcript noise
    if not transcript:
        return

    # -------------------------
    # USER STARTED SPEAKING
    # -------------------------
    if not event.end_of_turn:

        if not is_user_speaking:
            print("🟢 USER STARTED SPEAKING")
            is_user_speaking = True

        # INTERRUPTION DETECTION
        if is_assistant_speaking:
            stop_tts()

        return

    # -------------------------
    # USER FINISHED SPEAKING
    # -------------------------
    if event.end_of_turn:

        # Avoid duplicate formatted + unformatted prints
        if last_turn_order == event.turn_order and event.turn_is_formatted:
            return

        print(f"🔴 USER FINISHED: {transcript}")

        is_user_speaking = False
        last_turn_order = event.turn_order

        # Trigger LLM
        response = call_llm(transcript)

        # Play TTS
        play_tts(response)


def on_terminated(self: Type[StreamingClient], event: TerminationEvent):
    print(
        f"\n🛑 Session terminated: "
        f"{event.audio_duration_seconds} seconds processed"
    )


def on_error(self: Type[StreamingClient], error: StreamingError):
    print(f"\n❌ Error occurred: {error}")


# -----------------------
# MAIN
# -----------------------

def main():
    client = StreamingClient(
        StreamingClientOptions(
            api_key=api_key,
            api_host="streaming.assemblyai.com",
        )
    )

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True,
        )
    )

    try:
        client.stream(
            aai.extras.MicrophoneStream(sample_rate=16000)
        )
    finally:
        client.disconnect(terminate=True)


if __name__ == "__main__":
    main()