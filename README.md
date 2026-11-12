# Finance Bot

My personal money tracker in Telegram. I type `25 coffee` and it is saved; I write "coffee with a friend yesterday 25" or send a photo of a receipt, and Claude drafts the entry for me to save with one button. It keeps my categories, monthly budgets, savings goals and three currencies (EUR, USD, UAH), and sends a summary of the month.

I am a product person, not a software developer. I set the goal, made every product decision and accepted each phase in Telegram; the code was written, reviewed and tested by AI agents in Claude Code. The `stages/` folder is the real build trail: the research, the specs, the plans, the build logs, QA reports and release records, with my approvals.

> Public copy of my working repository, published as one snapshot. Server details, ids and my own entries are removed.

## The problem

I spend in euros, dollars and hryvnias. I did not want a bank connection or a third-party app, only the fastest possible manual input, in a chat I already have open, and an honest picture at the end of the month. The research found no ready product that does this for these three currencies.

## What it does

**Typed entries, no AI.** `25 coffee`, `1200 uah taxi`, `+3000 salary`, `25 coffee yesterday`, or several at once: `850.00 rent, 120 utilities`. The bot learns which word goes to which category after I pick it once.

**AI input (phase 1.4).** Free text in Russian, Ukrainian or English and receipt photos go to Claude (Sonnet 5.5), which drafts 1 to 10 entries. Nothing is saved until I press Save; a correction replaces the open draft. I can also ask "how much did I spend on eating out in October?": the model answers only from numbers the bot computes through three read-only tools and never adds things up itself.

**The rest:**
- `/month` report and an automatic monthly summary with a CSV of all entries
- `/last` to change or delete recent entries, `/undo`, `/clear` a month (asks first)
- own categories and monthly budgets per category, with spent and left shown on every new expense
- savings pots with a goal, a deadline and the monthly amount needed
- manual exchange rates (`/rate usd 0.92`); entries in a currency without a rate wait and are converted later
- a nightly database backup, 14 kept

**Safety rails around the model.** Only the owner's private chat is answered. The model cannot save anything: it can only propose a draft. Daily cap of 100 model calls, 90 seconds per message, and a monthly spend limit on the API account. The key and message texts are never written to logs. Text inside messages and receipts is treated as data, not instructions. Tests block the network and run the real Anthropic SDK over a mock transport.

## How it was built

Research and the first working version took one day (31 October 2026); it went to the server on 1 November. Every phase ran the same loop, each step with a written result and my explicit approval before the next one:

research -> spec -> plan -> build -> QA -> my acceptance in Telegram -> deploy

| Stage | What | Files |
|---|---|---|
| 01 Research | Is there a ready product? Mini App or a plain bot? Open-source engines, reference apps, hosting. Two rounds, every claim re-checked by a second agent | `stages/01_research/output/`, `stages/01_research/references/evidence/` |
| 02 Spec | Product spec for phases 1-3; AI input spec, independent review from three angles (edge cases, LLM integration, security), then v2 | `stages/02_spec/output/`, `stages/02_spec/references/` |
| 03 Plan | Roadmap; phase 1 in 15 tasks and 7 waves; plans for phases 1.1 to 1.4 | `stages/03_plan/output/` |
| 04 Build | Per task: commit, tests, review, deviations, rulings | `stages/04_build/output/build-log-phase1.md`, `stages/04_build/references/` |
| 05 QA | Independent QA of each phase, findings and how each was closed | `stages/05_qa/output/` |
| 06 Release | Release records with every check, the acceptance checklist, the live check on the real model before deploy | `stages/06_release/` |

Every decision I made is in `shared/decisions.md`, with my words (in Russian, my working language with the agents).

| Phase | Date (2026) | What |
|---|---|---|
| 1 | 31 Oct - 1 Nov | Ledger: typed entries, three currencies, savings, reports, backups |
| 1.1 | 1 Nov | Fixes from my acceptance: dates in replies, record view, goal deadlines, Telegram menu |
| 1.2 | 1 Nov | Own categories, monthly budgets, clearing a month |
| 1.3 | 1 Nov | Several entries in one message |
| 1.4 | 12 Nov | AI input: free text, receipt photos, questions about my money |

Tests grew from 312 in phase 1 to 1120 now.

**Who did what.** I decided what to build and why, approved every spec and plan, accepted each phase in the bot and approved every deploy. A main Claude Code session acted as product owner and engineering lead: it wrote task specs and handed them to developer agents (`.claude/agents/`), and every task got a two-axis review (standards and spec) before the next one. A separate QA agent tested each phase as a whole. The project follows the Interpretable Context Methodology (Van Clief and McDermott, [arXiv:2603.16021](https://arxiv.org/abs/2603.16021)): numbered stage folders, each with a `CONTEXT.md` contract, and rules for the agents in `_config/`.

## Stack

- Python 3.12, aiogram 3 (Telegram, long polling), SQLite
- Anthropic Python SDK, Claude Sonnet 5.5 with tool use
- A small Linux server, systemd service and timer; `app/deploy/deploy.sh` runs the tests on the server first, backs up the database, deploys, checks and prints the rollback command
- pytest, ruff, pyright

## Run it

```bash
cd app
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
cp .env.example .env              # BOT_TOKEN from @BotFather and your Telegram id as OWNER_ID
.venv/bin/python -m pytest -q     # offline, no network
.venv/bin/python -m finbot        # start the bot
```

AI input turns on when `ANTHROPIC_API_KEY` is set in `.env`; without it the bot works with typed entries only.

## Status

Running on my server since 1 November 2026; AI input since 12 November. Next: bill splitting in group chats (phase 2), then a Mini App with charts (phase 3).
