import { PropsWithChildren } from "react";
import Cursor from "./Cursor";
import Landing from "./Landing";
import Navbar from "./Navbar";

const MainContainer = ({ children }: PropsWithChildren) => {
  return (
    <div className="container-main">
      <Cursor />
      <Navbar />
      <Landing>{children}</Landing>
    </div>
  );
};

export default MainContainer;
