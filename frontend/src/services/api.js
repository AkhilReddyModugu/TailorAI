// Axios calls to backend
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE_URL });

export async function uploadResume(resumeFile, jobDescription) {
  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("job_description", jobDescription);

  const { data } = await client.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getSession(sessionId) {
  const { data } = await client.get(`/api/session/${sessionId}`);
  return data;
}
