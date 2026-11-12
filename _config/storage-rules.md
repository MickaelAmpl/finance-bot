# Storage rules

Method: Interpretable Context Methodology, `../shared/methodology/Agentic Folder Structure.pdf`, pp. 5-10. Same lifecycle as Misha's OutSpoken workspace.

## Where things live

| Kind of material | Location | ICM layer |
|---|---|---|
| Rules applied on every run | `_config/` | 3 |
| Approval register, structure, methodology | `shared/` | 3 |
| Stage-specific stable material: evidence, checklists, templates | `stages/NN_*/references/` | 3 |
| Current deliverables of a stage: drafts and approved versions | `stages/NN_*/output/` | 4 |
| Product code, tests, deploy files | `app/` (git) | 4 |
| Superseded or unselected versions | `stages/NN_*/references/history/` | history |
| Old generators and data no longer used | `archive/` | history |

All project work is saved inside `~/Desktop/finance-bot`. Raw research goes to `references/evidence/`, never to `output/`. Runtime data (the SQLite database, backups, `.env`) never enters git and never leaves the server, except the CSV export Misha asks for.

## Lifecycle of a document deliverable

1. Route via root `CONTEXT.md`; load only that stage's `CONTEXT.md` and its inputs.
2. Draft to the stage's `output/` as `<name>-YYYY-MM-DD.<ext>`. First line under the title: `Status: draft - awaiting Misha's review`. A next iteration is a new file (`-v2`), not an overwrite.
3. Approval is an explicit message from Misha ("утверждаю", "согласовано", "делаем", "зафиксируй"). Silence or a topic change is not approval. If ambiguous, ask one line.
4. On approval, in the same session: set `Status: approved by Misha on YYYY-MM-DD`; add a row to `shared/decisions.md` with his exact words; move superseded versions to `references/history/`; update `HANDOFF.md`; update routing if it changed.
5. A change to approved work is a new dated variant beside it.

## Code

Code changes follow `engineering-rules.md`: one task, one commit, tests first. Git history is the version record for `app/`; no dated copies of code files.

## Boundaries

- Never delete files; move them to `references/history/` or `archive/`. Deletion needs Misha's explicit yes.
- A new stage is created only after Misha agrees.
- At session end, `HANDOFF.md` records changed files, evidence, open questions and the exact review gate.
