# Server rules

- Server: Misha's VPS, ssh alias `the server`. It also runs job-digest (`/opt/job-digest`) and another project. Never touch their files, services, cron lines or databases.
- Finance bot lives in `/opt/finance-bot`: own venv, own `.env` (mode 600), own database `data/finbot.db` (mode 600), own systemd units `finance-bot.service` and `finance-bot-daily.timer`.
- Every deploy, and every server command that changes state, needs Misha's explicit approval in chat for that specific deploy. Read-only checks (status, logs, `timedatectl`) are allowed during an approved release.
- Deploy only with `app/deploy/deploy.sh`: dry-run first, database backup before switching, tests run on the server copy, printed rollback line. Modeled on job-digest's `scripts/deploy.sh`.
- Trap: rsync copies local file modes and once dropped `+x` on a job-digest script. The deploy script checks executable bits after copying.
- Trap: never start a remote wait loop whose `pgrep` pattern appears in its own command line (job-digest, 26.10.2026).
- Backups: nightly copy of the database to `/opt/finance-bot/data/backups`, 14 newest kept. Monthly CSV of all entries arrives in Misha's chat with the summary.
- If the server is unpaid it goes down. Data stays on disk; the bot is silent until payment.
- The bot token is entered by Misha himself into `/opt/finance-bot/.env` following the release instructions. Agents never read or print it.
