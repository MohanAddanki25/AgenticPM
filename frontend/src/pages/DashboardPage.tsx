import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import {
  createProject, createTask, fetchProjects, fetchTasks, runAnalysis, updateTask, deleteTask,
} from "../api/client";
import type { AnalysisResult, Project, Task, TaskStatus } from "../types";
import HealthBanner from "../components/HealthBanner";
import RAGAssistant from "../components/RAGAssistant";
import { Badge, Card, severityColor, statusColor } from "../components/ui";
import { useAuth } from "../context/AuthContext";

const STATUS_OPTIONS: TaskStatus[] = ["Not Started", "In Progress", "Completed", "Blocked", "Delayed"];

const DashboardPage: React.FC = () => {
  const { logout } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [showNewProject, setShowNewProject] = useState(false);
  const [showNewTask, setShowNewTask] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedProject = useMemo(
    () => projects.find((p) => p.id === selectedProjectId) || null,
    [projects, selectedProjectId]
  );

  const loadProjects = async () => {
    const data = await fetchProjects();
    setProjects(data);
    if (!selectedProjectId && data.length) setSelectedProjectId(data[0].id);
  };

  const loadTasks = async (projectId: string) => {
    const data = await fetchTasks(projectId);
    setTasks(data);
  };

  useEffect(() => {
    loadProjects().catch((e) => setError(e?.response?.data?.detail || "Failed to load projects"));
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadTasks(selectedProjectId).catch(() => {});
      setAnalysis(null);
    }
  }, [selectedProjectId]);

  const handleRunAnalysis = async () => {
    if (!selectedProjectId) return;
    setLoadingAnalysis(true);
    setError(null);
    try {
      const result = await runAnalysis(selectedProjectId);
      setAnalysis(result);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Analysis failed. Add at least one task first.");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const statusChartData = analysis
    ? Object.entries(analysis.task_status_summary).map(([status, count]) => ({ status, count }))
    : [];

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="font-bold text-slate-800">Agentic AI Project Management & Risk Monitoring</h1>
            <p className="text-xs text-slate-500">Multi-agent risk analysis, dependency tracking & prioritization</p>
          </div>
          <button onClick={logout} className="text-sm text-slate-500 hover:text-slate-800">Sign out</button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Project selector */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedProjectId || ""}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white"
          >
            <option value="" disabled>Select a project…</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button
            onClick={() => setShowNewProject(true)}
            className="text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white hover:bg-slate-50"
          >
            + New Project
          </button>
          {selectedProjectId && (
            <button
              onClick={() => setShowNewTask(true)}
              className="text-sm px-3 py-2 rounded-lg border border-slate-300 bg-white hover:bg-slate-50"
            >
              + New Task
            </button>
          )}
          {selectedProjectId && (
            <button
              onClick={handleRunAnalysis}
              disabled={loadingAnalysis}
              className="ml-auto text-sm px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-medium disabled:opacity-60"
            >
              {loadingAnalysis ? "Running agents…" : "Run Risk Analysis"}
            </button>
          )}
        </div>

        {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-2">{error}</div>}

        {showNewProject && (
          <NewProjectForm
            onClose={() => setShowNewProject(false)}
            onCreated={async (p) => {
              await loadProjects();
              setSelectedProjectId(p.id);
              setShowNewProject(false);
            }}
          />
        )}

        {showNewTask && selectedProjectId && (
          <NewTaskForm
            projectId={selectedProjectId}
            existingTasks={tasks}
            onClose={() => setShowNewTask(false)}
            onCreated={async () => {
              await loadTasks(selectedProjectId);
              setShowNewTask(false);
            }}
          />
        )}

        {selectedProject && (
          <p className="text-sm text-slate-500">
            {selectedProject.description} · Target delivery:{" "}
            <span className="font-medium text-slate-700">{selectedProject.target_end_date}</span>
          </p>
        )}

        {/* Task board */}
        <Card title="Tasks" subtitle="Task status, deadlines, and dependencies">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-4">Task</th>
                  <th className="py-2 pr-4">Due</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Depends On</th>
                  <th className="py-2 pr-4">Assignee</th>
                  <th className="py-2 pr-4"></th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((t) => (
                  <tr key={t.id} className="border-b border-slate-100 last:border-0">
                    <td className="py-2 pr-4 font-medium text-slate-800">{t.name}</td>
                    <td className="py-2 pr-4 text-slate-600">{t.due_date}</td>
                    <td className="py-2 pr-4">
                      <select
                        value={t.status}
                        onChange={async (e) => {
                          await updateTask(selectedProjectId!, t.id, { status: e.target.value as TaskStatus });
                          await loadTasks(selectedProjectId!);
                        }}
                        className="text-xs rounded-md border border-slate-300 px-2 py-1 bg-white"
                      >
                        {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                      </select>
                      {t.is_delayed && <span className="ml-2"><Badge text="Overdue" color="red" /></span>}
                    </td>
                    <td className="py-2 pr-4 text-slate-600">{t.depends_on.join(", ") || "—"}</td>
                    <td className="py-2 pr-4 text-slate-600">{t.assignee || "Unassigned"}</td>
                    <td className="py-2 pr-4">
                      <button
                        onClick={async () => {
                          await deleteTask(selectedProjectId!, t.id);
                          await loadTasks(selectedProjectId!);
                        }}
                        className="text-xs text-red-500 hover:underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {tasks.length === 0 && (
                  <tr><td colSpan={6} className="py-6 text-center text-slate-400">No tasks yet. Add one to get started.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {selectedProject && (
          <RAGAssistant
            projectId={selectedProject.id}
            projectName={selectedProject.name}
          />
        )}

        {analysis && (
          <>
            <HealthBanner health={analysis.project_health} explanation={analysis.health_explanation} usedLlm={analysis.used_llm} />


            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card title="Task Status Breakdown" className="lg:col-span-1">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={statusChartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="status" tick={{ fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={50} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#4f6df5" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              <Card title="Upcoming Deadlines" subtitle="Due within 7 days" className="lg:col-span-1">
                <ul className="space-y-2">
                  {analysis.upcoming_deadlines.length === 0 && <p className="text-sm text-slate-400">None</p>}
                  {analysis.upcoming_deadlines.map((d, i) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span className="text-slate-700">{d.task_name}</span>
                      <span className="text-slate-500">{d.due_date}</span>
                    </li>
                  ))}
                </ul>
              </Card>

              <Card title="Delayed Tasks" className="lg:col-span-1">
                <ul className="space-y-2">
                  {analysis.delayed_tasks.length === 0 && <p className="text-sm text-slate-400">No delayed tasks</p>}
                  {analysis.delayed_tasks.map((d, i) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span className="text-slate-700">{d.task_name}</span>
                      <Badge text={`${d.overdue_days}d overdue`} color="red" />
                    </li>
                  ))}
                </ul>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card title="Dependencies & Downstream Impact" subtitle="What breaks if a task slips">
                <ul className="space-y-3">
                  {analysis.dependency_graph.map((d, i) => (
                    <li key={i} className="text-sm border border-slate-100 rounded-lg p-3">
                      <p className="font-medium text-slate-800">{d.task} <span className="text-slate-400 font-normal">depends on</span> {d.depends_on.join(", ")}</p>
                      <p className="text-slate-500 mt-1">Status: <Badge text={d.status} color={statusColor(d.status)} /></p>
                      {d.downstream_impact.length > 0 && (
                        <p className="text-amber-700 mt-1">⚠ Downstream impact if delayed: {d.downstream_impact.join(", ")}</p>
                      )}
                    </li>
                  ))}
                  {analysis.dependency_graph.length === 0 && <p className="text-sm text-slate-400">No dependencies declared</p>}
                </ul>
              </Card>

              <Card title="Critical Blockers">
                <ul className="space-y-3">
                  {analysis.critical_blockers.length === 0 && <p className="text-sm text-slate-400">No active blockers</p>}
                  {analysis.critical_blockers.map((b, i) => (
                    <li key={i} className="text-sm border border-red-100 bg-red-50 rounded-lg p-3">
                      <p className="font-medium text-red-800">{b.task_name}</p>
                      <p className="text-red-600">{b.reason}</p>
                      {b.downstream_impact.length > 0 && (
                        <p className="text-red-500 mt-1">Impacts: {b.downstream_impact.join(", ")}</p>
                      )}
                    </li>
                  ))}
                </ul>
              </Card>
            </div>

            <Card title="Identified Risks" subtitle="Every risk is explainable via evidence drawn from your project data">
              <ul className="space-y-3">
                {analysis.risks.map((r) => (
                  <li key={r.id} className="border border-slate-100 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge text={r.severity} color={severityColor(r.severity)} />
                      <Badge text={r.type} color="gray" />
                      {r.task_name && <span className="text-sm font-medium text-slate-800">{r.task_name}</span>}
                    </div>
                    <p className="text-sm text-slate-700">{r.description}</p>
                    <details className="mt-2">
                      <summary className="text-xs text-brand-600 cursor-pointer">Why? (evidence)</summary>
                      <ul className="mt-1 text-xs text-slate-500 list-disc list-inside space-y-0.5">
                        {r.evidence.map((e, i) => <li key={i}>{e}</li>)}
                      </ul>
                    </details>
                  </li>
                ))}
                {analysis.risks.length === 0 && <p className="text-sm text-slate-400">No risks detected</p>}
              </ul>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card title="Priority Recommendations" subtitle="Tasks ranked by urgency">
                <ul className="space-y-3">
                  {analysis.priorities.map((p) => (
                    <li key={p.task_id} className="border border-slate-100 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-slate-800 text-sm">{p.task_name}</span>
                        <Badge text={`${p.priority_level} (${p.priority_score})`} color={severityColor(p.priority_level === "Urgent" ? "Critical" : p.priority_level)} />
                      </div>
                      <p className="text-xs text-slate-500 mt-1">{p.reason}</p>
                    </li>
                  ))}
                  {analysis.priorities.length === 0 && <p className="text-sm text-slate-400">No open tasks</p>}
                </ul>
              </Card>

              <Card title="Next Actions">
                <ul className="space-y-3">
                  {analysis.next_actions.map((a, i) => (
                    <li key={i} className="border border-slate-100 rounded-lg p-3 text-sm">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge text={a.urgency} color={severityColor(a.urgency)} />
                        <span className="text-slate-500 text-xs">{a.owner}</span>
                      </div>
                      <p className="text-slate-700">{a.action}</p>
                    </li>
                  ))}
                  {analysis.next_actions.length === 0 && <p className="text-sm text-slate-400">No urgent actions</p>}
                </ul>
              </Card>
            </div>

            <Card title="Weekly Project Summary">
              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{analysis.weekly_summary}</p>
              <p className="text-xs text-slate-400 mt-3">Generated {new Date(analysis.generated_at).toLocaleString()}</p>
            </Card>
          </>
        )}
      </main>
    </div>
  );
};

const NewProjectForm: React.FC<{ onClose: () => void; onCreated: (p: Project) => void }> = ({ onClose, onCreated }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const p = await createProject({ name, description, start_date: startDate, target_end_date: endDate });
      onCreated(p);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card title="New Project">
      <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <input required placeholder="Project name" value={name} onChange={(e) => setName(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" />
        <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" />
        <label className="text-xs text-slate-500">Start date
          <input required type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm mt-1" />
        </label>
        <label className="text-xs text-slate-500">Target end date
          <input required type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm mt-1" />
        </label>
        <div className="md:col-span-2 flex gap-2 justify-end">
          <button type="button" onClick={onClose} className="text-sm px-3 py-2 rounded-lg border border-slate-300">Cancel</button>
          <button type="submit" disabled={busy} className="text-sm px-3 py-2 rounded-lg bg-brand-600 text-white disabled:opacity-60">
            {busy ? "Creating…" : "Create Project"}
          </button>
        </div>
      </form>
    </Card>
  );
};

const NewTaskForm: React.FC<{
  projectId: string;
  existingTasks: Task[];
  onClose: () => void;
  onCreated: () => void;
}> = ({ projectId, existingTasks, onClose, onCreated }) => {
  const [name, setName] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [status, setStatus] = useState<TaskStatus>("Not Started");
  const [assignee, setAssignee] = useState("");
  const [dependsOn, setDependsOn] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await createTask(projectId, { name, due_date: dueDate, status, assignee, depends_on: dependsOn });
      onCreated();
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card title="New Task">
      <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <input required placeholder="Task name" value={name} onChange={(e) => setName(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" />
        <label className="text-xs text-slate-500">Due date
          <input required type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm mt-1" />
        </label>
        <label className="text-xs text-slate-500">Status
          <select value={status} onChange={(e) => setStatus(e.target.value as TaskStatus)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm mt-1">
            {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <input placeholder="Assignee (optional)" value={assignee} onChange={(e) => setAssignee(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2" />
        <div className="md:col-span-2">
          <p className="text-xs text-slate-500 mb-1">Depends on (select existing tasks)</p>
          <select multiple value={dependsOn} onChange={(e) => setDependsOn(Array.from(e.target.selectedOptions, o => o.value))}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm h-24">
            {existingTasks.map((t) => <option key={t.id} value={t.name}>{t.name}</option>)}
          </select>
        </div>
        <div className="md:col-span-2 flex gap-2 justify-end">
          <button type="button" onClick={onClose} className="text-sm px-3 py-2 rounded-lg border border-slate-300">Cancel</button>
          <button type="submit" disabled={busy} className="text-sm px-3 py-2 rounded-lg bg-brand-600 text-white disabled:opacity-60">
            {busy ? "Creating…" : "Create Task"}
          </button>
        </div>
      </form>
    </Card>
  );
};

export default DashboardPage;
