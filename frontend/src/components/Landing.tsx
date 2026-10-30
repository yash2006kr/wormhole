import { PropsWithChildren, useState } from "react";
import "./styles/Landing.css";
import AISearchBar from "./AISearchBar/AISearchBar";
import VoiceHeroStage from "./VoiceHero/VoiceHeroStage";

interface LandingProps extends PropsWithChildren {
  onPromptSubmit?: (query: string, mode: "purple" | "blue", attachedFile?: File | null) => void;
  isTransitioningOut?: boolean;
}

const Landing = ({ children, onPromptSubmit, isTransitioningOut = false }: LandingProps) => {
  const [heroMode, setHeroMode] = useState<"text" | "voice">("text");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);

  // In full voice mode, speaking automatically sends prompt
  const handleVoiceComplete = (transcript: string) => {
    if (onPromptSubmit && transcript.trim()) {
      onPromptSubmit(transcript.trim(), "blue", attachedFile);
    }
  };

  // In text mode, send button or enter submits prompt
  const handleTextSearchSubmit = (query: string) => {
    if (onPromptSubmit && query.trim()) {
      onPromptSubmit(query.trim(), "purple", attachedFile);
    }
  };

  return (
    <div className={`landing-section ${isTransitioningOut ? "landing-transition-out" : ""}`} id="landingDiv">
      {/* 1. TEXT MODE: 3D ROBOT HERO */}
      <div className={`hero-scene-wrapper ${heroMode === "text" ? "active" : "inactive"}`}>
        {children}

        {/* GLOWING AI SEARCH BAR AT BOTTOM (ONLY IN TEXT MODE) */}
        {heroMode === "text" && (
          <AISearchBar
            theme="purple"
            title="WHAT'S ON YOUR MIND?"
            subtitle="Your AI. Your Universe. One Portal."
            onAttachFile={(file) => setAttachedFile(file)}
            onSearch={handleTextSearchSubmit}
            onEnterVoiceMode={() => setHeroMode("voice")}
          />
        )}
      </div>

      {/* 2. FULL VOICE MODE: WORMHOLE VOICE ORB FROM SCREENSHOT (NO TEXT BAR) */}
      {heroMode === "voice" && (
        <VoiceHeroStage
          onClose={() => setHeroMode("text")}
          onVoiceComplete={handleVoiceComplete}
        />
      )}
    </div>
  );
};

export default Landing;
