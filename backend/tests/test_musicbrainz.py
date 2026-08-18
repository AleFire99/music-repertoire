from collections.abc import Generator

import httpx
import pytest

from repertoire import musicbrainz
from repertoire.config import settings


@pytest.fixture(autouse=True)
def _musicbrainz_enabled() -> Generator[None, None, None]:
    original = settings.musicbrainz_enabled
    settings.musicbrainz_enabled = True
    try:
        yield
    finally:
        settings.musicbrainz_enabled = original


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class FakeClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, dict]] = []

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def get(self, url: str, params: dict | None = None) -> FakeResponse:
        self.calls.append((url, params or {}))
        return self._responses.pop(0)


class RaisingClient:
    def __enter__(self) -> "RaisingClient":
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def get(self, url: str, params: dict | None = None) -> FakeResponse:
        raise httpx.ConnectError("connection refused")


def _install_fake_client(monkeypatch: pytest.MonkeyPatch, client: object) -> None:
    monkeypatch.setattr(musicbrainz.httpx, "Client", lambda **kwargs: client)
    monkeypatch.setattr(musicbrainz.time, "sleep", lambda *_: None)


def test_high_confidence_match_returns_composer(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeClient(
        [
            FakeResponse({"works": [{"id": "mbid-1", "score": 95}]}),
            FakeResponse(
                {
                    "relations": [
                        {"type": "composer", "artist": {"name": "Ludwig van Beethoven"}}
                    ]
                }
            ),
        ]
    )
    _install_fake_client(monkeypatch, fake)

    result = musicbrainz.find_composer_for_title("Moonlight Sonata")

    assert result == "Ludwig van Beethoven"
    assert len(fake.calls) == 2


def test_low_confidence_match_skips_followup(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeClient([FakeResponse({"works": [{"id": "mbid-1", "score": 40}]})])
    _install_fake_client(monkeypatch, fake)

    result = musicbrainz.find_composer_for_title("Some Ambiguous Title")

    assert result is None
    assert len(fake.calls) == 1


def test_no_matches_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeClient([FakeResponse({"works": []})])
    _install_fake_client(monkeypatch, fake)

    result = musicbrainz.find_composer_for_title("Untitled piece")

    assert result is None


def test_no_composer_relation_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeClient(
        [
            FakeResponse({"works": [{"id": "mbid-1", "score": 100}]}),
            FakeResponse({"relations": [{"type": "lyricist", "artist": {"name": "Someone"}}]}),
        ]
    )
    _install_fake_client(monkeypatch, fake)

    result = musicbrainz.find_composer_for_title("Some Title")

    assert result is None


def test_network_error_degrades_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_client(monkeypatch, RaisingClient())

    result = musicbrainz.find_composer_for_title("Some Title")

    assert result is None


def test_disabled_setting_short_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.musicbrainz_enabled = False

    def _fail_client(**kwargs: object) -> None:
        raise AssertionError("httpx.Client should not be constructed when disabled")

    monkeypatch.setattr(musicbrainz.httpx, "Client", _fail_client)

    result = musicbrainz.find_composer_for_title("Some Title")

    assert result is None
