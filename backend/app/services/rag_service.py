"""
RAG (Retrieval-Augmented Generation) Service for Agentic PM System.

Provides:
- Semantic chunking of project documents (PRDs, specs, meeting notes).
- Automatic indexing of tasks (status, due date, dependencies, blockers) and analysis reports.
- Dual-mode embeddings:
    1. Gemini embeddings (`models/gemini-embedding-001`) via LangChain when GOOGLE_API_KEY is present.
    2. Deterministic term-frequency hash vectorizer fallback for 100% offline/mock test reliability.
- Cosine similarity vector search over project-scoped knowledge.
- Factual, grounded question-answering with structured source citations.
"""
import logging
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import RAGQueryResponse, RAGReindexResponse, RAGSource
from app.services.llm import extract_text_content, get_llm, is_llm_available

logger = logging.getLogger("rag_service")

_embeddings_client = None
_embeddings_init_attempted = False
_using_fallback_embeddings = False


# ---------------- Embedding Layer ----------------

def _init_embeddings():
    global _embeddings_client, _embeddings_init_attempted, _using_fallback_embeddings
    if _embeddings_init_attempted:
        return _embeddings_client
    _embeddings_init_attempted = True

    if not settings.GOOGLE_API_KEY:
        logger.info("GOOGLE_API_KEY not set - using deterministic vectorizer for RAG.")
        _using_fallback_embeddings = True
        _embeddings_client = None
        return None

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        client = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        # Test probe
        client.embed_query("probe")
        _embeddings_client = client
        _using_fallback_embeddings = False
        logger.info("Gemini Embeddings initialized (%s).", settings.GEMINI_EMBEDDING_MODEL)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Failed to initialize Gemini Embeddings (%s). Falling back to deterministic vectorizer.",
            exc,
        )
        _embeddings_client = None
        _using_fallback_embeddings = True
    return _embeddings_client


def _deterministic_hash_vector(text: str, dim: int = 256) -> List[float]:
    """Generates a normalized frequency hash vector in pure Python.
    Guarantees 100% deterministic, offline vector similarity matching without external dependencies."""
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return [0.0] * dim

    vec = [0.0] * dim
    for tok in tokens:
        # FNV-1a inspired hash into bucket
        h = 2166136261
        for char in tok:
            h = ((h ^ ord(char)) * 16777619) & 0xFFFFFFFF
        bucket = h % dim
        vec[bucket] += 1.0

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [round(x / norm, 6) for x in vec]
    return vec


def generate_embedding(text: str) -> List[float]:
    """Generate vector embedding for text using Gemini if available, else deterministic vectorizer."""
    emb_client = _init_embeddings()
    if emb_client is not None and not _using_fallback_embeddings:
        try:
            return emb_client.embed_query(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini embed_query failed: %s; falling back to hash vector.", exc)
    return _deterministic_hash_vector(text)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot / (norm_a * norm_b))


