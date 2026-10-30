import gsap from "gsap";
import { smoother } from "../Navbar";

export function initialFX() {
  document.body.style.overflow = "hidden";
  if ((smoother as { paused?: (state: boolean) => void })?.paused) {
    (smoother as { paused: (state: boolean) => void }).paused(false);
  }
  document.getElementsByTagName("main")[0]?.classList.add("main-active");
  gsap.to("body", {
    backgroundColor: "#0b080c",
    duration: 0.5,
    delay: 1,
  });

  gsap.fromTo(
    [".nav-fade", ".landing-circle1", ".landing-circle2"],
    { opacity: 0 },
    {
      opacity: 1,
      duration: 1.2,
      ease: "power1.inOut",
      delay: 0.1,
    }
  );
}
