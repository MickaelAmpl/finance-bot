# 02 Spec

Job: define what the product does, phase by phase. The spec is the source of truth for plans, code and QA.

## Inputs

| Layer | File / scope |
|---|---|
| 3 | `../../shared/decisions.md`, `../../_config/working-rules.md` |
| 4 | `output/plan-page-v2-2026-10-31.html` - the plan Misha approved (Russian, his reading copy). Artifact: https://claude.ai/artifact/FjKWD1zkf6SZskBxFVjcgW |
| 4 | `output/spec-2026-10-31.md` - the agent spec derived from it (English) |
| 4 | `../01_research/output/` only when a requirement needs evidence |

## Process

Any scope change starts here: write a new dated spec variant beside the approved one, list what changed and why, ask Misha. Phase 2 and phase 3 get detailed requirements here before their plans are written.

## Outputs and review gate

`output/spec-<phase or topic>-YYYY-MM-DD.md`. Nothing downstream changes until Misha approves the new variant. Superseded versions go to `references/history/`.
