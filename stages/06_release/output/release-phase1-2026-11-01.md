# Release: phase 1, 01.11.2026

## What was deployed

- Commit `461f40a` (code head `fa769f4` plus docs), `main`, nothing pushed.
- Host `the server` (Misha's VPS), `/opt/finance-bot`, units `finance-bot.service` and `finance-bot-daily.timer`.
- Bot: @my_finance_bot ("Finance Bot"). It was created as the dev bot and is now the only bot (no separate prod bot).

## Approval

- Acceptance moved from the Mac to the server: "такой вариант не подходит ноутбук слишком сильно грузит, давай класть на сервак". Measured before stopping the local bot: the bot used 0.1% CPU and 17 MB RSS; the load came from a Chrome renderer (100% CPU) and `replayd` (35%). Misha was told; the move stands.
- Deploy: "Да, выкладывай" (after the one-line summary: phase 1, commit 461f40a, `/opt/finance-bot`, bot around the clock, daily job at 09:00 Vienna).

## Token

- Local `app/.env`: Misha typed the token in a Terminal panel prompt (hidden input). His Telegram id could not be taken from @userinfobot, so a scratch script read `getUpdates` of his own bot and wrote `OWNER_ID` (it prints sender ids and names only, never the token).
- Server `.env`: Misha ran `ssh the server '... cat > /opt/finance-bot/.env && chmod 600 ...' < app/.env` himself. Checked without values: mode 600, 76 bytes, `BOT_TOKEN` and `OWNER_ID` set.

## Checks

Before the deploy (read-only):
- Server: Python 3.12.3, systemd 255, time zone Europe/Berlin (the timer names Europe/Vienna itself), 174 GB free, 11 GB RAM free, `/opt/finance-bot` did not exist.
- Neighbours baseline: `job-digest-bot.service` active, `other-service.timer` active, root crontab 18 lines, md5 `<md5>`.
- `deploy.sh --dry-run`: all 8 steps printed, nothing changed.

Deploy (`FINBOT_HOST=myvps app/deploy/deploy.sh`, exit 0):
- Step 2: backup dir `/opt/finance-bot-backups/2026-11-01-114032` created; no database existed yet, so no backup file.
- Step 4: `372 passed in 32.56s` on the server copy.
- Step 8: `finance-bot.service: active, NRestarts 0`, `finance-bot-daily.timer: active`. The release note "NRestarts must be 0 on the first deploy" is confirmed.
- Final line: "no database backup on the server, so there is nothing to roll back" (first deploy, expected).

After the deploy:
- `systemctl status finance-bot.service`: active (running) since 11:41:53 CET, memory 150 MB.
- Journal: `Start polling`, `Run polling for bot @my_finance_bot id=<bot id> - 'Finance Bot'`; no token in the log (checked through a mask).
- Timer: next run Mon 2026-11-02 09:00 CET, not run yet.
- Files: `.env` 600 root; `data/` 700, `finbot.db` and WAL files 600 root.
- Neighbours: `job-digest-bot.service` active, `other-service.timer` active, crontab md5 unchanged.

## Rollback

- Database: none to restore (first deploy). Later deploys print their own rollback line.
- Stop the bot: `ssh the server "systemctl disable --now finance-bot.service finance-bot-daily.timer"`.

## Known after this release

- rsync kept the Mac owner on the code files (`/opt/finance-bot` and the code are owned by uid 501 / staff; `.env` and `data/` are root). The services run as root, so it works; `--chown=root:root` in step 1 would tidy it. Not changed (no change without Misha's decision).
- Misha's first test messages went to the local bot on the Mac; they stay in the local `app/data/finbot.db` and were not deployed.
- The first backup file appears at the first daily run (02.11 09:00) or a manual run of `finance-bot-daily.service`.
- The daily run on 02.11 checks the October summary: it sends one only if the database has October entries (for example the acceptance line `25 coffee 28.10`).

## Acceptance on the server bot (01.11)

Misha's answers (screenshot of `/last` attached in chat):
- 1 Entry: dates land right (`/last`: `31.10` for `yesterday`, `28.10`), but the reply does not show the date -> phase 1.1 Task 1.
- 2 Rate: works; "USD rate set: 0.92 EUR. Converted 1 pending entry." was not understood -> Task 1.
- 3 New word (`42 dm`): the checklist wording was unclear to him (dm is the drugstore); no category picked. Not a defect.
- 4 Buttons: "работают хорошо".
- 5 `/last`: clear but "#1 category" buttons are inconvenient -> Task 2.
- 6 Errors: "все ок".
- 7 `/goal`: wants a deadline -> Task 3.
- 8 `/export`: "удобно работает"; wants comments on entries. Already possible: everything after the first word is the note (checked with `parse_entry`: `25 coffee с другом на рынке` -> keyword `coffee`, note the whole text).
- Navigation: does not want to remember commands -> Task 4 (Telegram Menu button).

Items 7, 8, 10 run by the agent ("пройди сам"): the real dispatcher (`build_dispatcher`, MockedBot transport) on a read-only copy of the server database (`iterdump` over ssh into the scratchpad), owner id <owner id>, today 01.11:
- 7: `save 200 emergency` -> `total 350.00 EUR`; `take 50 emergency` -> `total 300.00 EUR`; `take 9999 emergency` -> `Emergency has 300.00 EUR, cannot take 9,999.00`; `/goal emergency 10000` and `/savings` -> `Emergency: 300.00 EUR of 10,000.00 (3%)` with dated moves. Pass.
- 8: `/month` November `Spent 65.00`, `Saved 300.00`, `Net -365.00`; the `/export` CSV for November sums expense 65.00, save 400.00, take 100.00 (300.00 net saved); no pending rows. `/month 10` `Spent 50.00` = the two October `coffee` rows. Pass.
- 10: a foreign user's text, command and button press, and the owner's message in a group: no reply and no API call. Pass (simulated updates; a real second Telegram account was not used).
- 9 (monthly summary) and 11 (backup) still open.

## Still open

- Phase 1.1 fixes (`stages/03_plan/output/phase1-1-fixes-plan-2026-11-01.md`), then a redeploy with Misha's yes.
- Item 9 after the fixes (manual run of `finance-bot-daily.service` with Misha's yes), item 11 after 02.11 09:00.
- After acceptance: clear the test entries, only with Misha's yes.
