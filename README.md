<<<<<<< HEAD
# AgenticPM
=======
# Agentic AI Project Management & Risk Monitoring System with RAG

An enterprise-grade, agent-driven project management platform that continuously monitors project health, detects schedule, dependency, resource, and delivery risks, prioritizes critical-path tasks, and grounds recommendations using **LangGraph Multi-Agent Workflows** and a **Retrieval-Augmented Generation (RAG) Knowledge Assistant**.

🔗 **GitHub Repository**: [https://github.com/MohanAddanki25/AgenticPM](https://github.com/MohanAddanki25/AgenticPM)

---

## Key Features

1. **Deterministic Rule Engine & Explainable AI**:
   - Every risk and priority score is calculated by a deterministic rule engine (`backend/app/agents/engine.py`) directly from raw task data (due dates, statuses, dependency graphs).
   - Guarantees transparency: each risk carries an `evidence` array citing the exact dates, tasks, and dependency chains that triggered it.
2. **LangGraph Multi-Agent Pipeline**:
   - Autonomous multi-agent pipeline: Planning Agent → Progress Agent → Dependency Agent → Risk Agent → Prioritization Agent → Reviewer/Reporting Agent.
3. **Retrieval-Augmented Generation (RAG) Project Assistant**:
   - **Vector Knowledge Base**: Indexes user-uploaded project documents (PRDs, architecture specifications, sprint retrospectives, meeting notes), live project tasks, and historical analysis reports.
   - **Dual-Mode Embedding**: High-dimensional semantic vectors via Google Gemini (`models/gemini-embedding-001`) with automatic fallback to an offline deterministic frequency-hash vectorizer when running without an API key.
   - **Grounded Q&A with Citations**: Answers natural language questions with source citations, relevance scores, and direct excerpt quotes.
4. **Resilient Local Demo Architecture**:
   - Automatic in-memory mock fallbacks for MongoDB (`mongomock-motor`), Redis (in-process stub), and Gemini LLM (rule-based narrator). Runs out of the box with zero external infrastructure required.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Recharts, Vite |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, Uvicorn |
| **Agent Framework** | LangGraph (StateGraph pipeline), LangChain Core |
| **RAG & Embeddings** | LangChain Google GenAI (`models/gemini-embedding-001`), Cosine Vector Search |
| **LLM Narrator** | Google Gemini (`gemini-3.6-flash`) with factual grounding prompt guards |
| **Database** | MongoDB (Motor async driver) with automatic `mongomock` in-memory fallback |
| **State / Cache** | Redis with automatic in-process dictionary fallback |
| **Authentication** | JWT (python-jose) + bcrypt password hashing |

---

## System Architecture

```
                                    ┌──────────────────────────────────────────────┐
                                    │            FRONTEND (React + Vite)           │
                                    │  • Health Banner    • Task Board & Graph     │
                                    │  • Risk Evidence    • RAG Assistant & Docs   │
                                    └──────────────────────┬───────────────────────┘
                                                           │ HTTP / REST (JWT Auth)
                                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       FASTAPI BACKEND                                             │
│                                                                                                   │
│   ┌───────────────────────────────┐                  ┌────────────────────────────────────────┐   │
│   │   LANGGRAPH MULTI-AGENT GRAPH │                  │          RAG VECTOR ENGINE             │   │
│   │                               │                  │                                        │   │
│   │   1. Planning Agent           │                  │  • Document Chunker (Specs, PRDs)      │   │
│   │   2. Progress Monitoring Agent│                  │  • Task Context & Blocker Indexer      │   │
│   │   3. Dependency Agent         │                  │  • Historical Risk Analysis Indexer    │   │
│   │   4. Risk Detection Agent     │                  │  • Gemini Embeddings + Local Fallback  │   │
│   │   5. Prioritization Agent     │                  │  • Cosine Similarity Vector Retrieval  │   │
│   │   6. Reviewer / Narrator Agent│                  │  • Grounded Answer & Source Citations  │   │
│   └──────────────┬────────────────┘                  └───────────────────┬────────────────────┘   │
│                  │                                                       │                        │
│                  ▼                                                       ▼                        │
│   ┌───────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                        DATA PERSISTENCE & IN-MEMORY FALLBACK LAYER                        │   │
│   │    MongoDB Atlas / mongomock-motor   │   Redis / InMemoryStub   │   Google Gemini API     │   │
│   └───────────────────────────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
AgenticPM/
├── backend/
│   ├── app/
│   │   ├── agents/            # engine.py (deterministic rules) + graph.py (LangGraph)
│   │   ├── core/              # config.py, database.py, redis_client.py, security.py
│   │   ├── models/            # schemas.py (Pydantic models for tasks, risks, RAG)
│   │   ├── routers/           # auth, projects, tasks, analysis, rag
│   │   └── services/          # llm.py (Gemini narrator), rag_service.py (vector store & Q&A)
│   ├── tests/                 # pytest suite (engine unit tests, API tests, RAG tests)
│   ├── seed_demo.py           # seeds worked example + PRD spec + tests RAG query
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/               # axios API client with JWT interceptor & RAG endpoints
│   │   ├── components/        # HealthBanner, Card, Badge, RAGAssistant
│   │   ├── context/           # AuthContext (token storage & auth state)
│   │   ├── pages/             # Login, Register, Dashboard
│   │   └── types/             # TypeScript definitions
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Step-by-Step Setup & Running Guide

### Prerequisites
- **Python**: 3.11 or 3.12 installed
- **Node.js**: v18+ and npm installed
- **Git** (for version control)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/MohanAddanki25/AgenticPM.git
cd AgenticPM
```

---

### Step 2: Backend Setup

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` as needed:
   ```env
   # Leave USE_MOCK_DB_FALLBACK=true to run without any local MongoDB installed!
   USE_MOCK_DB_FALLBACK=true
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=agentic_pm

   # Redis (falls back to in-memory stub automatically)
   REDIS_URL=redis://localhost:6379/0

   # JWT secret
   JWT_SECRET_KEY=super-secret-key-change-in-prod
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   # Google Gemini (Optional - system functions with deterministic fallback if omitted)
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.6-flash
   GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001

   # Allowed frontend origins for CORS
   FRONTEND_ORIGIN=http://localhost:5173
   ```

5. Seed demo data (creates demo user, projects, tasks, and indexes PRD for RAG):
   ```bash
   python seed_demo.py
   ```
   *Demo credentials created:*
   - **Email**: `pm@example.com`
   - **Password**: `password123`

6. Start the backend API server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Backend will be live at: **http://localhost:8000** (Swagger documentation at **http://localhost:8000/docs**).

---

### Step 3: Frontend Setup

1. Open a new terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   ```
   Ensure `.env` contains:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   Frontend will be live at: **http://localhost:5173**

---

### Step 4: Accessing the Application

1. Open **http://localhost:5173** in your browser.
2. Log in with:
   - **Email**: `pm@example.com`
   - **Password**: `password123`
3. Features to explore:
   - **Risk Analysis**: Click **Run Risk Analysis** to execute the multi-agent workflow. Review project health, status breakdown, dependency chains, and evidence for detected risks.
   - **RAG AI Assistant**: Switch to the **Ask AI Assistant** tab to ask questions like:
     - *"What are our critical dependency risks?"*
     - *"What does the specification say about SLAs and deadlines?"*
     - *"Which tasks are delayed or missing dependencies?"*
   - **Project Documents**: Switch to **Project Documents** to view or upload new PRDs, specs, and meeting notes with automatic chunking and vector indexing.

---

## Running Automated Tests

Execute the full test suite (deterministic engine tests, API integration tests, and RAG vector search tests):

```bash
cd backend
pytest -v
```

All 11 tests run with `mongomock` and deterministic vector fallbacks, requiring no external database or API key to pass.

---

## Option B: Running via Docker Compose

Run the entire stack (MongoDB, Redis, Backend, and Frontend) in isolated containers:

```bash
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

---

## API Reference

### Authentication
- `POST /api/auth/register` — Register a new project manager account.
- `POST /api/auth/login` — Authenticate and receive a JWT Bearer token.

### Projects & Tasks
- `GET /api/projects` — List user projects.
- `POST /api/projects` — Create a project (`name`, `description`, `start_date`, `target_end_date`).
- `GET /api/projects/{id}/tasks` — List tasks with statuses, deadlines, and dependencies.
- `POST /api/projects/{id}/tasks` — Create a task (automatically indexed into RAG).
- `PATCH /api/projects/{id}/tasks/{task_id}` — Update task status or fields.
- `DELETE /api/projects/{id}/tasks/{task_id}` — Delete a task (removes associated RAG chunks).

### Multi-Agent Analysis
- `POST /api/projects/{id}/analyze` — Run LangGraph multi-agent pipeline (calculates health, schedule/dependency/resource risks, priorities, and weekly narrative summary).
- `GET /api/projects/{id}/analyze/history` — Retrieve historical analysis runs.

### RAG Knowledge Base & Grounded AI Assistant
- `POST /api/projects/{id}/documents` — Upload/index project specification or PRD.
- `GET /api/projects/{id}/documents` — List uploaded documents and vector chunk counts.
- `DELETE /api/projects/{id}/documents/{doc_id}` — Delete document and its vector embeddings.
- `POST /api/projects/{id}/rag/query` — Ask a question grounded in project documents, tasks, and risk reports. Returns answer with source citations.
- `POST /api/projects/{id}/rag/reindex` — Reindexes all documents, tasks, and analysis runs into the vector store.

---

