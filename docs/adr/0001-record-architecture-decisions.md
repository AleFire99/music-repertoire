# 0001 — Record Architecture Decisions

## Status

Accepted

## Context

This project doubles as an engineering-practice lab. Significant decisions (stack choices, workflow model) need a durable record of *why*, not just *what* — especially since Claude Code agents will pick up this project without the conversation history that produced these choices.

## Decision

Use lightweight ADRs (Nygard style) in `docs/adr/`, numbered sequentially. Only write one for decisions with real consequences (stack choice, branching model) — not for routine implementation details.

## Consequences

Future agents/contributors can see the reasoning behind a choice before proposing to change it, without needing to ask.
