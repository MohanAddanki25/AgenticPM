import React, { useEffect, useState } from "react";
import {
  createDocument,
  deleteDocument,
  fetchDocuments,
  queryRAG,
  reindexRAG,
} from "../api/client";
import type { ProjectDocument, RAGQueryResponse, RAGSource } from "../types";
import { Badge, Card } from "./ui";

interface RAGAssistantProps {
  projectId: string;
  projectName: string;
}

const SUGGESTED_QUERIES = [
  "What are our critical dependency risks and what causes them?",
  "What does the specification say about SLAs and deadlines?",
  "Which tasks are delayed or at risk, and who is assigned?",
  "Summarize key recommendations and next actions for delivery.",
];

export const RAGAssistant: React.FC<RAGAssistantProps> = ({ projectId, projectName }) => {
  const [activeTab, setActiveTab] = useState<"qa" | "documents">("qa");
  const [query, setQuery] = useState("");
  const [loadingQuery, setLoadingQuery] = useState(false);
  const [ragResult, setRagResult] = useState<RAGQueryResponse | null>(null);
  const [showSources, setShowSources] = useState(true);

  // Documents state
  const [documents, setDocuments] = useState<ProjectDocument[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [showAddDoc, setShowAddDoc] = useState(false);
  const [docTitle, setDocTitle] = useState("");
  const [docType, setDocType] = useState<string>("spec");
  const [docContent, setDocContent] = useState("");
  const [savingDoc, setSavingDoc] = useState(false);

  // Sync state
  const [reindexing, setReindexing] = useState(false);
  const [reindexMsg, setReindexMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadDocs = async () => {
    setLoadingDocs(true);
    try {
      const docs = await fetchDocuments(projectId);
      setDocuments(docs);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to load project documents");
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadDocs();
      setRagResult(null);
      setError(null);
      setReindexMsg(null);
    }
  }, [projectId]);

  const handleQuery = async (queryText?: string) => {
    const q = (queryText || query).trim();
    if (!q) return;
    setLoadingQuery(true);
    setError(null);
    try {
      const res = await queryRAG(projectId, q);
      setRagResult(res);
      setQuery(q);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to execute RAG query");
    } finally {
      setLoadingQuery(false);
    }
  };

  const handleAddDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docTitle.trim() || !docContent.trim()) return;
    setSavingDoc(true);
    setError(null);
    try {
      await createDocument(projectId, {
        title: docTitle.trim(),
        doc_type: docType,
        content: docContent.trim(),
      });
      setDocTitle("");
      setDocContent("");
      setShowAddDoc(false);
      await loadDocs();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to save document");
    } finally {
      setSavingDoc(false);
    }
  };

  const handleDeleteDoc = async (docId: string) => {
    if (!window.confirm("Delete this document and its indexed vector chunks?")) return;
    try {
      await deleteDocument(projectId, docId);
      await loadDocs();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to delete document");
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setReindexMsg(null);
    try {
      const res = await reindexRAG(projectId);
      setReindexMsg(res.message);
      await loadDocs();
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Failed to reindex knowledge base");
    } finally {
      setReindexing(false);
    }
  };

  const sourceBadgeColor = (type: string): "blue" | "green" | "amber" | "gray" => {
    if (type === "document") return "blue";
    if (type === "task") return "amber";
    if (type === "analysis") return "green";
    return "gray";
  };

  return (
    <Card
      title="Project Knowledge & AI Assistant (RAG)"
      subtitle={`Semantic search & grounded Q&A across documents, tasks, and risk analyses for ${projectName}`}
      className="border-indigo-100 shadow-sm"
    >
      {/* Header controls & Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3 mb-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab("qa")}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              activeTab === "qa"
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Ask AI Assistant
          </button>
          <button
            onClick={() => setActiveTab("documents")}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center space-x-1 ${
              activeTab === "documents"
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            <span>Project Documents</span>
            <span className="ml-1 px-1.5 py-0.2 bg-white/20 rounded-full text-[10px]">
              {documents.length}
            </span>
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleReindex}
            disabled={reindexing}
            className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium flex items-center space-x-1 disabled:opacity-60"
            title="Sync latest tasks, docs and analysis into vector store"
          >
            <span>{reindexing ? "Syncing..." : "Sync Knowledge Base"}</span>
          </button>
        </div>
      </div>

      {reindexMsg && (
        <div className="mb-3 p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center justify-between">
          <span>{reindexMsg}</span>
          <button onClick={() => setReindexMsg(null)} className="text-emerald-600 font-bold ml-2">×</button>
        </div>
      )}

      {error && (
        <div className="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 font-bold ml-2">×</button>
        </div>
      )}

      {/* Tab 1: Q&A */}
      {activeTab === "qa" && (
        <div className="space-y-4">
          {/* Query Input */}
          <div className="relative">
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleQuery()}
                placeholder="Ask any question about project specifications, deadlines, or risks…"
                className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
              <button
                onClick={() => handleQuery()}
                disabled={loadingQuery || !query.trim()}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium text-xs rounded-xl shadow-sm transition whitespace-nowrap"
              >
                {loadingQuery ? "Thinking..." : "Ask AI"}
              </button>
            </div>
          </div>

          {/* Prompt chips */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] text-slate-400 mr-1 font-medium">Try asking:</span>
            {SUGGESTED_QUERIES.map((sq, i) => (
              <button
                key={i}
                onClick={() => handleQuery(sq)}
                className="text-[11px] px-2.5 py-1 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-600 rounded-full border border-slate-200 transition text-left"
              >
                {sq}
              </button>
            ))}
          </div>

          {/* Loading indicator */}
          {loadingQuery && (
            <div className="p-6 bg-slate-50 rounded-xl border border-slate-100 flex flex-col items-center justify-center space-y-2">
              <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs text-slate-500">Searching project vector knowledge & synthesizing grounded answer…</p>
            </div>
          )}

          {/* RAG Answer Display */}
          {ragResult && !loadingQuery && (
            <div className="bg-gradient-to-br from-indigo-50/40 via-white to-slate-50 border border-indigo-100 rounded-2xl p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-indigo-100/60 pb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-indigo-900">
                    AI Response
                  </span>
                  <Badge
                    text={ragResult.used_llm ? "Gemini Grounded" : "Deterministic Fallback"}
                    color={ragResult.used_llm ? "blue" : "gray"}
                  />
                </div>
                <span className="text-[10px] text-slate-400">
                  {new Date(ragResult.generated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>

              {/* Formatted answer */}
              <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
                {ragResult.answer}
              </div>

              {/* Sources Section */}
              {ragResult.sources.length > 0 && (
                <div className="pt-2 border-t border-slate-200/60">
                  <button
                    onClick={() => setShowSources(!showSources)}
                    className="text-xs font-semibold text-slate-600 hover:text-indigo-600 flex items-center space-x-1"
                  >
                    <span>{showSources ? "▼ Hide" : "▶ Show"} Grounded Sources & Citations ({ragResult.sources.length})</span>
                  </button>

                  {showSources && (
                    <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                      {ragResult.sources.map((s: RAGSource, idx: number) => (
                        <div
                          key={idx}
                          className="bg-white p-2.5 rounded-lg border border-slate-200 text-xs space-y-1 shadow-2xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-slate-700 truncate max-w-[200px]">
                              {s.title}
                            </span>
                            <div className="flex items-center space-x-1">
                              <Badge text={s.source_type} color={sourceBadgeColor(s.source_type)} />
                              <span className="text-[10px] text-slate-400">
                                {Math.round(s.score * 100)}% match
                              </span>
                            </div>
                          </div>
                          <p className="text-[11px] text-slate-500 line-clamp-3 bg-slate-50 p-1.5 rounded italic">
                            "{s.excerpt}"
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Documents */}
      {activeTab === "documents" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500">
              Project specifications, PRDs, and meeting notes indexed for semantic retrieval.
            </p>
            <button
              onClick={() => setShowAddDoc(!showAddDoc)}
              className="text-xs px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition"
            >
              {showAddDoc ? "Cancel" : "+ Add Document"}
            </button>
          </div>

          {/* Add document form */}
          {showAddDoc && (
            <form
              onSubmit={handleAddDocument}
              className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3"
            >
              <h4 className="text-xs font-bold text-slate-700 uppercase">Add Project Document</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="md:col-span-2">
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    Document Title
                  </label>
                  <input
                    type="text"
                    required
                    value={docTitle}
                    onChange={(e) => setDocTitle(e.target.value)}
                    placeholder="e.g. Checkout Revamp Architecture & SLA Specification"
                    className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-600 mb-1">
                    Document Type
                  </label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white"
                  >
                    <option value="spec">Technical Specification</option>
                    <option value="prd">Product Requirement (PRD)</option>
                    <option value="meeting_notes">Meeting Notes</option>
                    <option value="retrospective">Sprint Retrospective</option>
                    <option value="risk_log">Risk Register / Policy</option>
                    <option value="general">General Documentation</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">
                  Document Content (Markdown or plain text)
                </label>
                <textarea
                  required
                  rows={5}
                  value={docContent}
                  onChange={(e) => setDocContent(e.target.value)}
                  placeholder="Paste specification, SLA requirements, architecture contracts, or team decisions here..."
                  className="w-full rounded-lg border border-slate-300 p-2.5 text-xs bg-white font-mono"
                />
              </div>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddDoc(false)}
                  className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingDoc}
                  className="text-xs px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium disabled:opacity-60"
                >
                  {savingDoc ? "Chunking & Embedding..." : "Index Document"}
                </button>
              </div>
            </form>
          )}

          {/* Document list */}
          {loadingDocs ? (
            <p className="text-xs text-slate-400 py-4 text-center">Loading documents...</p>
          ) : documents.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200">
              <p className="text-xs text-slate-500 mb-1">No documents uploaded yet for this project.</p>
              <p className="text-[11px] text-slate-400">
                Upload architecture specs, PRDs, or guidelines to ground the AI assistant in your team's knowledge.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((d) => (
                <div
                  key={d.id}
                  className="p-3 bg-white rounded-xl border border-slate-200 flex items-start justify-between hover:border-indigo-200 transition shadow-2xs"
                >
                  <div className="space-y-1 pr-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-slate-800">{d.title}</span>
                      <Badge text={d.doc_type} color="blue" />
                      <span className="text-[10px] text-slate-400">
                        {d.chunk_count} vector chunk{d.chunk_count === 1 ? "" : "s"}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 line-clamp-2">{d.content}</p>
                    <span className="text-[10px] text-slate-400">
                      Uploaded {new Date(d.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteDoc(d.id)}
                    className="text-xs text-slate-400 hover:text-red-600 px-2 py-1 rounded transition"
                    title="Delete document"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default RAGAssistant;
