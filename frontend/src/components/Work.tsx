import "./styles/Work.css";
import WorkImage from "./WorkImage";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);

const Work = () => {
  useGSAP(() => {
  let translateX: number = 0;

  function setTranslateX() {
    const box = document.getElementsByClassName("work-box");
    const rectLeft = document
      .querySelector(".work-container")!
      .getBoundingClientRect().left;
    const rect = box[0].getBoundingClientRect();
    const parentWidth = box[0].parentElement!.getBoundingClientRect().width;
    let padding: number =
      parseInt(window.getComputedStyle(box[0]).padding) / 2;
    translateX = rect.width * box.length - (rectLeft + parentWidth) + padding;
  }

  setTranslateX();

  let timeline = gsap.timeline({
    scrollTrigger: {
      trigger: ".work-section",
      start: "top top",
      end: `+=${translateX}`, // Use actual scroll width
      scrub: true,
      pin: true,
      id: "work",
    },
  });

  timeline.to(".work-flex", {
    x: -translateX,
    ease: "none",
  });

  // Clean up (optional, good practice)
  return () => {
    timeline.kill();
    ScrollTrigger.getById("work")?.kill();
  };
}, []);
  return (
    <div className="work-section" id="work">
      <div className="work-container section-container">
        <h2>
          My <span>Work</span>
        </h2>
        <div className="work-flex">
          <div className="work-box">
            <div className="work-info">
              <div className="work-title">
                <h3>01</h3>
                <div>
                  <h4>JARVIS AI Assistant</h4>
                  <p>AI / Automation</p>
                </div>
              </div>
              <h4>Tools and features</h4>
              <p>Python, AI Agents, Voice Interaction, System Automation</p>
            </div>
            <WorkImage image="/images/jarvis.png.png" alt="JARVIS AI Assistant" />
          </div>
          <div className="work-box">
            <div className="work-info">
              <div className="work-title">
                <h3>02</h3>
                <div>
                  <h4>AURA AI</h4>
                  <p>AI / Interaction</p>
                </div>
              </div>
              <h4>Tools and features</h4>
              <p>Python, AI/ML, Intelligent Interaction</p>
            </div>
            <WorkImage image="/images/aura-ai.png.png" alt="AURA AI" />
          </div>
          <div className="work-box">
            <div className="work-info">
              <div className="work-title">
                <h3>03</h3>
                <div>
                  <h4>Spam Detection</h4>
                  <p>Machine Learning</p>
                </div>
              </div>
              <h4>Tools and features</h4>
              <p>Python, ML, Classification</p>
            </div>
            <WorkImage image="/images/spam-detection.png.png" alt="Spam Detection" />
          </div>
          <div className="work-box">
            <div className="work-info">
              <div className="work-title">
                <h3>04</h3>
                <div>
                  <h4>Movie Recommendation System</h4>
                  <p>Machine Learning</p>
                </div>
              </div>
              <h4>Tools and features</h4>
              <p>Python, ML, Recommendation Algorithms</p>
            </div>
            <WorkImage image="/images/movie-recommendation.png.png" alt="Movie Recommendation System" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Work;
