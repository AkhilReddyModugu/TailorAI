import { useState } from "react";

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button
      onClick={handleCopy}
      style={{
        fontSize: "0.75rem",
        padding: "0.25rem 0.6rem",
        border: "1px solid #ccc",
        borderRadius: 6,
        background: copied ? "#dcfce7" : "#fff",
        cursor: "pointer",
      }}
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

export default function BulletRewrite({ bullets }) {
  if (!bullets || bullets.length === 0) return null;

  return (
    <section style={{ marginBottom: "2.5rem" }}>
      <h2>Resume Bullet Rewrites</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {bullets.map((bullet, i) => (
          <div key={i} style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: "1rem" }}>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 260 }}>
                <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#888", marginBottom: "0.35rem" }}>
                  ORIGINAL
                </div>
                <p style={{ margin: 0, color: "#555" }}>{bullet.original}</p>
              </div>
              <div style={{ flex: 1, minWidth: 260 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.35rem",
                  }}
                >
                  <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#4f46e5" }}>REWRITTEN</span>
                  <CopyButton text={bullet.rewritten} />
                </div>
                <p style={{ margin: 0 }}>{bullet.rewritten}</p>
              </div>
            </div>
            {bullet.reason && (
              <p style={{ margin: "0.75rem 0 0", fontSize: "0.8rem", color: "#888", fontStyle: "italic" }}>
                {bullet.reason}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
