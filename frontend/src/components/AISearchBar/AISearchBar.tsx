import React, { useState, useRef, useEffect } from "react";
import "./AISearchBar.css";

interface AISearchBarProps {
  onSearch?: (query: string) => void;
  onActivateWormhole?: () => void;
  title?: string;
  subtitle?: string;
  isSearchHidden?: boolean;
  theme?: "purple" | "blue";
  isDocked?: boolean;
  isListening?: boolean;
  onToggleListening?: () => void;
  onAttachFile?: (file: File) => void;
  initialValue?: string;
}

export const AISearchBar: React.FC<AISearchBarProps> = ({
  onSearch,
  onActivateWormhole,
  title = "WHAT'S ON YOUR MIND?",
  subtitle = "Your AI. Your Universe. One Portal.",
  isSearchHidden = false,
  theme = "purple",
  isDocked = false,
  isListening = false,
  onToggleListening,
  onAttachFile,
  initialValue = "",
}) => {
  const [query, setQuery] = useState(initialValue);
  const [isFocused, setIsFocused] = useState(false);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialValue) {
      setQuery(initialValue);
    }
  }, [initialValue]);

  const handleContainerClick = () => {
    inputRef.current?.focus();
  };

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim() && !attachedFileName) return;
    if (onSearch) {
      onSearch(query.trim());
      setQuery("");
      setAttachedFileName(null);
    }
  };

  const handleWormholeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleListening) {
      onToggleListening();
    } else if (onActivateWormhole) {
      onActivateWormhole();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachedFileName(file.name);
      if (onAttachFile) {
        onAttachFile(file);
      }
    }
  };

  return (
    <div
      className={`ai-search-wrapper theme-${theme} ${isDocked ? "docked" : ""}`}
    >
      {/* Header Tagline - shown only in full / hero mode */}
      {!isDocked && (
        <div className="ai-search-header">
          <h2 className="ai-search-title">{title}</h2>
          <p className="ai-search-subtitle">{subtitle}</p>
        </div>
      )}

      {/* Main Pill Search Bar */}
      <div
        className={`ai-search-container ${isFocused ? "focused" : ""} ${
          isSearchHidden ? "hidden" : ""
        }`}
        onClick={handleContainerClick}
      >
        {/* Hidden File Input */}
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileChange}
          accept="image/*,.pdf,.doc,.docx,.txt"
        />

        {/* Outer Glow Backdrop */}
        <div className="ai-search-glow-backdrop" />

        {/* Outer Gradient Frame */}
        <div className="ai-search-frame" />

        {/* Glassmorphic Dark Body */}
        <div className="ai-search-glass-bg">
          <div className="ai-search-energy-wave" />
        </div>

        {/* Ethereal Edge Flares */}
        <div className="ai-search-flare-top" />
        <div className="ai-search-flare-bottom" />

        {/* Content Layout: Sparkle icon → Paperclip → Text input → Send button → Voice button */}
        <div className="ai-search-inner">
          {/* AI 4-Point Sparkle Icon */}
          <div className="ai-search-sparkle">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 2C12 7.52285 7.52285 12 2 12C7.52285 12 12 16.4771 12 22C12 16.4771 16.4771 12 22 12C16.4771 12 12 7.52285 12 2Z"
                fill="currentColor"
              />
            </svg>
          </div>

          {/* Paperclip File Attachment Button inside Pill */}
          <button
            type="button"
            data-cursor="disable"
            className={`ai-search-attach-btn ${attachedFileName ? "attached" : ""}`}
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            title={attachedFileName ? `Attached: ${attachedFileName}` : "Attach Document or Photo for Healing"}
            aria-label="Attach file"
          >
            📎
          </button>

          {/* Text Input ("Ask anything...") */}
          <div className="ai-search-input-box">
            <input
              ref={inputRef}
              type="text"
              data-cursor="disable"
              className="ai-search-input"
              placeholder={
                theme === "blue"
                  ? isListening
                    ? "Listening... Speak your command now"
                    : "Speak or type your command..."
                  : attachedFileName
                  ? `[${attachedFileName}] Ask anything...`
                  : "Ask anything..."
              }
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSend();
                }
              }}
            />
          </div>

          {/* Action Buttons: Send Button → Voice Waveform Button */}
          <div className="ai-search-actions">
            {/* Glowing Send Button */}
            <button
              type="button"
              data-cursor="disable"
              className="ai-search-send-btn"
              onClick={handleSend}
              title="Submit query / Proceed"
              aria-label="Send query"
            >
              <svg
                className="ai-search-send-icon"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M3.4 20.4l17.45-7.48c.81-.35.81-1.49 0-1.84L3.4 3.6c-.66-.29-1.39.2-1.39.91L2 9.12c0 .5.37.93.87.99L17 12 2.87 13.88c-.5.07-.87.49-.87 1l.01 4.61c0 .71.73 1.2 1.39.91z" />
              </svg>
            </button>

            {/* Voice Assistant Waveform Button */}
            <button
              type="button"
              data-cursor="disable"
              className={`ai-search-wormhole-btn ${isListening ? "recording" : ""}`}
              onClick={handleWormholeClick}
              title={
                theme === "blue"
                  ? isListening
                    ? "Mute / Stop Voice"
                    : "Activate Listening"
                  : "Switch to Wormhole Voice Mode"
              }
              aria-label="Voice Assistant"
            >
              <svg
                className="ai-search-voice-icon"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <rect x="3.25" y="8.5" width="2.5" height="7" rx="1.25" fill="currentColor" />
                <rect x="8.25" y="3.5" width="2.5" height="17" rx="1.25" fill="currentColor" />
                <rect x="13.25" y="6" width="2.5" height="12" rx="1.25" fill="currentColor" />
                <rect x="18.25" y="8.5" width="2.5" height="7" rx="1.25" fill="currentColor" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISearchBar;
