import { PropsWithChildren } from "react";
import "./styles/Landing.css";
import AISearchBar from "./AISearchBar/AISearchBar";

interface LandingProps extends PropsWithChildren {
  onPromptSubmit?: (query: string) => void;
  onActivateVoice?: () => void;
}

const Landing = ({ children, onPromptSubmit, onActivateVoice }: LandingProps) => {
  return (
    <div className="landing-section" id="landingDiv">
      {children}
      <AISearchBar
        onSearch={onPromptSubmit}
        onActivateWormhole={onActivateVoice}
      />
    </div>
  );
};

export default Landing;
