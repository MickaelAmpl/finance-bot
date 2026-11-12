# 06 Release

Job: Misha accepts the phase with the dev bot, then the product owner deploys to the server only with his explicit approval.

## Inputs

| Layer | File / scope |
|---|---|
| 3 | `../../_config/server-rules.md`, `../../_config/telegram-rules.md` |
| 3 | `../05_qa/references/acceptance-checklist-phase1.md` |
| 4 | the passed QA report in `../05_qa/output/` |
| 4 | `../../app/deploy/` (deploy script, systemd units) |

## Process

1. Acceptance: the product owner runs the bot locally on the Mac with the dev bot token. Misha walks the checklist in Telegram and answers "ок" or lists fixes.
2. Ask Misha for deploy approval in one line naming what will be deployed. Wait for an explicit yes.
3. First release only: Misha creates the prod bot, the product owner gives him the exact steps to put the token into `/opt/finance-bot/.env` himself.
4. `deploy.sh --dry-run`, then `deploy.sh`. Check `systemctl status`, the timer, one message to the prod bot from Misha, the backup file.
5. Record the release.

## Outputs and review gate

`output/release-phase<N>-YYYY-MM-DD.md`: what was deployed (commit), checks with output, rollback line, Misha's approval quote. Update `HANDOFF.md` and `shared/decisions.md`.
