import os
from stt.stt_sarvam_stream import stream_stt_sarvam
from stt.stt_assembly import stream_stt_assembly, AssemblySTTModel

def stream_stt(provider):
    if provider == "assemblyai":
        model_str = os.getenv("ASSEMBLY_MODEL", "universal_2")
        
        model_enum = AssemblySTTModel.UNIVERSAL_3_PRO if model_str == "universal_3_pro" else AssemblySTTModel.UNIVERSAL_2
        
        return stream_stt_assembly(model=model_enum)
    
    elif provider == "sarvam":
        return stream_stt_sarvam()
    
    raise ValueError(f"Unknown provider: {provider}")
