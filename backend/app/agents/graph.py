"""
Multi-agent workflow built with LangGraph.

Pipeline:
  Project Planning Agent
        -> Progress Monitoring Agent
        -> Dependency Agent
        -> Risk Detection Agent
        -> Prioritization Agent
        -> Reporting / Reviewer Agent

Each node mutates a shared typed state (AgentState). All numeric/structural
decisions come from the deterministic engine (app/agents/engine.py) so
outputs stay explainable; the Reporting agent is the only node that calls
the LLM (services/llm.py), purely to phrase already-computed facts.
"""
import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from app.agents import engine
from app.services.llm import generate_narrative, is_llm_available

logger = logging.getLogger("agent_graph")


class AgentState(TypedDict, total=False):
    project: dict
    tasks: List[dict]
    milestones: List[dict]
    task_status_summary: dict
    upcoming_deadlines: List[dict]
    delayed_tasks: List[dict]
    dependency_graph: List[dict]
    critical_blockers: List[dict]
    risks: List[dict]
    priorities: List[dict]
    next_actions: List[dict]
    project_health: str
    health_explanation: str
    weekly_summary: str
    trace: List[str]  # execution trace for transparency / debugging


def _log(state: AgentState, msg: str):
    state.setdefault("trace", []).append(msg)
    logger.info(msg)


# ---------------- Agent Nodes ----------------

def planning_agent(state: AgentState) -> AgentState:
    """Project Planning Agent: evaluates scope, builds milestone list from tasks."""
    tasks = state["tasks"]
    milestones = [
        {
            "name": t["name"],
            "due_date": str(t["due_date"]),
            "status": t["status"],
        }
        for t in tasks
    ]
    state["milestones"] = milestones
    _log(state, f"Planning Agent: evaluated {len(tasks)} task(s) as project milestones.")
    return state


def progress_agent(state: AgentState) -> AgentState:
    """Progress Monitoring Agent: tracks completed / pending / delayed / blocked counts."""
    tasks = state["tasks"]
    today = date.today()
    summary = {"Completed": 0, "In Progress": 0, "Not Started": 0, "Blocked": 0, "Delayed": 0}
    delayed_tasks = []
    upcoming = []
    for t in tasks:
        summary[t["status"]] = summary.get(t["status"], 0) + 1
        due = t["due_date"] if isinstance(t["due_date"], date) else datetime.fromisoformat(str(t["due_date"])).date()
        if t["status"] != "Completed" and due < today:
            delayed_tasks.append({
                "task_name": t["name"], "due_date": str(due), "status": t["status"],
                "overdue_days": (today - due).days,
            })
        elif t["status"] != "Completed" and 0 <= (due - today).days <= 7:
            upcoming.append({"task_name": t["name"], "due_date": str(due), "status": t["status"]})

    state["task_status_summary"] = summary
    state["delayed_tasks"] = delayed_tasks
    state["upcoming_deadlines"] = sorted(upcoming, key=lambda x: x["due_date"])
    _log(state, f"Progress Agent: {len(delayed_tasks)} delayed, {len(upcoming)} due within 7 days.")
    return state


def dependency_agent(state: AgentState) -> AgentState:
    """Dependency Agent: builds dependency graph and downstream impact map."""
    tasks = state["tasks"]
    by_id = {t["id"]: t for t in tasks}
    downstream_map = engine.build_dependency_graph(tasks)
    graph_out = []
    blockers = []
    for t in tasks:
        if t.get("depends_on"):
            impact = engine.get_downstream_impact(t["id"], downstream_map, by_id)
            graph_out.append({
                "task": t["name"],
                "depends_on": t["depends_on"],
                "status": t["status"],
                "downstream_impact": impact,
            })
        if t["status"] == "Blocked":
            blockers.append({
                "task_name": t["name"],
                "reason": t.get("resource_notes") or "Marked Blocked",
                "downstream_impact": engine.get_downstream_impact(t["id"], downstream_map, by_id),
            })
    state["dependency_graph"] = graph_out
    state["critical_blockers"] = blockers
    _log(state, f"Dependency Agent: mapped {len(graph_out)} dependency edge(s), {len(blockers)} blocker(s).")
    return state


