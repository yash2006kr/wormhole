import React, { useState, useRef, useEffect } from "react";
import "./AISearchBar.css";

interface AISearchBarProps {
  onSearch?: (query: string) => void;
  onEnterVoiceMode?: () => void;
  title?: string;
  subtitle?: string;
  isSearchHidden?: boolean;
  theme?: "purple" | "blue";
  isDocked?: boolean;
  onAttachFile?: (file: File) => void;
  initialValue?: string;
}

export const AISearchBar: React.FC<AISearchBarProps> = ({
  onSearch,
  onEnterVoiceMode,
  title = "WHAT'S ON YOUR MIND?",
  subtitle = "Your AI. Your Universe. One Portal.",
  isSearchHidden = false,
  theme = "purple",
  isDocked = false,
  onAttachFile,
  initialValue = "",
}) => {
  const [query, setQuery] = useState(initialValue);
  const [isFocused, setIsFocused] = useState(false);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const micRecognitionRef = useRef<any>(null);

  // Up/Down Arrow Prompt History (Terminal & Modern AI Chatbot style)
  const [promptHistory, setPromptHistory] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem("wh_prompt_history");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const tempDraftRef = useRef<string>("");

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
    const textToSend = query.trim();
    if (!textToSend && !attachedFileName) return;

    if (textToSend) {
      setPromptHistory((prev) => {
        const next = [...prev.filter((p) => p !== textToSend), textToSend];
        try {
          localStorage.setItem("wh_prompt_history", JSON.stringify(next.slice(-60)));
        } catch {}
        return next;
      });
      setHistoryIndex(-1);
      tempDraftRef.current = "";
    }

    if (onSearch) {
      onSearch(textToSend);
      setQuery("");
      setAttachedFileName(null);
    }
  };

  // Mic Button: Transcribes speech into text input box ONLY (DOES NOT AUTO-SEND)
  const toggleSpeechToTextInput = (e: React.MouseEvent) => {
    e.stopPropagation();

    if (isTranscribing) {
      micRecognitionRef.current?.stop();
      setIsTranscribing(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    try {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = "en-US";

      rec.onstart = () => {
        setIsTranscribing(true);
      };

      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setQuery((prev) => (prev ? `${prev} ${transcript}` : transcript));
        }
      };

      rec.onerror = () => {
        setIsTranscribing(false);
      };

      rec.onend = () => {
        setIsTranscribing(false);
      };

      micRecognitionRef.current = rec;
      rec.start();
    } catch (err) {
      console.error("Mic transcription error:", err);
      setIsTranscribing(false);
    }
  };

  const handleVoiceModeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEnterVoiceMode) {
      onEnterVoiceMode();
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

        {/* Circulating Glowing Orbit Beam around Search Bar */}
        <div className="ai-search-orbit-glow" />

        {/* Outer Gradient Frame */}
        <div className="ai-search-frame" />

        {/* Glassmorphic Dark Body */}
        <div className="ai-search-glass-bg">
          <div className="ai-search-energy-wave" />
        </div>

        {/* Ethereal Edge Flares */}
        <div className="ai-search-flare-top" />
        <div className="ai-search-flare-bottom" />

        {/* Content Layout: Sparkle icon → Paperclip SVG → Text input → Mic transcription → Send button → Full Voice mode button */}
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

          {/* Crisp SVG Paperclip File Attachment Button (Matching Image 2) */}
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
            <svg
              className="ai-search-attach-icon"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
            </svg>
          </button>

          {/* Text Input ("Ask anything...") */}
          <div className="ai-search-input-box">
            <input
              ref={inputRef}
              type="text"
              data-cursor="disable"
              className="ai-search-input"
              placeholder={
                isTranscribing
                  ? "Transcribing voice to text..."
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
                } else if (e.key === "ArrowUp") {
                  // Up arrow: recall previous prompt
                  if (promptHistory.length === 0) return;
                  e.preventDefault();
                  if (historyIndex === -1) {
                    tempDraftRef.current = query;
                    const nextIdx = promptHistory.length - 1;
                    setHistoryIndex(nextIdx);
                    setQuery(promptHistory[nextIdx]);
                  } else if (historyIndex > 0) {
                    const nextIdx = historyIndex - 1;
                    setHistoryIndex(nextIdx);
                    setQuery(promptHistory[nextIdx]);
                  }
                } else if (e.key === "ArrowDown") {
                  // Down arrow: cycle toward newer prompts or restore draft
                  if (historyIndex === -1) return;
                  e.preventDefault();
                  if (historyIndex < promptHistory.length - 1) {
                    const nextIdx = historyIndex + 1;
                    setHistoryIndex(nextIdx);
                    setQuery(promptHistory[nextIdx]);
                  } else {
                    setHistoryIndex(-1);
                    setQuery(tempDraftRef.current || "");
                  }
                }
              }}
            />
          </div>

          {/* Action Buttons */}
          <div className="ai-search-actions">
            {/* Inline Speech-to-Text Mic (Puts text in input box, user sends later) */}
            <button
              type="button"
              data-cursor="disable"
              className={`ai-search-mic-transcribe-btn ${isTranscribing ? "recording" : ""}`}
              onClick={toggleSpeechToTextInput}
              title={isTranscribing ? "Listening... click to stop" : "Speak to transcribe text into input"}
              aria-label="Transcribe speech to text"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="22" />
              </svg>
            </button>

            {/* Glowing Send / Proceed Button */}
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

            {/* Full Wormhole Voice Mode Button (Only in hero mode) */}
            {!isDocked && onEnterVoiceMode && (
              <button
                type="button"
                data-cursor="disable"
                className="ai-search-wormhole-btn"
                onClick={handleVoiceModeClick}
                title="Open Wormhole Voice Mode"
                aria-label="Wormhole Voice Mode"
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
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISearchBar;
