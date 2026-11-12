# 03 Plan

Job: turn an approved spec into a roadmap and a task-by-task implementation plan that Haiku developers can execute without guessing.

## Inputs

| Layer | File / scope |
|---|---|
| 3 | `../../_config/engineering-rules.md`, `../../_config/telegram-rules.md`, `../../_config/team.md` |
| 4 | `../02_spec/output/spec-2026-10-31.md` (the phase's section) |
| 4 | `output/roadmap-2026-10-31.md` |

## Process

Use `superpowers:writing-plans`. Plans live here, not in `docs/superpowers/plans/`. Each plan has: header (goal, architecture, stack, spec link), Global Constraints, Review Focus, file map, waves of parallel tasks with disjoint files, and per task: Files, Interfaces, test steps with exact values, verification commands, commit message. A plan decides names, signatures, values and tests; it does not contain function bodies the tests already determine.

Phase 2 and phase 3 plans are written only after the previous phase is released and Misha has used it.

## Outputs and review gate

`output/phase<N>-implementation-plan-YYYY-MM-DD.md` with `Status: draft - awaiting Misha's review`. Build starts only after Misha approves the plan.
