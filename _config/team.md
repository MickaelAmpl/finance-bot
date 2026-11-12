# Team

Same council Misha set up for job-digest (08-14.10.2026), applied here.

| Role | Model | Does | Never |
|---|---|---|---|
| Product owner | Main session (Opus) | Writes plans and task specs, hands out tasks, reviews each task against the plan, runs releases after Misha's approval, reports to Misha | Writes product code itself when a developer can do it |
| Developer | Haiku (`.claude/agents/developer.md`) | One task from the phase plan: test first, minimal code, ruff + pytest green, one commit, report | Deploys, touches the server, edits files outside the task, adds scope |
| QA | Sonnet (`.claude/agents/qa.md`) | Checks a task or a phase against spec and plan: tests, review, Review Focus inputs, scope creep | Fixes code |
| Customer | Misha | Reviews plans, accepts each phase in Telegram by checklist, approves every deploy | - |

## How the product owner runs a phase

1. Take the next wave of tasks from the phase plan (`stages/03_plan/output/`). Tasks in one wave touch disjoint files and can run in parallel.
2. Spawn one developer per task: `Agent(subagent_type="developer")` in a session started in this folder, or `general-purpose` with model `haiku` and the contents of `.claude/agents/developer.md` plus the task text.
3. Review each report: tests pasted, files match the task, no extra scope. Send corrections back to the same developer.
4. After the last wave: one QA pass on the whole phase (`stages/05_qa/CONTEXT.md`). All QA findings go to Misha; nothing found by QA is changed without his decision, except blockers for the release, which are still reported.
5. Misha's acceptance with the dev bot, then a release only with his approval (`stages/06_release/CONTEXT.md`).

## Quality tools and where they run

Installed for this project only (31.10.2026, Misha: "скилы ставим все 4"). They load only in a session started in this folder.

| Tool | Where it runs | What it catches |
|---|---|---|
| `superpowers:subagent-driven-development` | product owner, every wave | tasks handed out and reviewed one by one |
| `superpowers:test-driven-development` | developers, every task | code without a failing test first |
| `pyright-lsp` plugin (needs `pyright` in `~/.local/bin`, installed via `uv tool`) | developers, every edit | type errors before tests run |
| `two-axis-review` skill (`.claude/skills/`) | product owner after each task; QA on the phase | broken rules (Standards) and missing or extra scope (Spec) |
| `pr-review-toolkit` plugin: `silent-failure-hunter`, `pr-test-analyzer`, `code-simplifier` agents | QA, once per phase | swallowed errors, untested paths, needless complexity |
| built-in `/code-review`, `/simplify` (report only), `/security-review` | QA, once per phase | bugs, dead code, security holes |
| git guardrail hook (`.claude/hooks/block-dangerous-git.sh`) | always, every Bash call | `git push`, `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .` |
| `superpowers:systematic-debugging`, `superpowers:verification-before-completion` | everyone | guessing at bugs; "done" without evidence |
