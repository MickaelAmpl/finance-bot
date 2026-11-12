# 05 QA

Job: prove or disprove that a phase does what the spec and plan say, and nothing more.

## Inputs

| Layer | File / scope |
|---|---|
| 3 | `../../_config/engineering-rules.md`, `../../.claude/agents/qa.md` |
| 3 | `references/acceptance-checklist-phase1.md` |
| 4 | `../02_spec/output/spec-2026-10-31.md` (the phase section), the approved phase plan in `../03_plan/output/` |
| 4 | `../../app/` and `git log` for the phase |

## Process

One Sonnet QA agent per phase (or per risky task when the product owner asks):
1. ruff and pytest on a clean venv.
2. Every spec requirement and every Review Focus line: test or command as evidence.
3. Review the diff for the phase: the `two-axis-review` skill (Standards and Spec); the `pr-review-toolkit` agents `silent-failure-hunter`, `pr-test-analyzer` and `code-simplifier` (report only); the built-in `/code-review` and `/security-review`; `/simplify` in report-only mode to list dead or redundant code; `pyright app/` with zero errors.
4. Scope check: anything the plan did not ask for is a finding.
5. Run the bot locally with the dev bot only if the product owner provides the dev token in the environment; never the prod token.

## Outputs and review gate

`output/qa-phase<N>-YYYY-MM-DD.md`: verdict, findings by severity with evidence, extra scope, not tested. All findings go to Misha. Fixes happen only after his decision (blockers for the release are fixed and still reported). Gate to stage 06: verdict pass, or Misha accepts the listed issues.
