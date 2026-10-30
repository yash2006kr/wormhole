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
      <Landing onPromptSubmit={onPromptSubmit} isTransitioningOut={isTransitioningOut}>
        {children}
      </Landing>
    </div>
  );
};

export default MainContainer;
