import { PropsWithChildren } from "react";
import Cursor from "./Cursor";
import Landing from "./Landing";
import Navbar from "./Navbar";

interface MainContainerProps extends PropsWithChildren {
  onPromptSubmit?: (query: string) => void;
  onActivateVoice?: () => void;
}

const MainContainer = ({ children, onPromptSubmit, onActivateVoice }: MainContainerProps) => {
  return (
    <div className="container-main">
      <Cursor />
      <Navbar />
      <Landing onPromptSubmit={onPromptSubmit} onActivateVoice={onActivateVoice}>
        {children}
      </Landing>
    </div>
  );
};

export default MainContainer;
