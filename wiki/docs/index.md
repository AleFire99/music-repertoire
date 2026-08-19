# Jazz Reference Wiki

A hand-maintained reference of jazz standards: form, common keys, style, and
notable recordings, alongside freeform playing notes. Browsed independently
of the Music Repertoire app — a `Piece` can optionally link out to a page
here via its wiki reference field, but the two systems are not otherwise
coupled.

## Standards

Each entry follows the schema documented in the
[template](standards/_template.md). Start there before adding a new page.

- [Autumn Leaves](standards/autumn-leaves.md)

## Contributing a page

1. Copy `docs/standards/_template.md` to `docs/standards/<slug>.md`.
2. Fill in the front matter and add playing notes in the body.
3. Add the new page to the `nav` section of `mkdocs.yml`.
4. Run `uv run mkdocs serve` locally to check it renders, then `uv run mkdocs
   build --strict` before committing — the same check CI runs.
