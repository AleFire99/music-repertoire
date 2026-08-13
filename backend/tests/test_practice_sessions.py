from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient


def _create_piece(client: TestClient, title: str) -> int:
    return client.post("/api/pieces", json={"title": title}).json()["id"]


def _at_days_ago(days: int, hour: int = 10) -> str:
    """ISO timestamp on the UTC calendar date `days` before today, at `hour`."""
    moment = datetime.now(UTC) - timedelta(days=days)
    return moment.strftime("%Y-%m-%dT") + f"{hour:02d}:00:00Z"


def _log_session(client: TestClient, piece_id: int, days_ago: int, hour: int = 10) -> None:
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": _at_days_ago(days_ago, hour),
            "duration_minutes": 10,
        },
    )


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


def _week_start_utc_date() -> date:
    """Monday of the current UTC calendar week (matches the endpoint's convention)."""
    today = datetime.now(UTC).date()
    return today - timedelta(days=today.weekday())


def _month_start_utc_date() -> date:
    today = datetime.now(UTC).date()
    return today.replace(day=1)


def test_create_and_list_practice_session(client: TestClient) -> None:
    piece_id = _create_piece(client, "Clair de Lune")
    payload = {
        "piece_id": piece_id,
        "practiced_at": "2026-08-01T10:00:00Z",
        "duration_minutes": 30,
        "notes": "Worked on the arpeggios",
        "rating": 4,
        "section": "measures 1-16",
    }
    create_response = client.post("/api/practice-sessions", json=payload)
    assert create_response.status_code == 201
    session = create_response.json()
    assert session["piece_id"] == piece_id
    assert session["duration_minutes"] == 30
    assert session["notes"] == "Worked on the arpeggios"
    assert session["rating"] == 4
    assert session["section"] == "measures 1-16"

    list_response = client.get("/api/practice-sessions")
    assert list_response.status_code == 200
    assert [s["id"] for s in list_response.json()] == [session["id"]]


def test_create_session_missing_piece_404(client: TestClient) -> None:
    payload = {
        "piece_id": 999999,
        "practiced_at": "2026-08-01T10:00:00Z",
        "duration_minutes": 15,
    }
    response = client.post("/api/practice-sessions", json=payload)
    assert response.status_code == 404


def test_create_session_invalid_rating_422(client: TestClient) -> None:
    piece_id = _create_piece(client, "Etude")
    payload = {
        "piece_id": piece_id,
        "practiced_at": "2026-08-01T10:00:00Z",
        "duration_minutes": 15,
        "rating": 6,
    }
    response = client.post("/api/practice-sessions", json=payload)
    assert response.status_code == 422


def test_list_sessions_filter_by_piece(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 20},
    )

    response = client.get("/api/practice-sessions", params={"piece_id": piece_a})
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 1
    assert sessions[0]["piece_id"] == piece_a


def test_list_sessions_empty(client: TestClient) -> None:
    response = client.get("/api/practice-sessions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_sessions_ordered_newest_first(client: TestClient) -> None:
    piece_id = _create_piece(client, "Sonata")
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_id, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_id, "practiced_at": "2026-08-03T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_id, "practiced_at": "2026-08-02T10:00:00Z", "duration_minutes": 10},
    )

    response = client.get("/api/practice-sessions")
    dates = [s["practiced_at"] for s in response.json()]
    assert dates == sorted(dates, reverse=True)


def test_stats_empty(client: TestClient) -> None:
    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    assert response.json() == {
        "total_minutes": 0,
        "pieces": [],
        "recently_practiced": [],
        "neglected": [],
        "current_streak_days": 0,
        "longest_streak_days": 0,
        "minutes_this_week": 0,
        "minutes_this_month": 0,
    }


def test_stats_empty_with_pieces_but_no_sessions(client: TestClient) -> None:
    _create_piece(client, "Never Practiced")

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    body = response.json()

    assert body["pieces"] == []
    assert body["recently_practiced"] == []
    assert len(body["neglected"]) == 1
    assert body["neglected"][0]["last_practiced_at"] is None


def test_stats_aggregates_across_pieces(client: TestClient) -> None:
    piece_a = _create_piece(client, "Clair de Lune")
    piece_b = _create_piece(client, "Sonata")

    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 20},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-03T10:00:00Z", "duration_minutes": 15},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-02T10:00:00Z", "duration_minutes": 30},
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    body = response.json()

    assert body["total_minutes"] == 65

    by_id = {p["piece_id"]: p for p in body["pieces"]}
    assert by_id[piece_a]["total_minutes"] == 35
    assert by_id[piece_a]["session_count"] == 2
    assert by_id[piece_a]["last_practiced_at"] == "2026-08-03T10:00:00Z"
    assert by_id[piece_b]["total_minutes"] == 30
    assert by_id[piece_b]["session_count"] == 1

    # ordered by last_practiced_at desc: piece_a (Aug 3) before piece_b (Aug 2)
    assert [p["piece_id"] for p in body["pieces"]] == [piece_a, piece_b]


