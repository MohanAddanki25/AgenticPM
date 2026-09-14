from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Tasks ----------
class TaskStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"
    DELAYED = "Delayed"


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    due_date: date
    status: TaskStatus = TaskStatus.NOT_STARTED
    assignee: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)  # list of task names/ids this task depends on
    resource_notes: Optional[str] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    assignee: Optional[str] = None
    depends_on: Optional[List[str]] = None
    resource_notes: Optional[str] = None


class TaskOut(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str] = ""
    due_date: date
    status: TaskStatus
    assignee: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    resource_notes: Optional[str] = None
    is_delayed: bool = False
    created_at: datetime
    updated_at: datetime


# ---------- Projects ----------
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    start_date: date
    target_end_date: date


class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    start_date: date
    target_end_date: date
    owner_id: str
    created_at: datetime


# ---------- Agent / analysis outputs ----------
class RiskSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskItem(BaseModel):
    id: str
    type: str  # schedule | dependency | resource | delivery
    severity: RiskSeverity
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    description: str
    evidence: List[str]  # explainability: raw data points that led to this risk
    affected_tasks: List[str] = Field(default_factory=list)


class PriorityItem(BaseModel):
    task_id: str
    task_name: str
    priority_score: float
    priority_level: str  # Urgent | High | Medium | Low
    reason: str
    evidence: List[str]


class NextAction(BaseModel):
    action: str
    owner: Optional[str] = None
    related_task: Optional[str] = None
    urgency: str


class ProjectHealth(str, Enum):
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    DELAYED = "Delayed"


class AnalysisResult(BaseModel):
    project_id: str
    generated_at: datetime
    project_health: ProjectHealth
    health_explanation: str
    milestones: List[dict]
    task_status_summary: dict
    upcoming_deadlines: List[dict]
    delayed_tasks: List[dict]
    dependency_graph: List[dict]
    critical_blockers: List[dict]
    risks: List[RiskItem]
    priorities: List[PriorityItem]
    next_actions: List[NextAction]
    weekly_summary: str
    used_llm: bool


# ---------- Documents & RAG ----------
class DocumentType(str, Enum):
    SPEC = "spec"
    PRD = "prd"
    MEETING_NOTES = "meeting_notes"
    RETROSPECTIVE = "retrospective"
    RISK_LOG = "risk_log"
    GENERAL = "general"


class DocumentCreate(BaseModel):
    title: str
    content: str
    doc_type: DocumentType = DocumentType.GENERAL
    metadata: dict = Field(default_factory=dict)


class DocumentOut(BaseModel):
    id: str
    project_id: str
    title: str
    content: str
    doc_type: DocumentType
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime


class RAGSource(BaseModel):
    source_id: str
    source_type: str  # document | task | analysis
    title: str
    excerpt: str
    score: float
    metadata: dict = Field(default_factory=dict)


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 4


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[RAGSource]
    used_llm: bool
    generated_at: datetime


class RAGReindexResponse(BaseModel):
    indexed_documents: int
    indexed_tasks: int
    indexed_analyses: int
    total_chunks: int
    message: str

