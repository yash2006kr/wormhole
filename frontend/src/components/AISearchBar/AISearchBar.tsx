import React, { useState, useRef } from "react";
import "./AISearchBar.css";

interface AISearchBarProps {
  onSearch?: (query: string) => void;
  onActivateWormhole?: () => void;
  title?: string;
  subtitle?: string;
  isSearchHidden?: boolean;
}

const AISearchBar: React.FC<AISearchBarProps> = ({
  onSearch,
  onActivateWormhole,
  title = "WHAT'S ON YOUR MIND?",
  subtitle = "Your AI. Your Universe. One Portal.",
  isSearchHidden = false,
}) => {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleContainerClick = () => {
    inputRef.current?.focus();
  };

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim()) return;
    if (onSearch) {
      onSearch(query.trim());
    }
  };

  const handleWormholeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onActivateWormhole) {
      onActivateWormhole();
    }
  };

  return (
    <div className={`ai-search-wrapper ${isSearchHidden ? "hidden" : ""}`}>
      {/* Header Tagline */}
      <div className="ai-search-header">
        <h2 className="ai-search-title">{title}</h2>
        <p className="ai-search-subtitle">{subtitle}</p>
      </div>

      {/* Main Pill Search Bar */}
      <div
        className={`ai-search-container ${isFocused ? "focused" : ""} ${
          isSearchHidden ? "hidden" : ""
        }`}
        onClick={handleContainerClick}
      >
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

        {/* Content Layout: Sparkle icon → Text input → Existing send button → New Wormhole agent symbol */}
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

          {/* Text Input ("Ask anything...") */}
          <div className="ai-search-input-box">
            <input
              ref={inputRef}
              type="text"
              data-cursor="disable"
              className="ai-search-input"
              placeholder="Ask anything..."
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

          {/* Action Buttons: Existing Send Button → New Wormhole Agent Symbol */}
          <div className="ai-search-actions">
            {/* Existing Glowing Orb Send Button */}
            <button
              type="button"
              data-cursor="disable"
              className="ai-search-send-btn"
              onClick={handleSend}
              title="Submit query"
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

            {/* 4. Voice Assistant Waveform Button (FAR RIGHT) */}
            <button
              type="button"
              data-cursor="disable"
              className="ai-search-wormhole-btn"
              onClick={handleWormholeClick}
              title="Activate Wormhole Voice Assistant"
              aria-label="Activate Wormhole Voice Assistant"
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
