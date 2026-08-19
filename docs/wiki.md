# Jazz Reference Wiki

`wiki/` is a hand-maintained MkDocs + Material site of structured jazz-standard
reference pages — form, keys, style, notable recordings, plus freeform playing
notes. It's a separate, independent toolchain (Python + MkDocs, not
FastAPI/Svelte/Docker) with its own `uv`-managed `pyproject.toml`/`uv.lock`,
browsed on its own rather than served by the app. A `Piece` can optionally
carry a `wiki_reference` link out to a page here (see below); the app never
reads or validates wiki content.

See the "Jazz reference wiki" section of [backlog.md](backlog.md) for the
scoping decisions (why MkDocs over Zensical, why plain Markdown files over
database rows, why link-out only).

## Running it locally

```bash
cd wiki
uv sync
uv run mkdocs serve
```

Open http://127.0.0.1:8000. Search and tag filtering work out of the box
(the `search` and `material/tags` plugins configured in `wiki/mkdocs.yml`).

Before committing changes to the wiki, run the same strict build CI runs:

```bash
cd wiki
uv run mkdocs build --strict
```

`--strict` fails the build on broken internal links, invalid front matter, or
config errors — this is the wiki's test suite; there are no unit tests in the
traditional sense.

## Adding a standard

1. Copy `wiki/docs/standards/_template.md` to `wiki/docs/standards/<slug>.md`.
2. Fill in every front-matter field for real (see schema below) and write
   freeform playing notes in the body.
3. Add the new page under `nav: Standards:` in `wiki/mkdocs.yml`.
4. `uv run mkdocs build --strict` before committing.

### Front-matter schema

| Field | Type | Notes |
|---|---|---|
| `title` | string | Canonical title as commonly published. |
| `composer` | string | Primary composer credit. |
| `alternate_titles` | list[string] | Other names the tune is known by. |
| `form` | string | Structural form, e.g. "AABA 32-bar", "rhythm changes", "12-bar blues". |
| `common_keys` | list[string] | Keys it's commonly played/called in. |
| `style_or_era` | string | e.g. "bebop", "bossa nova", "ballad". |
| `notable_recordings` | list[string] | "Artist – Album (Year)" style entries. |
| `tags` | list[string] | Free tags; feeds the Material tags plugin index. |

The Markdown body below the front matter is freeform — history, harmonic
quirks, reharmonization ideas, or anything else that doesn't fit a field.

## Linking a Piece to a wiki page

`Piece.wiki_reference` is a nullable, unvalidated string — paste a relative
path (e.g. `/standards/autumn-leaves/`) or a full URL into the "Wiki
reference" field on a piece's edit form. When set, the piece grid and list
views show a link icon that opens it in a new tab. Leaving it blank shows no
link. The app does not check that the target page exists.

## Out of scope for now

Hosting/publishing (GitHub Pages, a custom domain, etc.) is not set up —
`mkdocs serve` locally is enough. Bulk content population is also out of
scope; standards get added by hand over time.
