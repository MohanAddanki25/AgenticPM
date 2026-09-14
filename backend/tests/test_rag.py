"""
Tests for RAG (Retrieval-Augmented Generation) services and API endpoints.
Uses mongomock-motor for in-memory isolation.
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import connect_to_mongo
from app.core.redis_client import connect_to_redis
from app.main import app
from app.services.rag_service import (
    _deterministic_hash_vector,
    chunk_text,
    cosine_similarity,
    generate_embedding,
)


def test_chunk_text_boundaries():
    short_text = "This is a short specification."
    chunks = chunk_text(short_text, chunk_size=100)
    assert len(chunks) == 1
    assert chunks[0] == short_text

    long_para = "Word " * 200  # 1000 characters
    chunks = chunk_text(long_para, chunk_size=300, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 350 for c in chunks)


def test_vector_similarity_computation():
    vec_a = _deterministic_hash_vector("Database performance and migration")
    vec_b = _deterministic_hash_vector("Database performance tuning and indexing")
    vec_c = _deterministic_hash_vector("Frontend user interface styling")

    sim_ab = cosine_similarity(vec_a, vec_b)
    sim_ac = cosine_similarity(vec_a, vec_c)

    # Identical vector similarity is ~1.0
    assert cosine_similarity(vec_a, vec_a) > 0.99
    # Closely related topics have higher similarity than unrelated topics
    assert sim_ab > sim_ac


import uuid


@pytest.mark.asyncio
async def test_rag_end_to_end_flow():
    await connect_to_mongo()
    await connect_to_redis()
    test_email = f"rag_{uuid.uuid4().hex[:6]}@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register & Login
        reg = await client.post("/api/auth/register", json={
            "name": "RAG Tester",
            "email": test_email,
            "password": "secretpassword",
        })
        assert reg.status_code == 201

        login = await client.post("/api/auth/login", json={
            "email": test_email,
            "password": "secretpassword",
        })

        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Project
        proj = await client.post("/api/projects", json={
            "name": "Cloud Migration",
            "description": "Migrating database to cloud cluster",
            "start_date": "2026-09-01",
            "target_end_date": "2026-09-30",
        }, headers=headers)
        assert proj.status_code == 201
        project_id = proj.json()["id"]

        # 3. Add Document
        doc_payload = {
            "title": "Cloud Migration Architecture",
            "content": (
                "The database migration must execute zero-downtime replication. "
                "Primary replica failover must occur on weekend maintenance window. "
                "The target database SLA requires 99.99% availability."
            ),
            "doc_type": "spec",
        }
        doc_res = await client.post(f"/api/projects/{project_id}/documents", json=doc_payload, headers=headers)
        assert doc_res.status_code == 201
        doc_data = doc_res.json()
        assert doc_data["title"] == "Cloud Migration Architecture"
        assert doc_data["chunk_count"] >= 1
        doc_id = doc_data["id"]

        # 4. List Documents
        list_res = await client.get(f"/api/projects/{project_id}/documents", headers=headers)
        assert list_res.status_code == 200
        docs = list_res.json()
        assert len(docs) >= 1

        # 5. Add Tasks
        await client.post(f"/api/projects/{project_id}/tasks", json={
            "name": "Data Replication Setup",
            "due_date": "2026-09-15",
            "status": "In Progress",
            "assignee": "DevOps Lead",
            "depends_on": [],
            "resource_notes": "Awaiting network security clearance",
        }, headers=headers)

        # 6. Reindex RAG
        reindex_res = await client.post(f"/api/projects/{project_id}/rag/reindex", headers=headers)
        assert reindex_res.status_code == 200
        reindex_data = reindex_res.json()
        assert reindex_data["indexed_documents"] >= 1
        assert reindex_data["indexed_tasks"] >= 1

        # 7. Query RAG
        q_res = await client.post(f"/api/projects/{project_id}/rag/query", json={
            "query": "What are the SLA requirements and database migration guidelines?",
            "top_k": 3,
        }, headers=headers)
        assert q_res.status_code == 200
        q_data = q_res.json()
        assert q_data["answer"]
        assert len(q_data["sources"]) >= 1
        assert any("Cloud Migration" in s["title"] or "Data Replication" in s["title"] for s in q_data["sources"])

        # 8. Delete Document
        del_res = await client.delete(f"/api/projects/{project_id}/documents/{doc_id}", headers=headers)
        assert del_res.status_code == 204
