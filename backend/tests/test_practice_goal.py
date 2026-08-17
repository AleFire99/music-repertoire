from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def _week_start_utc_date() -> date:
    """Monday of the current UTC calendar week (matches the endpoint's convention)."""
    today = datetime.now(UTC).date()
    return today - timedelta(days=today.weekday())


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
    week_start = _week_start_utc_date()
    # Both anchored to this week's Monday, so they land in the current week
    # regardless of which weekday the test actually runs on.
    _log_session_at(client, piece_id, f"{week_start.isoformat()}T01:00:00Z", duration_minutes=90)
    _log_session_at(client, piece_id, f"{week_start.isoformat()}T02:00:00Z", duration_minutes=30)
    # 7 days before this week's Monday — always in the prior week, must not count.
    _log_session_at(
        client, piece_id, f"{(week_start - timedelta(days=7)).isoformat()}T10:00:00Z", 1000
    )

    client.put("/api/practice-goal", json={"target_minutes": 300})

    response = client.get("/api/practice-goal")
    assert response.status_code == 200
    body = response.json()
    assert body["target_minutes"] == 300
    assert body["minutes_this_week"] == 120
