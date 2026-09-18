# 🚀 Agentic AI Project Management & Risk Monitoring System with RAG
### *End-to-End Enterprise Architecture, Multi-Agent Workflow, Rule Engine & Deployment Guide*

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/MohanAddanki25/AgenticPM)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)](https://langchain-ai.github.io/langgraph/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Flash%20%26%20Embeddings-8E75B2?logo=google)](https://ai.google.dev/)

---

## 📌 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Key Value Propositions](#2-key-value-propositions)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [Technology Stack](#4-technology-stack)
5. [LangGraph Multi-Agent Pipeline](#5-langgraph-multi-agent-pipeline)
6. [Deterministic Risk Detection & Priority Engine](#6-deterministic-risk-detection--priority-engine)
7. [Retrieval-Augmented Generation (RAG) Engine](#7-retrieval-augmented-generation-rag-engine)
8. [Frontend & Interactive Dashboard](#8-frontend--interactive-dashboard)
9. [Detailed End-to-End Execution Walkthrough](#9-detailed-end-to-end-execution-walkthrough)
10. [Step-by-Step Installation & Local Setup](#10-step-by-step-installation--local-setup)
11. [Docker Deployment Guide](#11-docker-deployment-guide)
12. [API Reference & Schema Specifications](#12-api-reference--schema-specifications)
13. [Automated Testing & Quality Assurance](#13-automated-testing--quality-assurance)
14. [Repository & Contribution Links](#14-repository--contribution-links)

---

## 1. Project Overview

**AgenticPM** is an enterprise-ready, autonomous project intelligence and delivery assurance system. Traditional project management software (such as Jira, Asana, or Monday.com) behaves merely as a passive tracking database where human teams manually diagnose delays, unearth blockers, and compute priorities. 

**AgenticPM revolutionizes this paradigm** by deploying an autonomous **LangGraph Multi-Agent Network** that continuously audits task dependencies, evaluates schedule health using a deterministic zero-hallucination rule engine, calculates transitive downstream impacts using DAG traversal, and serves grounded answers via a **RAG Knowledge Assistant** with document source citations.

---

## 2. Key Value Propositions

* 🔍 **Zero-Hallucination Risk Engine**: AI hallucination in critical delivery schedules is unacceptable. All risk detections, critical-path scores, and downstream impact analyses are calculated via mathematical graph algorithms in Python before reaching any LLM.
* 📋 **Explainable AI (XAI) Audit Trails**: Every detected risk carries an immutable `evidence` array citing exact database fields (e.g., `due_date`, `overdue_by_days`, `upstream_blocker`).
* 🤖 **Collaborative 6-Agent Pipeline**: Specialized autonomous agents (Planning, Progress, Dependency, Risk, Prioritization, and Reviewer/Narrator) coordinate sequentially over a shared typed state graph.
* 📚 **Context-Grounded RAG Assistant**: Allows PMs and engineers to query complex PRDs, architecture specifications, and retrospective logs alongside live sprint tasks, returning answers with relevance scores and direct quotations.
* 🛡️ **Fail-Safe Offline Architecture**: Runs completely out of the box. Automatically activates in-memory fallbacks (`mongomock-motor`, in-memory Redis stub, and offline frequency-hash vectorizer) if cloud credentials are not supplied.

---

## 3. System Architecture Diagram

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │                FRONTEND (React 18 + Vite)              │
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

## 4. Technology Stack

### Backend
* **Language & Runtime**: Python 3.11 / 3.12
* **Web Framework**: FastAPI (Asynchronous REST API with Pydantic v2 schemas)
* **Agent Framework**: LangGraph (`StateGraph`), LangChain Core
* **Security & Auth**: Python-Jose (JWT Bearer Tokens), Passlib (Bcrypt hashing)
* **Database & Persistence**: MongoDB Atlas via Motor async driver (`mongomock-motor` for offline operation)
* **Caching & Queue**: Redis (`redis-py`) with automatic in-process fallback
* **AI & LLM Services**: Google Gemini (`gemini-3.6-flash`), Google GenAI Embeddings (`models/gemini-embedding-001`)

### Frontend
* **Core Framework**: React 18, TypeScript, Vite
* **Styling & UI**: Tailwind CSS, Lucide React Icons
* **Data Visualization**: Recharts (Project health and completion charts)
* **HTTP Client**: Axios with automatic JWT Authorization interceptor

---

## 5. LangGraph Multi-Agent Pipeline

The core intelligence workflow is orchestrated via a typed LangGraph `StateGraph(AgentState)`. Each agent functions as an independent specialist with designated duties:

```
                  ┌──────────────────────┐
                  │ 1. Planning Agent    │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ 2. Progress Agent    │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ 3. Dependency Agent  │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ 4. Risk Agent        │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ 5. Priority Agent    │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ 6. Reviewer Agent    │
                  └──────────────────────┘
```

### Agent Roles & Responsibilities

1. **Planning Agent**:
   * Evaluates project scope, milestone dates, and target completion deadlines against current calendar time.
   * Assesses total task volume and flags missing project configurations.
2. **Progress Monitoring Agent**:
   * Computes completed vs. pending tasks and milestone burnup rates.
   * Detects velocity stalls and flags tasks lingering in progress without updates.
3. **Dependency Agent**:
   * Constructs the project Directed Acyclic Graph (DAG).
   * Identifies circular dependency deadlocks and computes transitive blocker cascades using Breadth-First Search (BFS).
4. **Risk Detection Agent**:
   * Ingests the dependency map and task dates into the deterministic rule engine.
   * Categorizes risks into **Schedule**, **Dependency**, **Resource**, and **Delivery** severities.
5. **Prioritization Agent**:
   * Calculates a multi-factor critical-path urgency score ($0 - 100$) for every active task.
   * Produces ranked action items recommending which tasks to execute first to unblock the critical path.
6. **Reviewer & Narrator Agent**:
   * Ingests the purely mathematical outputs from agents 1–5.
   * Passes the verified context into Google Gemini to craft an executive briefing while strictly enforcing prompt guards against hallucination.

---

## 6. Deterministic Risk Detection & Priority Engine

The system's core philosophy is **trust through transparency**. In `backend/app/agents/engine.py`:

### Mathematical Risk Rules
* **Overdue Schedule Risk**:
  Triggered when $Status \neq \text{'Completed'}$ and $Due Date < Today$.
  $$\text{Severity} = \begin{cases} \text{Critical}, & \text{if } OverdueDays \ge 3 \\ \text{High}, & \text{otherwise} \end{cases}$$
* **Dependency Slippage Risk**:
  Triggered when Upstream Task $A$ is overdue or incomplete, while Downstream Task $B$ has an approaching deadline:
  $$\text{Evidence} = [Task_A \text{ due } D_A, Task_B \text{ depends on } Task_A, \text{Slack} < 0]$$
* **Transitive Downstream Impact**:
  Uses BFS traversal to determine every task in the project that will be delayed if an upstream task slips.

### Composite Priority Scoring Formula
For each incomplete task, the engine computes:
$$\text{PriorityScore} = (30 \times \text{OverdueFactor}) + (25 \times \text{DownstreamImpactFactor}) + (25 \times \text{SeverityWeight}) + (20 \times \text{UrgencyFactor})$$
* **Result**: Tasks directly blocking multiple dependent milestones bubble to the top of the sprint backlog automatically.

---

## 7. Retrieval-Augmented Generation (RAG) Engine

The built-in RAG assistant (`backend/app/services/rag_service.py`) grounds AI queries in real project facts:

1. **Document Ingestion**:
   * Accepts Product Requirement Documents (PRDs), engineering specs, and meeting notes.
   * Chunks text into semantic passages with metadata (title, category, timestamp).
2. **Context Federation**:
   * Automatically combines uploaded documents with **live task states** and **recent multi-agent risk audits**.
3. **Embedding Vectorization**:
   * High-dimensional embeddings via Google Gemini `models/gemini-embedding-001`.
   * Offline fallback: Deterministic frequency-hash vectorizer ensuring zero crashes when offline.
4. **Grounded Generation with Exact Citations**:
   * Performs cosine similarity search to retrieve top-$k$ relevant chunks.
   * Feeds the chunks to the LLM with strict instructions to cite the exact document, section, and relevance score for every claim made.

---

## 8. Frontend & Interactive Dashboard

The React frontend (`frontend/src/`) provides a modern interface:

* 📊 **Project Health Banner**: Live visual status badge (`Healthy`, `At Risk`, `Critical`) accompanied by percentage completion rings and open risk counters.
* 🔄 **Live Agent Trigger**: "Run Agent Analysis" button executes the multi-agent pipeline on demand with interactive loading states.
* 🕸️ **Dependency & Blocker Visualizer**: Visualizes task relationships, identifying which tasks are currently blocked and which upstream items are causing delays.
* 📋 **Explainable Risk Panel**: Displays every detected risk card with its severity, affected downstream tasks, and exact data evidence points.
* 💡 **Critical Path Recommendations**: Ranked cards guiding team leads on immediate actions to mitigate timeline slippage.
* 💬 **RAG AI Assistant Drawer**: Slide-out chat widget allowing team members to ask questions regarding project scope, architecture, or reasons for delay.

---

## 9. Detailed End-to-End Execution Walkthrough

Here is what happens during a real execution cycle:

1. **User Action**: Team lead opens the dashboard and triggers an agent audit.
2. **Data Ingestion**: Backend queries MongoDB for all tasks in the project (e.g., *Database Migration*, *Auth Service*, *Frontend Integration*).
3. **Graph Analysis**:
   * *Database Migration* is detected as 4 days overdue.
   * Dependency graph identifies that *Auth Service* and *Frontend Integration* are waiting on *Database Migration*.
4. **Risk Generation**: Risk Agent registers a `Critical Schedule Risk` for *Database Migration* and a `Dependency Risk` for *Auth Service*.
5. **Priority Assignment**: Prioritization Agent assigns *Database Migration* a priority score of **96/100**, placing it at Rank #1.
6. **Executive Summary**: Reviewer Agent creates a concise summary highlighting the blockers.
7. **RAG Indexing**: The analysis report is embedded into vector memory.
8. **User Query**: PM asks the assistant, *"Why is the frontend blocked?"*
   * System performs vector lookup $\rightarrow$ matches current analysis report chunk.
   * Responds: *"The Frontend Integration is blocked because its prerequisite 'Auth Service' is waiting on 'Database Migration', which is 4 days overdue."* (Citing Analysis Run #12 and Task #101).

---

## 10. Step-by-Step Installation & Local Setup

### Prerequisites
* **Python**: 3.11 or 3.12
* **Node.js**: v18+ and npm
* **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/MohanAddanki25/AgenticPM.git
cd AgenticPM
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment Variables (`backend/.env`):
```env
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=Cluster0
MONGO_DB_NAME=agentic_pm_system
USE_MOCK_DB_FALLBACK=true

REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-super-secure-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
FRONTEND_ORIGIN=http://localhost:5174
```

#### Seed Demo Data:
```bash
python seed_demo.py
```
*Seeds admin user (`admin@agenticpm.local` / `Admin1234!`), sample projects, tasks, PRD documents, and initial analysis.*

#### Start Backend Server:
```bash
uvicorn app.main:app --reload --port 8000
```
*API is accessible at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Web dashboard opens at `http://localhost:5174` (or `http://localhost:5173`).*

---

## 11. Docker Deployment Guide

To run the entire system (MongoDB, Redis, Backend, and Frontend) in Docker:

```bash
docker compose up --build
```
* **Frontend**: `http://localhost:5173`
* **Backend API**: `http://localhost:8000`
* **Interactive API Docs**: `http://localhost:8000/docs`

---

## 12. API Reference & Schema Specifications

### Authentication
* `POST /api/auth/register` — Create user account.
* `POST /api/auth/login` — Authenticate and receive JWT token.

### Projects & Tasks
* `GET /api/projects` — List accessible projects.
* `POST /api/projects` — Create project.
* `GET /api/projects/{id}/tasks` — Fetch tasks with dependencies.
* `POST /api/projects/{id}/tasks` — Add new task (auto-indexed in RAG).
* `PATCH /api/projects/{id}/tasks/{task_id}` — Update task details or status.
* `DELETE /api/projects/{id}/tasks/{task_id}` — Remove task.

### Multi-Agent Workflows
* `POST /api/projects/{id}/analyze` — Run 6-agent LangGraph workflow.
* `GET /api/projects/{id}/analyze/history` — Fetch previous analysis runs.

### RAG Assistant & Documents
* `POST /api/projects/{id}/documents` — Upload and index PRD or spec.
* `GET /api/projects/{id}/documents` — View uploaded knowledge base docs.
* `POST /api/projects/{id}/rag/query` — Run grounded Q&A with source citations.
* `POST /api/projects/{id}/rag/reindex` — Force vector reindexing of all data.

---

## 13. Automated Testing & Quality Assurance

Run the comprehensive automated test suite:

```bash
cd backend
pytest -v
```

### Test Coverage Highlights:
* `tests/test_engine.py`: Unit tests verifying zero-hallucination mathematical risk calculations, BFS transitive dependency traversals, and critical-path score accuracy.
* `tests/test_rag.py`: Verifies document chunking, dual embedding modes, cosine search similarity, and source attribution integrity.
* `tests/test_api.py`: Tests FastAPI endpoints, JWT auth validation, and task CRUD cycles.

---

## 14. Repository & Contribution Links

* **Official Repository**: [https://github.com/MohanAddanki25/AgenticPM](https://github.com/MohanAddanki25/AgenticPM)
* **Author / Maintainer**: Mohan Addanki
* **License**: MIT Open Source License

*Built with passion for deterministic, transparent, and agentic AI systems.*
