import time

import httpx

from repertoire.config import settings

MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2"
USER_AGENT = "MusicRepertoire/0.1 (personal repertoire-tracking app; solo use)"
HIGH_CONFIDENCE_SCORE = 90
RATE_LIMIT_DELAY_SECONDS = 1.1
REQUEST_TIMEOUT_SECONDS = 5.0


def find_composer_for_title(title: str) -> str | None:
    """Look up a work by title and return a composer name on a high-confidence match.

    Best-effort only: any network error, timeout, missing match, or malformed
    response returns None rather than raising, so it never blocks piece creation.
    """
    if not settings.musicbrainz_enabled:
        return None

    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS, headers=headers) as client:
            search_response = client.get(
                f"{MUSICBRAINZ_BASE_URL}/work",
                params={"query": f'work:"{title}"', "fmt": "json"},
            )
            search_response.raise_for_status()
            works = search_response.json().get("works", [])
            if not works:
                return None

            top_work = works[0]
            if top_work.get("score", 0) < HIGH_CONFIDENCE_SCORE:
                return None

            mbid = top_work.get("id")
            if not mbid:
                return None

            time.sleep(RATE_LIMIT_DELAY_SECONDS)

            work_response = client.get(
                f"{MUSICBRAINZ_BASE_URL}/work/{mbid}",
                params={"inc": "artist-rels", "fmt": "json"},
            )
            work_response.raise_for_status()
            relations = work_response.json().get("relations", [])
            for relation in relations:
                if relation.get("type") == "composer":
                    name = relation.get("artist", {}).get("name")
                    if name:
                        return str(name)
            return None
    except (httpx.HTTPError, ValueError, KeyError):
        return None
