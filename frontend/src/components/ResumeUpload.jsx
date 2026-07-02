import { useRef, useState } from "react";

export default function ResumeUpload({ file, onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile && droppedFile.type === "application/pdf") {
      onFileSelect(droppedFile);
    }
  }

  function handleChange(e) {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) onFileSelect(selectedFile);
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${isDragging ? "#4f46e5" : "#ccc"}`,
        borderRadius: 8,
        padding: "2rem",
        textAlign: "center",
        cursor: "pointer",
        background: isDragging ? "#eef2ff" : "#fafafa",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        onChange={handleChange}
        style={{ display: "none" }}
      />
      {file ? (
        <p>{file.name}</p>
      ) : (
        <p>Drag &amp; drop your resume PDF here, or click to browse</p>
      )}
    </div>
  );
}
