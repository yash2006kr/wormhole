import React, { useState, useEffect, useRef, useCallback } from "react";
import "./AgentWorkspace.css";
import AISearchBar from "../AISearchBar/AISearchBar";

interface Tab {
  index: number;
  title: string;
  url: string;
  active: boolean;
}

interface ChatMessage {
  id: string;
  sender: "user" | "agent" | "system";
  text: string;
  timestamp: string;
  emergency?: boolean;
  telemetry?: any;
  proofImage?: string;
}

interface AgentWorkspaceProps {
  initialPrompt?: string;
  initialFile?: File | null;
  theme?: "purple" | "blue";
  onReset?: () => void;
}

export const AgentWorkspace: React.FC<AgentWorkspaceProps> = ({
  initialPrompt,
  initialFile,
  theme = "purple",
  onReset,
}) => {
  const [currentTheme, setCurrentTheme] = useState<"purple" | "blue">(theme);
  const [inputMode, setInputMode] = useState<"text" | "voice">(theme === "blue" ? "voice" : "text");
  const [agentStatus, setAgentStatus] = useState<"IDLE" | "RUNNING" | "PAUSED_FOR_HUMAN" | "SUCCESS" | "ERROR">("IDLE");
  const [wsConnected, setWsConnected] = useState(false);
  const [urlInput, setUrlInput] = useState("about:blank");
  const [currentUrl, setCurrentUrl] = useState("about:blank");
  const [tabs, setTabs] = useState<Tab[]>([
    { index: 0, title: "Portal Home", url: "about:blank", active: true },
  ]);
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const [interactiveMode, setInteractiveMode] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Temporary telemetry state: shown during execution with shimmer, disappears once agent replies
  const [activeTelemetry, setActiveTelemetry] = useState<string | null>(null);

  // Draggable Splitter Slider State
  const [splitPercent, setSplitPercent] = useState<number>(() => {
    const saved = localStorage.getItem("wh_split_percent");
    return saved ? parseFloat(saved) : 44;
  });
  const [isDragging, setIsDragging] = useState(false);
  const workbenchRef = useRef<HTMLDivElement>(null);

  // Dedicated Voice Mode Speech Recognition
  const [isListeningVoice, setIsListeningVoice] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState("");
  const voiceRecognitionRef = useRef<any>(null);
  const voiceSilenceTimerRef = useRef<any>(null);

  const handleSplitterMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !workbenchRef.current) return;
      const rect = workbenchRef.current.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      const totalWidth = rect.width;
      const minPercent = 22;
      const maxPercent = 75;
      const pct = Math.min(maxPercent, Math.max(minPercent, (offsetX / totalWidth) * 100));
      setSplitPercent(pct);
    };

    const handleMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
        localStorage.setItem("wh_split_percent", splitPercent.toString());
      }
    };

    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    } else {
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isDragging, splitPercent]);

  const toggleVoiceListen = () => {
    if (isListeningVoice) {
      if (voiceRecognitionRef.current) {
        voiceRecognitionRef.current.stop();
      }
      setIsListeningVoice(false);
      if (voiceTranscript.trim()) {
        const textToSend = voiceTranscript.trim();
        setVoiceTranscript("");
        handleExecute(textToSend);
      }
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome.");
      return;
    }

    try {
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";

      rec.onstart = () => {
        setIsListeningVoice(true);
        setVoiceTranscript("");
      };

      rec.onresult = (event: any) => {
        let fullText = "";
        for (let i = 0; i < event.results.length; i++) {
          fullText += event.results[i][0].transcript;
        }
        if (fullText.trim()) {
          setVoiceTranscript(fullText.trim());

          // Auto-submit after 1.8s of silence
          if (voiceSilenceTimerRef.current) clearTimeout(voiceSilenceTimerRef.current);
          voiceSilenceTimerRef.current = setTimeout(() => {
            rec.stop();
            setIsListeningVoice(false);
            const textToSend = fullText.trim();
            setVoiceTranscript("");
            handleExecute(textToSend);
          }, 1800);
        }
      };

      rec.onerror = (err: any) => {
        console.warn("Voice error:", err);
        setIsListeningVoice(false);
      };

      rec.onend = () => {
        setIsListeningVoice(false);
      };

      voiceRecognitionRef.current = rec;
      rec.start();
    } catch (e) {
      console.error("Speech init error:", e);
      setIsListeningVoice(false);
    }
  };

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const chatScrollRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll chat feed
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, activeTelemetry, agentStatus]);

  // Connect WebSocket to real-time agent screencast & telemetry
  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host || "localhost:8000";
    const wsUrl = `${protocol}//${host}/ws/screencast`;

    let reconnectTimer: any = null;

    const connectWs = () => {
      try {
        const socket = new WebSocket(wsUrl);
        wsRef.current = socket;

        socket.onopen = () => {
          setWsConnected(true);
        };

        socket.onclose = () => {
          setWsConnected(false);
          reconnectTimer = setTimeout(connectWs, 2000);
        };

        socket.onerror = (err) => {
          console.error("[WS] Screencast error:", err);
          socket.close();
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

            // 1. Live Frame
            if (data.type === "FRAME" && data.data) {
              const canvas = canvasRef.current;
              if (canvas) {
                const ctx = canvas.getContext("2d");
                const img = new Image();
                img.onload = () => {
                  canvas.width = img.width;
                  canvas.height = img.height;
                  ctx?.drawImage(img, 0, 0);
                };
                img.src = `data:image/jpeg;base64,${data.data}`;
              }
              if (data.url) {
                setCurrentUrl(data.url);
                setUrlInput(data.url);
              }
              if (data.state) {
                if (data.state === "RUNNING") setAgentStatus("RUNNING");
                else if (data.state === "PAUSED_FOR_HUMAN") setAgentStatus("PAUSED_FOR_HUMAN");
                else if (data.state === "IDLE") setAgentStatus("IDLE");
              }
            }

            // 2. Tabs Update
            else if (data.type === "TABS_UPDATE") {
              if (Array.isArray(data.tabs)) {
                setTabs(data.tabs);
                setActiveTabIndex(data.active_index ?? 0);
              }
              if (data.url) {
                setCurrentUrl(data.url);
                setUrlInput(data.url);
              }
            }

            // 3. State Change
            else if (data.type === "STATE_CHANGE") {
              if (data.state === "RUNNING") setAgentStatus("RUNNING");
              else if (data.state === "PAUSED_FOR_HUMAN") setAgentStatus("PAUSED_FOR_HUMAN");
              else if (data.state === "IDLE") {
                setAgentStatus("IDLE");
                setActiveTelemetry(null); // Telemetry disappears after agent finishes
              }
            }

            // 4. Chat Response from Model (Official Reply)
            else if (data.type === "CHAT_RESPONSE" && data.text) {
              setActiveTelemetry(null); // Telemetry disappears once agent replies!
              setAgentStatus("SUCCESS");
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                if (last && last.sender === "agent") {
                  return [
                    ...prev.slice(0, -1),
                    {
                      ...last,
                      text: data.text,
                    },
                  ];
                }
                return [
                  ...prev,
                  {
                    id: Math.random().toString(),
                    sender: "agent",
                    text: data.text,
                    timestamp: now,
                  },
                ];
              });
            }

            // 5. Agent Action Telemetry (Temporary concise status banner)
            else if (data.type === "ACTION") {
              const actionSummary = data.reason || `Executing action: ${data.action}`;
              setActiveTelemetry(`1 task running · ${actionSummary}`);
            }

            // 6. Navigation Step Telemetry (Temporary concise status banner)
            else if (data.type === "STEP") {
              const domain = data.url ? new URL(data.url).hostname : "web";
              setActiveTelemetry(`1 task running · Step ${data.step}: Inspecting ${domain}`);
            }

            // 7. Telemetry Log
            else if (data.type === "LOG" && data.message) {
              setActiveTelemetry(`1 task running · ${data.message}`);
            }

            // 8. Task Complete
            else if (data.type === "COMPLETE") {
              setAgentStatus("SUCCESS");
              setActiveTelemetry(null); // Disappears after completion
            }

            // 9. SOS Emergency Alert
            else if (data.type === "SOS_EMERGENCY_ACTIVATED") {
              setActiveTelemetry(null);
              setMessages((prev) => [
                ...prev,
                {
                  id: Math.random().toString(),
                  sender: "agent",
                  text: "🚨 Acute Medical Emergency Distress Signal Activated.",
                  timestamp: now,
                  emergency: true,
                  telemetry: data.telemetry,
                },
              ]);
            }
          } catch (e) {
            console.error("[WS] Parse error:", e);
          }
        };
      } catch (err) {
        console.error("[WS] Failed:", err);
      }
    };

    connectWs();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Fetch initial tabs from backend
  const refreshTabs = useCallback(async () => {
    try {
      const res = await fetch("/api/tabs");
      if (res.ok) {
        const json = await res.json();
        if (json.tabs) {
          setTabs(json.tabs);
          setActiveTabIndex(json.active_index ?? 0);
        }
      }
    } catch (e) {
      console.warn("Tabs fetch error:", e);
    }
  }, []);

  useEffect(() => {
    refreshTabs();
  }, [refreshTabs]);

  // Execute Agent Command
  const handleExecute = async (queryText: string) => {
    const textToSend = queryText.trim();
    if (!textToSend) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    // Append user message
    const userMsg: ChatMessage = {
      id: Math.random().toString(),
      sender: "user",
      text: textToSend,
      timestamp: timeStr,
    };

    setMessages((prev) => [...prev, userMsg]);
    setAgentStatus("RUNNING");
    setActiveTelemetry("1 task running"); // Temporary telemetry banner begins

    try {
      const res = await fetch("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: textToSend }),
      });

      const data = await res.json();

      // If protocol finished immediately (e.g. Doc Exorcist, Transit Rush, Dark Pattern, Fraud Sentinel)
      if (data.status === "COMPLETED") {
        setActiveTelemetry(null); // Telemetry disappears once complete!
        setAgentStatus("SUCCESS");

        const isEmergency =
          data.protocol === "SOS_MEDICAL_EMERGENCY" ||
          textToSend.toLowerCase().includes("heart attack") ||
          textToSend.toLowerCase().includes("emergency");

        const agentMsg: ChatMessage = {
          id: Math.random().toString(),
          sender: "agent",
          text: data.response || data.reason || "Task executed successfully.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          emergency: isEmergency,
          telemetry: data.details || data.telemetry,
          proofImage: data.proof_image,
        };

        setMessages((prev) => [...prev, agentMsg]);
      } else if (data.status === "RUNNING") {
        setActiveTelemetry(`1 task running · ${data.reason || "Navigating browser..."}`);
      }

      refreshTabs();
    } catch (err: any) {
      console.error("Execution error:", err);
      setActiveTelemetry(null);
      const errorMsg: ChatMessage = {
        id: Math.random().toString(),
        sender: "system",
        text: `Execution failed: ${err.message || "Connection to backend failed"}`,
        timestamp: timeStr,
      };
      setMessages((prev) => [...prev, errorMsg]);
      setAgentStatus("ERROR");
    }
  };

  // If initialPrompt is passed, run it
  useEffect(() => {
    if (initialPrompt && initialPrompt.trim()) {
      handleExecute(initialPrompt.trim());
    }
  }, [initialPrompt]);

  // Upload file to backend
  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: "system",
          text: `📁 File attached & uploaded: **${file.name}** (${(file.size / 1024).toFixed(1)} KB)${
            data.processed_size ? ` → Auto-healed: ${data.processed_size}` : ""
          }`,
          timestamp: timeStr,
        },
      ]);
    } catch (err: any) {
      console.error("Upload error:", err);
    }
  };

  // If initialFile is passed on mount
  useEffect(() => {
    if (initialFile) {
      handleFileUpload(initialFile);
    }
  }, [initialFile]);

  // Reset Session (+ New Chat)
  const handleNewChat = async () => {
    try {
      await fetch("/api/chat/new", { method: "POST" });
    } catch (e) {
      console.warn("Reset chat error:", e);
    }
    setMessages([]);
    setActiveTelemetry(null);
    setAgentStatus("IDLE");
    if (onReset) {
      onReset();
    }
  };

  // Stop Agent
  const handleStopAgent = async () => {
    try {
      await fetch("/api/abort", { method: "POST" });
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ABORT_TASK" }));
      }
      setAgentStatus("PAUSED_FOR_HUMAN");
      setActiveTelemetry(null);
    } catch (e) {
      console.error("Stop agent error:", e);
    }
  };

  // Browser Navigation
  const handleNavigate = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!urlInput.trim()) return;
    try {
      await fetch("/api/navigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput }),
      });
      refreshTabs();
    } catch (e) {
      console.error("Navigation error:", e);
    }
  };

  // Multi-tab actions
  const handleOpenTab = async () => {
    try {
      await fetch("/api/tabs/open", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: "https://www.google.com" }),
      });
      refreshTabs();
    } catch (e) {
      console.error("Open tab error:", e);
    }
  };

  const handleSwitchTab = async (index: number) => {
    try {
      await fetch("/api/tabs/switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index }),
      });
      refreshTabs();
    } catch (e) {
      console.error("Switch tab error:", e);
    }
  };

  const handleCloseTab = async (e: React.MouseEvent, index: number) => {
    e.stopPropagation();
    try {
      await fetch("/api/tabs/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index }),
      });
      refreshTabs();
    } catch (e) {
      console.error("Close tab error:", e);
    }
  };

  // ==============================================================================
  // PRECISE LETTERBOX-AWARE CANVAS COORDINATE NORMALIZATION
  // Eliminates top/bottom offset caused by object-fit: contain letterboxing!
  // ==============================================================================
  const getCanvasNormalizedCoordinates = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    const naturalWidth = canvas.width;
    const naturalHeight = canvas.height;

    if (!naturalWidth || !naturalHeight || !rect.width || !rect.height) return null;

    const elementRatio = rect.width / rect.height;
    const imageRatio = naturalWidth / naturalHeight;

    let renderWidth = rect.width;
    let renderHeight = rect.height;
    let offsetX = 0;
    let offsetY = 0;

    if (elementRatio > imageRatio) {
      // Letterbox on left and right
      renderWidth = rect.height * imageRatio;
      offsetX = (rect.width - renderWidth) / 2;
    } else {
      // Letterbox on top and bottom
      renderHeight = rect.width / imageRatio;
      offsetY = (rect.height - renderHeight) / 2;
    }

    const clientXInsideRender = e.clientX - rect.left - offsetX;
    const clientYInsideRender = e.clientY - rect.top - offsetY;

    // Normalized strictly 0.0 to 1.0 coordinates matching real web page
    const xRatio = Math.max(0, Math.min(1, clientXInsideRender / renderWidth));
    const yRatio = Math.max(0, Math.min(1, clientYInsideRender / renderHeight));

    return { x: xRatio, y: yRatio };
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const coords = getCanvasNormalizedCoordinates(e);
    if (!coords || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(
      JSON.stringify({
        type: "CANVAS_CLICK",
        x: coords.x,
        y: coords.y,
      })
    );
  };

  const handleCanvasWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    const coords = getCanvasNormalizedCoordinates(e);
    if (!coords || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(
      JSON.stringify({
        type: "CANVAS_WHEEL",
        x: coords.x,
        y: coords.y,
        deltaX: e.deltaX,
        deltaY: e.deltaY,
      })
    );
  };

  return (
    <div className={`workspace-root theme-${currentTheme}`}>
      {/* 1. MAIN WORKBENCH WITH DRAGGABLE SPLITTER (TOP BAR REMOVED) */}
      <div className="wh-workbench" ref={workbenchRef}>
        {/* LEFT PANE: Chat, Intelligence & Telemetry */}
        <section className="wh-left-pane" style={{ width: `calc(${splitPercent}% - 6px)`, flex: "none" }}>
          {/* Top edge fade flare */}
          <div className="wh-card-flare-top" />

          {/* Cockpit Header */}
          <div className="wh-cockpit-header">
            <div className="wh-mode-toggle">
              <button
                className={`wh-mode-btn ${inputMode === "text" ? "active" : ""}`}
                onClick={() => {
                  setInputMode("text");
                  setCurrentTheme("purple");
                }}
              >
                + Text
              </button>
              <button
                className={`wh-mode-btn ${inputMode === "voice" ? "active" : ""}`}
                onClick={() => {
                  setInputMode("voice");
                  setCurrentTheme("blue");
                }}
              >
                🔈)) Voice
              </button>
            </div>

            <div className="wh-action-btns">
              <div className={`wh-live-indicator-pill ${wsConnected ? "live" : "offline"}`}>
                <span className="wh-live-dot" />
                <span>{wsConnected ? "LIVE" : "OFFLINE"}</span>
              </div>
              <button className="wh-btn-pill wh-btn-pill-cyan" onClick={handleNewChat} title="Start New Chat & Return to 3D Robot Hero">
                + New Chat
              </button>
              <button className="wh-btn-pill wh-btn-pill-red" onClick={handleStopAgent} title="Emergency Stop">
                🛑 Stop Agent
              </button>
            </div>
          </div>

          {/* Chat Feed */}
          <div className="wh-chat-feed" ref={chatScrollRef}>
            {messages.length === 0 ? (
              <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--wh-text-muted)" }}>
                <h3 style={{ color: "#ffffff", marginBottom: "8px", fontWeight: 700 }}>
                  Wormhole Agent Ready
                </h3>
                <p style={{ fontSize: "12px", marginBottom: "18px" }}>
                  Ask anything to begin autonomous web navigation, document healing, or emergency triage.
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <button
                    className="wh-btn-pill wh-btn-pill-cyan"
                    style={{ justifyContent: "center" }}
                    onClick={() => handleExecute("browse who is yash2006kr in google and get me his education details")}
                  >
                    🔍 Inspect Yashwanth's Portfolio & Details
                  </button>
                  <button
                    className="wh-btn-pill wh-btn-pill-cyan"
                    style={{ justifyContent: "center" }}
                    onClick={() => handleExecute("Book a sleeper seat on KSRTC from Bangalore to Mysore for tomorrow")}
                  >
                    🚌 Book KSRTC Seat Autonomous
                  </button>
                  <button
                    className="wh-btn-pill wh-btn-pill-red"
                    style={{ justifyContent: "center" }}
                    onClick={() => handleExecute("Emergency: Heart attack patient collapsed! Dispatch ambulance and hospital appointment now!")}
                  >
                    🚨 Acute Heart Attack SOS Sentinel
                  </button>
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <div key={m.id} className={`wh-msg-card ${m.sender === "user" ? "wh-msg-user" : "wh-msg-agent"}`}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontSize: "10.5px", color: "var(--wh-text-muted)" }}>
                    <span style={{ fontWeight: 800, color: "var(--wh-accent)" }}>
                      {m.sender === "user" ? "YOU" : "WORMHOLE COPILOT"}
                    </span>
                    <span>{m.timestamp}</span>
                  </div>

                  {/* SOS Emergency Badge */}
                  {m.emergency && (
                    <div style={{ background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.45)", borderRadius: "10px", padding: "12px", marginBottom: "12px" }}>
                      <div style={{ color: "#f87171", fontWeight: 800, fontSize: "11px", display: "flex", justifyContent: "space-between" }}>
                        <span>🚨 CODE RED: ACUTE MEDICAL EMERGENCY</span>
                        <span>CPR METRONOME: 110 BPM ♥</span>
                      </div>
                      <div style={{ fontSize: "11px", marginTop: "6px", color: "#fecaca", lineHeight: 1.6 }}>
                        • <strong>Ambulance:</strong> KA-05-EM-1108 (ACLS Cardiac) · ETA: <strong>6 Mins</strong><br />
                        • <strong>Hospital:</strong> BGS Gleneagles Hospital ER Bay 02 (Zero-Wait Entry)<br />
                        • <strong>Lead Physician:</strong> Dr. S. Rao, Chief Interventional Cardiologist
                      </div>
                    </div>
                  )}

                  {/* Text Message Content */}
                  <div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{m.text}</div>

                  {/* Proof Image if provided */}
                  {m.proofImage && (
                    <div style={{ marginTop: "10px" }}>
                      <img
                        src={m.proofImage}
                        alt="Proof"
                        style={{ maxWidth: "100%", borderRadius: "8px", border: "1px solid var(--wh-border)" }}
                      />
                    </div>
                  )}
                </div>
              ))
            )}

            {/* TEMPORARY RUNNING TELEMETRY BANNER (MATCHES IMAGE 3) */}
            {activeTelemetry && agentStatus === "RUNNING" && (
              <div className="wh-running-telemetry-banner">
                <span className="wh-telemetry-dot" />
                <span className="wh-shimmer-text">{activeTelemetry}</span>
              </div>
            )}
          </div>

          {/* BOTTOM DOCKED INPUT BAR: TEXT BAR OR PRESS-TO-SPEAK BAR */}
          <div className="wh-bottom-bar">
            {inputMode === "text" ? (
              <AISearchBar
                isDocked={true}
                theme={currentTheme}
                onAttachFile={handleFileUpload}
                onSearch={handleExecute}
                onEnterVoiceMode={() => {
                  setInputMode("voice");
                  setCurrentTheme("blue");
                }}
              />
            ) : (
              <div className="wh-voice-press-container">
                <button
                  type="button"
                  className={`wh-voice-press-btn ${isListeningVoice ? "recording" : ""}`}
                  onClick={toggleVoiceListen}
                  title={isListeningVoice ? "Tap to Finish & Send" : "Tap or Press to Speak"}
                >
                  <div className="wh-voice-press-inner">
                    {isListeningVoice ? (
                      <div className="wh-voice-press-bars">
                        <span />
                        <span />
                        <span />
                        <span />
                        <span />
                      </div>
                    ) : (
                      <svg className="wh-voice-press-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" y1="19" x2="12" y2="22" />
                      </svg>
                    )}
                    <span className="wh-voice-press-text">
                      {isListeningVoice
                        ? voiceTranscript
                          ? `"${voiceTranscript}"`
                          : "Listening... Tap to send"
                        : "Press to Speak"}
                    </span>
                  </div>
                </button>
              </div>
            )}

            <div className="wh-status-footer">
              <div>
                Status: <span className={`wh-status-pill ${agentStatus}`}>{agentStatus}</span>
              </div>
              <div>Click website anytime to pause or interact</div>
            </div>
          </div>

          {/* Bottom edge fade flare */}
          <div className="wh-card-flare-bottom" />
        </section>

        {/* DRAGGABLE ADJUSTABLE SLIDER BETWEEN CHAT AND LIVE WEB */}
        <div
          className={`wh-splitter-slider ${isDragging ? "active-drag" : ""}`}
          onMouseDown={handleSplitterMouseDown}
          title="Drag left/right to adjust chat and live web sections"
        >
          <div className="wh-splitter-track" />
          <div className="wh-splitter-thumb">
            <span />
            <span />
            <span />
          </div>
        </div>

        {/* RIGHT PANE: Live Browser Viewport & Navigation Bar */}
        <section className="wh-right-pane" style={{ width: `calc(${100 - splitPercent}% - 6px)`, flex: "none" }}>
          {/* Top edge fade flare */}
          <div className="wh-card-flare-top" />

          {/* Browser Tabs */}
          <div className="wh-browser-tabs-bar">
            {tabs.map((tab) => (
              <div
                key={tab.index}
                className={`wh-browser-tab ${tab.index === activeTabIndex ? "active" : ""}`}
                onClick={() => handleSwitchTab(tab.index)}
              >
                <span>🌐</span>
                <span>{tab.title || "New Tab"}</span>
                {tabs.length > 1 && (
                  <span className="wh-tab-close" onClick={(e) => handleCloseTab(e, tab.index)}>
                    ×
                  </span>
                )}
              </div>
            ))}
            <button className="wh-tab-add" onClick={handleOpenTab} title="Open New Tab">
              +
            </button>
          </div>

          {/* Browser Toolbar */}
          <div className="wh-browser-toolbar">
            <div className="wh-traffic-lights">
              <span className="wh-dot wh-dot-red" />
              <span className="wh-dot wh-dot-yellow" />
              <span className="wh-dot wh-dot-green" />
            </div>

            <div className="wh-nav-controls">
              <button className="wh-nav-btn" title="Back" onClick={() => refreshTabs()}>
                ◀
              </button>
              <button className="wh-nav-btn" title="Forward">
                ▶
              </button>
              <button className="wh-nav-btn" title="Refresh" onClick={() => handleNavigate()}>
                ↻
              </button>
            </div>

            <form className="wh-url-bar" onSubmit={handleNavigate}>
              <span className="wh-url-lock" title={currentUrl}>
                🔒
              </span>
              <input
                type="text"
                className="wh-url-input"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://..."
              />
              <button type="submit" className="wh-btn-go">
                Go
              </button>
            </form>

            <button
              className={`wh-btn-pill ${interactiveMode ? "wh-btn-pill-cyan" : ""}`}
              onClick={() => setInteractiveMode(!interactiveMode)}
              title="Toggle Direct Mouse Interaction Mode"
            >
              🖱️ Use Normally
            </button>

            <button className="wh-btn-pill wh-btn-pill-red" onClick={handleStopAgent} title="Stop Agent">
              🛑 Stop
            </button>
          </div>

          {/* Canvas Screencast Viewport */}
          <div className="wh-canvas-viewport">
            <canvas
              ref={canvasRef}
              className="wh-screencast-canvas"
              style={{ cursor: interactiveMode ? "crosshair" : "default" }}
              onClick={handleCanvasClick}
              onWheel={handleCanvasWheel}
            />
            {!wsConnected && (
              <div className="wh-canvas-placeholder">
                <div className="wh-thinking-spinner" />
                <span>Connecting to Live Screencast Viewport...</span>
              </div>
            )}
          </div>

          {/* Bottom edge fade flare */}
          <div className="wh-card-flare-bottom" />
        </section>
      </div>
    </div>
  );
};

export default AgentWorkspace;
