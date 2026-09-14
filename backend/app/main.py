import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_to_mongo, is_using_mock
from app.core.redis_client import connect_to_redis
from app.routers import analysis, auth, projects, rag, tasks

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Agentic AI Project Management & Risk Monitoring System",
    description=(
        "Multi-agent backend that analyzes project/task data, detects "
        "schedule/dependency/resource/delivery risks, prioritizes work and "
        "generates explainable, data-grounded recommendations."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(analysis.router)
app.include_router(rag.router)



@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    await connect_to_redis()


@app.get("/")
async def root():
    return {
        "service": "Agentic AI Project Management & Risk Monitoring System",
        "status": "running",
        "database_mode": "mongomock (in-memory fallback)" if is_using_mock() else "mongodb",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
