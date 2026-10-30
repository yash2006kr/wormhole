import { PropsWithChildren } from "react";
import "./styles/Landing.css";
import AISearchBar from "./AISearchBar/AISearchBar";

const Landing = ({ children }: PropsWithChildren) => {
  return (
    <div className="landing-section" id="landingDiv">
      {children}
      <AISearchBar />
    </div>
  );
};

export default Landing;
