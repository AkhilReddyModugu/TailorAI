const STRATEGY_STYLES = {
  light_tweaks: { label: "Light Keyword Tweaks", bg: "#dcfce7", fg: "#166534" },
  targeted_rewrite: { label: "Targeted Rewrite", bg: "#fef9c3", fg: "#854d0e" },
  aggressive_rewrite: { label: "Full Rewrite (Stretch Role)", bg: "#fee2e2", fg: "#991b1b" },
  skip_mismatch: { label: "Domain Mismatch — Rewrite Skipped", bg: "#e5e7eb", fg: "#374151" },
};

function matchColor(pct) {
  if (pct > 85) return "#16a34a";
  if (pct >= 40) return "#ca8a04";
  return "#dc2626";
}

function SkillList({ title, skills, color }) {
  return (
    <div style={{ flex: 1, minWidth: 200 }}>
      <h4 style={{ margin: "0 0 0.5rem" }}>{title}</h4>
      {skills.length === 0 ? (
        <p style={{ color: "#888", fontSize: "0.85rem" }}>None</p>
      ) : (
        <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
          {skills.map((skill) => (
            <li key={skill} style={{ color, marginBottom: "0.25rem" }}>
              {skill}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function GapReport({ gapReport }) {
  if (!gapReport) return null;

  const strategy = STRATEGY_STYLES[gapReport.agent_strategy] || {
    label: gapReport.agent_strategy,
    bg: "#e5e7eb",
    fg: "#374151",
  };

  return (
    <section style={{ marginBottom: "2.5rem" }}>
      <h2>Skill Gap Report</h2>

      <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
        <div
          style={{
            fontSize: "1.5rem",
            fontWeight: 700,
            color: matchColor(gapReport.match_percentage),
          }}
        >
          {gapReport.match_percentage}% match
        </div>
        <span
          style={{
            background: strategy.bg,
            color: strategy.fg,
            padding: "0.3rem 0.75rem",
            borderRadius: 999,
            fontSize: "0.8rem",
            fontWeight: 600,
          }}
        >
          {strategy.label}
        </span>
      </div>

      {gapReport.agent_reasoning && (
        <p style={{ color: "#555", fontSize: "0.9rem", marginBottom: "1.5rem" }}>{gapReport.agent_reasoning}</p>
      )}

      <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <SkillList title="Matching Skills" skills={gapReport.matching_skills} color="#166534" />
        <SkillList title="Missing Skills" skills={gapReport.missing_skills} color="#991b1b" />
      </div>

      <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
        <SkillList title="ATS Keywords Found" skills={gapReport.ats_keywords_found} color="#166534" />
        <SkillList title="ATS Keywords Missing" skills={gapReport.ats_keywords_missing} color="#991b1b" />
      </div>
    </section>
  );
}
