import { useEffect, useRef } from 'react';
import type { TranscriptEntry } from '../types';
import './TranscriptView.css';

interface TranscriptViewProps {
    transcripts: TranscriptEntry[];
    onClear: () => void;
}

export const TranscriptView: React.FC<TranscriptViewProps> = ({ transcripts, onClear }) => {
    const containerRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new transcripts arrive
    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [transcripts]);

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <div className="transcript-view">
            <div className="transcript-header">
                <h3 className="transcript-title">💬 Conversation</h3>
                {transcripts.length > 0 && (
                    <button className="clear-button" onClick={onClear}>
                        Clear
                    </button>
                )}
            </div>

            <div className="transcript-container" ref={containerRef}>
                {transcripts.length === 0 ? (
                    <div className="transcript-empty">
                        <p>No conversation yet. Start a session to begin!</p>
                    </div>
                ) : (
                    transcripts.map((entry) => (
                        <div
                            key={entry.id}
                            className={`transcript-entry ${entry.role}`}
                        >
                            <div className="transcript-meta">
                                <span className="transcript-role">
                                    {entry.role === 'user' ? '👤 You' : '🤖 Assistant'}
                                </span>
                                <span className="transcript-time">
                                    {formatTime(entry.timestamp)}
                                </span>
                            </div>
                            <div className="transcript-text">
                                {entry.text}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
