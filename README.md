# ⚡ AgenticPM: Enterprise Autonomous AI Project Management & Risk Intelligence Platform

> **An end-to-end, multi-agent AI system that transforms passive project tracking into proactive, deterministic delivery assurance.**  
> Powered by **LangGraph Multi-Agent Workflows**, a **Deterministic Zero-Hallucination Risk & Critical-Path Engine**, and a **Retrieval-Augmented Generation (RAG) Grounded Knowledge Assistant**.

[![GitHub Repository](https://img.shields.io/badge/GitHub-MohanAddanki25%2FAgenticPM-181717?style=for-the-badge&logo=github)](https://github.com/MohanAddanki25/AgenticPM)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent%20Pipeline-FF6F00?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.6%20Flash%20%26%20Embeddings-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas%20%26%20Motor-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 📑 Complete Table of Contents

1. [Executive Summary & The Problem We Solved](#1-executive-summary--the-problem-we-solved)
2. [End-to-End Journey: From Inception to Production Delivery](#2-end-to-end-journey-from-inception-to-production-delivery)
3. [System Architecture & Data Flow](#3-system-architecture--data-flow)
4. [Technology Stack & Architectural Selection Rationale](#4-technology-stack--architectural-selection-rationale)
5. [Backend Deep Dive & Agent Intelligence](#5-backend-deep-dive--agent-intelligence)
   - 5.1 [LangGraph 6-Agent Collaborative Workflow](#51-langgraph-6-agent-collaborative-workflow)
   - 5.2 [Deterministic Risk & Critical-Path Mathematics](#52-deterministic-risk--critical-path-mathematics)
   - 5.3 [Explainable AI (XAI) Audit Chain](#53-explainable-ai-xai-audit-chain)
6. [Retrieval-Augmented Generation (RAG) Knowledge Assistant](#6-retrieval-augmented-generation-rag-knowledge-assistant)
7. [Database, Caching & Zero-Config Fallback Layer](#7-database-caching--zero-config-fallback-layer)
8. [Frontend Architecture & Executive Dashboard](#8-frontend-architecture--executive-dashboard)
9. [Worked Real-World Execution Scenario](#9-worked-real-world-execution-scenario)
10. [Local Installation & Setup Guide](#10-local-installation--setup-guide)
11. [Docker Containerization & Orchestration](#11-docker-containerization--orchestration)
12. [Comprehensive API Reference](#12-comprehensive-api-reference)
13. [Automated Verification & Test Suite](#13-automated-verification--test-suite)
14. [Security, Production Readiness & Roadmap](#14-security-production-readiness--roadmap)

---

## 1. Executive Summary & The Problem We Solved

### The Pain Point
In modern engineering organizations, tools like Jira, Linear, and Asana act as **passive registries**. Project managers and engineering leads face recurring, costly problems:
* **Silent Cascading Delays**: When a core upstream task slips by 3 days, its ripple effects across 10 dependent tasks remain unnoticed until the release milestone is breached.
* **AI Hallucinations in Delivery Audits**: Generic LLMs summarizing sprints often fabricate dates, misunderstand topological blockers, and invent ungrounded advice.
* **Information Silos**: PRDs, architecture specifications, and post-mortems live in isolated Google Docs or Confluence pages, disconnected from live sprint tickets.

### Our Solution: AgenticPM
**AgenticPM** unites a **6-agent LangGraph network**, a **mathematically deterministic graph analysis engine**, and a **hybrid RAG knowledge assistant**:
* **100% Truthful**: Risk identification and critical-path ranks are computed deterministically via Python Directed Acyclic Graph (DAG) algorithms. The LLM only narrates verified facts.
* **Self-Auditing**: Every risk is backed by an `evidence` array containing timestamped database facts.
* **Deep Contextual Memory**: Queries PRDs, sprint tickets, and past retrospectives simultaneously to explain *why* blockers happened and *how* to unblock them.

---

## 2. End-to-End Journey: From Inception to Production Delivery

Below is the structured engineering path traversed to build this system from scratch:

```
[Phase 1: Conceptualization & Domain Modeling]
   │  • Define Task, Dependency DAG, Risk Severity & Project Health Domain Schemas
   ▼
[Phase 2: Mathematical Engine Development (engine.py)]
   │  • Implement BFS transitive impact traversal
   │  • Formulate composite critical-path scoring formula
   │  • Enforce zero-hallucination deterministic evidence generation
   ▼
[Phase 3: Multi-Agent Orchestration (graph.py)]
   │  • Construct LangGraph StateGraph with typed AgentState
   │  • Sequence: Planning ➔ Progress ➔ Dependency ➔ Risk ➔ Prioritization ➔ Reviewer
   ▼
[Phase 4: RAG Vector Knowledge Base (rag_service.py)]
   │  • Implement document chunker for PRDs, specs, and retrospectives
   │  • Build dual-mode embedding: Google Gemini 001 with offline frequency-hash fallback
   │  • Implement cosine similarity vector search with strict source citation grounding
   ▼
[Phase 5: High-Throughput REST API (FastAPI)]
   │  • JWT Bearer Authentication & Bcrypt hashing
   │  • Async Motor MongoDB persistence with seamless in-memory mongomock fallback
   │  • Redis session cache with in-process dictionary fallback
   ▼
[Phase 6: Frontend Development (React 18 + Vite + Tailwind)]
   │  • Build dynamic Project Health Gauge, live interactive Task Board & DAG Visualizer
   │  • Create Explainable Risk Evidence inspector and Priority Action cards
   │  • Embed interactive RAG Knowledge Assistant Drawer
   ▼
[Phase 7: End-to-End Testing & Packaging]
   │  • 11/11 automated pytest test suite passing
   │  • Docker & Docker Compose multi-service container orchestration
```

---

## 3. System Architecture & Data Flow

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │               FRONTEND (React 18 + Vite)               │
                                    │  • Health Status Banner   • Task Board & DAG Visualizer│
                                    │  • Explainable Risk Modal • RAG Knowledge Assistant    │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │ HTTP / REST (JWT Auth)
                                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                     FASTAPI BACKEND                                                    │
│                                                                                                                        │
│   ┌──────────────────────────────────────────────┐              ┌──────────────────────────────────────────────────┐   │
│   │        LANGGRAPH MULTI-AGENT PIPELINE        │              │              RAG VECTOR ENGINE                   │   │
│   │                                              │              │                                                  │   │
│   │   1. Planning Agent (Scope & Deadlines)      │              │  • Recursive Text Chunker (PRDs, Specs, Notes)   │   │
│   │   2. Progress Monitoring Agent (Velocity)    │              │  • Live Task & Dependency Context Indexer        │   │
│   │   3. Dependency Graph Agent (DAG / BFS)      │              │  • Historical Risk Analysis Indexer              │   │
│   │   4. Risk Detection Agent (Deterministic)    │              │  • Dual Embedding (Gemini 001 + Local Hash)      │   │
│   │   5. Prioritization Agent (Critical Path)    │              │  • Cosine Similarity Vector Retrieval            │   │
│   │   6. Reviewer / LLM Narrator Agent           │              │  • Factual Grounded Q&A with Source Citations    │   │
│   └──────────────────────┬───────────────────────┘              └────────────────────────┬─────────────────────────┘   │
│                          │                                                               │                             │
│                          ▼                                                               ▼                             │
│   ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                      PERSISTENCE & RESILIENT FALLBACK LAYER                                    │   │
│   │      • MongoDB Atlas (Motor Async) / mongomock-motor In-Memory Stub                                            │   │
│   │      • Redis Session Cache / In-Memory Python Dictionary Fallback                                              │   │
│   │      • Google Gemini (`gemini-3.6-flash`) / Deterministic Rule-Based Summarizer                                │   │
│   └────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack & Architectural Selection Rationale

| Layer | Chosen Technology | Why This Technology Was Chosen |
|---|---|---|
| **Frontend UI** | React 18, TypeScript, Vite | Sub-second HMR, strict type safety across shared schema models, component modularity. |
| **Styling & Icons** | Tailwind CSS, Lucide React | Highly responsive design tokens, accessible color contrasts, glassmorphic aesthetics. |
| **Data Visualization** | Recharts | Composable SVG charts for project milestone burnup, health gauges, and velocity indicators. |
| **Backend REST API** | FastAPI (Python 3.11/3.12) | Asynchronous non-blocking I/O, automatic OpenAPI/Swagger documentation, Pydantic v2 validation. |
| **Multi-Agent Engine** | LangGraph & LangChain Core | StateGraph architecture enables cyclical and acyclic multi-agent topologies with typed state snapshots. |
| **Deterministic Math** | Custom Graph BFS (`engine.py`) | 100% deterministic topological sorting and transitive impact tracking. No LLM randomness. |
| **Vector Embeddings** | Google GenAI (`models/gemini-embedding-001`) | High-dimensional semantic density for engineering terms; offline hash vectorizer for no-network modes. |
| **LLM Reasoning** | Google Gemini (`gemini-3.6-flash`) | Ultra-fast token latency, high context window, strict adherence to grounding prompt constraints. |
| **Database** | MongoDB Atlas with Motor Async | Native JSON document format matches dynamic task graphs; `mongomock-motor` allows zero-config local runs. |
| **Cache & Queue** | Redis | In-memory token revocation, agent execution state locks, sub-millisecond query caches. |

---

## 5. Backend Deep Dive & Agent Intelligence

### 5.1 LangGraph 6-Agent Collaborative Workflow

The multi-agent graph is defined in [`backend/app/agents/graph.py`](file:///c:/agentic-pm-system/backend/app/agents/graph.py). The graph shares a single typed context `AgentState`:

```
                 ┌────────────────────────────────┐
                 │       1. Planning Agent        │
                 └───────────────┬────────────────┘
                                 ▼
                 ┌────────────────────────────────┐
                 │      2. Progress Agent         │
                 └───────────────┬────────────────┘
                                 ▼
                 ┌────────────────────────────────┐
                 │     3. Dependency Agent        │
                 └───────────────┬────────────────┘
                                 ▼
                 ┌────────────────────────────────┐
                 │        4. Risk Agent           │
                 └───────────────┬────────────────┘
                                 ▼
                 ┌────────────────────────────────┐
                 │      5. Priority Agent         │
                 └───────────────┬────────────────┘
                                 ▼
                 ┌────────────────────────────────┐
                 │       6. Reviewer Agent        │
                 └────────────────────────────────┘
```

1. **Planning Agent**: Audits project scope, start date, target release date, and overall milestone volume.
2. **Progress Agent**: Evaluates completion percentage, velocity stagnation, and flagged blockers.
3. **Dependency Agent**: Builds the dependency DAG. Detects circular dependencies and identifies upstream blocking bottlenecks.
4. **Risk Agent**: Evaluates deterministic rules against each task. Categorizes risks into `schedule`, `dependency`, `resource`, and `delivery`.
5. **Prioritization Agent**: Computes the composite critical-path score ($0 - 100$) and orders tasks by urgency.
6. **Reviewer / Narrator Agent**: Ingests purely factual data from steps 1–5. Gemini formats an executive briefing with zero hallucination.

### 5.2 Deterministic Risk & Critical-Path Mathematics

Located in [`backend/app/agents/engine.py`](file:///c:/agentic-pm-system/backend/app/agents/engine.py), all risks and priorities are calculated using explicit formulas:

#### Overdue Schedule Risk Rule:
$$\text{OverdueDays} = \text{Date}_{\text{today}} - \text{Date}_{\text{due}}$$
$$\text{Severity} = \begin{cases} \text{Critical}, & \text{if } \text{OverdueDays} \ge 3 \\ \text{High}, & \text{if } \text{OverdueDays} > 0 \\ \text{Medium}, & \text{if Not Started and Due in } \le 2 \text{ days} \end{cases}$$

#### Transitive Downstream Impact (BFS Traversal):
When task $T$ is overdue, the engine traverses the downstream dependency graph:
```python
def get_downstream_impact(task_id, downstream_map, tasks_by_id):
    visited, queue, seen = [], list(downstream_map.get(task_id, [])), set()
    while queue:
        current = queue.pop(0)
        visited.append(tasks_by_id[current]["name"])
        for nxt in downstream_map.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return visited
```

#### Composite Critical-Path Priority Scoring:
$$\text{PriorityScore} = (30 \times O_f) + (25 \times D_f) + (25 \times S_w) + (20 \times U_f)$$
* $O_f$ = Overdue Factor ($\min(1.0, \frac{\text{overdue\_days}}{7})$)
* $D_f$ = Downstream Impact Factor ($\min(1.0, \frac{\text{affected\_tasks\_count}}{3})$)
* $S_w$ = Severity Weight ($\text{Critical}=1.0, \text{High}=0.75, \text{Medium}=0.5, \text{Low}=0.25$)
* $U_f$ = Near-Term Urgency ($\max(0, \frac{7 - \text{days\_until\_due}}{7})$)

### 5.3 Explainable AI (XAI) Audit Chain

Every risk output contains an immutable `evidence` list citing exact data points:
```json
{
  "id": "R1",
  "type": "schedule",
  "severity": "Critical",
  "task_name": "Database Schema Migration",
  "description": "Task 'Database Schema Migration' was due on 2026-09-10 and is 4 day(s) overdue while still marked 'In Progress'.",
  "evidence": [
    "Task 'Database Schema Migration' due_date = 2026-09-10",
    "Today = 2026-09-14",
    "Current status = 'In Progress'",
    "Overdue by 4 day(s)"
  ],
  "affected_tasks": [
    "Backend API Auth Service",
    "Frontend Dashboard Integration"
  ]
}
```

---

## 6. Retrieval-Augmented Generation (RAG) Knowledge Assistant

Implemented in [`backend/app/services/rag_service.py`](file:///c:/agentic-pm-system/backend/app/services/rag_service.py):

```
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│  PRDs & Architecture   │      │  Live Sprint Tasks &   │      │ Historical Multi-Agent │
│     Specifications     │      │   Dependency States    │      │    Risk Audit Runs     │
└───────────┬────────────┘      └───────────┬────────────┘      └───────────┬────────────┘
            │                               │                               │
            └───────────────────────┬───────┴───────────────────────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │ Recursive Document Chunker  │
                     └──────────────┬──────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │ Vector Embeddings Generator │
                     │ • Gemini Embedding-001      │
                     │ • Offline Hash Vectorizer   │
                     └──────────────┬──────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │ Cosine Similarity Search    │
                     └──────────────┬──────────────┘
                                    ▼
                     ┌─────────────────────────────┐
                     │ Grounded Q&A Assistant      │
                     │ with Source Citations       │
                     └─────────────────────────────┘
```

* **Natural Language Queries**: Engineering leads can ask questions like:  
  * *"Why is the frontend release delayed?"*  
  * *"What are the dependencies outlined in Section 3 of the PRD?"*
* **Grounded Answer Format**: Every response includes:
  * **Direct Answer**: Synthesized from retrieved passages.
  * **Source Citations**: Title, category, similarity score, and excerpt quote.

---

## 7. Database, Caching & Zero-Config Fallback Layer

AgenticPM is engineered for resilience. It functions in production cloud environments and offline demo environments without code changes:

* **MongoDB Atlas with `mongomock-motor` Fallback**:
  * Connected via async Motor driver in [`backend/app/core/database.py`](file:///c:/agentic-pm-system/backend/app/core/database.py).
  * If MongoDB Atlas is unreachable or `USE_MOCK_DB_FALLBACK=true`, the backend automatically instantiates an in-memory `mongomock-motor` instance.
* **Redis with In-Process Dictionary Fallback**:
  * Implemented in [`backend/app/core/redis_client.py`](file:///c:/agentic-pm-system/backend/app/core/redis_client.py).
  * If Redis is down, an in-process thread-safe dictionary mock intercepts cache and lock calls transparently.
* **Google Gemini with Rule Narrator Fallback**:
  * If no API key is provided, the Reviewer Agent defaults to a deterministic summarizer, ensuring the multi-agent pipeline never throws unhandled exceptions.

---

## 8. Frontend Architecture & Executive Dashboard

Located in [`frontend/src/pages/DashboardPage.tsx`](file:///c:/agentic-pm-system/frontend/src/pages/DashboardPage.tsx):

* **Project Health Banner**: Live status indicator badge (`Healthy` / `At Risk` / `Critical`) with progress bars and risk counters.
* **Agent Trigger Control**: One-click "Run Agent Analysis" executes the LangGraph multi-agent pipeline.
* **Interactive Task Board**: Color-coded task cards categorized by status (`Not Started`, `In Progress`, `Blocked`, `Completed`) with inline dependency badges.
* **Explainable Risk Panel**: Displays each detected risk, severity badge, affected downstream tasks, and expandable evidence items.
* **Critical-Path Priority List**: Ranked action items showing priority score, suggested action, and assigned engineer.
* **RAG Knowledge Assistant Drawer**: Embedded chat interface for interacting with project documents and sprint context.

---

## 9. Worked Real-World Execution Scenario

Here is an end-to-end trace of a sample project:

### Initial State:
* **Task 1: "Database Schema Migration"** (Due: 4 days ago | Status: `In Progress`)
* **Task 2: "Backend API Auth Service"** (Due: Tomorrow | Status: `Blocked` | Depends on: Task 1)
* **Task 3: "Frontend Dashboard Integration"** (Due: In 4 days | Status: `Not Started` | Depends on: Task 2)

### Agent Execution Steps:
1. **Planning Agent**: Reads 3 tasks, project deadline in 14 days.
2. **Progress Agent**: Flags completion velocity at 0% with 1 blocked task.
3. **Dependency Agent**: Builds the DAG: `Task 1` $\rightarrow$ `Task 2` $\rightarrow$ `Task 3`. Identifies Task 1 as root bottleneck.
4. **Risk Agent**: Detects:
   * `R1` (Critical Schedule): Task 1 is 4 days overdue.
   * `R2` (High Dependency): Task 2 blocked by overdue Task 1.
   * `R3` (High Resource): Task 2 explicitly flagged as Blocked.
5. **Prioritization Agent**: Assigns Task 1 a priority score of **96/100** (Rank #1).
6. **Reviewer Agent**: Synthesizes summary: *"Project health is CRITICAL. Root blocker is Database Schema Migration."*
7. **RAG Assistant Interaction**:
   * User query: *"Why can't frontend work start?"*
   * Assistant reply: *"Frontend Dashboard Integration depends on Backend API Auth Service, which is currently blocked by the overdue Database Schema Migration."* (Citing Task #2 and Task #1).

---

## 10. Local Installation & Setup Guide

### Prerequisites
* **Python**: 3.11 or 3.12 installed
* **Node.js**: v18+ and npm installed
* **Git** installed

### Step 1: Clone the Repository
```bash
git clone https://github.com/MohanAddanki25/AgenticPM.git
cd AgenticPM
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables (`backend/.env`):
```env
# MongoDB (uses in-memory fallback if unreachable)
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?appName=Cluster0
MONGO_DB_NAME=agentic_pm_system
USE_MOCK_DB_FALLBACK=true

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
JWT_SECRET_KEY=super-secret-production-grade-key-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google Gemini AI (Optional - falls back to deterministic narrator if omitted)
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash

# CORS
FRONTEND_ORIGIN=http://localhost:5174
```

#### Seed Demo Data (Worked Example):
```bash
python seed_demo.py
```
*Seeds user `admin@agenticpm.local` (Password: `Admin1234!`), creates the sample project, uploads a PRD, indexes vectors, and runs an initial analysis.*

#### Start Backend Server:
```bash
uvicorn app.main:app --reload --port 8000
```
*Backend runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.*

### Step 3: Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend opens at `http://localhost:5174` (or `http://localhost:5173`).*

---

## 11. Docker Containerization & Orchestration

Run the complete multi-tier stack (MongoDB, Redis, Backend, Frontend) with a single command:

```bash
docker compose up --build
```

### Container Endpoints:
* **Frontend Web App**: `http://localhost:5173`
* **FastAPI Backend**: `http://localhost:8000`
* **Swagger API Documentation**: `http://localhost:8000/docs`
* **MongoDB**: `localhost:27017`
* **Redis**: `localhost:6379`

---

## 12. Comprehensive API Reference

### Authentication Endpoints
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new project manager account |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT Bearer token |

### Project & Task Management
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/projects` | List all projects for authenticated user |
| `POST` | `/api/projects` | Create a new project |
| `GET` | `/api/projects/{id}/tasks` | List all tasks with status, dates, and dependencies |
| `POST` | `/api/projects/{id}/tasks` | Create task (automatically indexed into RAG) |
| `PATCH` | `/api/projects/{id}/tasks/{task_id}` | Update task status, due dates, or dependencies |
| `DELETE` | `/api/projects/{id}/tasks/{task_id}` | Delete task and remove associated RAG vectors |

### Multi-Agent Analysis
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/{id}/analyze` | Execute 6-agent LangGraph workflow |
| `GET` | `/api/projects/{id}/analyze/history` | Fetch historical analysis runs and metrics |

### RAG Knowledge Base
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/{id}/documents` | Upload and chunk PRD or technical specification |
| `GET` | `/api/projects/{id}/documents` | List uploaded documents and chunk counts |
| `DELETE` | `/api/projects/{id}/documents/{doc_id}`| Delete document and remove vector embeddings |
| `POST` | `/api/projects/{id}/rag/query` | Grounded Q&A query returning answer and citations |
| `POST` | `/api/projects/{id}/rag/reindex` | Reindex all documents, tasks, and analyses |

---

## 13. Automated Verification & Test Suite

The project includes an automated test suite verifying every layer of the architecture:

```bash
cd backend
pytest -v
```

### Test Suite Structure:
* **`tests/test_engine.py`**:
  * `test_detect_overdue_schedule_risk`: Validates overdue calculation and evidence logging.
  * `test_dependency_chain_and_downstream_impact`: Verifies BFS traversal of transitively blocked tasks.
  * `test_priority_scoring`: Confirms composite weighting algorithm correctly ranks blockers.
* **`tests/test_rag.py`**:
  * `test_rag_indexing_and_vector_query`: Tests document ingestion, chunking, and similarity search.
  * `test_offline_fallback_vectorizer`: Ensures deterministic vector search operates without network.
* **`tests/test_api.py`**:
  * Tests authentication, JWT issuance, task creation, and project analysis endpoints.

---

## 14. Security, Production Readiness & Roadmap

### Security Implementation
* **Password Security**: Bcrypt with salted rounds via Passlib.
* **JWT Authorization**: Cryptographically signed tokens (HS256) with strict expiration.
* **Data Sanitization**: Pydantic v2 schemas sanitize all inputs against injection.
* **Prompt Guardrails**: Factual grounding instructions prevent prompt injection in the RAG pipeline.

### Roadmap & Future Extensions
* [x] LangGraph 6-Agent Sequential Pipeline
* [x] Deterministic Rule Engine with XAI Audit Evidence
* [x] RAG Assistant with Source Citations & Dual-Mode Embeddings
* [x] Resilient In-Memory Fallbacks for Zero-Config Setup
* [ ] GitHub / GitLab Webhook Integration for automatic commit-to-task sync
* [ ] Slack / Microsoft Teams Agent Notifications for critical-path risk alerts
* [ ] Monte Carlo Simulation for probabilistic delivery date forecasting

---

## 👥 Authors & Maintainers
* **Lead Engineer**: Mohan Addanki ([@MohanAddanki25](https://github.com/MohanAddanki25))
* **Repository**: [https://github.com/MohanAddanki25/AgenticPM](https://github.com/MohanAddanki25/AgenticPM)

