import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ResumeUpload from "../components/ResumeUpload.jsx";
import JDInput from "../components/JDInput.jsx";
import { uploadResume } from "../services/api.js";

export default function HomePage() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!resumeFile || !jobDescription.trim()) {
      setError("Please upload a resume and paste a job description.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const { session_id } = await uploadResume(resumeFile, jobDescription);
      navigate(`/results/${session_id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Something went wrong. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "3rem 1.5rem" }}>
      <h1>TailorAI</h1>
      <p>
        Upload your resume and a job description to get a tailored skill gap
        report, rewritten bullets, and a cover letter.
      </p>
      <form onSubmit={handleSubmit}>
        <ResumeUpload file={resumeFile} onFileSelect={setResumeFile} />
        <div style={{ marginTop: "1.5rem" }}>
          <JDInput value={jobDescription} onChange={setJobDescription} />
        </div>
        {error && <p style={{ color: "crimson" }}>{error}</p>}
        <button
          type="submit"
          disabled={isSubmitting}
          style={{ marginTop: "1rem", padding: "0.75rem 1.5rem" }}
        >
          {isSubmitting ? "Analyzing..." : "Analyze"}
        </button>
      </form>
    </div>
  );
}
