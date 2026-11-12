# 04 Build

Job: implement the approved phase plan in `app/`, one task per developer agent, wave by wave.

## Inputs

| Layer | File / scope |
|---|---|
| 3 | `../../_config/engineering-rules.md` (mandatory), `../../_config/telegram-rules.md`, `../../_config/team.md` |
| 3 | `../../.claude/agents/developer.md` |
| 4 | the approved `../03_plan/output/phase<N>-implementation-plan-*.md`: header, Global Constraints, Review Focus, and the one task being built |
| 4 | `../../app/` - existing code, read only the files the task names and the Interfaces it consumes |

## Process

Before the first task of a phase, if `git log` is empty: one base commit of the workspace (`chore: workspace before phase <N> build`), after `git status` shows no `.env`, `*.db` or `data/`. It is the fixed point for reviewing task 1.

The product owner (main session) runs `superpowers:subagent-driven-development`: one Haiku developer per task, tasks of one wave in parallel only when their Files lists do not overlap. Each developer works test first, runs ruff and pytest, commits once. The product owner reviews each report against the task (files, interfaces, tests, no extra scope) with the `two-axis-review` skill before the next wave. Bugs go through `superpowers:systematic-debugging`.

Local setup on the Mac (task 1 creates it): `cd app && ~/.local/bin/uv venv --python 3.12 .venv && ~/.local/bin/uv pip install --python .venv/bin/python -r requirements-dev.txt`.

## Outputs and review gate

- Code and tests in `app/`, one commit per task.
- `output/build-log-phase<N>.md`: per task date, commit hash, test summary, deviations. Appended by the product owner.

Gate: all tasks of the phase merged and green, then stage 05 QA. No deploy from this stage.
