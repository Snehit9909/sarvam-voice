import { useState } from 'react';
import type { SessionConfig } from '../types';
import { AGENT_CONFIG, STT_LANGUAGES, STT_PROVIDERS, TTS_PROVIDERS, ASSEMBLY_MODELS } from '../types';
import './ControlPanel.css';

interface ControlPanelProps {
    onStart: (config: SessionConfig) => void;
    onStop: () => void;
    isSessionActive: boolean;
    disabled?: boolean;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
    onStart,
    onStop,
    isSessionActive,
    disabled = false
}) => {
    const [selectedAgent, setSelectedAgent] = useState<string>('agent_a');
    const [sttProvider, setSttProvider] = useState<string>('Sarvam');
    const [ttsProvider, setTtsProvider] = useState<string>('Sarvam');
    const [language, setLanguage] = useState<string>('English');
    const [assemblyModel, setAssemblyModel] = useState<string>('Universal-2');

    const handleStartSession = () => {
        const config: SessionConfig = {
            agent: selectedAgent,
            stt_provider: sttProvider,
            tts_provider: ttsProvider,
            language: STT_LANGUAGES[language],
            assembly_model: sttProvider === 'AssemblyAI'
                ? (assemblyModel === 'Universal-2' ? 'universal_2' : 'universal_3_pro')
                : undefined
        };
        onStart(config);
    };

    return (
        <div className="control-panel">
            <h2 className="panel-title">🎙️ Talk Buddy</h2>
            <p className="panel-subtitle">Streaming Voice Assistant</p>

            {/* Agent Selection */}
            <div className="control-group">
                <label className="control-label">🤖 Select Assistant</label>
                <select
                    className="control-select"
                    value={selectedAgent}
                    onChange={(e) => setSelectedAgent(e.target.value)}
                    disabled={isSessionActive || disabled}
                >
                    {Object.entries(AGENT_CONFIG).map(([key, config]) => (
                        <option key={key} value={key}>
                            {config.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Provider Selection */}
            <div className="control-row">
                <div className="control-group">
                    <label className="control-label">🎤 STT Provider</label>
                    <div className="radio-group">
                        {STT_PROVIDERS.map(provider => (
                            <label key={provider} className="radio-label">
                                <input
                                    type="radio"
                                    name="stt"
                                    value={provider}
                                    checked={sttProvider === provider}
                                    onChange={(e) => setSttProvider(e.target.value)}
                                    disabled={isSessionActive || disabled}
                                />
                                <span>{provider}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="control-group">
                    <label className="control-label">🔊 TTS Provider</label>
                    <div className="radio-group">
                        {TTS_PROVIDERS.map(provider => (
                            <label key={provider} className="radio-label">
                                <input
                                    type="radio"
                                    name="tts"
                                    value={provider}
                                    checked={ttsProvider === provider}
                                    onChange={(e) => setTtsProvider(e.target.value)}
                                    disabled={isSessionActive || disabled}
                                />
                                <span>{provider}</span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            {/* AssemblyAI Model Selection (conditional) */}
            {sttProvider === 'AssemblyAI' && (
                <div className="control-group">
                    <label className="control-label">⚙️ AssemblyAI Model</label>
                    <div className="radio-group">
                        {ASSEMBLY_MODELS.map(model => (
                            <label key={model} className="radio-label">
                                <input
                                    type="radio"
                                    name="assembly-model"
                                    value={model}
                                    checked={assemblyModel === model}
                                    onChange={(e) => setAssemblyModel(e.target.value)}
                                    disabled={isSessionActive || disabled}
                                />
                                <span>{model}</span>
                            </label>
                        ))}
                    </div>
                </div>
            )}

            {/* Language Selection */}
            <div className="control-group">
                <label className="control-label">🌐 Processing Language</label>
                <select
                    className="control-select"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    disabled={isSessionActive || disabled}
                >
                    {Object.keys(STT_LANGUAGES).map(lang => (
                        <option key={lang} value={lang}>
                            {lang}
                        </option>
                    ))}
                </select>
            </div>

            {/* Start/Stop Button */}
            <button
                className={`session-button ${isSessionActive ? 'active' : ''}`}
                onClick={isSessionActive ? onStop : handleStartSession}
                disabled={disabled}
            >
                {isSessionActive ? '⏹️ STOP SESSION' : '▶️ START SESSION'}
            </button>
        </div>
    );
};
