# Release: phase 1.4 (AI input), 12.11.2026

## What was deployed

- Commit `59745f8` (code head `2aa9174`): AI input - free text and receipt photos become drafts saved only by the Save button; money questions answered from bot-computed numbers (`stages/03_plan/output/phase1-4-plan-2026-11-12.md`, spec `stages/02_spec/output/spec-ai-input-v2-2026-11-01.md`). Database migration 3 -> 4 (`drafts` table).
- Host `the server`, `/opt/finance-bot`, same units. Bot @my_finance_bot. Model `claude-sonnet-5-5`.

## Approval

"Да, выкладывай" (answer to "Выкладываю ИИ-ввод на сервер?", after the live check result and the plain-words summary: the bot starts understanding free text and receipt photos and saves only by Save; restart about a minute with a database copy first; database to version 4, old entries untouched; rollback is code only).

## Checks

Before (20:52 UTC, read-only): crontab md5 `<md5>`; `finance-bot.service`, `job-digest-bot.service`, `other-service.timer` active; `finance-bot.service` NRestarts 0, MemoryCurrent 158,765,056 (about 151 MiB); database `user_version 3`, tables budgets 0, categories 15, entries 14, keywords 5, meta 1, pots 1, rates 1. `deploy.sh --dry-run` exit 0.

Deploy (`FINBOT_HOST=myvps app/deploy/deploy.sh`, 20:52:22-20:55:01 UTC, exit 0):
- Step 2: backup `/opt/finance-bot-backups/2026-11-12-215222/finbot.db` (53,248 bytes, mode 600).
- Step 4: `1120 passed in 85.32s` on the server copy.
- Step 5: `AI key: present`.
- Step 8: `finance-bot.service: active, NRestarts 0`, `finance-bot-daily.timer: active`.
- `sk-ant` in the deploy output: 0.

After:
- Journal: old process stopped cleanly 21:54:45 CET, new one started 21:54:50; `INFO:root:AI input: on` 21:54:59; `Start polling` and `Run polling for bot @my_finance_bot` 21:55:00. Traceback lines: 0. `journalctl ... | grep -c sk-ant` = 0.
- Database: `user_version 4`; `drafts` table present (0 rows); entries 14, categories 15, keywords 5, pots 1, rates 1, budgets 0, meta 1 - all unchanged.
- `pip check`: no broken requirements; pydantic 2.13.5 (below 2.14, as aiogram needs). `pip freeze` of `/opt/finance-bot/.venv`:
  aiofiles 25.1.0, aiogram 3.31.0, aiohappyeyeballs 2.7.1, aiohttp 3.14.5, aiosignal 1.4.0, annotated-types 0.8.0, anthropic 2.3.0, anyio 4.16.0, attrs 26.1.0, certifi 2026.10.23, docstring_parser 0.18.0, frozenlist 1.8.0, h11 0.16.0, httpcore2 2.16.0, httpx2 2.16.0, idna 3.20, jiter 0.19.0, magic-filter 1.0.12, multidict 7.2.1, opentelemetry-api 1.45.2, propcache 0.5.4, pydantic 2.13.5, pydantic_core 2.46.5, sniffio 1.3.1, truststore 0.10.5, typing-inspection 0.4.4, typing_extensions 4.16.0, yarl 1.25.1.
- Memory: MemoryCurrent 206,454,784 (about 197 MiB), +47.7 MB from the baseline - above the 25-40 MB expected from the SDK, harmless on this host (11.9 GB RAM, 10.7 GB free). Watch it once after a few days of use.
- Neighbours: crontab md5 unchanged; `job-digest-bot.service` and `other-service.timer` active.

## Rollback

Code only (the normal path): deploy `20115a4` again (phase 1.3 code); it runs on the version-4 database and ignores `drafts`.

Database only if the migration damaged data (loses entries made after the deploy), printed by the deploy:

```
ssh the server "test -f '/opt/finance-bot-backups/2026-11-12-215222/finbot.db' && systemctl stop finance-bot.service && rm -f '/opt/finance-bot/data/finbot.db-wal' '/opt/finance-bot/data/finbot.db-shm' && cp '/opt/finance-bot-backups/2026-11-12-215222/finbot.db' '/opt/finance-bot/data/finbot.db' && systemctl start finance-bot.service"
```

Key leak: revoke the key in the Console, put a new line in `/opt/finance-bot/.env`, `systemctl restart finance-bot.service`.

## First real messages (checklist step 2.8), 12.11 22:02-22:03 CET

Misha sent one text and one receipt photo and pressed Save on both. Journal clean: message words not in the journal, `sk-ant` 0, traceback 0, NRestarts 0. Both drafts were correct (Misha: "Да, оба верные"): text 1 of 10, receipt 1 of 5 toward acceptance. Entry details are left out of this public copy.

## Data cleared (12.11 22:06 CET)

At Misha's request all entries, pots, rates and taught words were cleared, categories kept; backup first, one transaction committed only if every count matched, checked through the bot's own code on a copy. Details are left out of this public copy.

## Still open

- Acceptance (checklist section 3): Misha's first 10 AI messages and first 5 receipts, target 9/10 and 4/5; misses go here as message / expected / got.
- Receipt photos were never run on the real model; the first real receipt is the first check.
- `/opt/finance-bot-livetest` stays on the server until Misha allows removal.
- Later, at Misha's choice: QA minors Q-4, Q-6..Q-11.
