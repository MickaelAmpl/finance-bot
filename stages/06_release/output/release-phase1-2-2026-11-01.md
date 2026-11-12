# Release: phase 1.2, 01.11.2026

## What was deployed

- Commit `54acfe0` (code head `e732645`): own categories, monthly budgets per expense category, `/clear` a month with confirmation, menu and help for them (`stages/03_plan/output/phase1-2-plan-2026-11-01.md`).
- Host `the server`, `/opt/finance-bot`, same units. Bot @my_finance_bot.

## Approval

"Да давай на все ок. Стартуй" (answer to: "Ставлю новую версию бота на сервер сейчас?", after the plain explanation that /budget, /category and /clear appear in the bot, the bot restarts for a couple of minutes and the database is copied first).

## Checks

Before: `deploy.sh --dry-run` passed. Baseline: crontab md5 `<md5>`, `job-digest-bot.service` and `other-service.timer` active, database `user_version 2`, 11 entries (1 live: Misha's own entry after the test cleanup).

Deploy (`FINBOT_HOST=myvps app/deploy/deploy.sh`):
- Step 2: backup `/opt/finance-bot-backups/2026-11-01-182621/finbot.db` (49152 bytes, mode 600).
- Step 4: `753 passed in 49.25s` on the server copy.
- Step 8: `finance-bot.service: active, NRestarts 0`, `finance-bot-daily.timer: active`.

After:
- Service active (running) since 18:27:44 CET; journal: `Start polling`, `Run polling for bot @my_finance_bot`; no "could not set the Telegram menu" line; no token-like string in the log.
- Telegram menu (`getMyCommands`, run on the server, token not printed): `month, last, undo, savings, goal, budget, category, clear, rate, export, help`.
- Database migrated: `user_version 3`, table `budgets` created as planned, 11 entries (1 live), unchanged.
- Timer: next run Mon 2026-11-02 09:00 CET.
- Neighbours: `job-digest-bot.service` active, `other-service.timer` active, crontab md5 unchanged.

## Rollback (printed by the deploy)

```
ssh the server "test -f '/opt/finance-bot-backups/2026-11-01-182621/finbot.db' && systemctl stop finance-bot.service && rm -f '/opt/finance-bot/data/finbot.db-wal' '/opt/finance-bot/data/finbot.db-shm' && cp '/opt/finance-bot-backups/2026-11-01-182621/finbot.db' '/opt/finance-bot/data/finbot.db' && systemctl start finance-bot.service"
```

Code rollback: deploy `4e710a8` again. The old code works on the version-3 database (it never reads `budgets`); budgets set in the meantime stay in the table and come back with the next forward deploy.

## Still open

- Misha tries `/category add`, `/budget`, `/clear` in Telegram.
- Known before this release: a multi-line message is saved as one entry with the other amounts inside the note (checked 01.11 on `parser.parse_entry`). Until phase 1.3: one entry per message.
