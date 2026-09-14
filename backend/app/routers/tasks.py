from datetime import date, datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services.rag_service import delete_source_chunks, index_task

router = APIRouter(prefix="/api/projects/{project_id}/tasks", tags=["tasks"])


def _serialize(doc) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("due_date"), str):
        doc["due_date"] = date.fromisoformat(doc["due_date"])
    return doc


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(project_id: str, payload: TaskCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = datetime.now(timezone.utc)
    doc = payload.model_dump()
    doc["due_date"] = doc["due_date"].isoformat()
    doc["status"] = doc["status"].value if hasattr(doc["status"], "value") else doc["status"]
    doc["project_id"] = project_id
    doc["created_at"] = now
    doc["updated_at"] = now
    result = await db.tasks.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Sync with RAG index
    try:
        await index_task(project_id, {"id": str(result.inserted_id), **doc}, db=db)
    except Exception:
        pass

    out = _serialize(doc)
    out["is_delayed"] = out["status"] != "Completed" and out["due_date"] < date.today()
    return TaskOut(**out)


@router.get("", response_model=list[TaskOut])
async def list_tasks(project_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.tasks.find({"project_id": project_id})
    tasks = []
    async for t in cursor:
        out = _serialize(t)
        out["is_delayed"] = out["status"] != "Completed" and out["due_date"] < date.today()
        tasks.append(TaskOut(**out))
    return tasks


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(project_id: str, task_id: str, payload: TaskUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "due_date" in update_data:
        update_data["due_date"] = update_data["due_date"].isoformat()
    if "status" in update_data and hasattr(update_data["status"], "value"):
        update_data["status"] = update_data["status"].value
    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.tasks.update_one({"_id": ObjectId(task_id), "project_id": project_id}, {"$set": update_data})
    doc = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")

    # Sync updated task with RAG index
    try:
        await index_task(project_id, {"id": task_id, **doc}, db=db)
    except Exception:
        pass

    out = _serialize(doc)
    out["is_delayed"] = out["status"] != "Completed" and out["due_date"] < date.today()
    return TaskOut(**out)


@router.delete("/{task_id}", status_code=204)
async def delete_task(project_id: str, task_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await db.tasks.delete_one({"_id": ObjectId(task_id), "project_id": project_id})
    try:
        await delete_source_chunks(task_id, db=db)
    except Exception:
        pass
    return None

