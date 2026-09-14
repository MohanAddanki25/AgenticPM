"""
Deterministic, explainable rule-engine that powers every agent.

Every risk, priority score and recommendation produced here carries an
`evidence` list of the exact raw data points (task name, due date, status,
dependency chain) that produced it. This guarantees the "AI-generated risks
and priority recommendations must be explainable using project data"
requirement, independent of whether an LLM is available - the LLM (see
services/llm.py) only rephrases this already-computed output, it never
invents it.
"""
from datetime import date, datetime, timezone
from typing import Dict, List

TODAY = date.today


def _days_between(a: date, b: date) -> int:
    return (a - b).days


def build_dependency_graph(tasks: List[dict]) -> Dict[str, List[str]]:
    """Map task_id -> list of task_ids that depend on it (downstream)."""
    by_name = {t["name"]: t for t in tasks}
    downstream: Dict[str, List[str]] = {t["id"]: [] for t in tasks}
    for t in tasks:
        for dep_name in t.get("depends_on", []):
            dep_task = by_name.get(dep_name)
            if dep_task:
                downstream.setdefault(dep_task["id"], []).append(t["id"])
    return downstream


def get_downstream_impact(task_id: str, downstream_map: Dict[str, List[str]], tasks_by_id: Dict[str, dict]) -> List[str]:
    """BFS to find every task transitively blocked by `task_id` being late."""
    visited = []
    queue = list(downstream_map.get(task_id, []))
    seen = set(queue)
    while queue:
        current = queue.pop(0)
        visited.append(tasks_by_id[current]["name"])
        for nxt in downstream_map.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return visited


