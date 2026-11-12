# Release checklist: phase 1.4 (AI input), 12.11.2026

Status: step 1 (live check) done 12.11.2026, passed; step 2 (deploy) done 12.11.2026 ("Да, выкладывай"), record `stages/06_release/output/release-phase1-4-2026-11-12.md`; step 2.8 and acceptance wait for Misha's real messages. Each step that spends money or changes the server needs Misha's explicit yes in chat for that step.

Code: `main`, code head `2aa9174` (QA fix set applied), pytest 1120 passed, ruff and pyright clean.

## 0. Before anything (done)

- [x] Credits: $100 promotional, granted 05.11.2026, expires 08.12.2026 00:00 UTC, $0 used, no payment method (Misha's Console screenshot 12.11 15:45).
- [x] Limit: organization monthly spend limit $20, $0 used, resets 01.12.2026; workspace `finance-bot` inherits it (screenshot 15:46).
- [x] QA findings decided by Misha ("Да, правь"; Q-1, Q-2, Q-3, Q-5 fixed and re-checked) (`stages/05_qa/output/qa-phase1-4-2026-11-12.md`), agreed fixes built, reviewed, gate green.

## 1. Live check on the real model ([Q6]) - needs Misha's yes for about $0.30

Runs on the server in a separate folder, never in `/opt/finance-bot`, never through the bot service, on a synthetic database the script builds itself. The key is read in-process from `/opt/finance-bot/.env` and never printed.

1. `rsync -az --exclude .env --exclude data/ --exclude .venv/ --exclude __pycache__/ app/ the server:/opt/finance-bot-livetest/app/`
2. `ssh the server "umask 077 && cd /opt/finance-bot-livetest/app && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt"`
3. `ssh the server "cd /opt/finance-bot-livetest/app && .venv/bin/python -m finbot.livetest --env /opt/finance-bot/.env --db /opt/finance-bot-livetest/live.db"` (15 messages, at most 60 model calls; the daily cap in the synthetic DB is separate from the bot's).
4. Save the printed output to `stages/06_release/references/livetest-phase1-4-YYYY-MM-DD.txt` (it contains synthetic data only). Check: every `ai call` line has `request=req_...`; no `sk-ant` anywhere (`grep -c sk-ant` = 0); every draft and answer compared with the `expected:` lines; the first call proves the API accepts the four strict tool schemas and `output_config.effort`.
5. Note the real tokens and cost per message from the log lines (spec Cost section: 0.6-4 cents expected). If the average thinking output looks large or answers slow, consider `thinking: between_tools` later (review finding, not in this phase).
6. Remove `/opt/finance-bot-livetest` only with Misha's yes.

Note: the live run calls the model directly, so it does not test routing; routing of `20 фунтов обед` and similar is covered by tests (Q-1). The script exits 1 if any turn failed.

### Result of the live check (12.11.2026, Misha: "Да, запускай")

Ran on the server in `/opt/finance-bot-livetest` (own venv: `pip check` clean, anthropic 2.3.0, aiogram 3.31.0), code `2aa9174`, synthetic database `/opt/finance-bot-livetest/live.db`, message date 12.11.2026 (Thursday). Output: `stages/06_release/references/livetest-phase1-4-2026-11-12.txt` (synthetic data only; `grep -c sk-ant` = 0 on the server and on the Mac copy). Exit 0, `failed turns: 0 of 15`.

- The API accepted the four strict tool schemas, `output_config.effort: low` and the request shape on the first call (no 400).
- Drafts, 10 of 10 correct: `вчера 25 на кофе с другом` -> -25.00 EUR Eating out 11.11; the correction -> 30.00; `300 грн такси` -> -300.00 UAH Transport; `в пятницу 40 продукты в Billa` -> Groceries 06.11 (most recent Friday); `зарплата 3000` -> +3,000.00 Salary; `50 баксов такси в аэропорт` -> -50.00 USD; `20 фунтов обед` -> exactly `Only EUR, USD and UAH for now. Write it as 25 coffee in one of them.`; `кино 15 и попкорн 7` -> two Entertainment entries; `позавчера аптека 12,80` -> -12.80 Health 10.11; `+200 фриланс за сайт` -> +200.00 Freelance.
- Questions, 5 of 5 match the bot-computed expectations: October spent 1,094.00; Eating out November 36.00 spent, 264.00 left of 300.00; Groceries 01.10-15.10 320.00; pot emergency 500.00; September income 3,000.00.
- Spend: 20 model calls, 50,764 input and 2,303 output tokens, about $0.12 (estimate was $0.30). A text draft is about 0.6 cents, a question (2 calls) about 1.2-1.4 cents. Slowest call 5.5 s.
- Note: one answer mentioned "your open draft ... isn't saved yet" - true in this run (the script never saves drafts); in the bot the memory marks `[draft saved]` after Save.
- Not covered by the live check: receipt photos (no synthetic receipt image), routing (covered by tests), real Telegram.
- `/opt/finance-bot-livetest` stays until Misha says it may be removed.

## 2. Deploy - needs Misha's explicit "да"

Plain words for Misha: "Ставлю ИИ-ввод на сервер: бот начнёт понимать свободный текст и фото чеков, сохраняет только по кнопке Save. Бот перезапустится примерно на минуту, перед этим копия базы. База обновится до версии 4 (новая таблица черновиков), старые записи не трогаются."

1. Baseline (read-only): crontab md5, `job-digest-bot.service` and `other-service.timer` active, `PRAGMA user_version` (3), entry count, `systemctl show -p MemoryCurrent finance-bot.service`.
2. `FINBOT_HOST=myvps app/deploy/deploy.sh --dry-run`, then the real run. Expect step 4 `1120 passed`, step 5 `AI key: present`, step 8 `NRestarts 0`.
3. Journal for the first minute: `AI input: on`, `Start polling`, no traceback; `journalctl -u finance-bot.service --since <start> | grep -c sk-ant` = 0.
4. Database: `user_version 4`, `drafts` table exists, entry count unchanged.
5. `pip freeze` of `/opt/finance-bot/.venv` saved into the release record; `pip check` clean (pydantic must stay below 2.14 for aiogram).
6. Memory after: `MemoryCurrent` (baseline about 151 MB; +25-40 MB expected from the SDK).
7. Neighbours unchanged (crontab md5, job-digest, m2-scheduler).
8. One real message from Misha: `вчера 25 на кофе с другом` -> a draft with Save / Cancel; then the agent checks the journal: one `ai call 1/4 ...` line per call, the word `кофе` does not appear in the journal.

## 3. Acceptance (spec, Acceptance)

Misha's first 10 AI messages and first 5 receipts, not written for the test: target 9/10 and 4/5 drafts correct (amount, currency, kind, date exact; category as he would pick; note not judged). At least 5 money questions checked against `/month` or `/export`. Each miss goes to the release record as message / expected / got and becomes a prompt fix.

## Rollback

- Code only: deploy `20115a4` again (phase 1.3 code); it runs on the version-4 database (the old code ignores the `drafts` table).
- Restore the database backup only if the migration damaged data; it loses entries made after the deploy.
- If the key leaks: revoke it in the Console, put a new line in `/opt/finance-bot/.env`, `systemctl restart finance-bot.service`.
- A restart during an AI call loses that one message with no reply.
