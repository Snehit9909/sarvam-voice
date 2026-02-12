"""
FastAPI Bridge Server for React Frontend

This server acts as a bridge between the React frontend and the Python voice assistant backend.
It provides:
- WebSocket endpoint for real-time status and transcript updates
- REST API endpoints for session control
- Subprocess management for orchestrator.main_streaming
"""

import asyncio
import os
import sys
import subprocess
import json
from typing import Optional, Dict, Any, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
import queue
import ast

app = FastAPI(title="Voice Assistant Bridge Server")

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_connections: Set[WebSocket] = set()
current_process: Optional[subprocess.Popen] = None
process_lock = threading.Lock()
message_queue = queue.Queue()

# Request/Response Models
class SessionConfig(BaseModel):
    agent: str
    stt_provider: str
    tts_provider: str
    language: str
    assembly_model: Optional[str] = "universal_2"

class SessionResponse(BaseModel):
    status: str
    message: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[WebSocket] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"[WebSocket] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Process output reader thread
def read_process_output(process: subprocess.Popen):
    """Read process output and parse it into structured events"""
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            print(f"[Process] {line}")
            
            # Parse output and create events
            event = parse_output_line(line)
            if event:
                asyncio.run(manager.broadcast(event))
    except Exception as e:
        print(f"[Process Reader] Error: {e}")
    finally:
        print("[Process Reader] Thread ending")

