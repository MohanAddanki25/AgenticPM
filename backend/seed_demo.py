"""
Seeds a demo user + project + the exact example scenario from the problem
statement, then runs the full multi-agent workflow and prints the result -
demonstrating end-to-end how a delay in "Frontend integration" propagates
through the dependency graph to threaten "Testing" and final delivery.

Run:
    python seed_demo.py
"""
import asyncio
import json
from datetime import date, datetime, timedelta, timezone

from app.agents.graph import run_analysis
from app.core.database import connect_to_mongo, get_db
from app.core.security import hash_password


async def main():
    await connect_to_mongo()
    db = get_db()

    # --- demo user ---
    email = "pm@example.com"
    existing = await db.users.find_one({"email": email})
    if not existing:
        result = await db.users.insert_one({
            "name": "Demo Project Manager",
            "email": email,
            "hashed_password": hash_password("password123"),
            "created_at": datetime.now(timezone.utc),
        })
        owner_id = str(result.inserted_id)
    else:
        owner_id = str(existing["_id"])

    today = date.today()

    # Dates chosen relative to "today" so the demo always shows live risk:
    # Backend API completed a few days ago; Frontend integration due
    # tomorrow but still In Progress; Testing due day-after depends on it.
    backend_due = today - timedelta(days=2)
    frontend_due = today + timedelta(days=1)
    testing_due = today + timedelta(days=2)

    project_doc = {
        "name": "E-Commerce Platform Revamp",
        "description": "Backend, frontend integration and QA for the new checkout flow.",
        "start_date": (today - timedelta(days=14)).isoformat(),
        "target_end_date": (today + timedelta(days=3)).isoformat(),
        "owner_id": owner_id,
        "created_at": datetime.now(timezone.utc),
    }
    project_result = await db.projects.insert_one(project_doc)
    project_id = str(project_result.inserted_id)

    tasks = [
        {
            "name": "Backend API",
            "description": "Core REST API for checkout and payments.",
            "due_date": backend_due.isoformat(),
            "status": "Completed",
            "assignee": "Asha (Backend)",
            "depends_on": [],
            "resource_notes": None,
            "project_id": project_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "name": "Frontend integration",
            "description": "Wire checkout UI to backend API.",
            "due_date": frontend_due.isoformat(),
            "status": "In Progress",
            "assignee": "Rahul (Frontend)",
            "depends_on": ["Backend API"],
            "resource_notes": None,
            "project_id": project_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        {
            "name": "Testing",
            "description": "End-to-end QA of checkout flow.",
            "due_date": testing_due.isoformat(),
            "status": "Not Started",
            "assignee": "Priya (QA)",
            "depends_on": ["Frontend integration"],
            "resource_notes": None,
            "project_id": project_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    ]
    await db.tasks.insert_many([dict(t) for t in tasks])

    print(f"Seeded project '{project_doc['name']}' (id={project_id}) with 3 tasks.")
    print(f"Demo login -> email: {email}  password: password123\n")

    # Reload with date objects the way the API layer would, and run agents
    project_for_engine = dict(project_doc)
    project_for_engine["start_date"] = date.fromisoformat(project_doc["start_date"])
    project_for_engine["target_end_date"] = date.fromisoformat(project_doc["target_end_date"])

    tasks_for_engine = []
    async for t in db.tasks.find({"project_id": project_id}):
        t["id"] = str(t.pop("_id"))
        t["due_date"] = date.fromisoformat(t["due_date"])
        tasks_for_engine.append(t)

    result = run_analysis(project_for_engine, tasks_for_engine)

    print("=" * 70)
    print("PROJECT HEALTH:", result["project_health"])
    print(result["health_explanation"])
    print("=" * 70)
    print("\nDEPENDENCY GRAPH:")
    print(json.dumps(result["dependency_graph"], indent=2))
    print("\nRISKS DETECTED:")
    for r in result["risks"]:
        print(f"- [{r['severity']}][{r['type']}] {r['description']}")
        for e in r["evidence"]:
            print(f"    evidence: {e}")
    print("\nPRIORITIES:")
    for p in result["priorities"]:
        print(f"- {p['task_name']}: {p['priority_level']} (score={p['priority_score']}) - {p['reason']}")
    print("\nNEXT ACTIONS:")
    for a in result["next_actions"]:
        print(f"- [{a['urgency']}] {a['action']} (owner: {a['owner']})")
    # Seed sample project documentation for RAG
    doc_content = (
        "E-Commerce Platform Revamp Specification & Guidelines\n\n"
        "1. Scope & Architecture:\n"
        "The revamp transitions our monolithic checkout into microservices with Stripe payment integration.\n"
        "Backend API must expose idempotent checkout sessions, order calculation, and webhook handling.\n\n"
        "2. Dependencies & Critical Path:\n"
        "Frontend Integration cannot proceed without validated schema contracts from the Backend API.\n"
        "End-to-end Testing strictly requires Frontend Integration to be complete with all UI mockups verified.\n\n"
        "3. Quality & SLA Guidelines:\n"
        "Any delay in Frontend Integration directly jeopardizes the hard launch deadline of the release.\n"
        "QA must execute at least 50 automated regression tests before final sign-off."
    )
    doc_result = await db.rag_documents.insert_one({
        "project_id": project_id,
        "title": "Architecture & Release Specification",
        "content": doc_content,
        "doc_type": "spec",
        "metadata": {"version": "1.0"},
        "chunk_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })

    # Reindex all project knowledge (docs, tasks, analysis)
    from app.services.rag_service import answer_rag_query, reindex_project
    reindex_res = await reindex_project(project_id, db=db)
    print(f"\nRAG Indexing: {reindex_res.message}")

    print("\n" + "=" * 70)
    print("DEMO RAG QUERY: 'What are the dependencies and delivery risks for Testing?'")
    rag_res = await answer_rag_query(
        project_id=project_id,
        query="What are the dependencies and delivery risks for Testing?",
        top_k=3,
        db=db,
    )
    print("RAG ANSWER:\n", rag_res.answer)
    print("\nRETRIEVED SOURCES:")
    for s in rag_res.sources:
        print(f" - [{s.source_type.upper()}] {s.title} (score={s.score})")
        print(f"   Excerpt: {s.excerpt}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

