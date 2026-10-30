import React, { useState, useEffect, useRef, useCallback } from "react";
import "./AgentWorkspace.css";

interface Tab {
  index: number;
  title: string;
  url: string;
  active: boolean;
}

interface MessageStep {
  text: string;
  time?: string;
  icon?: string;
}

interface ChatMessage {
  id: string;
  sender: "user" | "agent" | "system";
  text: string;
  timestamp: string;
  steps?: MessageStep[];
  emergency?: boolean;
  telemetry?: any;
}

interface AgentWorkspaceProps {
  initialPrompt?: string;
  onReset?: () => void;
}

export const AgentWorkspace: React.FC<AgentWorkspaceProps> = ({
  initialPrompt,
  onReset,
}) => {
  const [layout, setLayout] = useState<"default" | "wide" | "5050">("default");
  const [inputMode, setInputMode] = useState<"text" | "voice">("text");
  const [prompt, setPrompt] = useState("");
  const [agentStatus, setAgentStatus] = useState<"IDLE" | "RUNNING" | "PAUSED_FOR_HUMAN" | "SUCCESS" | "ERROR">("IDLE");
  const [wsConnected, setWsConnected] = useState(false);
  const [urlInput, setUrlInput] = useState("about:blank");
  const [currentUrl, setCurrentUrl] = useState("about:blank");
  const [tabs, setTabs] = useState<Tab[]>([
    { index: 0, title: "Portal Home", url: "about:blank", active: true },
  ]);
  const [activeTabIndex, setActiveTabIndex] = useState(0);
  const [interactiveMode, setInteractiveMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const chatScrollRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, agentStatus]);

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
          console.error("[WS] Error:", err);
          socket.close();
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
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
            } else if (data.type === "TABS_UPDATE") {
              if (Array.isArray(data.tabs)) {
                setTabs(data.tabs);
                setActiveTabIndex(data.active_index ?? 0);
              }
              if (data.url) {
                setCurrentUrl(data.url);
                setUrlInput(data.url);
              }
            } else if (data.type === "STATE_CHANGE") {
              if (data.state === "RUNNING") setAgentStatus("RUNNING");
              else if (data.state === "PAUSED_FOR_HUMAN") setAgentStatus("PAUSED_FOR_HUMAN");
              else if (data.state === "IDLE") setAgentStatus("IDLE");
            } else if (data.type === "AGENT_STEP") {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
                if (last && last.sender === "agent") {
                  return [
                    ...prev.slice(0, -1),
                    {
                      ...last,
                      steps: [...(last.steps || []), { text: data.text, time: now }],
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
                    steps: [{ text: data.text, time: now }],
                  },
                ];
              });
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

  const handleExecute = async (overridePrompt?: string) => {
    const textToSend = (overridePrompt ?? prompt).trim();
    if (!textToSend) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const userMsg: ChatMessage = {
      id: Math.random().toString(),
      sender: "user",
      text: textToSend,
      timestamp: timeStr,
    };

    setMessages((prev) => [...prev, userMsg]);
    setPrompt("");
    setAgentStatus("RUNNING");

    try {
      const res = await fetch("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: textToSend }),
      });

      const data = await res.json();
      const isEmergency = data.is_emergency || data.status === "EMERGENCY_DISPATCH_COMPLETE" || textToSend.toLowerCase().includes("heart attack") || textToSend.toLowerCase().includes("emergency");

      const agentMsg: ChatMessage = {
        id: Math.random().toString(),
        sender: "agent",
        text: data.response || data.message || "Task processed successfully.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        emergency: isEmergency,
        telemetry: data.telemetry,
        steps: data.steps?.map((s: string) => ({ text: s, time: timeStr })),
      };

      setMessages((prev) => [...prev, agentMsg]);
      setAgentStatus("SUCCESS");
      refreshTabs();
    } catch (err: any) {
      console.error("Execution error:", err);
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

  useEffect(() => {
    if (initialPrompt && initialPrompt.trim()) {
      handleExecute(initialPrompt.trim());
    }
  }, [initialPrompt]);

  const handleNewChat = async () => {
    try {
      await fetch("/api/chat/new", { method: "POST" });
    } catch (e) {
      console.warn("Reset chat backend error:", e);
    }
    setMessages([]);
    setAgentStatus("IDLE");
    if (onReset) {
      onReset();
    }
  };

  const handleStopAgent = async () => {
    try {
      await fetch("/api/abort", { method: "POST" });
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ABORT_TASK" }));
      }
      setAgentStatus("PAUSED_FOR_HUMAN");
    } catch (e) {
      console.error("Stop agent error:", e);
    }
  };

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

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    const rect = canvas.getBoundingClientRect();
    const xRatio = (e.clientX - rect.left) / rect.width;
    const yRatio = (e.clientY - rect.top) / rect.height;

    wsRef.current.send(
      JSON.stringify({
        type: "CANVAS_CLICK",
        x: Math.max(0, Math.min(1, xRatio)),
        y: Math.max(0, Math.min(1, yRatio)),
      })
    );
  };

  const handleCanvasWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    const rect = canvas.getBoundingClientRect();
    const xRatio = (e.clientX - rect.left) / rect.width;
    const yRatio = (e.clientY - rect.top) / rect.height;

    wsRef.current.send(
      JSON.stringify({
        type: "CANVAS_WHEEL",
        x: Math.max(0, Math.min(1, xRatio)),
        y: Math.max(0, Math.min(1, yRatio)),
        deltaX: e.deltaX,
        deltaY: e.deltaY,
      })
    );
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

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
          text: `📁 File uploaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)${
            data.processed_size ? ` → Healed: ${data.processed_size}` : ""
          }`,
          timestamp: timeStr,
        },
      ]);
    } catch (err: any) {
      console.error("Upload error:", err);
    }
  };

  const toggleVoiceRecording = () => {
    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use text input.");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsRecording(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setPrompt((prev) => (prev ? `${prev} ${transcript}` : transcript));
      };

      recognition.onerror = () => {
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e) {
      console.error("Speech recognition error:", e);
      setIsRecording(false);
    }
  };

  return (
    <div className="workspace-root">
      {/* 1. TOP APP HEADER */}
      <header className="wh-top-header">
        <div className="wh-brand">
          <div className="wh-logo-orb">W</div>
          <span className="wh-brand-title">warmhole</span>
          <span className="wh-brand-subtitle">your agentic workspace</span>
        </div>

        <div className="wh-top-controls">
          <div className="wh-layout-group">
            <span className="wh-layout-label">Workspace:</span>
            <div className="wh-pills">
              <button
                className={`wh-pill-btn ${layout === "default" ? "active" : ""}`}
                onClick={() => setLayout("default")}
              >
                Default
              </button>
              <button
                className={`wh-pill-btn ${layout === "wide" ? "active" : ""}`}
                onClick={() => setLayout("wide")}
              >
                Wide Browser
              </button>
              <button
                className={`wh-pill-btn ${layout === "5050" ? "active" : ""}`}
                onClick={() => setLayout("5050")}
              >
                50:50
              </button>
            </div>
          </div>

          <div className="wh-live-badge">
            <span className="wh-live-dot" />
            <span>{wsConnected ? "LIVE STREAM ACTIVE" : "STREAM OFFLINE"}</span>
          </div>
        </div>
      </header>

      {/* 2. MAIN WORKBENCH SPLIT PANE */}
      <div className={`wh-workbench layout-${layout}`}>
        {/* LEFT PANE */}
        <section className="wh-left-pane">
          <div className="wh-cockpit-header">
            <div className="wh-mode-toggle">
              <button
                className={`wh-mode-btn ${inputMode === "text" ? "active" : ""}`}
                onClick={() => setInputMode("text")}
              >
                + Text
              </button>
              <button
                className={`wh-mode-btn ${inputMode === "voice" ? "active" : ""}`}
                onClick={() => {
                  setInputMode("voice");
                  toggleVoiceRecording();
                }}
              >
                🔈)) Voice
              </button>
            </div>

            <div className="wh-action-btns">
              <button className="wh-btn-pill wh-btn-pill-cyan" onClick={handleNewChat} title="Start New Chat & Return to Hero">
                + New Chat
              </button>
              <button className="wh-btn-pill wh-btn-pill-red" onClick={handleStopAgent} title="Emergency Stop">
                🛑 Stop Agent
              </button>
            </div>
          </div>

          {/* CHAT FEED CONTAINER */}
          <div className="wh-chat-feed" ref={chatScrollRef}>
            {messages.length === 0 ? (
              <div style={{ padding: "30px 20px", textAlign: "center", color: "var(--wh-muted)" }}>
                <h4 style={{ color: "#fff", marginBottom: "8px" }}>Wormhole Autonomous Agent Ready</h4>
                <p style={{ fontSize: "11px", marginBottom: "16px" }}>Type any travel booking, checkout, document healing, or emergency prompt.</p>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <button
                    className="wh-btn-pill wh-btn-pill-cyan"
                    style={{ justifyContent: "center" }}
                    onClick={() => handleExecute("Book a sleeper seat on KSRTC from Bangalore to Mysore for tomorrow")}
                  >
                    🚌 Book KSRTC Seat Autonomous
                  </button>
                  <button
                    className="wh-btn-pill wh-btn-pill-cyan"
                    style={{ justifyContent: "center" }}
                    onClick={() => handleExecute("Strip dark pattern charges and insurance from checkout cart")}
                  >
                    🛒 Anti-Dark-Pattern Fee Stripper
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
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px", fontSize: "10px", color: "var(--wh-muted)" }}>
                    <span style={{ fontWeight: 700, color: m.sender === "user" ? "var(--wh-purple)" : "var(--wh-cyan)" }}>
                      {m.sender === "user" ? "YOU" : m.sender === "agent" ? "WORMHOLE COPILOT" : "SYSTEM"}
                    </span>
                    <span>{m.timestamp}</span>
                  </div>

                  {m.emergency && (
                    <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: "8px", padding: "10px", marginBottom: "10px" }}>
                      <div style={{ color: "#f87171", fontWeight: 800, fontSize: "11px", display: "flex", justifyContent: "space-between" }}>
                        <span>🚨 CODE RED: ACUTE MEDICAL EMERGENCY</span>
                        <span>CPR METRONOME: 110 BPM ♥</span>
                      </div>
                      <div style={{ fontSize: "11px", marginTop: "6px", color: "#fecaca" }}>
                        • <strong>Ambulance:</strong> KA-05-EM-1108 (ACLS Cardiac) · ETA: <strong>6 Mins</strong><br />
                        • <strong>Hospital:</strong> BGS Gleneagles Hospital ER Bay 02 (Zero-Wait Entry)<br />
                        • <strong>Lead Physician:</strong> Dr. S. Rao, Chief Interventional Cardiologist
                      </div>
                    </div>
                  )}

                  <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>

                  {m.steps && m.steps.length > 0 && (
                    <div style={{ marginTop: "10px", borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: "8px" }}>
                      <div style={{ fontSize: "10px", color: "var(--wh-muted)", marginBottom: "4px", fontWeight: 700 }}>
                        TELEMETRY EXECUTION LOGS ({m.steps.length})
                      </div>
                      {m.steps.map((st, i) => (
                        <div key={i} style={{ fontSize: "10.5px", color: "#94a3b8", display: "flex", gap: "6px", alignItems: "baseline", margin: "2px 0" }}>
                          <span style={{ color: "var(--wh-cyan)" }}>•</span>
                          <span style={{ flex: 1 }}>{st.text}</span>
                          {st.time && <span style={{ fontSize: "9px", color: "#64748b" }}>{st.time}</span>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}

            {agentStatus === "RUNNING" && (
              <div className="wh-thinking-box">
                <div className="wh-thinking-spinner" />
                <span>Wormhole Copilot executing autonomous task on browser...</span>
              </div>
            )}
          </div>

          {/* BOTTOM BAR */}
          <div className="wh-bottom-bar">
            <div className="wh-input-container">
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={handleFileUpload}
                accept="image/*,.pdf,.doc,.docx"
              />
              <button
                type="button"
                className="wh-attach-btn"
                onClick={() => fileInputRef.current?.click()}
                title="Attach Document or Photo for Healing"
              >
                📎
              </button>
              <input
                type="text"
                className="wh-text-input"
                placeholder="Ask anything..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleExecute();
                  }
                }}
              />
              <button
                type="button"
                className={`wh-mic-btn ${isRecording ? "listening" : ""}`}
                onClick={toggleVoiceRecording}
                title={isRecording ? "Stop voice listening" : "Speak voice command"}
              >
                {isRecording ? "🔴" : "🎙️"}
              </button>
              <button
                type="button"
                className="wh-run-btn"
                onClick={() => handleExecute()}
                disabled={agentStatus === "RUNNING" && !prompt.trim()}
              >
                Run ↗
              </button>
            </div>

            <div className="wh-status-footer">
              <div>
                Status: <span className={`wh-status-pill ${agentStatus}`}>{agentStatus}</span>
              </div>
              <div>Click website anytime to pause</div>
            </div>
          </div>
        </section>

        {/* RIGHT PANE */}
        <section className="wh-right-pane">
          {/* TABS BAR */}
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

          {/* BROWSER TOOLBAR */}
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

          {/* SCREENCAST VIEWPORT */}
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
        </section>
      </div>
    </div>
  );
};

export default AgentWorkspace;
