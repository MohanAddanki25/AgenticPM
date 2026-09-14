import axios from "axios";
import type {
  AnalysisResult,
  Project,
  ProjectDocument,
  RAGQueryResponse,
  RAGReindexResponse,
  Task,
  User,
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function registerUser(name: string, email: string, password: string): Promise<User> {
  const res = await api.post("/api/auth/register", { name, email, password });
  return res.data;
}

export async function loginUser(email: string, password: string): Promise<string> {
  const res = await api.post("/api/auth/login", { email, password });
  return res.data.access_token;
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await api.get("/api/projects");
  return res.data;
}

export async function createProject(payload: {
  name: string;
  description: string;
  start_date: string;
  target_end_date: string;
}): Promise<Project> {
  const res = await api.post("/api/projects", payload);
  return res.data;
}

export async function fetchTasks(projectId: string): Promise<Task[]> {
  const res = await api.get(`/api/projects/${projectId}/tasks`);
  return res.data;
}

export async function createTask(
  projectId: string,
  payload: Partial<Task> & { name: string; due_date: string; status: string }
): Promise<Task> {
  const res = await api.post(`/api/projects/${projectId}/tasks`, payload);
  return res.data;
}

export async function updateTask(projectId: string, taskId: string, payload: Partial<Task>): Promise<Task> {
  const res = await api.patch(`/api/projects/${projectId}/tasks/${taskId}`, payload);
  return res.data;
}

export async function deleteTask(projectId: string, taskId: string): Promise<void> {
  await api.delete(`/api/projects/${projectId}/tasks/${taskId}`);
}

export async function runAnalysis(projectId: string): Promise<AnalysisResult> {
  const res = await api.post(`/api/projects/${projectId}/analyze`);
  return res.data;
}

export async function fetchDocuments(projectId: string): Promise<ProjectDocument[]> {
  const res = await api.get(`/api/projects/${projectId}/documents`);
  return res.data;
}

export async function createDocument(
  projectId: string,
  payload: { title: string; content: string; doc_type: string }
): Promise<ProjectDocument> {
  const res = await api.post(`/api/projects/${projectId}/documents`, payload);
  return res.data;
}

export async function deleteDocument(projectId: string, docId: string): Promise<void> {
  await api.delete(`/api/projects/${projectId}/documents/${docId}`);
}

export async function queryRAG(
  projectId: string,
  query: string,
  top_k: number = 4
): Promise<RAGQueryResponse> {
  const res = await api.post(`/api/projects/${projectId}/rag/query`, { query, top_k });
  return res.data;
}

export async function reindexRAG(projectId: string): Promise<RAGReindexResponse> {
  const res = await api.post(`/api/projects/${projectId}/rag/reindex`);
  return res.data;
}