def risk_agent(state: AgentState) -> AgentState:
    """Risk Detection Agent: schedule / dependency / resource / delivery risks."""
    risks = engine.detect_risks(state["tasks"], state["project"])
    state["risks"] = risks
    health, explanation = engine.compute_project_health(state["tasks"], risks)
    state["project_health"] = health
    state["health_explanation"] = explanation
    _log(state, f"Risk Agent: detected {len(risks)} risk(s). Project health = {health}.")
    return state


def prioritization_agent(state: AgentState) -> AgentState:
    """Prioritization Agent: scores tasks needing immediate attention."""
    priorities = engine.compute_priorities(state["tasks"], state["risks"])
    next_actions = engine.compute_next_actions(state["tasks"], state["risks"], priorities)
    state["priorities"] = priorities
    state["next_actions"] = next_actions
    _log(state, f"Prioritization Agent: ranked {len(priorities)} open task(s), produced {len(next_actions)} action(s).")
    return state


def reporting_agent(state: AgentState) -> AgentState:
    """Reporting / Reviewer Agent: validates recommendations against data and
    generates the weekly narrative summary (via LLM if available, else a
    deterministic template built purely from computed facts)."""
    project = state["project"]
    risks = state["risks"]
    priorities = state["priorities"]

    # Reviewer / validation step: ensure every risk references real evidence
    # grounded in the actual task list (guards against any future LLM misuse).
    valid_task_names = {t["name"] for t in state["tasks"]}
    for r in risks:
        if r.get("task_name") and r["task_name"] not in valid_task_names:
            logger.error("Reviewer Agent: risk references unknown task %s - dropping.", r["task_name"])
    state["risks"] = [r for r in risks if not r.get("task_name") or r["task_name"] in valid_task_names]

    fallback_summary = (
        f"Project '{project['name']}' is currently '{state['project_health']}'. "
        f"{state['health_explanation']} "
        f"Task status breakdown: {state['task_status_summary']}. "
        f"{len(state['delayed_tasks'])} task(s) are delayed. "
        f"{len(risks)} risk(s) identified "
        f"({sum(1 for r in risks if r['severity'] in ('High','Critical'))} high/critical). "
        f"Top priority items: "
        + ", ".join(p["task_name"] for p in priorities[:3]) if priorities else "no open tasks."
    )

    prompt = (
        f"Project: {project['name']}\n"
        f"Health status: {state['project_health']}\n"
        f"Health explanation: {state['health_explanation']}\n"
        f"Task status summary: {state['task_status_summary']}\n"
        f"Delayed tasks: {[d['task_name'] for d in state['delayed_tasks']]}\n"
        f"Risks: {[r['description'] for r in risks]}\n"
        f"Top priorities: {[p['task_name'] + ' (' + p['priority_level'] + ')' for p in priorities[:5]]}\n"
        f"Next actions: {[a['action'] for a in state['next_actions']]}\n\n"
        "Write a concise weekly project status summary (4-6 sentences) for a "
        "project manager, based ONLY on the facts above."
    )
    state["weekly_summary"] = generate_narrative(prompt, fallback_summary)
    _log(state, f"Reporting Agent: validated {len(state['risks'])} risk(s), generated weekly summary (llm_used={is_llm_available()}).")
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planning", planning_agent)
    graph.add_node("progress", progress_agent)
    graph.add_node("dependency", dependency_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("prioritization", prioritization_agent)
    graph.add_node("reporting", reporting_agent)

    graph.set_entry_point("planning")
    graph.add_edge("planning", "progress")
    graph.add_edge("progress", "dependency")
    graph.add_edge("dependency", "risk")
    graph.add_edge("risk", "prioritization")
    graph.add_edge("prioritization", "reporting")
    graph.add_edge("reporting", END)
    return graph.compile()


_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_analysis(project: dict, tasks: List[dict]) -> AgentState:
    initial_state: AgentState = {"project": project, "tasks": tasks, "trace": []}
    graph = get_compiled_graph()
    result = graph.invoke(initial_state)
    return result