def test_stats_recently_practiced_ordered_most_recent_first(client: TestClient) -> None:
    piece_a = _create_piece(client, "Clair de Lune")
    piece_b = _create_piece(client, "Sonata")
    piece_c = _create_piece(client, "Etude")

    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-05T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_c, "practiced_at": "2026-08-03T10:00:00Z", "duration_minutes": 10},
    )
    # A second, more recent session on piece_a should make it the most recent overall.
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-10T10:00:00Z", "duration_minutes": 10},
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    recently_practiced = response.json()["recently_practiced"]

    assert [p["piece_id"] for p in recently_practiced] == [piece_a, piece_b, piece_c]
    assert recently_practiced[0]["last_practiced_at"] == "2026-08-10T10:00:00Z"


def test_stats_recently_practiced_capped_at_five(client: TestClient) -> None:
    piece_ids = [_create_piece(client, f"Piece {i}") for i in range(6)]
    for i, piece_id in enumerate(piece_ids):
        client.post(
            "/api/practice-sessions",
            json={
                "piece_id": piece_id,
                "practiced_at": f"2026-08-{i + 1:02d}T10:00:00Z",
                "duration_minutes": 10,
            },
        )

    response = client.get("/api/practice-sessions/stats")
    recently_practiced = response.json()["recently_practiced"]

    assert len(recently_practiced) == 5
    # Most recently created/practiced piece (last one) should be first.
    assert recently_practiced[0]["piece_id"] == piece_ids[-1]


def test_stats_neglected_includes_never_practiced_first(client: TestClient) -> None:
    piece_practiced = _create_piece(client, "Practiced")
    piece_never = _create_piece(client, "Never Practiced")

    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_practiced,
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 10,
        },
    )

    response = client.get("/api/practice-sessions/stats")
    neglected = response.json()["neglected"]

    assert [p["piece_id"] for p in neglected] == [piece_never, piece_practiced]
    assert neglected[0]["last_practiced_at"] is None
    assert neglected[1]["last_practiced_at"] == "2026-08-01T10:00:00Z"


def test_stats_neglected_ordered_oldest_last_practiced_first(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")

    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_a, "practiced_at": "2026-08-05T10:00:00Z", "duration_minutes": 10},
    )
    client.post(
        "/api/practice-sessions",
        json={"piece_id": piece_b, "practiced_at": "2026-08-01T10:00:00Z", "duration_minutes": 10},
    )

    response = client.get("/api/practice-sessions/stats")
    neglected = response.json()["neglected"]

    # piece_b was practiced longer ago than piece_a, so it's more neglected.
    assert [p["piece_id"] for p in neglected] == [piece_b, piece_a]


def test_stats_neglected_capped_at_five(client: TestClient) -> None:
    for i in range(6):
        _create_piece(client, f"Untouched {i}")

    response = client.get("/api/practice-sessions/stats")
    neglected = response.json()["neglected"]

    assert len(neglected) == 5


def test_stats_streak_no_sessions(client: TestClient) -> None:
    response = client.get("/api/practice-sessions/stats")
    body = response.json()

    assert body["current_streak_days"] == 0
    assert body["longest_streak_days"] == 0


def test_stats_streak_single_day(client: TestClient) -> None:
    piece_id = _create_piece(client, "Solo")
    _log_session(client, piece_id, days_ago=0)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["current_streak_days"] == 1
    assert body["longest_streak_days"] == 1


def test_stats_streak_multi_day_consecutive(client: TestClient) -> None:
    piece_id = _create_piece(client, "Consecutive")
    for days_ago in (2, 1, 0):
        _log_session(client, piece_id, days_ago)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["current_streak_days"] == 3
    assert body["longest_streak_days"] == 3


def test_stats_streak_same_day_sessions_counted_once(client: TestClient) -> None:
    piece_id = _create_piece(client, "Same day")
    _log_session(client, piece_id, days_ago=0, hour=9)
    _log_session(client, piece_id, days_ago=0, hour=21)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["current_streak_days"] == 1
    assert body["longest_streak_days"] == 1


def test_stats_streak_broken_by_gap(client: TestClient) -> None:
    piece_id = _create_piece(client, "Broken")
    for days_ago in (10, 9, 8):
        _log_session(client, piece_id, days_ago)
    _log_session(client, piece_id, days_ago=0)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["longest_streak_days"] == 3
    assert body["current_streak_days"] == 1


def test_stats_streak_current_vs_longest_distinction(client: TestClient) -> None:
    piece_id = _create_piece(client, "Past peak")
    for days_ago in (20, 19, 18, 17):
        _log_session(client, piece_id, days_ago)
    _log_session(client, piece_id, days_ago=0)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["longest_streak_days"] == 4
    assert body["current_streak_days"] == 1


def test_stats_streak_zero_when_gap_since_last_session(client: TestClient) -> None:
    piece_id = _create_piece(client, "Stale")
    _log_session(client, piece_id, days_ago=5)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["current_streak_days"] == 0
    assert body["longest_streak_days"] == 1


