import time


def test_create_task_logs_created_event(client):
    response = client.post("/tasks", json={"title": "New task"})
    assert response.status_code == 201
    task_id = response.json()["id"]

    activity = client.get("/activity").json()
    assert len(activity) == 1
    assert activity[0]["task_id"] == task_id
    assert activity[0]["action"] == "created"
    assert "id" in activity[0]
    assert "details" in activity[0]
    assert "timestamp" in activity[0]


def test_update_task_logs_updated_event(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "Renamed task"})
    assert response.status_code == 200

    activity = client.get(f"/tasks/{task_id}/activity").json()
    actions = [event["action"] for event in activity]
    assert "updated" in actions


def test_delete_task_logs_deleted_event(client, created_task):
    task_id = created_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    activity = client.get("/activity").json()
    deleted_events = [e for e in activity if e["action"] == "deleted"]
    assert len(deleted_events) == 1
    assert deleted_events[0]["task_id"] == task_id


def test_status_change_logs_status_changed_event(client, created_task):
    task_id = created_task["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})

    activity = client.get(f"/tasks/{task_id}/activity").json()
    status_events = [e for e in activity if e["action"] == "status_changed"]
    assert len(status_events) == 1
    assert "InProgress" in status_events[0]["details"]


def test_get_activity_returns_most_recent_first(client):
    client.post("/tasks", json={"title": "First"})
    time.sleep(0.01)
    client.post("/tasks", json={"title": "Second"})

    activity = client.get("/activity").json()
    assert len(activity) >= 2
    timestamps = [event["timestamp"] for event in activity]
    assert timestamps == sorted(timestamps, reverse=True)


def test_get_task_activity_returns_only_that_tasks_events(client):
    first = client.post("/tasks", json={"title": "Task A"}).json()
    second = client.post("/tasks", json={"title": "Task B"}).json()
    client.patch(f"/tasks/{first['id']}", json={"title": "Task A updated"})

    activity = client.get(f"/tasks/{first['id']}/activity").json()
    assert all(event["task_id"] == first["id"] for event in activity)
    assert second["id"] not in {event["task_id"] for event in activity}


def test_get_task_activity_not_found_returns_404(client):
    task_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/tasks/{task_id}/activity")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Task with id {task_id} not found"