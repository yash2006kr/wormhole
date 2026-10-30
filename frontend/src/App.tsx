import { useState, lazy, Suspense } from "react";
import "./App.css";
import Cursor from "./components/Cursor";

const CharacterModel = lazy(() => import("./components/Character"));
const MainContainer = lazy(() => import("./components/MainContainer"));
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

    // Trigger smooth fade out transition of the hero scene
    setIsTransitioning(true);
    setTimeout(() => {
      setHasStarted(true);
      setIsTransitioning(false);
    }, 450);
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
        <Suspense fallback={<div className="loading-fallback" />}>
          {!hasStarted ? (
            <MainContainer
              onPromptSubmit={handlePromptSubmit}
              isTransitioningOut={isTransitioning}
            >
              <Suspense fallback={null}>
                <CharacterModel />
              </Suspense>
            </MainContainer>
          ) : (
            <Suspense fallback={<div className="workspace-loading">Initializing Wormhole Cockpit...</div>}>
              <AgentWorkspace
                initialPrompt={activePrompt}
                initialFile={attachedFile}
                theme={activeTheme}
                onReset={handleResetToHero}
              />
            </Suspense>
          )}
        </Suspense>
      </LoadingProvider>
    </>
  );
};

export default App;