# ---------------- Text Chunking ----------------

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 80) -> List[str]:
    """Splits a document text into overlapping chunks respecting line/paragraph boundaries."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current) + len(p) + 2 <= chunk_size:
            current = f"{current}\n\n{p}".strip()
        else:
            if current:
                chunks.append(current)
            # If a single paragraph is longer than chunk_size, split by sentences/window
            if len(p) > chunk_size:
                step = chunk_size - chunk_overlap
                for i in range(0, len(p), step):
                    window = p[i : i + chunk_size].strip()
                    if window:
                        chunks.append(window)
                current = ""
            else:
                current = p

    if current and current not in chunks:
        chunks.append(current)

    return chunks if chunks else [text]


def _resolve_db(db=None):
    return get_db() if db is None else db


# ---------------- Indexing Functions ----------------

async def index_document(
    project_id: str,
    doc_id: str,
    title: str,
    content: str,
    doc_type: str,
    db=None,
) -> int:
    """Chunks and indexes a project document into rag_chunks."""
    db = _resolve_db(db)
    await db.rag_chunks.delete_many({"source_id": doc_id})

    chunks = chunk_text(content)
    now = datetime.now(timezone.utc)
    docs_to_insert = []

    for idx, chunk in enumerate(chunks):
        embedding = generate_embedding(f"Title: {title}\nContent: {chunk}")
        docs_to_insert.append({
            "project_id": project_id,
            "source_id": doc_id,
            "source_type": "document",
            "source_title": title,
            "content": chunk,
            "embedding": embedding,
            "metadata": {
                "doc_type": doc_type,
                "chunk_index": idx,
                "total_chunks": len(chunks),
            },
            "created_at": now,
        })

    if docs_to_insert:
        await db.rag_chunks.insert_many(docs_to_insert)
    return len(docs_to_insert)


async def index_task(project_id: str, task: dict, db=None) -> None:
    """Indexes a single task as structured PM knowledge into rag_chunks."""
    db = _resolve_db(db)
    task_id = str(task.get("id") or task.get("_id"))
    await db.rag_chunks.delete_many({"source_id": task_id})

    deps = task.get("depends_on", [])
    deps_str = ", ".join(deps) if deps else "None"
    notes = task.get("resource_notes") or "None"
    desc = task.get("description") or "None"
    assignee = task.get("assignee") or "Unassigned"

    task_content = (
        f"Task: {task['name']}\n"
        f"Status: {task.get('status', 'Not Started')}\n"
        f"Due Date: {task.get('due_date')}\n"
        f"Assignee: {assignee}\n"
        f"Dependencies: {deps_str}\n"
        f"Resource Notes: {notes}\n"
        f"Description: {desc}"
    )

    embedding = generate_embedding(task_content)
    await db.rag_chunks.insert_one({
        "project_id": project_id,
        "source_id": task_id,
        "source_type": "task",
        "source_title": f"Task: {task['name']}",
        "content": task_content,
        "embedding": embedding,
        "metadata": {
            "task_id": task_id,
            "status": task.get("status"),
            "due_date": str(task.get("due_date")),
            "assignee": assignee,
        },
        "created_at": datetime.now(timezone.utc),
    })


async def index_analysis(project_id: str, analysis: dict, db=None) -> None:
    """Indexes the latest multi-agent risk & priority analysis report."""
    db = _resolve_db(db)
    analysis_id = str(analysis.get("run_id", "latest_analysis"))
    await db.rag_chunks.delete_many({"source_id": analysis_id})

    risks = analysis.get("risks", [])
    priorities = analysis.get("priorities", [])
    health = analysis.get("project_health", "Unknown")
    summary = analysis.get("weekly_summary", "")

    content = (
        f"Project Health: {health}\n"
        f"Health Explanation: {analysis.get('health_explanation', '')}\n"
        f"Weekly Summary: {summary}\n"
        f"Risks Detected ({len(risks)}):\n"
        + "\n".join(
            f"- [{r.get('severity')}] {r.get('type')}: {r.get('description')}"
            for r in risks[:6]
        )
        + "\nPriority Recommendations:\n"
        + "\n".join(
            f"- {p.get('task_name')} ({p.get('priority_level')}): {p.get('reason')}"
            for p in priorities[:5]
        )
    )

    embedding = generate_embedding(content)
    await db.rag_chunks.insert_one({
        "project_id": project_id,
        "source_id": analysis_id,
        "source_type": "analysis",
        "source_title": f"Agent Analysis ({health})",
        "content": content,
        "embedding": embedding,
        "metadata": {
            "health": health,
            "risk_count": len(risks),
        },
        "created_at": datetime.now(timezone.utc),
    })


async def delete_source_chunks(source_id: str, db=None) -> None:
    db = _resolve_db(db)
    await db.rag_chunks.delete_many({"source_id": source_id})


async def delete_project_rag_data(project_id: str, db=None) -> None:
    db = _resolve_db(db)
    await db.rag_documents.delete_many({"project_id": project_id})
    await db.rag_chunks.delete_many({"project_id": project_id})


async def reindex_project(project_id: str, db=None) -> RAGReindexResponse:
    """Reindexes all documents, tasks, and recent analysis for a given project."""
    db = _resolve_db(db)
    await db.rag_chunks.delete_many({"project_id": project_id})

    total_chunks = 0

    # 1. Documents
    doc_count = 0
    async for d in db.rag_documents.find({"project_id": project_id}):
        doc_id = str(d["_id"])
        c_count = await index_document(
            project_id=project_id,
            doc_id=doc_id,
            title=d["title"],
            content=d["content"],
            doc_type=d.get("doc_type", "general"),
            db=db,
        )
        await db.rag_documents.update_one(
            {"_id": d["_id"]},
            {"$set": {"chunk_count": c_count}},
        )
        total_chunks += c_count
        doc_count += 1

    # 2. Tasks
    task_count = 0
    async for t in db.tasks.find({"project_id": project_id}):
        t["id"] = str(t["_id"])
        await index_task(project_id, t, db=db)
        total_chunks += 1
        task_count += 1

    # 3. Latest Analysis
    analysis_count = 0
    latest_analysis = await db.analysis_history.find_one(
        {"project_id": project_id},
        sort=[("created_at", -1)],
    )
    if latest_analysis and "result" in latest_analysis:
        await index_analysis(project_id, latest_analysis["result"], db=db)
        total_chunks += 1
        analysis_count += 1

    return RAGReindexResponse(
        indexed_documents=doc_count,
        indexed_tasks=task_count,
        indexed_analyses=analysis_count,
        total_chunks=total_chunks,
        message=f"Successfully indexed {doc_count} document(s), {task_count} task(s), and {analysis_count} analysis report(s).",
    )


# ---------------- Retrieval & Search ----------------

async def search_project_context(
    project_id: str,
    query: str,
    top_k: int = 4,
    db=None,
) -> List[Tuple[dict, float]]:
    """Performs cosine-similarity vector retrieval over all indexed project knowledge."""
    db = _resolve_db(db)
    query_vec = generate_embedding(query)

    chunks = []
    async for c in db.rag_chunks.find({"project_id": project_id}):
        chunks.append(c)

    if not chunks:
        return []

    scored: List[Tuple[dict, float]] = []
    for c in chunks:
        chunk_vec = c.get("embedding", [])
        score = cosine_similarity(query_vec, chunk_vec)
        scored.append((c, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# ---------------- Grounded RAG Query Answering ----------------

async def answer_rag_query(
    project_id: str,
    query: str,
    top_k: int = 4,
    db=None,
) -> RAGQueryResponse:
    """Answers a project question strictly grounded in retrieved knowledge with source citations."""
    db = _resolve_db(db)
    top_results = await search_project_context(project_id, query, top_k=top_k, db=db)


    now = datetime.now(timezone.utc)

    if not top_results:
        return RAGQueryResponse(
            query=query,
            answer=(
                "No relevant documents, tasks, or analysis reports were found for this project yet. "
                "Add project documents or tasks to enable grounded AI Q&A."
            ),
            sources=[],
            used_llm=False,
            generated_at=now,
        )

    sources: List[RAGSource] = []
    context_blocks: List[str] = []

    for chunk_doc, score in top_results:
        source_title = chunk_doc.get("source_title", "Untitled Source")
        source_type = chunk_doc.get("source_type", "document")
        content = chunk_doc.get("content", "")
        excerpt = content[:200] + ("…" if len(content) > 200 else "")

        sources.append(
            RAGSource(
                source_id=str(chunk_doc.get("source_id", "")),
                source_type=source_type,
                title=source_title,
                excerpt=excerpt,
                score=round(score, 4),
                metadata=chunk_doc.get("metadata", {}),
            )
        )
        context_blocks.append(
            f"[{source_type.upper()}: {source_title}]\n{content}"
        )

    formatted_context = "\n\n---\n\n".join(context_blocks)

    system_instruction = (
        "You are an expert Project Management AI Assistant. "
        "Your role is to answer user inquiries strictly grounded in the provided project context "
        "(documents, tasks, status, and analysis reports).\n\n"
        "Guidelines:\n"
        "1. Base your answer ONLY on the provided context.\n"
        "2. Do NOT invent or assume facts, deadlines, dependencies, or names not in the context.\n"
        "3. Cite the relevant source title or task name in your answer when referencing specific information.\n"
        "4. If the context does not contain enough information to answer completely, acknowledge what is known and state what is missing."
    )

    prompt = (
        f"CONTEXT INFORMATION:\n{formatted_context}\n\n"
        f"USER QUESTION: {query}\n\n"
        "Provide a concise, direct, professional answer grounded in the facts above:"
    )

    llm = get_llm()
    used_llm = False
    answer_text = ""

    if llm is not None:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=system_instruction),
                HumanMessage(content=prompt),
            ]
            resp = llm.invoke(messages)
            raw = resp.content if hasattr(resp, "content") else resp
            text = extract_text_content(raw).strip()
            if text:
                answer_text = text
                used_llm = True
        except Exception as exc:  # noqa: BLE001
            logger.warning("RAG LLM invocation failed (%s); using deterministic summary.", exc)

    if not answer_text:
        # Deterministic grounded fallback synthesis
        source_bullets = "\n".join(
            f"• {s.title} ({s.source_type.title()}): {s.excerpt.strip()}" for s in sources
        )
        answer_text = (
            f"Based on retrieved project knowledge for '{query}':\n\n"
            f"{source_bullets}\n\n"
            "(Synthesized from matched project records and documents.)"
        )

    return RAGQueryResponse(
        query=query,
        answer=answer_text,
        sources=sources,
        used_llm=used_llm,
        generated_at=now,
    )
