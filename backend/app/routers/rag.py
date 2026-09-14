"""
Router for Project Documents and RAG (Retrieval-Augmented Generation) endpoints.
"""
from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import (
    DocumentCreate,
    DocumentOut,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGReindexResponse,
)
from app.services.rag_service import (
    answer_rag_query,
    delete_source_chunks,
    index_document,
    reindex_project,
)

router = APIRouter(prefix="/api/projects/{project_id}", tags=["rag", "documents"])


async def _verify_project(project_id: str, db, user: dict):
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _serialize_doc(d: dict) -> dict:
    d["id"] = str(d.pop("_id"))
    return d


# ---------------- Document Endpoints ----------------

@router.post("/documents", response_model=DocumentOut, status_code=201)
async def create_document(
    project_id: str,
    payload: DocumentCreate,
    user: dict = Depends(get_current_user),
):
    """Uploads or registers a project document (PRD, architecture spec, meeting notes)
    and automatically chunks and indexes it into the RAG vector store."""
    db = get_db()
    await _verify_project(project_id, db, user)

    now = datetime.now(timezone.utc)
    doc_data = {
        "project_id": project_id,
        "title": payload.title.strip(),
        "content": payload.content.strip(),
        "doc_type": payload.doc_type,
        "metadata": payload.metadata,
        "chunk_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.rag_documents.insert_one(doc_data)
    doc_id = str(result.inserted_id)

    # Index into RAG vector collection
    chunk_count = await index_document(
        project_id=project_id,
        doc_id=doc_id,
        title=doc_data["title"],
        content=doc_data["content"],
        doc_type=doc_data["doc_type"],
        db=db,
    )

    await db.rag_documents.update_one(
        {"_id": result.inserted_id},
        {"$set": {"chunk_count": chunk_count}},
    )
    doc_data["chunk_count"] = chunk_count

    return DocumentOut(**_serialize_doc(doc_data))


@router.get("/documents", response_model=List[DocumentOut])
async def list_documents(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """Lists all knowledge documents associated with a project."""
    db = get_db()
    await _verify_project(project_id, db, user)

    cursor = db.rag_documents.find({"project_id": project_id}).sort("created_at", -1)
    documents = [DocumentOut(**_serialize_doc(d)) async for d in cursor]
    return documents


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    project_id: str,
    document_id: str,
    user: dict = Depends(get_current_user),
):
    """Deletes a document and its indexed vector chunks."""
    db = get_db()
    await _verify_project(project_id, db, user)

    res = await db.rag_documents.delete_one({"_id": ObjectId(document_id), "project_id": project_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    await delete_source_chunks(document_id, db=db)
    return None


# ---------------- RAG Query & Reindex Endpoints ----------------

@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag(
    project_id: str,
    payload: RAGQueryRequest,
    user: dict = Depends(get_current_user),
):
    """Answers a project question grounded in retrieved knowledge (documents, tasks, and risk reports)."""
    db = get_db()
    await _verify_project(project_id, db, user)

    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    response = await answer_rag_query(
        project_id=project_id,
        query=payload.query.strip(),
        top_k=max(1, min(payload.top_k, 10)),
        db=db,
    )
    return response


@router.post("/rag/reindex", response_model=RAGReindexResponse)
async def reindex_rag(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """Reindexes all documents, current tasks, and latest analysis results for the project."""
    db = get_db()
    await _verify_project(project_id, db, user)

    response = await reindex_project(project_id=project_id, db=db)
    return response
