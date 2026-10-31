import React from "react";
import "./VoiceOrb.css";

interface VoiceOrbProps {
  status: "entering" | "active" | "exiting";
  onExitVoiceMode: () => void;
}

const VoiceOrb: React.FC<VoiceOrbProps> = ({ status, onExitVoiceMode }) => {
  return (
    <div
      className={`voice-orb-container ${status}`}
      onClick={onExitVoiceMode}
      title="Click to return to Text Mode"
    >
      <div className="voice-orb-wrapper">
        {/* 1. Atmospheric Deep Cosmic Glow Halo */}
        <div className="voice-orb-halo" />

        {/* 2. Orbiting Quantum Energy Rings */}
        <div className="voice-orb-ring voice-orb-ring-1" />
        <div className="voice-orb-ring voice-orb-ring-2" />

        {/* 3. The Core Glass Spherical Image */}
        <div className="voice-orb-sphere">
          <img
            src="/images/wormhole-orb-transparent.png"
            alt="WORMHOLE AI Voice Orb"
            className="voice-orb-image"
          />
          {/* 4. Glass Surface Refraction Sheen Overlay */}
          <div className="voice-orb-sheen" />
        </div>
      </div>

      {/* 5. Sleek Voice Status Pill HUD */}
      <div className="voice-orb-hud">
        <div className="voice-orb-wave">
          <span className="voice-orb-wave-bar" />
          <span className="voice-orb-wave-bar" />
          <span className="voice-orb-wave-bar" />
          <span className="voice-orb-wave-bar" />
          <span className="voice-orb-wave-bar" />
        </div>
        <span className="voice-orb-hud-text">WORMHOLE VOICE ACTIVE</span>
        <span className="voice-orb-hud-close" title="Switch to Text Mode">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </span>
      </div>
    </div>
  );
};

export default VoiceOrb;

