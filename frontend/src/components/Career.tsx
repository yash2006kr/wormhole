import "./styles/Career.css";

const Career = () => {
  return (
    <div className="career-section section-container">
      <div className="career-container">
        <h2>
          My journey <span>&</span>
          <br /> education
        </h2>
        <div className="career-info">
          <div className="career-timeline">
            <div className="career-dot"></div>
          </div>
          <div className="career-info-box">
            <div className="career-info-in">
              <div className="career-role">
                <h4>Student</h4>
                <h5>MH National Public English School, Ramnagar</h5>
              </div>
              <h3>School</h3>
            </div>
            <p>
              Completed schooling with a strong foundation in academics and
              early interest in technology and creative work.
            </p>
          </div>
          <div className="career-info-box">
            <div className="career-info-in">
              <div className="career-role">
                <h4>Student</h4>
                <h5>Universal Pre-University College</h5>
              </div>
              <h3>PU</h3>
            </div>
            <p>
              Pursued pre-university education, further developing analytical
              and problem-solving skills.
            </p>
          </div>
          <div className="career-info-box">
            <div className="career-info-in">
              <div className="career-role">
                <h4>Third-Year Student</h4>
                <h5>Don Bosco Institute of Technology</h5>
              </div>
              <h3>NOW</h3>
            </div>
            <p>
              Currently pursuing my degree while actively building full-stack
              web applications, AI/ML projects and creative digital content.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Career;
