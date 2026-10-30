import React from "react";
import "./VoiceHeroStage.css";

interface VoiceHeroStageProps {
  isListening?: boolean;
  onToggleListening?: () => void;
}

export const VoiceHeroStage: React.FC<VoiceHeroStageProps> = ({
  isListening = false,
  onToggleListening,
}) => {
  return (
    <div className="voice-hero-wrapper">
      <div className="voice-hero-container">
        {/* Ambient Glow */}
        <div className="voice-ambient-glow" />

        {/* Concentric ripples */}
        <div className="voice-ripple ripple-1" />
        <div className="voice-ripple ripple-2" />
        <div className="voice-ripple ripple-3" />

        {/* Orbital rings */}
        <div className="voice-orbital-ring ring-outer" />
        <div className="voice-orbital-ring ring-inner" />

        {/* Central Core Orb */}
        <div
          className={`voice-core-orb ${isListening ? "listening" : ""}`}
          onClick={onToggleListening}
          title={isListening ? "Listening... Click to pause" : "Click to activate microphone"}
        >
          {/* Animated waveform bars */}
          <div className="voice-wave-bars">
            <span className="wave-bar" />
            <span className="wave-bar" />
            <span className="wave-bar" />
            <span className="wave-bar" />
            <span className="wave-bar" />
          </div>
        </div>

        {/* Status Badge */}
        <div className="voice-status-badge">
          <span className="voice-status-dot" />
          <span className="voice-status-text">
            {isListening ? "VOICE MATRIX LISTENING" : "CLICK ORB OR SPEAK"}
          </span>
        </div>
      </div>
    </div>
  );
};

export default VoiceHeroStage;
