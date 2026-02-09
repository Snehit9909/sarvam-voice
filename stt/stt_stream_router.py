from stt.stt_assembly_stream import stream_stt_assembly
from stt.stt_sarvam_stream import stream_stt_sarvam

def stream_stt(provider):
    if provider == "assemblyai":
        return stream_stt_assembly()
    if provider == "sarvam":
        return stream_stt_sarvam()

    raise ValueError("Unsupported STT provider")
