export interface User {
  id: string;
  name: string;
  email: string;
}

export type TaskStatus = "Not Started" | "In Progress" | "Completed" | "Blocked" | "Delayed";

export interface Task {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  due_date: string;
  status: TaskStatus;
  assignee?: string;
  depends_on: string[];
  resource_notes?: string;
  is_delayed: boolean;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  start_date: string;
  target_end_date: string;
  owner_id: string;
  created_at: string;
}

export type RiskSeverity = "Low" | "Medium" | "High" | "Critical";

export interface RiskItem {
  id: string;
  type: string;
  severity: RiskSeverity;
  task_id?: string;
  task_name?: string;
  description: string;
  evidence: string[];
  affected_tasks: string[];
}

export interface PriorityItem {
  task_id: string;
  task_name: string;
  priority_score: number;
  priority_level: string;
  reason: string;
  evidence: string[];
}

export interface NextAction {
  action: string;
  owner?: string;
  related_task?: string;
  urgency: string;
}

export type ProjectHealth = "On Track" | "At Risk" | "Delayed";

export interface AnalysisResult {
  project_id: string;
  generated_at: string;
  project_health: ProjectHealth;
  health_explanation: string;
  milestones: { name: string; due_date: string; status: string }[];
  task_status_summary: Record<string, number>;
  upcoming_deadlines: { task_name: string; due_date: string; status: string }[];
  delayed_tasks: { task_name: string; due_date: string; status: string; overdue_days: number }[];
  dependency_graph: { task: string; depends_on: string[]; status: string; downstream_impact: string[] }[];
  critical_blockers: { task_name: string; reason: string; downstream_impact: string[] }[];
  risks: RiskItem[];
  priorities: PriorityItem[];
  next_actions: NextAction[];
  weekly_summary: string;
  used_llm: boolean;
}

export type DocumentType = "spec" | "prd" | "meeting_notes" | "retrospective" | "risk_log" | "general";

export interface ProjectDocument {
  id: string;
  project_id: string;
  title: string;
  content: string;
  doc_type: DocumentType;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface RAGSource {
  source_id: string;
  source_type: "document" | "task" | "analysis" | string;
  title: string;
  excerpt: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  sources: RAGSource[];
  used_llm: boolean;
  generated_at: string;
}

export interface RAGReindexResponse {
  indexed_documents: number;
  indexed_tasks: number;
  indexed_analyses: number;
  total_chunks: number;
  message: string;
}

