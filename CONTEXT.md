# Workspace routing

Start with `HANDOFF.md`. Use `shared/decisions.md` when approval status matters. Load one stage contract and only its scoped inputs.

| Request | Stage | Existing state |
|---|---|---|
| Market, reference apps, stack facts, Telegram limits | [01 Research](stages/01_research/CONTEXT.md) | Two verified research rounds, 31.10.2026 |
| What the product does, scope per phase | [02 Spec](stages/02_spec/CONTEXT.md) | Plan v2 approved 31.10.2026; agent spec derived from it |
| Roadmap and task-by-task implementation plans | [03 Plan](stages/03_plan/CONTEXT.md) | Roadmap + phase 1 plan, approved 31.10.2026 |
| Write or change code in `app/` | [04 Build](stages/04_build/CONTEXT.md) | Phase 1 built 31.10.2026 (15 tasks); phase 1.1 and 1.2 built 01.11.2026 (log in `output/`) |
| Test, review, check a task or a phase | [05 QA](stages/05_qa/CONTEXT.md) | Phase 1.4 QA 12.11.2026: pass with issues (1 major, 10 minor), findings with Misha |
| Misha's acceptance and deploy to the server | [06 Release](stages/06_release/CONTEXT.md) | Phase 1 and 1.1 deployed 01.11.2026 to the server; acceptance items done; phase 1.2 waits for deploy approval |

Each phase (1 personal ledger, 2 groups, 3 Mini App) runs stages 03 to 06 again. Stage outputs are dated files. Code is the exception: it lives in `app/` and is versioned by git.

Stable rules: `_config/`. Decisions and provenance: `shared/`. Superseded versions: `stages/NN_*/references/history/`.
