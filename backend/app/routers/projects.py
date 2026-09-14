from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import ProjectCreate, ProjectOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _serialize(doc) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(payload: ProjectCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = payload.model_dump()
    doc["start_date"] = doc["start_date"].isoformat()
    doc["target_end_date"] = doc["target_end_date"].isoformat()
    doc["owner_id"] = user["_id"]
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db.projects.insert_one(doc)
    doc["_id"] = result.inserted_id
    return ProjectOut(**_serialize(doc))


@router.get("", response_model=list[ProjectOut])
async def list_projects(user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.projects.find({"owner_id": user["_id"]})
    projects = [ProjectOut(**_serialize(p)) async for p in cursor]
    return projects


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    doc = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectOut(**_serialize(doc))


from app.services.rag_service import delete_project_rag_data


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await db.projects.delete_one({"_id": ObjectId(project_id)})
    await db.tasks.delete_many({"project_id": project_id})
    await delete_project_rag_data(project_id, db=db)
    return None

