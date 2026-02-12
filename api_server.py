from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os

app = FastAPI()

# Allow React to talk to this API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/start-session")
async def start_session(): # <--- Remove agent_arn, stt, tts from here
    def generate_logs():
        # Using -u for unbuffered logs is vital!
        process = subprocess.Popen(
            ["python", "-u", "-m", "orchestrator.main_streaming"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1,
            env=os.environ.copy() # Inherits your .env or system vars
        )
        
        for line in iter(process.stdout.readline, ""):
            if line:
                yield f"data: {line}\n\n"
        
        process.stdout.close()
        process.wait()

    return StreamingResponse(generate_logs(), media_type="text/event-stream")