---
title: Title of the standard
composer: Composer name
alternate_titles: []
form: "e.g. AABA 32-bar, rhythm changes, 12-bar blues"
common_keys: []
style_or_era: "e.g. bebop, bossa nova, ballad"
notable_recordings: []
tags: []
---

# Title of the standard

> This file is a template, not a real entry — copy it to
> `docs/standards/<slug>.md` and fill in every field for real. Leave a field
> as an empty list (`[]`) rather than deleting it if it doesn't apply yet.

## Front-matter schema

| Field                | Type          | Notes                                                              |
| --------------------- | ------------- | ------------------------------------------------------------------- |
| `title`               | string        | Canonical title as commonly published.                             |
| `composer`            | string        | Primary composer credit.                                            |
| `alternate_titles`    | list[string]  | Other names the tune is known by.                                   |
| `form`                | string        | Structural form, e.g. "AABA 32-bar", "rhythm changes", "12-bar blues". |
| `common_keys`         | list[string]  | Keys it's commonly played/called in.                                 |
| `style_or_era`        | string        | e.g. "bebop", "bossa nova", "ballad".                                |
| `notable_recordings`  | list[string]  | "Artist – Album (Year)" style entries.                               |
| `tags`                | list[string]  | Free tags; feeds the Material tags plugin index.                     |

## Body

The Markdown body below the front matter is freeform: playing notes, history,
harmonic quirks, reharmonization ideas, or anything else that doesn't fit a
front-matter field.
