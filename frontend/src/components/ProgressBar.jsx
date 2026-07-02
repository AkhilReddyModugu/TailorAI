const STEPS = [
  "Parsing resume",
  "Analyzing job description",
  "Detecting skill gaps",
  "Rewriting bullets",
  "Generating cover letter",
];

export default function ProgressBar({ currentStep, currentStepName, status }) {
  return (
    <div style={{ margin: "2rem 0" }}>
      <div style={{ display: "flex", alignItems: "center" }}>
        {STEPS.map((label, i) => {
          const stepNum = i + 1;
          const isDone = status === "completed" || currentStep > stepNum;
          const isActive = status !== "completed" && currentStep === stepNum;
          return (
            <div key={label} style={{ display: "flex", alignItems: "center", flex: i < STEPS.length - 1 ? 1 : "none" }}>
              <div
                title={label}
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  flexShrink: 0,
                  color: isDone || isActive ? "#fff" : "#666",
                  background: isDone ? "#16a34a" : isActive ? "#4f46e5" : "#e5e7eb",
                }}
              >
                {isDone ? "✓" : stepNum}
              </div>
              {i < STEPS.length - 1 && (
                <div
                  style={{
                    flex: 1,
                    height: 3,
                    background: currentStep > stepNum || status === "completed" ? "#16a34a" : "#e5e7eb",
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
      <p style={{ marginTop: "0.75rem", fontSize: "0.9rem", color: "#555" }}>
        {status === "completed"
          ? "Done!"
          : status === "failed"
            ? "Something went wrong."
            : currentStepName || "Starting..."}
      </p>
    </div>
  );
}
