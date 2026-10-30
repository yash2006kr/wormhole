import { PropsWithChildren, useState, useEffect, useRef } from "react";
import "./styles/Landing.css";
import AISearchBar from "./AISearchBar/AISearchBar";
import VoiceHeroStage from "./VoiceHero/VoiceHeroStage";

interface LandingProps extends PropsWithChildren {
  onPromptSubmit?: (query: string, mode: "purple" | "blue", attachedFile?: File | null) => void;
  isTransitioningOut?: boolean;
}

const Landing = ({ children, onPromptSubmit, isTransitioningOut = false }: LandingProps) => {
  const [heroMode, setHeroMode] = useState<"text" | "voice">("text");
  const [isListening, setIsListening] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize SpeechRecognition when entering voice mode
  const startSpeechListening = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Speech recognition not supported in browser.");
      return;
    }

    try {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }

      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";

      rec.onstart = () => {
        setIsListening(true);
      };

      rec.onresult = (event: any) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript) {
          setVoiceTranscript(transcript);
        }
      };

      rec.onerror = (e: any) => {
        console.warn("Speech recognition notice:", e);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
      rec.start();
    } catch (e) {
      console.error("Speech start error:", e);
      setIsListening(false);
    }
  };

  const stopSpeechListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  };

  const handleToggleVoiceMode = () => {
    if (heroMode === "text") {
      setHeroMode("voice");
      startSpeechListening();
    } else {
      setHeroMode("text");
      stopSpeechListening();
    }
  };

  const handleToggleListening = () => {
    if (isListening) {
      stopSpeechListening();
    } else {
      startSpeechListening();
    }
  };

  const handleSearchSubmit = (query: string) => {
    stopSpeechListening();
    if (onPromptSubmit) {
      const modeTheme = heroMode === "voice" ? "blue" : "purple";
      onPromptSubmit(query, modeTheme, attachedFile);
    }
  };

  useEffect(() => {
    return () => {
      stopSpeechListening();
    };
  }, []);

  return (
    <div className={`landing-section ${isTransitioningOut ? "landing-transition-out" : ""}`} id="landingDiv">
      {/* 1. TEXT MODE: 3D ROBOT HERO */}
      <div className={`hero-scene-wrapper ${heroMode === "text" ? "active" : "inactive"}`}>
        {children}
      </div>

      {/* 2. VOICE MODE: HOLOGRAPHIC CYAN/BLUE VOICE ORB */}
      {heroMode === "voice" && (
        <VoiceHeroStage
          isListening={isListening}
          onToggleListening={handleToggleListening}
        />
      )}

      {/* Mode Switcher pill badge at top */}
      <div className="hero-mode-pill">
        <button
          className={`hero-mode-btn ${heroMode === "text" ? "active" : ""}`}
          onClick={() => {
            setHeroMode("text");
            stopSpeechListening();
          }}
        >
          🤖 3D Robot
        </button>
        <button
          className={`hero-mode-btn ${heroMode === "voice" ? "active" : ""}`}
          onClick={() => {
            setHeroMode("voice");
            startSpeechListening();
          }}
        >
          ⚡ Voice Orb
        </button>
      </div>

      {/* 3. GLOWING AI SEARCH BAR AT BOTTOM */}
      <AISearchBar
        theme={heroMode === "voice" ? "blue" : "purple"}
        title={
          heroMode === "voice"
            ? "VOICE ASSISTANT ONLINE"
            : "WHAT'S ON YOUR MIND?"
        }
        subtitle={
          heroMode === "voice"
            ? isListening
              ? "Listening to your voice... Speak your goal"
              : "Click orb or microphone to speak anytime"
            : "Your AI. Your Universe. One Portal."
        }
        initialValue={heroMode === "voice" ? voiceTranscript : ""}
        isListening={isListening}
        onToggleListening={handleToggleListening}
        onActivateWormhole={handleToggleVoiceMode}
        onAttachFile={(file) => setAttachedFile(file)}
        onSearch={handleSearchSubmit}
      />
    </div>
  );
};

export default Landing;
