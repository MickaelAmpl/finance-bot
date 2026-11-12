# ICM architecture mapping

Reference: `methodology/Agentic Folder Structure.pdf` (Interpretable Context Methodology, Van Clief & McDermott, arXiv:2603.16021v2), pp. 5-10. Applied the same way as Misha's OutSpoken workspace.

| ICM layer | Implementation |
|---|---|
| 0 - identity / entry | `AGENTS.md`; thin `CLAUDE.md` adapter; `START-HERE.md` for Misha |
| 1 - task routing | `CONTEXT.md` |
| 2 - stage contracts | `stages/01_research` ... `stages/06_release`, each `CONTEXT.md` with Inputs / Process / Outputs / Review gate |
| 3 - stable constraints | `_config/*.md`, `shared/decisions.md`, stage `references/` |
| 4 - working artifacts | stage `output/` (dated files) and `app/` (code under git) |

## Why code sits in `app/` and not in a stage `output/`

ICM handoffs are files a human can open and edit. Code is such a file set, but it must be deployable as one tree and versioned line by line. So the build stage's working artifact is `app/`, tracked by git, while each stage still writes its human-reviewable reports (task reports, QA reports, release notes) as dated files to its own `output/`.

## The loop per phase

Phases 1-3 each run stages 03 Plan -> 04 Build -> 05 QA -> 06 Release. Every arrow is a review gate: Misha approves the plan, QA verifies the build, Misha accepts in Telegram, Misha approves the deploy. Stages 01 and 02 are re-entered only when scope changes.

`HANDOFF.md` is the live restart summary. `shared/decisions.md` is the approval register.