def test_stats_streak_counts_from_yesterday(client: TestClient) -> None:
    piece_id = _create_piece(client, "Yesterday")
    _log_session(client, piece_id, days_ago=1)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["current_streak_days"] == 1
    assert body["longest_streak_days"] == 1


def test_stats_streak_spans_across_pieces(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")
    _log_session(client, piece_a, days_ago=2)
    _log_session(client, piece_b, days_ago=1)
    _log_session(client, piece_a, days_ago=0)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["current_streak_days"] == 3
    assert body["longest_streak_days"] == 3


def test_stats_minutes_this_week_and_month_count_current_sessions(client: TestClient) -> None:
    piece_id = _create_piece(client, "Current")
    _log_session_at(client, piece_id, _at_days_ago(0), duration_minutes=25)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["minutes_this_week"] == 25
    assert body["minutes_this_month"] == 25


def test_stats_minutes_this_week_excludes_prior_week(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prior week")
    # 7 days ago is always before this week's Monday, regardless of today's weekday.
    _log_session_at(client, piece_id, _at_days_ago(7), duration_minutes=40)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["minutes_this_week"] == 0


def test_stats_minutes_this_month_excludes_prior_month(client: TestClient) -> None:
    piece_id = _create_piece(client, "Prior month")
    # 32 days ago is always before this month's 1st, since no month has 32 days.
    _log_session_at(client, piece_id, _at_days_ago(32), duration_minutes=50)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["minutes_this_month"] == 0


def test_stats_minutes_this_week_boundary(client: TestClient) -> None:
    """Monday 00:00:00 UTC counts as this week; the following Monday does not."""
    piece_id = _create_piece(client, "Week boundary")
    week_start = _week_start_utc_date()
    next_week_start = week_start + timedelta(days=7)

    _log_session_at(client, piece_id, f"{week_start.isoformat()}T00:00:00Z", 15)
    _log_session_at(client, piece_id, f"{next_week_start.isoformat()}T00:00:00Z", 99)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["minutes_this_week"] == 15


def test_stats_sections_empty_for_piece_with_no_sessions(client: TestClient) -> None:
    piece_id = _create_piece(client, "Untouched")

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    body = response.json()

    assert body["pieces"] == []
    assert piece_id  # sanity: piece exists but contributes nothing to `pieces`


def test_stats_sections_distinct_totals(client: TestClient) -> None:
    piece_id = _create_piece(client, "Sonata")
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 20,
            "section": "exposition",
        },
    )
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": "2026-08-02T10:00:00Z",
            "duration_minutes": 5,
            "section": "exposition",
        },
    )
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": "2026-08-03T10:00:00Z",
            "duration_minutes": 15,
            "section": "coda",
        },
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    sections = response.json()["pieces"][0]["sections"]

    assert {(s["section"], s["total_minutes"]) for s in sections} == {
        ("exposition", 25),
        ("coda", 15),
    }
    # ordered by total_minutes desc
    assert [s["section"] for s in sections] == ["exposition", "coda"]


def test_stats_sections_null_and_empty_grouped_as_unspecified(client: TestClient) -> None:
    piece_id = _create_piece(client, "Etude")
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 10,
        },
    )
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": "2026-08-02T10:00:00Z",
            "duration_minutes": 5,
            "section": "",
        },
    )
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_id,
            "practiced_at": "2026-08-03T10:00:00Z",
            "duration_minutes": 7,
            "section": "trills",
        },
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    sections = response.json()["pieces"][0]["sections"]

    assert {(s["section"], s["total_minutes"]) for s in sections} == {
        ("(unspecified)", 15),
        ("trills", 7),
    }


def test_stats_sections_do_not_leak_across_pieces(client: TestClient) -> None:
    piece_a = _create_piece(client, "A")
    piece_b = _create_piece(client, "B")
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_a,
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 10,
            "section": "intro",
        },
    )
    client.post(
        "/api/practice-sessions",
        json={
            "piece_id": piece_b,
            "practiced_at": "2026-08-01T10:00:00Z",
            "duration_minutes": 20,
            "section": "finale",
        },
    )

    response = client.get("/api/practice-sessions/stats")
    assert response.status_code == 200
    by_id = {p["piece_id"]: p for p in response.json()["pieces"]}

    assert [s["section"] for s in by_id[piece_a]["sections"]] == ["intro"]
    assert [s["section"] for s in by_id[piece_b]["sections"]] == ["finale"]


def test_stats_minutes_this_month_boundary(client: TestClient) -> None:
    """The 1st at 00:00:00 UTC counts as this month; the 1st of next month does not."""
    piece_id = _create_piece(client, "Month boundary")
    month_start = _month_start_utc_date()
    next_month_start = (
        month_start.replace(year=month_start.year + 1, month=1)
        if month_start.month == 12
        else month_start.replace(month=month_start.month + 1)
    )

    _log_session_at(client, piece_id, f"{month_start.isoformat()}T00:00:00Z", 12)
    _log_session_at(client, piece_id, f"{next_month_start.isoformat()}T00:00:00Z", 88)

    body = client.get("/api/practice-sessions/stats").json()

    assert body["minutes_this_month"] == 12
