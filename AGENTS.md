# AGENTS.md - Notification Router

## GitLab Workflow

- GitLab project `ha-platform/control` is the central workflow truth.
- Relevant work requires a GitLab issue in `ha-platform/control`.
- Before work starts, read the issue description and all issue notes.
- Document current state, decisions, scope changes, tests, commits, merge requests, blockers, and completion in the issue.
- Code changes happen in this GitLab repository. `origin` must point to GitLab.
- GitHub is only the public distribution and HACS mirror. Do not develop directly on GitHub and do not push manually to GitHub.
- Plane and Forgejo are historical sources only and are not used for active work.
- Full rules live in `ha-platform/control/AGENTS.md`, `ha-platform/control/CLAUDE.md`, and `ha-platform/control/docs/workflow/`.

## Project-Memory Bootstrap

- Before significant work, read the matching GitLab issue description and all notes, then `ha-platform/control/docs/workflow/README.md`, its linked workflow documents, and relevant `ha-platform/control` wiki pages.
- GitLab is the workflow truth. GitHub is only the distribution/HACS mirror; do not develop there directly. Plane is frozen historical context, and Forgejo is out of service.
- Stay inside the decided issue scope: no side quests and no overwriting foreign branches or dirty worktrees.
- Use the smallest sufficient verification for the risk tier. Stable changes to behavior, contracts, operations, or rules belong in the wiki; use live evidence when runtime behavior must be proved. Completion notes must document wiki impact, verification/tests, release state where applicable, and required live evidence.

## Safety

- Do not put secrets in issues, commits, logs, or reports.
- Do not touch production Home Assistant systems without explicit approval.
- No admin, delete, runner, or bulk actions without explicit approval.

## Repo Context

- Read `CLAUDE.md` in this repository for module context before implementation work.
- Use the `einhornzentrale` Home Assistant MCP server for HA context. Do not use `haos_benni`.
- This repository is the standalone target for Notification Router.
- Current productive code historically lived in `bennis_toolbox/modules/notification_router/`; treat that as extraction context, not as an active workflow system.
- Use `Entity-Title-Mapper` / `title-classifier` as the extraction-pattern reference when the extraction work is explicitly assigned.

## Extraction Notes

When the extraction is explicitly assigned:

1. Analyze `bennis_toolbox/modules/notification_router/`.
2. Move the implementation into `custom_components/notification_router/`.
3. Adjust imports and domain ownership for a standalone integration.
4. Provide standalone `storage.py` and `services.py` as needed.
5. Update `manifest.json`, `hacs.json`, tests, `CHANGELOG.md`, and `README.md`.
6. Create a follow-up change in `bennis_toolbox` to remove the old module only when explicitly approved.

## Anti-Patterns

- No cross-repo imports.
- No Lastenheft consolidation into this repo.
- Do not build features on the old `haos_benni` VM.

## UX-Frontend-Standard (verbindlich)

Für jede UX-/Frontend-Arbeit gilt der verbindliche, fleet-weite UX-, Technologie- und
Designstandard. Kanonische Quelle: ADR `ha-platform/control:docs/adr/0001-ux-frontend-standard.md`
(Issue `control#58`). Kurzform: Svelte 5 · Vite · TypeScript · Bits UI · shadcn-svelte ·
Tailwind · CSS Custom Properties · Lucide; Design "Graphite Dark – semantic accent system";
zentrale UX = statisches Bundle + dünnes UX-Gateway (primär HA-Ingress); versionierte/typisierte
Contracts. Details und Abweichungsprozess: `docs/ux-frontend-standard.md` und das ADR. Bestehende
Regeln werden dadurch ergänzt, nie überschrieben oder entfernt.
