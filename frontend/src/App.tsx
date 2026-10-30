import { useState, lazy, Suspense } from "react";
import "./App.css";

const CharacterModel = lazy(() => import("./components/Character"));
const MainContainer = lazy(() => import("./components/MainContainer"));
const AgentWorkspace = lazy(() => import("./components/AgentWorkspace/AgentWorkspace"));
import { LoadingProvider } from "./context/LoadingProvider";

const App = () => {
  const [hasStarted, setHasStarted] = useState(false);
  const [activePrompt, setActivePrompt] = useState<string>("");

  const handlePromptSubmit = (query: string) => {
    if (!query.trim()) return;
    setActivePrompt(query.trim());
    setHasStarted(true);
  };

  const handleActivateVoice = () => {
    setActivePrompt("");
    setHasStarted(true);
  };

  const handleResetToHero = () => {
    setActivePrompt("");
    setHasStarted(false);
  };

  return (
    <LoadingProvider>
      <Suspense fallback={<div className="loading-fallback" />}>
        {!hasStarted ? (
          <MainContainer
            onPromptSubmit={handlePromptSubmit}
            onActivateVoice={handleActivateVoice}
          >
            <Suspense fallback={null}>
              <CharacterModel />
            </Suspense>
          </MainContainer>
        ) : (
          <Suspense fallback={<div className="workspace-loading">Loading Wormhole Cockpit...</div>}>
            <AgentWorkspace
              initialPrompt={activePrompt}
              onReset={handleResetToHero}
            />
          </Suspense>
        )}
      </Suspense>
    </LoadingProvider>
  );
};

export default App;
