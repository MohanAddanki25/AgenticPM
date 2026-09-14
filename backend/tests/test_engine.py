"""
Unit tests for the deterministic rule engine, including the exact
dependency-delay-propagation scenario from the project spec:
Backend API (done) -> Frontend integration (in progress, due soon)
-> Testing (not started, depends on frontend integration).
"""
from datetime import date, timedelta

from app.agents import engine


def make_tasks(today: date):
    return [
        {
            "id": "t1", "name": "Backend API", "status": "Completed",
            "due_date": today - timedelta(days=2), "depends_on": [],
        },
        {
            "id": "t2", "name": "Frontend integration", "status": "In Progress",
            "due_date": today, "depends_on": ["Backend API"],
        },
        {
            "id": "t3", "name": "Testing", "status": "Not Started",
            "due_date": today + timedelta(days=1), "depends_on": ["Frontend integration"],
        },
    ]


def test_dependency_graph_maps_downstream_correctly():
    today = date.today()
    tasks = make_tasks(today)
    downstream = engine.build_dependency_graph(tasks)
    by_id = {t["id"]: t for t in tasks}
    impact = engine.get_downstream_impact("t2", downstream, by_id)
    assert impact == ["Testing"]


def test_dependency_risk_detected_when_upstream_task_not_completed():
    today = date.today()
    tasks = make_tasks(today)
    project = {"target_end_date": today + timedelta(days=2)}
    risks = engine.detect_risks(tasks, project)

    dep_risks = [r for r in risks if r["type"] == "dependency" and r["task_name"] == "Testing"]
    assert len(dep_risks) == 1
    risk = dep_risks[0]
    assert "Frontend integration" in risk["description"]
    assert any("depends_on" in e for e in risk["evidence"])


def test_delivery_risk_raised_when_high_or_critical_risks_exist():
    today = date.today()
    tasks = make_tasks(today)
    project = {"target_end_date": today + timedelta(days=2)}
    risks = engine.detect_risks(tasks, project)
    delivery_risks = [r for r in risks if r["type"] == "delivery"]
    assert len(delivery_risks) == 1


def test_project_health_reflects_risk_severity():
    today = date.today()
    tasks = make_tasks(today)
    project = {"target_end_date": today + timedelta(days=2)}
    risks = engine.detect_risks(tasks, project)
    health, explanation = engine.compute_project_health(tasks, risks)
    assert health in ("At Risk", "Delayed")
    assert explanation


def test_priorities_rank_dependency_blocking_task_highly():
    today = date.today()
    tasks = make_tasks(today)
    project = {"target_end_date": today + timedelta(days=2)}
    risks = engine.detect_risks(tasks, project)
    priorities = engine.compute_priorities(tasks, risks)
    names = [p["task_name"] for p in priorities]
    assert "Frontend integration" in names
    assert "Testing" in names
    # Completed task should not appear
    assert "Backend API" not in names


def test_next_actions_reference_dependency_chain():
    today = date.today()
    tasks = make_tasks(today)
    project = {"target_end_date": today + timedelta(days=2)}
    risks = engine.detect_risks(tasks, project)
    priorities = engine.compute_priorities(tasks, risks)
    actions = engine.compute_next_actions(tasks, risks, priorities)
    assert len(actions) > 0


def test_no_risks_when_all_tasks_completed_on_time():
    today = date.today()
    tasks = [
        {"id": "t1", "name": "A", "status": "Completed", "due_date": today - timedelta(days=1), "depends_on": []},
        {"id": "t2", "name": "B", "status": "Completed", "due_date": today, "depends_on": ["A"]},
    ]
    project = {"target_end_date": today + timedelta(days=5)}
    risks = engine.detect_risks(tasks, project)
    assert risks == []
    health, _ = engine.compute_project_health(tasks, risks)
    assert health == "On Track"
