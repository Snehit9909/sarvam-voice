import { useState } from 'react';
import axios from 'axios';
import { VoiceVisualizer } from './components/VoiceVisualizer';
import { ControlPanel } from './components/ControlPanel';
import { TranscriptView } from './components/TranscriptView';
import { StatusIndicator } from './components/StatusIndicator';
import { useWebSocket } from './hooks/useWebSocket';
import type { SessionConfig } from './types';
import './App.css';

const API_BASE_URL = 'http://localhost:8001';

function App() {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { status, transcripts, isConnected, clearTranscripts } = useWebSocket();

  const handleStartSession = async (config: SessionConfig) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/start`, config);
      console.log('[App] Session started:', response.data);
      setIsSessionActive(true);
    } catch (error) {
      console.error('[App] Failed to start session:', error);
      alert('Failed to start session. Make sure the bridge server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopSession = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/stop`);
      console.log('[App] Session stopped:', response.data);
      setIsSessionActive(false);
    } catch (error) {
      console.error('[App] Failed to stop session:', error);
      alert('Failed to stop session.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="app-container">
        <StatusIndicator status={status} isConnected={isConnected} />

        <VoiceVisualizer status={status} />

        <ControlPanel
          onStart={handleStartSession}
          onStop={handleStopSession}
          isSessionActive={isSessionActive}
          disabled={isLoading || !isConnected}
        />

        <TranscriptView
          transcripts={transcripts}
          onClear={clearTranscripts}
        />

        {!isConnected && (
          <div className="connection-warning">
            ⚠️ Not connected to server. Make sure the bridge server is running on port 8001.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