def parse_output_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse process output line into structured event"""
    line_lower = line.lower()
    
    # 1. Check for Raw Agent Data (highest priority for assistant response)
    # Format: [DEBUG] Raw Agent Data: {'result': {'role': 'assistant', 'content': [{'text': "..."}]}}
    if "raw agent data:" in line_lower:
        try:
            # Extract the dict part
            json_str = line.split("Raw Agent Data:", 1)[1].strip()
            # Parse as Python literal since it's a printed dict, not necessarily pure JSON
            data = ast.literal_eval(json_str)
            content = data.get('result', {}).get('content', [])
            if content and len(content) > 0:
                text = content[0].get('text', '')
                if text:
                    return {"type": "transcript", "role": "assistant", "text": text}
        except Exception as e:
            print(f"[Parser] Error parsing Raw Agent Data: {e}")
            
    # 2. Transcripts - User input (Explicit marker)
    if "user said:" in line_lower:
        parts = line.split("User said:", 1) if "User said:" in line else line.split("user said:", 1)
        text = parts[1].strip() if len(parts) > 1 else ""
        return {"type": "transcript", "role": "user", "text": text}

    # 3. Status changes
    if "listening" in line_lower and "[mic]" not in line_lower:
        return {"type": "status", "status": "listening", "message": "Listening for input..."}
    elif "thinking" in line_lower or "invoking agent" in line_lower:
        return {"type": "status", "status": "thinking", "message": "Processing..."}
    elif "speaking" in line_lower or "tts" in line_lower:
        return {"type": "status", "status": "speaking", "message": "Speaking..."}

    # 4. Filter out STT interim/final result logs to prevent UI clutter
    if "[assemblyai]:" in line_lower or "[sarvam]:" in line_lower:
        return None
        
    # 5. Fallback Assistant Transcripts
    if "assistant:" in line_lower:
        if "Assistant:" in line:
            text = line.split("Assistant:", 1)[1].strip()
        elif "assistant:" in line:
            text = line.split("assistant:", 1)[1].strip()
        else:
            text = ""
        
        if text:
            return {"type": "transcript", "role": "assistant", "text": text}

    # Errors
    if "error" in line_lower:
        return {"type": "error", "message": line}
    
    # Default to log
    return {"type": "log", "message": line}

# REST API Endpoints
@app.get("/")
async def root():
    return {"message": "Voice Assistant Bridge Server", "status": "running"}

@app.get("/status")
async def get_status():
    """Get current session status"""
    with process_lock:
        if current_process and current_process.poll() is None:
            return {"status": "active", "message": "Session is running"}
        else:
            return {"status": "idle", "message": "No active session"}

@app.post("/start", response_model=SessionResponse)
async def start_session(config: SessionConfig):
    """Start voice assistant session with given configuration"""
    global current_process
    
    with process_lock:
        # Check if session already running
        if current_process and current_process.poll() is None:
            raise HTTPException(status_code=400, detail="Session already running")
        
        # Prepare environment variables
        env = os.environ.copy()
        env["AGENT_RUNTIME_ARN"] = get_agent_arn(config.agent)
        env["STT_PROVIDER"] = config.stt_provider.lower()
        env["STT_LANGUAGE"] = config.language
        env["TTS_PROVIDER"] = config.tts_provider.lower()
        env["ASSEMBLY_MODEL"] = config.assembly_model or "universal_2"
        
        print(f"[Bridge] Starting session with config: {config.dict()}")
        
        try:
            # Start the orchestrator process
            current_process = subprocess.Popen(
                [sys.executable, "-u", "-m", "orchestrator.main_streaming"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace"
            )
            
            # Start output reader thread
            reader_thread = threading.Thread(
                target=read_process_output,
                args=(current_process,),
                daemon=True
            )
            reader_thread.start()
            
            # Broadcast session started
            await manager.broadcast({
                "type": "status",
                "status": "listening",
                "message": "Session started successfully"
            })
            
            return SessionResponse(
                status="success",
                message="Session started successfully"
            )
        
        except Exception as e:
            print(f"[Bridge] Error starting session: {e}")
            current_process = None
            raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@app.post("/stop", response_model=SessionResponse)
async def stop_session():
    """Stop active voice assistant session"""
    global current_process
    
    with process_lock:
        if not current_process or current_process.poll() is not None:
            return SessionResponse(
                status="info",
                message="No active session to stop"
            )
        
        try:
            print("[Bridge] Stopping session...")
            current_process.terminate()
            
            # Wait for process to terminate (with timeout)
            try:
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("[Bridge] Process didn't terminate, forcing kill...")
                current_process.kill()
                current_process.wait()
            
            current_process = None
            
            # Broadcast session stopped
            await manager.broadcast({
                "type": "status",
                "status": "idle",
                "message": "Session stopped"
            })
            
            return SessionResponse(
                status="success",
                message="Session stopped successfully"
            )
        
        except Exception as e:
            print(f"[Bridge] Error stopping session: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial status
        with process_lock:
            if current_process and current_process.poll() is None:
                await websocket.send_json({
                    "type": "status",
                    "status": "listening",
                    "message": "Connected to active session"
                })
            else:
                await websocket.send_json({
                    "type": "status",
                    "status": "idle",
                    "message": "Connected - No active session"
                })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle any client messages if needed
                print(f"[WebSocket] Received: {data}")
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        manager.disconnect(websocket)

# Helper functions
def get_agent_arn(agent_key: str) -> str:
    """Get agent ARN from config"""
    from config.config import AGENT_CONFIG
    
    if agent_key not in AGENT_CONFIG:
        raise ValueError(f"Invalid agent key: {agent_key}")
    
    return AGENT_CONFIG[agent_key]["runtime_arn"]

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    print("[Bridge] Server starting up...")
    print("[Bridge] WebSocket endpoint: ws://localhost:8001/ws")
    print("[Bridge] REST API: http://localhost:8001")

@app.on_event("shutdown")
async def shutdown_event():
    print("[Bridge] Server shutting down...")
    global current_process
    
    with process_lock:
        if current_process and current_process.poll() is None:
            print("[Bridge] Terminating active session...")
            current_process.terminate()
            try:
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                current_process.kill()

if __name__ == "__main__":
    import uvicorn
    
    print("="* 60)
    print("Voice Assistant Bridge Server")
    print("=" * 60)
    print("Starting server on http://localhost:8001")
    print("WebSocket endpoint: ws://localhost:8001/ws")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
