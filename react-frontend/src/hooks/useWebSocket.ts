import { useEffect, useRef, useState, useCallback } from 'react';
import type { WebSocketMessage, AssistantStatus, TranscriptEntry } from '../types';

interface UseWebSocketReturn {
    status: AssistantStatus;
    transcripts: TranscriptEntry[];
    logs: string[];
    isConnected: boolean;
    connect: () => void;
    disconnect: () => void;
    clearTranscripts: () => void;
}

const WS_URL = 'ws://localhost:8001/ws';
const RECONNECT_DELAY = 3000;

export const useWebSocket = (): UseWebSocketReturn => {
    const [status, setStatus] = useState<AssistantStatus>('idle');
    const [transcripts, setTranscripts] = useState<TranscriptEntry[]>([]);
    const [logs, setLogs] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const shouldReconnectRef = useRef(true);

    const handleMessage = useCallback((event: MessageEvent) => {
        try {
            const message: WebSocketMessage = JSON.parse(event.data);

            switch (message.type) {
                case 'status':
                    if (message.status) {
                        setStatus(message.status);
                    }
                    if (message.message) {
                        setLogs(prev => [...prev.slice(-49), message.message!]);
                    }
                    break;

                case 'transcript':
                    if (message.role && message.text) {
                        const entry: TranscriptEntry = {
                            id: `${Date.now()}-${Math.random()}`,
                            role: message.role,
                            text: message.text,
                            timestamp: new Date()
                        };
                        setTranscripts(prev => [...prev, entry]);
                    }
                    break;

                case 'log':
                    if (message.message) {
                        setLogs(prev => [...prev.slice(-49), message.message!]);
                    }
                    break;

                case 'error':
                    if (message.message) {
                        console.error('[WebSocket Error]', message.message);
                        setLogs(prev => [...prev.slice(-49), `ERROR: ${message.message}`]);
                    }
                    break;
            }
        } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
        }
    }, []);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            console.log('[WebSocket] Already connected');
            return;
        }

        shouldReconnectRef.current = true;

        try {
            console.log('[WebSocket] Connecting to', WS_URL);
            const ws = new WebSocket(WS_URL);

            ws.onopen = () => {
                console.log('[WebSocket] Connected');
                setIsConnected(true);
                setLogs(prev => [...prev, 'Connected to server']);
            };

            ws.onmessage = handleMessage;

            ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error);
                setLogs(prev => [...prev, 'Connection error']);
            };

            ws.onclose = () => {
                console.log('[WebSocket] Disconnected');
                setIsConnected(false);
                setLogs(prev => [...prev, 'Disconnected from server']);

                // Auto-reconnect if should reconnect
                if (shouldReconnectRef.current) {
                    console.log(`[WebSocket] Reconnecting in ${RECONNECT_DELAY}ms...`);
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, RECONNECT_DELAY);
                }
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('[WebSocket] Connection failed:', error);
            setIsConnected(false);
        }
    }, [handleMessage]);

    const disconnect = useCallback(() => {
        shouldReconnectRef.current = false;

        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        setIsConnected(false);
    }, []);

    const clearTranscripts = useCallback(() => {
        setTranscripts([]);
    }, []);

    // Auto-connect on mount
    useEffect(() => {
        connect();

        return () => {
            disconnect();
        };
    }, [connect, disconnect]);

    return {
        status,
        transcripts,
        logs,
        isConnected,
        connect,
        disconnect,
        clearTranscripts
    };
};
