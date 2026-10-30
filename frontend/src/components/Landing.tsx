import { PropsWithChildren, useState } from "react";
import "./styles/Landing.css";
import AISearchBar from "./AISearchBar/AISearchBar";
import VoiceOrb from "./VoiceOrb/VoiceOrb";

type UIMode =
  | "robot"
  | "transitioning-to-orb"
  | "orb"
  | "transitioning-to-robot";

const Landing = ({ children }: PropsWithChildren) => {
  const [uiMode, setUiMode] = useState<UIMode>("robot");

  const handleEnterVoiceMode = () => {
    if (uiMode !== "robot") return;
    setUiMode("transitioning-to-orb");
    setTimeout(() => {
      setUiMode("orb");
    }, 1100);
  };

  const handleExitVoiceMode = () => {
    if (uiMode !== "orb") return;
    setUiMode("transitioning-to-robot");
    setTimeout(() => {
      setUiMode("robot");
    }, 900);
  };

  let robotClass = "visible";
  if (uiMode === "transitioning-to-orb") {
    robotClass = "dissolving";
  } else if (uiMode === "orb") {
    robotClass = "hidden";
  } else if (uiMode === "transitioning-to-robot") {
    robotClass = "restoring";
  }

  const isSearchHidden =
    uiMode === "transitioning-to-orb" || uiMode === "orb";
  const isAtmosphereActive =
    uiMode === "transitioning-to-orb" || uiMode === "orb";

  return (
    <div className="landing-section" id="landingDiv">
      {/* Ambient Cyan Energy Atmosphere during Voice Mode */}
      <div
        className={`voice-atmosphere-glow ${
          isAtmosphereActive ? "active" : ""
        }`}
      />

      {/* 3D Robot Container - genuinely unrendered/hidden in voice mode */}
      <div
        className={`robot-view-wrapper ${robotClass}`}
        style={uiMode === "orb" ? { display: "none" } : undefined}
      >
        {children}
      </div>

      {/* Living Glowing AI Voice Orb */}
      {uiMode !== "robot" && (
        <VoiceOrb
          status={
            uiMode === "transitioning-to-orb"
              ? "entering"
              : uiMode === "orb"
              ? "active"
              : "exiting"
          }
          onExitVoiceMode={handleExitVoiceMode}
        />
      )}

      {/* Futuristic Search Bar with ChatGPT-style Voice Button */}
      {uiMode !== "orb" && (
        <AISearchBar
          isSearchHidden={isSearchHidden}
          onActivateWormhole={handleEnterVoiceMode}
        />
      )}
    </div>
  );
};

export default Landing;
