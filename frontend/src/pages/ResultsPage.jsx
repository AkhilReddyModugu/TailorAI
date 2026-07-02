import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { getSession } from "../services/api.js";
import ProgressBar from "../components/ProgressBar.jsx";
import GapReport from "../components/GapReport.jsx";
import BulletRewrite from "../components/BulletRewrite.jsx";
import CoverLetter from "../components/CoverLetter.jsx";

const POLL_INTERVAL_MS = 2000;

export default function ResultsPage() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await getSession(sessionId);
        if (cancelled) return;
        setSession(data);
        if (data.status !== "processing" && intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err.response?.data?.detail || "Failed to load session.");
        if (intervalRef.current) clearInterval(intervalRef.current);
      }
    }

    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [sessionId]);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "3rem 1.5rem" }}>
      <h1>Results</h1>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {!error && !session && <p>Loading...</p>}

      {session && (
        <>
          <ProgressBar
            currentStep={session.current_step}
            currentStepName={session.current_step_name}
            status={session.status}
          />

          {session.status === "failed" && (
            <p style={{ color: "crimson" }}>{session.error_message || "Processing failed."}</p>
          )}

          {session.status === "completed" && (
            <>
              <GapReport gapReport={session.gap_report} />
              <BulletRewrite bullets={session.rewritten_bullets} />
              <CoverLetter coverLetter={session.cover_letter} />
            </>
          )}
        </>
      )}
    </div>
  );
}
