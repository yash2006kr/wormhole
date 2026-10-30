import { PropsWithChildren } from "react";
import Landing from "./Landing";
import Navbar from "./Navbar";

interface MainContainerProps extends PropsWithChildren {
  onPromptSubmit?: (query: string, mode: "purple" | "blue", attachedFile?: File | null) => void;
  isTransitioningOut?: boolean;
}

const MainContainer = ({ children, onPromptSubmit, isTransitioningOut }: MainContainerProps) => {
  return (
    <div className="container-main">
      <Navbar />
      {children}
      <Landing onPromptSubmit={onPromptSubmit} isTransitioningOut={isTransitioningOut} />
    </div>
  );
};

export default MainContainer;
