# Release: phase 1.3, 01.11.2026

## What was deployed

- Commit `20115a4` (code head `02817fe`): several entries in one message, one per line or comma-separated (`stages/03_plan/output/phase1-3-plan-2026-11-01.md`). No database change.
- Host `the server`, `/opt/finance-bot`, same units. Bot @my_finance_bot.

## Approval

"Да, ставь" (answer to: "Ставлю «несколько расходов в одном сообщении» на сервер: да или подождать?", after the summary of the behaviour, the review fixes, the two behaviour changes and "база при этой установке не меняется").

## Checks

Before: `deploy.sh --dry-run` exit 0. Baseline: crontab md5 `<md5>`, `job-digest-bot.service` and `other-service.timer` active, database `user_version 3`, 11 entries (1 live).

Deploy (`FINBOT_HOST=myvps app/deploy/deploy.sh`, exit 0):
- Step 2: backup `/opt/finance-bot-backups/2026-11-01-184230/finbot.db`.
- Step 4: `813 passed in 48.39s` on the server copy.
- Step 8: `finance-bot.service: active, NRestarts 0`, `finance-bot-daily.timer: active`.

After:
- Service active (running) since 18:43:50 CET; journal: `Start polling`, `Run polling for bot @my_finance_bot`; no error, traceback or menu failure line; no token-like string in the log.
- New parser on the server (`ENTRY_START_RE` present in `/opt/finance-bot/finbot/parser.py`).
- Database unchanged: `user_version 3`, 11 entries (1 live).
- Neighbours: `job-digest-bot.service` active, `other-service.timer` active, crontab md5 unchanged.

## Rollback (printed by the deploy)

```
ssh the server "test -f '/opt/finance-bot-backups/2026-11-01-184230/finbot.db' && systemctl stop finance-bot.service && rm -f '/opt/finance-bot/data/finbot.db-wal' '/opt/finance-bot/data/finbot.db-shm' && cp '/opt/finance-bot-backups/2026-11-01-184230/finbot.db' '/opt/finance-bot/data/finbot.db' && systemctl start finance-bot.service"
```

Code rollback: deploy `96b0137` again (phase 1.2 code; same database version).

## Still open

- Misha sends a multi-line or comma-separated message in Telegram.
- Next: AI input (free text and receipt photos with a confirm button; voice later). Needs Misha's API key on the server.
