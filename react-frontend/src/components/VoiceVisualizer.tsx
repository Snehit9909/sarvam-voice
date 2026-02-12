import { motion } from 'framer-motion';
import type { AssistantStatus } from '../types';
import './VoiceVisualizer.css';

interface VoiceVisualizerProps {
    status: AssistantStatus;
}

export const VoiceVisualizer: React.FC<VoiceVisualizerProps> = ({ status }) => {
    const getAnimationVariants = () => {
        switch (status) {
            case 'listening':
                return {
                    scale: [1, 1.2, 1],
                    opacity: [0.6, 1, 0.6],
                };
            case 'thinking':
                return {
                    scale: [1, 1.1, 1],
                    rotate: [0, 360],
                };
            case 'speaking':
                return {
                    scale: [1, 1.3, 1.1, 1.3, 1],
                    opacity: [0.8, 1, 0.8, 1, 0.8],
                };
            default: // idle
                return {
                    scale: [1, 1.05, 1],
                    opacity: [0.4, 0.6, 0.4],
                };
        }
    };

    const getTransition = () => {
        switch (status) {
            case 'listening':
                return { duration: 2, repeat: Infinity, ease: 'easeInOut' };
            case 'thinking':
                return { duration: 3, repeat: Infinity, ease: 'linear' };
            case 'speaking':
                return { duration: 0.8, repeat: Infinity, ease: 'easeInOut' };
            default:
                return { duration: 3, repeat: Infinity, ease: 'easeInOut' };
        }
    };

    const getGlowColor = () => {
        switch (status) {
            case 'listening':
                return 'rgba(59, 130, 246, 0.8)'; // Blue
            case 'thinking':
                return 'rgba(251, 191, 36, 0.8)'; // Yellow
            case 'speaking':
                return 'rgba(34, 197, 94, 0.8)'; // Green
            default:
                return 'rgba(148, 163, 184, 0.5)'; // Gray
        }
    };

    return (
        <div className="visualizer-container">
            <motion.div
                className="visualizer-orb"
                animate={getAnimationVariants()}
                transition={getTransition()}
                style={{
                    boxShadow: `0 0 60px 20px ${getGlowColor()}, 0 0 100px 40px ${getGlowColor()}`,
                    background: `radial-gradient(circle, ${getGlowColor()}, transparent)`,
                }}
            />

            {/* Concentric rings for listening state */}
            {status === 'listening' && (
                <>
                    <motion.div
                        className="visualizer-ring"
                        animate={{
                            scale: [1, 2, 2],
                            opacity: [0.5, 0.2, 0],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeOut',
                        }}
                        style={{ borderColor: getGlowColor() }}
                    />
                    <motion.div
                        className="visualizer-ring"
                        animate={{
                            scale: [1, 2, 2],
                            opacity: [0.5, 0.2, 0],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeOut',
                            delay: 0.5,
                        }}
                        style={{ borderColor: getGlowColor() }}
                    />
                </>
            )}
        </div>
    );
};
