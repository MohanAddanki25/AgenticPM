import uuid
from datetime import date, datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.agents.graph import run_analysis
from app.core.database import get_db
from app.core.redis_client import save_workflow_state
from app.core.security import get_current_user
from app.models.schemas import AnalysisResult
from app.services.llm import is_llm_available

router = APIRouter(prefix="/api/projects/{project_id}", tags=["analysis"])


async def _load_project_and_tasks(project_id: str, db):
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project["id"] = str(project.pop("_id"))
    project["start_date"] = date.fromisoformat(project["start_date"])
    project["target_end_date"] = date.fromisoformat(project["target_end_date"])

    tasks = []
    async for t in db.tasks.find({"project_id": project_id}):
        t["id"] = str(t.pop("_id"))
        t["due_date"] = date.fromisoformat(t["due_date"])
        tasks.append(t)
    return project, tasks


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_project(project_id: str, user: dict = Depends(get_current_user)):
    """Runs the full multi-agent workflow (Planning -> Progress -> Dependency
    -> Risk -> Prioritization -> Reporting) over the project's current data."""
    db = get_db()
    project, tasks = await _load_project_and_tasks(project_id, db)
    if not tasks:
        raise HTTPException(status_code=400, detail="Project has no tasks to analyze")

    result_state = run_analysis(project, tasks)

    run_id = str(uuid.uuid4())
    generated_at = datetime.now(timezone.utc)

    analysis = AnalysisResult(
        project_id=project_id,
        generated_at=generated_at,
        project_health=result_state["project_health"],
        health_explanation=result_state["health_explanation"],
        milestones=result_state["milestones"],
        task_status_summary=result_state["task_status_summary"],
        upcoming_deadlines=result_state["upcoming_deadlines"],
        delayed_tasks=result_state["delayed_tasks"],
        dependency_graph=result_state["dependency_graph"],
        critical_blockers=result_state["critical_blockers"],
        risks=result_state["risks"],
        priorities=result_state["priorities"],
        next_actions=result_state["next_actions"],
        weekly_summary=result_state["weekly_summary"],
        used_llm=is_llm_available(),
    )

    # Persist workflow state in Redis (agent memory / run trace) and Mongo (history)
    await save_workflow_state(run_id, {
        "project_id": project_id,
        "trace": result_state.get("trace", []),
        "generated_at": generated_at.isoformat(),
    })
    await db.analysis_history.insert_one({
        "run_id": run_id,
        "project_id": project_id,
        "result": analysis.model_dump(mode="json"),
        "created_at": generated_at,
    })

    # Index analysis report into RAG vector store for context retrieval
    try:
        from app.services.rag_service import index_analysis
        await index_analysis(project_id, analysis.model_dump(mode="json"), db=db)
    except Exception:
        pass

    return analysis



@router.get("/analyze/history")
async def analysis_history(project_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.analysis_history.find({"project_id": project_id}).sort("created_at", -1).limit(20)
    history = []
    async for h in cursor:
        h["_id"] = str(h["_id"])
        history.append(h)
    return history
