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
