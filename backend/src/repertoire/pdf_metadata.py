import io
import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

TOP_FRACTION = 0.4
LINE_TOLERANCE = 2.0
MAX_COMPOSER_LINE_LENGTH = 60
COMPOSER_LOOKAHEAD_LINES = 3
MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 120

# Some notation-software exports draw title text as duplicated/overlapping glyphs
# for a faux-bold effect (confirmed against real files: repeated same-character
# draws land within ~0.24pt of each other, while genuine adjacent-character
# advances are never below ~2.2pt at these font sizes) — collapse those before
# joining a line's text.
DUPLICATE_GLYPH_X_TOLERANCE = 1.0

# Matches the "Composer - Title" filename convention, including en/em-dash
# variants, but only when the separator is surrounded by spaces — this keeps
# compound-hyphenated slugs like "bach-aria-quarta-corda.pdf" from being
# mis-split.
FILENAME_SEPARATOR_RE = re.compile(r"\s[-–—]\s")

TEMPO_MARKINGS = {
    "adagio",
    "allegretto",
    "allegro",
    "andante",
    "andantino",
    "grave",
    "largo",
    "larghetto",
    "lento",
    "maestoso",
    "moderato",
    "presto",
    "prestissimo",
    "sostenuto",
    "vivace",
}

COMPOSER_PREFIX_RE = re.compile(r"^(?:by|arr\.?|arranged by|music by)\s+(.+)$", re.IGNORECASE)


@dataclass
class _Line:
    text: str
    font_size: float
    top: float


def _lines_from_chars(chars: list[dict]) -> list[_Line]:
    printable = [c for c in chars if c.get("text", "") != ""]
    if not printable:
        return []
    printable.sort(key=lambda c: (c["top"], c["x0"]))

    groups: list[list[dict]] = []
    current: list[dict] = []
    current_top: float | None = None
    for ch in printable:
        if current_top is None or abs(ch["top"] - current_top) <= LINE_TOLERANCE:
            current.append(ch)
            current_top = ch["top"] if current_top is None else current_top
        else:
            groups.append(current)
            current = [ch]
            current_top = ch["top"]
    if current:
        groups.append(current)

    lines = []
    for group in groups:
        group.sort(key=lambda c: c["x0"])
        deduped = _dedupe_overlapping_glyphs(group)
        text = "".join(c["text"] for c in deduped).strip()
        if not text:
            continue
        lines.append(
            _Line(
                text=text,
                font_size=max(c["size"] for c in group),
                top=min(c["top"] for c in group),
            )
        )
    return lines


def _dedupe_overlapping_glyphs(group: list[dict]) -> list[dict]:
    """Collapse consecutive same-character draws at (near-)identical x0.

    `group` must already be sorted by x0. Requiring matching text (not just
    proximity) avoids collapsing legitimate adjacent characters that happen to
    sit close together.
    """
    deduped: list[dict] = []
    for ch in group:
        if (
            deduped
            and ch["text"] == deduped[-1]["text"]
            and abs(ch["x0"] - deduped[-1]["x0"]) <= DUPLICATE_GLYPH_X_TOLERANCE
        ):
            continue
        deduped.append(ch)
    return deduped


def _is_plausible_title(text: str) -> bool:
    text = text.strip()
    if not (MIN_TITLE_LENGTH <= len(text) <= MAX_TITLE_LENGTH):
        return False
    return any(ch.isalpha() for ch in text)


def _looks_like_tempo_marking(text: str) -> bool:
    return text.strip().lower().rstrip(".") in TEMPO_MARKINGS


def _guess_composer(lines: list[_Line], title_index: int) -> str | None:
    lookahead = lines[title_index + 1 : title_index + 1 + COMPOSER_LOOKAHEAD_LINES]
    for line in lookahead:
        text = line.text.strip()
        match = COMPOSER_PREFIX_RE.match(text)
        if match:
            return match.group(1).strip()
        if _looks_like_tempo_marking(text):
            continue
        if len(text) <= MAX_COMPOSER_LINE_LENGTH:
            return text
    return None


def extract_title_and_composer(pdf_bytes: bytes) -> tuple[str | None, str | None]:
    """Best-effort page-1 title/composer guess from the PDF text layer.

    Never raises: scanned PDFs (no text layer) or unparseable files return (None, None).
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if not pdf.pages:
                return None, None
            page = pdf.pages[0]
            lines = _lines_from_chars(page.chars)
            page_height = page.height
    except Exception:
        return None, None

    if not lines:
        return None, None

    top_region_limit = page_height * TOP_FRACTION
    candidates = [line for line in lines if line.top <= top_region_limit]
    plausible_candidates = [line for line in candidates if _is_plausible_title(line.text)]
    if not plausible_candidates:
        return None, None

    title_line = max(plausible_candidates, key=lambda line: line.font_size)
    title_index = lines.index(title_line)
    composer = _guess_composer(lines, title_index)

    return title_line.text, composer


def parse_composer_title_from_filename(filename: str | None) -> tuple[str | None, str | None]:
    """Split an uploaded filename on the "Composer - Title" convention.

    Returns (composer, title). If the filename doesn't follow the convention
    (no ` - `/en-dash/em-dash separator, or one side would be empty), `composer`
    is None and `title` falls back to the whole filename stem — matching the
    long-standing filename-as-title fallback behavior for files that don't
    follow the convention. A blank/missing filename returns (None, None).
    """
    stem = Path(filename).stem.strip() if filename else ""
    if not stem:
        return None, None

    match = FILENAME_SEPARATOR_RE.search(stem)
    if match:
        composer = stem[: match.start()].strip()
        title = stem[match.end() :].strip()
        if composer and title:
            return composer, title

    return None, stem
