import type { AssistantStatus } from '../types';
import './StatusIndicator.css';

interface StatusIndicatorProps {
    status: AssistantStatus;
    isConnected: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, isConnected }) => {
    const getStatusColor = () => {
        if (!isConnected) return '#ef4444'; // Red

        switch (status) {
            case 'listening':
                return '#3b82f6'; // Blue
            case 'thinking':
                return '#fbbf24'; // Yellow
            case 'speaking':
                return '#22c55e'; // Green
            default:
                return '#94a3b8'; // Gray
        }
    };

    const getStatusText = () => {
        if (!isConnected) return 'Disconnected';

        switch (status) {
            case 'listening':
                return 'Listening...';
            case 'thinking':
                return 'Thinking...';
            case 'speaking':
                return 'Speaking...';
            default:
                return 'Idle';
        }
    };

    return (
        <div className="status-indicator">
            <div
                className="status-dot"
                style={{ backgroundColor: getStatusColor() }}
            />
            <span className="status-text">{getStatusText()}</span>
        </div>
    );
};