def detect_risks(tasks: List[dict], project: dict) -> List[dict]:
    risks = []
    today = TODAY()
    by_id = {t["id"]: t for t in tasks}
    downstream_map = build_dependency_graph(tasks)
    rid = 0

    for t in tasks:
        due = t["due_date"] if isinstance(t["due_date"], date) else datetime.fromisoformat(str(t["due_date"])).date()
        status = t["status"]
        overdue_days = _days_between(today, due)

        # --- Schedule risk: overdue and not completed ---
        if status != "Completed" and overdue_days > 0:
            rid += 1
            risks.append({
                "id": f"R{rid}",
                "type": "schedule",
                "severity": "Critical" if overdue_days >= 3 else "High",
                "task_id": t["id"],
                "task_name": t["name"],
                "description": (
                    f"Task '{t['name']}' was due on {due.isoformat()} and is {overdue_days} "
                    f"day(s) overdue while still marked '{status}'."
                ),
                "evidence": [
                    f"Task '{t['name']}' due_date = {due.isoformat()}",
                    f"Today = {today.isoformat()}",
                    f"Current status = '{status}'",
                    f"Overdue by {overdue_days} day(s)",
                ],
                "affected_tasks": get_downstream_impact(t["id"], downstream_map, by_id),
            })
        # --- Schedule risk: due very soon but not started ---
        elif status == "Not Started" and 0 <= overdue_days >= 0 and (due - today).days <= 2:
            rid += 1
            risks.append({
                "id": f"R{rid}",
                "type": "schedule",
                "severity": "High" if (due - today).days <= 1 else "Medium",
                "task_id": t["id"],
                "task_name": t["name"],
                "description": (
                    f"Task '{t['name']}' is due in {(due - today).days} day(s) "
                    f"({due.isoformat()}) but has not started."
                ),
                "evidence": [
                    f"Task '{t['name']}' status = 'Not Started'",
                    f"Due date = {due.isoformat()} ({(due - today).days} day(s) from today)",
                ],
                "affected_tasks": get_downstream_impact(t["id"], downstream_map, by_id),
            })

        # --- Blocked task risk ---
        if status == "Blocked":
            rid += 1
            risks.append({
                "id": f"R{rid}",
                "type": "resource",
                "severity": "High",
                "task_id": t["id"],
                "task_name": t["name"],
                "description": f"Task '{t['name']}' is explicitly marked as Blocked.",
                "evidence": [
                    f"Task '{t['name']}' status = 'Blocked'",
                    f"Notes: {t.get('resource_notes') or 'none provided'}",
                ],
                "affected_tasks": get_downstream_impact(t["id"], downstream_map, by_id),
            })

        # --- Dependency risk: this task depends on a not-yet-completed upstream task
        #     whose own timeline threatens this task's due date ---
        for dep_name in t.get("depends_on", []):
            dep_task = next((x for x in tasks if x["name"] == dep_name), None)
            if not dep_task:
                continue
            dep_due = dep_task["due_date"] if isinstance(dep_task["due_date"], date) else datetime.fromisoformat(str(dep_task["due_date"])).date()
            dep_status = dep_task["status"]
            if dep_status != "Completed":
                dep_overdue = _days_between(today, dep_due)
                gap_days = _days_between(due, dep_due)  # how much slack between dep due and this task's due
                will_likely_slip = dep_overdue > 0 or dep_status in ("Blocked", "Delayed") or gap_days <= 1
                if will_likely_slip:
                    rid += 1
                    severity = "Critical" if (dep_overdue > 0 and gap_days <= 1) else "High"
                    risks.append({
                        "id": f"R{rid}",
                        "type": "dependency",
                        "severity": severity,
                        "task_id": t["id"],
                        "task_name": t["name"],
                        "description": (
                            f"'{t['name']}' (due {due.isoformat()}) depends on '{dep_name}' "
                            f"which is currently '{dep_status}' (due {dep_due.isoformat()}"
                            f"{', ' + str(dep_overdue) + ' day(s) overdue' if dep_overdue > 0 else ''}). "
                            f"A delay in '{dep_name}' may push back the start of '{t['name']}' "
                            f"and any tasks that depend on it, threatening final delivery."
                        ),
                        "evidence": [
                            f"'{t['name']}' depends_on = '{dep_name}'",
                            f"'{dep_name}' status = '{dep_status}', due_date = {dep_due.isoformat()}",
                            f"'{t['name']}' due_date = {due.isoformat()} (only {gap_days} day(s) of slack after dependency due date)",
                        ],
                        "affected_tasks": get_downstream_impact(t["id"], downstream_map, by_id) or [t["name"]],
                    })

    # --- Delivery risk: project target end date threatened by any critical/high risk chain ---
    target_end = project.get("target_end_date")
    if target_end:
        target_end = target_end if isinstance(target_end, date) else datetime.fromisoformat(str(target_end)).date()
        blocking_risks = [r for r in risks if r["severity"] in ("High", "Critical")]
        if blocking_risks:
            rid += 1
            involved = sorted({r["task_name"] for r in blocking_risks if r["task_name"]})
            risks.append({
                "id": f"R{rid}",
                "type": "delivery",
                "severity": "Critical" if any(r["severity"] == "Critical" for r in blocking_risks) else "High",
                "task_id": None,
                "task_name": None,
                "description": (
                    f"Project target delivery date {target_end.isoformat()} is at risk due to "
                    f"{len(blocking_risks)} unresolved high/critical risk(s) involving: {', '.join(involved)}."
                ),
                "evidence": [f"High/Critical risk on: {name}" for name in involved]
                + [f"Project target_end_date = {target_end.isoformat()}"],
                "affected_tasks": involved,
            })

    return risks


def compute_project_health(tasks: List[dict], risks: List[dict]) -> tuple[str, str]:
    critical = [r for r in risks if r["severity"] == "Critical"]
    high = [r for r in risks if r["severity"] == "High"]
    delayed = [t for t in tasks if t["status"] in ("Delayed", "Blocked")]

    if critical or len(delayed) >= 2:
        return "Delayed", (
            f"{len(critical)} critical risk(s) and {len(delayed)} delayed/blocked task(s) "
            f"detected. Immediate intervention required to protect the delivery date."
        )
    if high or delayed:
        return "At Risk", (
            f"{len(high)} high-severity risk(s) detected"
            + (f" and {len(delayed)} task(s) delayed/blocked" if delayed else "")
            + ". Project can still recover with prompt action on flagged items."
        )
    return "On Track", "No critical or high-severity risks detected; all tasks are progressing against their due dates."


