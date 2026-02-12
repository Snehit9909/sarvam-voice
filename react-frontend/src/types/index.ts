// Type definitions for the Voice Assistant application

export interface AgentConfig {
    name: string;
    runtime_arn: string;
}

export interface AgentConfigMap {
    [key: string]: AgentConfig;
}

export interface STTLanguages {
    [key: string]: string;
}

export interface SessionConfig {
    agent: string;
    stt_provider: string;
    tts_provider: string;
    language: string;
    assembly_model?: string;
}

export type AssistantStatus = 'idle' | 'listening' | 'thinking' | 'speaking';

export interface TranscriptEntry {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    timestamp: Date;
}

export interface WebSocketMessage {
    type: 'status' | 'transcript' | 'log' | 'error';
    status?: AssistantStatus;
    message?: string;
    role?: 'user' | 'assistant';
    text?: string;
}

export interface SessionResponse {
    status: string;
    message: string;
}

// Configuration constants
export const AGENT_CONFIG: AgentConfigMap = {
    agent_a: {
        name: "General Assistant",
        runtime_arn: "arn:aws:bedrock-agentcore:us-east-1:762233739050:runtime/app3-3trSxmCEpL"
    },
    agent_b: {
        name: "Banking Agent",
        runtime_arn: "arn:aws:bedrock-agentcore:us-east-1:762233739050:runtime/test_bank-74XtOQ9Uy7"
    },
    agent_c: {
        name: "Shipement Tracking Agent",
        runtime_arn: "arn:aws:bedrock-agentcore:us-east-1:762233739050:runtime/test_track-CpuOQN9ms8"
    }
};

export const STT_LANGUAGES: STTLanguages = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Marathi": "mr-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Bengali": "bn-IN",
    "Auto-Detect": "unknown"
};

export const STT_PROVIDERS = ["Sarvam", "AssemblyAI"];
export const TTS_PROVIDERS = ["Sarvam", "ElevenLabs"];
export const ASSEMBLY_MODELS = ["Universal-2", "Universal-3 Pro"];
