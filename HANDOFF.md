# Handoff

Public copy, 12.11.2026. The working handoff (server state, backups, open gate) stays in the private repository.

- Phase 1.4 "AI input" deployed 12.11.2026: free text (RU/UK/EN) and receipt photos drafted by Claude Sonnet 5.5, saved only by the Save button; questions about money answered from bot-computed numbers through three read-only tools.
- Gate at the last build commit: ruff clean, pyright 0 errors, pytest 1120 passed.
- QA 12.11: pass with issues, no blocker; the major finding and three minors fixed and re-checked; the remaining minors are backlog (`stages/05_qa/output/qa-phase1-4-2026-11-12.md`).
- Live check on the real model before deploy: 10/10 drafts and 5/5 answers correct, 20 calls, about $0.12 (`stages/06_release/output/release-phase1-4-checklist-2026-11-12.md`).
- Next: phase 2, bill splitting in group chats (`stages/02_spec/output/spec-2026-10-31.md`).
- Every decision with the owner's words: `shared/decisions.md`.
