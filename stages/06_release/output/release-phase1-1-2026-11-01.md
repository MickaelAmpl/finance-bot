# Release: phase 1.1, 01.11.2026

## What was deployed

- Commit `4e710a8` (code head `aaf9e4e`): the acceptance fixes of phase 1.1 (`stages/03_plan/output/phase1-1-fixes-plan-2026-11-01.md`) plus the closing-review fix (a pot never goes below zero on delete).
- Host `the server`, `/opt/finance-bot`, same units. Bot @my_finance_bot.

## Approval

"Да, выкладывай" (after the summary of the five changes, the pot guard the agent added, and the database update).

## Checks

Before: `deploy.sh --dry-run` passed; neighbours baseline from the phase 1 release (crontab md5 `<md5>`).

Deploy (`FINBOT_HOST=myvps app/deploy/deploy.sh`, exit 0):
- Step 2: backup `/opt/finance-bot-backups/2026-11-01-134631/finbot.db` (version 1, 10 entries).
- Step 4: `472 passed in 39.36s` on the server copy.
- Step 8: `finance-bot.service: active, NRestarts 0`, `finance-bot-daily.timer: active`.

After:
- Service active (running) since 13:47:56 CET; journal: `Start polling`, `Run polling for bot @my_finance_bot`, no error from the menu call (a failure would be logged), no token in the log (masked check).
- Database migrated: `user_version 2`, 10 entries, `pots` columns `id, name, goal_cents, goal_month`.
- Timer: next run Mon 2026-11-02 09:00 CET.
- Neighbours: `job-digest-bot.service` active, `other-service.timer` active, crontab md5 unchanged.
- Note: the read-only check of the backup created empty `-shm`/`-wal` side files next to it (13:48); the backup file itself is unchanged and the rollback line copies only `finbot.db`.

## Rollback (printed by the deploy)

```
ssh the server "test -f '/opt/finance-bot-backups/2026-11-01-134631/finbot.db' && systemctl stop finance-bot.service && rm -f '/opt/finance-bot/data/finbot.db-wal' '/opt/finance-bot/data/finbot.db-shm' && cp '/opt/finance-bot-backups/2026-11-01-134631/finbot.db' '/opt/finance-bot/data/finbot.db' && systemctl start finance-bot.service"
```

Code rollback: deploy `461f40a` again (the old code works on the version-2 database; its `/goal` keeps an old `goal_month`).

## Acceptance items 9 and 11 (01.11, Misha: "да запускай")

- Item 9: `systemctl start finance-bot-daily.service` at 13:54:23: exit 0, `meta` gained `summary_sent:2026-10 = 2026-11-01` (written only after the summary text and the CSV were sent; October had the two test `coffee` entries). Second run at 13:54:32: exit 0, `meta` unchanged, so nothing was sent again. Misha to confirm the message and the file arrived.
- Item 11: the same run wrote `/opt/finance-bot/data/backups/finbot-2026-11-01.db` (49152 bytes, mode 600). The timer runs it daily at 09:00 (next 02.11).

## Test data cleared (01.11 14:10, Misha: "да удаляй сейчас")

- Backup first: `/opt/finance-bot-backups/2026-11-01-141014-before-cleanup/finbot.db` (10 entries, version 2).
- One `BEGIN IMMEDIATE` transaction: the 6 active test entries soft-deleted (ids are kept, so old buttons in the chat answer "Already deleted." and can never hit a new entry); the emergency goal cleared (goal and month); test keywords `flowers`, `tickets`, `salary` removed. Kept: categories, keyword `coffee` -> Eating out, USD rate 0.92, the October summary mark.
- Check on a fresh copy through the real dispatcher: `/last` "No entries yet.", `/month` and `/month 10` "No entries.", `/savings` "No pots yet."

## Still open

- Misha checks the new replies, `/last` view, goal deadline and Menu button in Telegram.
- Misha confirms the October summary and file arrived.
