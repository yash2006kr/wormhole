import { useState } from "react";
import "./styles/Landing.css";
import AISearchBar from "./AISearchBar/AISearchBar";
import VoiceOrb from "./VoiceOrb/VoiceOrb";

interface LandingProps {
  onPromptSubmit?: (query: string, mode: "purple" | "blue", attachedFile?: File | null) => void;
  onEnterWorkspace?: () => void;
  isTransitioningOut?: boolean;
}

const Landing = ({ onPromptSubmit, onEnterWorkspace, isTransitioningOut = false }: LandingProps) => {
  const [heroMode, setHeroMode] = useState<"text" | "voice">("text");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);

  // In text mode, send button or enter submits prompt
  const handleTextSearchSubmit = (query: string) => {
    if (onPromptSubmit && (query.trim() || attachedFile)) {
      onPromptSubmit(query.trim(), "purple", attachedFile);
    } else if (onEnterWorkspace) {
      onEnterWorkspace();
    }
  };

  const handleEnterClick = () => {
    if (onEnterWorkspace) {
      onEnterWorkspace();
    } else if (onPromptSubmit) {
      onPromptSubmit("", "purple", attachedFile);
    }
  };

  return (
    <div className={`landing-section ${isTransitioningOut ? "landing-transition-out" : ""}`} id="landingDiv">
      {/* 1. TEXT MODE: BOTTOM GLOWING AI SEARCH BAR WITH ENTER WORMHOLE ACTION */}
      {heroMode === "text" && (
        <div className="hero-search-wrapper">
          <AISearchBar
            theme="purple"
            title="WHAT'S ON YOUR MIND?"
            subtitle="Your AI. Your Universe. One Portal."
            onAttachFile={(file) => setAttachedFile(file)}
            onSearch={handleTextSearchSubmit}
            onEnterVoiceMode={() => setHeroMode("voice")}
          />
          <div style={{ marginTop: "16px", display: "flex", justifyContent: "center" }}>
            <button
              type="button"
              onClick={handleEnterClick}
              className="enter-wormhole-btn"
              style={{
                background: "linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(56, 189, 248, 0.25))",
                border: "1px solid rgba(168, 85, 247, 0.5)",
                borderRadius: "30px",
                color: "#f1f5f9",
                padding: "8px 22px",
                fontSize: "12px",
                fontWeight: 600,
                letterSpacing: "0.5px",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                backdropFilter: "blur(12px)",
                transition: "all 0.3s ease",
                boxShadow: "0 4px 15px rgba(0, 0, 0, 0.3)"
              }}
            >
              <span>🌀 Enter WormHole Cockpit</span>
              <span style={{ fontSize: "14px" }}>→</span>
            </button>
          </div>
        </div>
      )}

      {/* 2. FULL VOICE MODE: WORMHOLE VOICE ORB */}
      {heroMode === "voice" && (
        <VoiceOrb
          status="active"
          onExitVoiceMode={() => setHeroMode("text")}
        />
      )}
    </div>
  );
};

export default Landing;
