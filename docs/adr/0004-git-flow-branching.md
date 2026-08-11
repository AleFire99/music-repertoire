# 0004 — Git Flow Branching Model

## Status

Accepted

## Context

This project is a deliberate lab for learning a full engineering workflow (Git Flow, multi-agent development, CI/CD), not just for shipping features fast. A personal single-maintainer project doesn't strictly *need* Git Flow's ceremony — trunk-based development would ship features just as well.

## Decision

Use Git Flow explicitly: `main` / `develop` / `feature/*` / `release/*` / `hotfix/*`, Conventional Commits, PRs required even solo, CI gating merges. Chosen deliberately as a workflow-learning goal, not because the app's complexity demands it — see the project's engineering-lab intent in `README.md`.

## Consequences

More ceremony per change than trunk-based development would require (a feature branch + PR even for one-person work). Accepted as the point of the exercise. If this ever becomes genuine friction rather than a learning exercise, revisit — but that's a deliberate future decision, not a default to drift into.
