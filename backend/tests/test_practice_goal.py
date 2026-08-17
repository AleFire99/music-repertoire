from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from repertoire.date_utils import current_week_bounds


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def _at_days_ago(days: int, hour: int = 10) -> str:
    """ISO timestamp on the UTC calendar date `days` before today, at `hour`."""
    moment = datetime.now(UTC) - timedelta(days=days)
    return moment.strftime("%Y-%m-%dT") + f"{hour:02d}:00:00Z"


def _log_session_at(
    client: TestClient, piece_id: int, practiced_at: str, duration_minutes: int
) -> None:
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": practiced_at,
            "duration_minutes": duration_minutes,
        },
    )


def _log_session(client: TestClient, piece_id: int, days_ago: int, duration_minutes: int) -> None:
    _log_session_at(client, piece_id, _at_days_ago(days_ago), duration_minutes)


def test_get_goal_returns_null_when_none_set(client: TestClient) -> None:
    response = client.get("/api/practice-goal")
    assert response.status_code == 200
    assert response.json() is None


def test_set_goal_creates_it(client: TestClient) -> None:
    response = client.put("/api/practice-goal", json={"target_minutes": 300})
    assert response.status_code == 200
    body = response.json()
    assert body["target_minutes"] == 300
    assert body["minutes_this_week"] == 0
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_get_goal_returns_previously_set_goal(client: TestClient) -> None:
    client.put("/api/practice-goal", json={"target_minutes": 300})

    response = client.get("/api/practice-goal")
    assert response.status_code == 200
    assert response.json()["target_minutes"] == 300


def test_set_goal_twice_replaces_not_duplicates(client: TestClient) -> None:
    first = client.put("/api/practice-goal", json={"target_minutes": 300}).json()
    second = client.put("/api/practice-goal", json={"target_minutes": 450}).json()

    assert first["id"] == second["id"]
    assert second["target_minutes"] == 450

    response = client.get("/api/practice-goal")
    assert response.json()["target_minutes"] == 450


def test_set_goal_rejects_non_positive_target(client: TestClient) -> None:
    response = client.put("/api/practice-goal", json={"target_minutes": 0})
    assert response.status_code == 422


def test_goal_progress_reflects_minutes_this_week(client: TestClient) -> None:
    piece_id = _create_piece(client, "Etude")
    week_start, _ = current_week_bounds(datetime.now(UTC).date())
    _log_session_at(client, piece_id, week_start.isoformat().replace("+00:00", "Z"), 90)
    _log_session_at(
        client,
        piece_id,
        (week_start + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        30,
    )
    # Outside the current week — must not count toward progress.
    _log_session(client, piece_id, days_ago=7, duration_minutes=1000)

    client.put("/api/practice-goal", json={"target_minutes": 300})

    response = client.get("/api/practice-goal")
    assert response.status_code == 200
    body = response.json()
    assert body["target_minutes"] == 300
    assert body["minutes_this_week"] == 120