def compute_priorities(tasks: List[dict], risks: List[dict]) -> List[dict]:
    """Score each incomplete task using: overdue-ness, number of blocked
    downstream tasks, whether it has dependency/blocker risks, proximity to due date."""
    today = TODAY()
    downstream_map = build_dependency_graph(tasks)
    by_id = {t["id"]: t for t in tasks}
    risks_by_task: Dict[str, List[dict]] = {}
    for r in risks:
        if r.get("task_id"):
            risks_by_task.setdefault(r["task_id"], []).append(r)

    severity_weight = {"Critical": 40, "High": 25, "Medium": 10, "Low": 3}
    priorities = []
    for t in tasks:
        if t["status"] == "Completed":
            continue
        due = t["due_date"] if isinstance(t["due_date"], date) else datetime.fromisoformat(str(t["due_date"])).date()
        days_to_due = (due - today).days
        task_risks = risks_by_task.get(t["id"], [])
        downstream_count = len(get_downstream_impact(t["id"], downstream_map, by_id))

        score = 0.0
        evidence = []
        for r in task_risks:
            score += severity_weight.get(r["severity"], 0)
            evidence.append(f"Risk [{r['severity']}/{r['type']}]: {r['description']}")

        score += downstream_count * 8
        if downstream_count:
            evidence.append(f"{downstream_count} downstream task(s) depend on this task completing on time")

        if days_to_due < 0:
            score += min(abs(days_to_due) * 5, 30)
            evidence.append(f"Overdue by {abs(days_to_due)} day(s)")
        elif days_to_due <= 1:
            score += 15
            evidence.append(f"Due within {days_to_due} day(s)")

        if t["status"] == "Blocked":
            score += 20
            evidence.append("Task is currently Blocked")

        if not evidence:
            evidence.append(f"Status '{t['status']}', due {due.isoformat()}, no active risks")

        if score >= 60:
            level = "Urgent"
        elif score >= 35:
            level = "High"
        elif score >= 15:
            level = "Medium"
        else:
            level = "Low"

        priorities.append({
            "task_id": t["id"],
            "task_name": t["name"],
            "priority_score": round(score, 1),
            "priority_level": level,
            "reason": (
                f"Priority '{level}' driven by "
                + (f"{len(task_risks)} active risk(s), " if task_risks else "")
                + f"{downstream_count} downstream dependent task(s), and due date proximity."
            ),
            "evidence": evidence,
        })

    priorities.sort(key=lambda p: p["priority_score"], reverse=True)
    return priorities


def compute_next_actions(tasks: List[dict], risks: List[dict], priorities: List[dict]) -> List[dict]:
    actions = []
    top_priorities = [p for p in priorities if p["priority_level"] in ("Urgent", "High")][:5]
    by_id = {t["id"]: t for t in tasks}

    for p in top_priorities:
        task = by_id.get(p["task_id"])
        if not task:
            continue
        if task["status"] == "Blocked":
            action_text = f"Unblock '{task['name']}' immediately - it is holding up dependent work."
        elif task["status"] == "Not Started" and p["priority_level"] == "Urgent":
            action_text = f"Start '{task['name']}' today; it is on the critical path and overdue-risk."
        else:
            action_text = f"Escalate and closely track '{task['name']}' to prevent further slippage."
        actions.append({
            "action": action_text,
            "owner": task.get("assignee") or "Unassigned - needs owner",
            "related_task": task["name"],
            "urgency": p["priority_level"],
        })

    dep_risks = [r for r in risks if r["type"] == "dependency"]
    for r in dep_risks[:3]:
        actions.append({
            "action": (
                f"Review dependency chain for '{r['task_name']}': confirm recovery plan so "
                f"downstream tasks ({', '.join(r['affected_tasks']) or 'none'}) are not delayed."
            ),
            "owner": "Project Manager",
            "related_task": r["task_name"],
            "urgency": r["severity"],
        })

    return actions
