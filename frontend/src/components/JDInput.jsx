export default function JDInput({ value, onChange }) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Paste the job description here..."
      rows={12}
      style={{
        width: "100%",
        padding: "0.75rem",
        fontFamily: "inherit",
        fontSize: "0.95rem",
        boxSizing: "border-box",
      }}
    />
  );
}
