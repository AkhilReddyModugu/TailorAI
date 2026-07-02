import { useState } from "react";

export default function CoverLetter({ coverLetter }) {
  const [copied, setCopied] = useState(false);

  if (!coverLetter) return null;

  async function handleCopy() {
    await navigator.clipboard.writeText(coverLetter);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <section style={{ marginBottom: "2.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Cover Letter</h2>
        <button
          onClick={handleCopy}
          style={{
            fontSize: "0.85rem",
            padding: "0.4rem 0.9rem",
            border: "1px solid #ccc",
            borderRadius: 6,
            background: copied ? "#dcfce7" : "#fff",
            cursor: "pointer",
          }}
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre
        style={{
          whiteSpace: "pre-wrap",
          fontFamily: "inherit",
          fontSize: "0.95rem",
          lineHeight: 1.6,
          border: "1px solid #e5e7eb",
          borderRadius: 8,
          padding: "1.25rem",
          background: "#fafafa",
        }}
      >
        {coverLetter}
      </pre>
    </section>
  );
}
