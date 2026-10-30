import React, { useState, useEffect, useRef } from "react";
import "./VoiceHeroStage.css";

interface VoiceHeroStageProps {
  onClose: () => void;
  onVoiceComplete: (transcript: string) => void;
}

export const VoiceHeroStage: React.FC<VoiceHeroStageProps> = ({
  onClose,
  onVoiceComplete,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [statusText, setStatusText] = useState("Listening... Speak your goal");
  const recognitionRef = useRef<any>(null);
  const silenceTimerRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setStatusText("Speech recognition not supported in browser. Please use text mode.");
      return;
    }

    try {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";

      rec.onstart = () => {
        setIsListening(true);
        setStatusText("Listening... Speak your goal");
      };

      rec.onresult = (event: any) => {
        let currentTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }

        if (currentTranscript.trim()) {
          setTranscript(currentTranscript.trim());
          setStatusText(`"${currentTranscript.trim()}"`);

          // Auto-submit after 1.5s silence
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = setTimeout(() => {
            rec.stop();
            onVoiceComplete(currentTranscript.trim());
          }, 1600);
        }
      };

      rec.onerror = (e: any) => {
        console.warn("Voice speech error:", e);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
      rec.start();
    } catch (e) {
      console.error("Speech init error:", e);
    }

    return () => {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [onVoiceComplete]);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      setStatusText("Paused. Click orb to resume listening.");
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
      setStatusText("Listening... Speak your goal");
    }
  };

  return (
    <div className="voice-hero-screen">
      {/* Corner Ambient Flares */}
      <div className="voice-corner-flare-left" />
      <div className="voice-corner-flare-right" />

      {/* Main Orb Center */}
      <div
        className={`voice-orb-wrapper ${isListening ? "listening" : ""}`}
        onClick={toggleListening}
        title={isListening ? "Listening... Click to pause" : "Click to resume listening"}
      >
        {/* Glowing Backdrop */}
        <div className="voice-orb-glow-backdrop" />

        {/* The Exact Glowing Cyan/Teal Wormhole Orb from Screenshot */}
        <img
          src="/images/wormhole-orb.jpg"
          alt="Wormhole Voice Orb"
          className="voice-orb-image"
          onError={(e) => {
            // Fallback to transparent png if jpg fails
            (e.target as HTMLImageElement).src = "/images/wormhole-orb-transparent.png";
          }}
        />

        {/* Pill Badge: ||||| WORMHOLE VOICE ACTIVE × */}
        <div className="voice-active-pill" onClick={(e) => e.stopPropagation()}>
          <div className="voice-equalizer">
            <span className="voice-bar" />
            <span className="voice-bar" />
            <span className="voice-bar" />
            <span className="voice-bar" />
            <span className="voice-bar" />
          </div>
          <span className="voice-active-label">WORMHOLE VOICE ACTIVE</span>
          <button
            type="button"
            className="voice-close-btn"
            onClick={onClose}
            title="Return to 3D Robot Text Mode"
          >
            ×
          </button>
        </div>

        {/* Live speech preview */}
        {transcript && (
          <div className="voice-transcript-preview">
            {transcript}
          </div>
        )}

        <div className="voice-hint-text">
          {isListening ? "Speak freely · Auto-submits on speech completion" : statusText}
        </div>
      </div>
    </div>
  );
};

export default VoiceHeroStage;
