"""
End-to-end API tests using FastAPI's TestClient. The database layer falls
back to in-memory mongomock automatically (see app/core/database.py), so
these tests run without any external MongoDB/Redis dependency.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import connect_to_mongo
from app.core.redis_client import connect_to_redis


import uuid


@pytest.mark.asyncio
async def test_register_login_and_full_analysis_flow():
    await connect_to_mongo()
    await connect_to_redis()
    test_email = f"flow_{uuid.uuid4().hex[:6]}@example.com"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # register
        r = await client.post("/api/auth/register", json={
            "name": "Test PM", "email": test_email, "password": "secret123",
        })
        assert r.status_code == 201

        # login
        r = await client.post("/api/auth/login", json={"email": test_email, "password": "secret123"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}


        # create project
        r = await client.post("/api/projects", json={
            "name": "Checkout Revamp", "description": "d",
            "start_date": "2026-09-01", "target_end_date": "2026-09-17",
        }, headers=headers)
        assert r.status_code == 201
        project_id = r.json()["id"]

        # create tasks reproducing the spec scenario
        tasks = [
            {"name": "Backend API", "due_date": "2026-09-10", "status": "Completed", "depends_on": []},
            {"name": "Frontend integration", "due_date": "2026-09-12", "status": "In Progress", "depends_on": ["Backend API"]},
            {"name": "Testing", "due_date": "2026-09-13", "status": "Not Started", "depends_on": ["Frontend integration"]},
        ]
        for t in tasks:
            r = await client.post(f"/api/projects/{project_id}/tasks", json=t, headers=headers)
            assert r.status_code == 201

        # run analysis
        r = await client.post(f"/api/projects/{project_id}/analyze", headers=headers)
        assert r.status_code == 200
        result = r.json()

        assert result["project_health"] in ("On Track", "At Risk", "Delayed")
        dep_risks = [x for x in result["risks"] if x["type"] == "dependency"]
        assert len(dep_risks) >= 1
        assert "Frontend integration" in dep_risks[0]["description"]
        assert len(result["priorities"]) >= 1
        assert result["weekly_summary"]
