import { useState, lazy, Suspense } from "react";
import "./App.css";
import Cursor from "./components/Cursor";
import Navbar from "./components/Navbar";
import Landing from "./components/Landing";

const CharacterModel = lazy(() => import("./components/Character"));
const AgentWorkspace = lazy(() => import("./components/AgentWorkspace/AgentWorkspace"));
import { LoadingProvider } from "./context/LoadingProvider";

const App = () => {
  const [hasStarted, setHasStarted] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [activePrompt, setActivePrompt] = useState<string>("");
  const [activeTheme, setActiveTheme] = useState<"purple" | "blue">("purple");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);

  const handlePromptSubmit = (query: string, mode: "purple" | "blue", file?: File | null) => {
    setActivePrompt(query.trim());
    setActiveTheme(mode);
    if (file) setAttachedFile(file);

    // Fade out the initial search bar and reveal the transparent glass workspace cards
    setIsTransitioning(true);
    setTimeout(() => {
      setHasStarted(true);
      setIsTransitioning(false);
    }, 350);
  };

  const handleResetToHero = () => {
    setActivePrompt("");
    setAttachedFile(null);
    setHasStarted(false);
    setIsTransitioning(false);
  };

  return (
    <>
      {/* Global custom cursor maintained across all views */}
      <Cursor />

      <LoadingProvider>
        <div className="app-main-viewport">
          {/* Ambient Lighting & Flares */}
          <Navbar />

          {/* PERMANENT 3D HUMANOID ROBOT BACKGROUND - NEVER VANISHES, NEVER UNMOUNTS */}
          <div className="app-permanent-robot-bg">
            <Suspense fallback={null}>
              <CharacterModel />
            </Suspense>
          </div>

          {/* INITIAL SCREEN LAYER: ASK ANYTHING SEARCH BAR & HERO OVERLAY */}
          {!hasStarted && (
            <div className={`initial-hero-overlay ${isTransitioning ? "search-bar-fade-out" : ""}`}>
              <Landing onPromptSubmit={handlePromptSubmit} isTransitioningOut={isTransitioning} />
            </div>
          )}

          {/* WORKSPACE COCKPIT: TRANSLUCENT GLASS CARDS FADING IN OVER ROBOT */}
          {hasStarted && (
            <div className="workspace-glass-layer">
              <Suspense fallback={<div className="workspace-loading">Initializing Wormhole Cockpit...</div>}>
                <AgentWorkspace
                  initialPrompt={activePrompt}
                  initialFile={attachedFile}
                  theme={activeTheme}
                  onReset={handleResetToHero}
                />
              </Suspense>
            </div>
          )}
        </div>
      </LoadingProvider>
    </>
  );
};

export default App;
