# CLAUDE.md — Notification Router

## GitLab Workflow

- GitLab project `ha-platform/control` is the central workflow truth.
- Relevant work requires a GitLab issue in `ha-platform/control`.
- Before work starts, read the issue description and all issue notes.
- Document current state, decisions, scope changes, tests, commits, merge requests, blockers, and completion in the issue.
- Code changes happen in this GitLab repository. `origin` must point to GitLab.
- GitHub is only the public distribution and HACS mirror. Do not develop directly on GitHub and do not push manually to GitHub.
- Plane and Forgejo are historical sources only and are not used for active work.
- Full rules live in `ha-platform/control/AGENTS.md`, `ha-platform/control/CLAUDE.md`, and `ha-platform/control/docs/workflow/`.
- Repo-specific implementation rules for Codex and other agents are in `AGENTS.md`.

## Safety

- Do not put secrets in issues, commits, logs, or reports.
- Do not touch production Home Assistant systems without explicit approval.
- No admin, delete, runner, or bulk actions without explicit approval.

**Status:** Eigenständige HACS-Repo, enthält alten Code. **Wird im Hybrid-Pivot mit aktuellem Stand aus `bennis_toolbox/modules/notification_router/` überschrieben (Codex-Aufgabe).**
**Toolbox-Modul-ID (alt):** `notification_router`
**Letzte Aktualisierung:** 2026-05-27

---

## Was ist dieses Modul

Notification-Routing: nimmt zentrale Notification-Requests entgegen, entscheidet basierend auf Bio-State + Presence + Context, wo/wann/wie sie zugestellt werden (HomePod TTS, Mobile Push, persistent_notification, Doorbell-Light, etc.).

## Architektur-Kontext

Eigene HACS-Custom-Integration. Foundation lebt in `bennis_toolbox`, dieses Modul wird eigenständig.

**Pendant-Briefings:**
- `bennis_toolbox/CLAUDE.md` — Foundation + Pattern
- `einhornzentrale/CLAUDE.md` — YAML + Cut-Over-Status
- `einhornzentrale/docs/roadmap.md` — Phase 2 (Pivot)

## Aktueller Stand

- Code im Repo: alt
- Aktueller produktiver Code: `bennis_toolbox/modules/notification_router/` — Status READY
- HACS: aktuell über `bennis_toolbox`-Umbrella

## Migration

Siehe `AGENTS.md`.
