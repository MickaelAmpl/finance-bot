# Review of spec-ai-input-2026-11-01.md: security, privacy, operations, cost

Reviewer angle: security, privacy, operations, cost control. Read-only. Date of review: 01.11.2026.
Repo state unchanged (`git status` shows only the untracked `.agents/` and `.codex/` that were there before).

Verdict: nothing in the spec is unsafe to approve in principle (owner-only gate, read-only tools, Save button, no card on the Anthropic account). One spec statement cannot work as written (finding 1). Findings 2-11 should go into v2 before the plan is written. Findings 12-16 are minor.

## How this was checked (evidence sources)

- Files read: the spec, `_config/*.md`, `app/deploy/*`, `app/finbot/{config,__main__,jobs,db,ledger,texts,reports}.py`, `app/finbot/bot/{session,access,app,handlers}.py`, `app/tests/{conftest,test_runner,test_deploy_files}.py`, release record phase 1.3, `HANDOFF.md`, `shared/decisions.md`, (setup notes kept private), QA report Q-12, the claude-api skill (error codes, Sonnet 5.5 section).
- aiogram 3.31.0 source in `app/.venv` (dispatcher polling).
- anthropic 2.3.0 wheel and httpx2 downloaded into the scratchpad and read (not installed into the repo). A scratch venv (`.../scratchpad/venv-check`, Python 3.12) with `aiogram==3.31.0` + `anthropic==2.3.0` was used for a probe script: `.../scratchpad/probe/probe_log.py` (fake key `sk-ant-api03-FAKE...`, base URL `http://127.0.0.1:9`, so no external network).
- Read-only ssh on `the server`: `free -m`, `nproc`, `uname -m`, `df -h`, python versions, `pip list` of the app venv, `systemctl cat finance-bot.service`, `systemctl show` (MemoryCurrent, NRestarts), `journalctl --disk-usage`, `curl -sI https://api.anthropic.com` (no key, plain, with -4 and -6). No `.env` was opened.
- One slip on my side: I opened a terminal tab (`c4`) with `echo skip` by mistake. It did nothing.

## Findings, most important first

### 1. [blocker] A2.2 "no extended thinking" cannot be implemented as written on Sonnet 5.5

Evidence: claude-api skill, Sonnet 5.5 section and `shared/error-codes.md`: on `claude-sonnet-5-5`, `thinking: {"type": "disabled"}` returns HTTP 400; leaving `thinking` out runs adaptive thinking; effort defaults to `high`. The only "off" switch is `thinking: {"type": "between_tools"}` (accepted at effort `high` or below, no other field inside `thinking`).

Why it matters here: (a) someone follows the spec literally and sends `disabled`: every call is a 400, and the fake-client tests cannot see it; only the live run would. (b) Someone omits it: thinking tokens are billed as output and count against `max_tokens` 1024, so a draft with 10 entries can be cut off (`stop_reason: max_tokens`), which the bot then reports as "I could not make sense of that" (A9.3). The cost estimate in the spec (300 output tokens) assumes no thinking.

Spec change, A2.2: replace "no extended thinking" with:
"`thinking: {"type": "between_tools"}` (the only way to switch thinking off on this model: `disabled` is a 400 and leaving it out turns adaptive thinking on), `output_config: {"effort": "medium"}` (the default `high` is for coding; `between_tools` is accepted only at `high` or below). In the tool loop the assistant content blocks are sent back unchanged, including any `thinking` blocks. A `max_tokens` stop reason is a failure (A9.3) and shows in the log line."
Add to the live run (Testing 2): "the log line of every call shows `end_turn` or `tool_use`, never `max_tokens`; choose effort `low` or `medium` by the result".

### 2. [should fix] A2.2 "timeout 60 s, retries 2" does not bound how long one message can hang

Evidence: anthropic 2.3.0 `_base_client.py` `_calculate_retry_timeout`: "If the API asks us to wait a certain amount of time, just do what it says" and `return min(retry_after, 4_294_967.0)`. There is no cap on `Retry-After`; a 429 with a long header makes the SDK sleep for that long inside the call. Without that, the arithmetic is already: 60 s x 3 attempts x 4 calls = 12 minutes (the skill also notes "Timeouts are retried - wall-clock can reach timeout x (max_retries+1)"). A float `timeout=60` also replaces the SDK's 5 s connect timeout with 60 s.
aiogram does not help: updates run as separate tasks with no limit (`dispatcher.py:359-410`, `handle_as_tasks=True`, `tasks_concurrency_limit=None`; `__main__.py:26` uses the defaults), so the bot stays responsive, but Misha gets no reply, and with finding 3's lock every later AI message waits behind the hung one. The daily job is a separate systemd process and is not affected.

Spec change, A2.2, add: "The client is `AsyncAnthropic(api_key=<from settings>, timeout=anthropic.Timeout(60.0, connect=10.0), max_retries=2)`, created once at startup and closed on shutdown. The SDK obeys a `Retry-After` header without an upper limit, so the whole handling of one user message (all model calls, tools, retries) runs under `asyncio.timeout(100)`. On timeout: the A9.2 reply and one log line with the word `deadline`."
Add to A9.2 list: "or the 100 s deadline".

### 3. [should fix] A8, A2.4: no rule for concurrent AI messages; shared memory and one outer catch-all missing

Evidence: aiogram runs every update as its own task (finding 2). Misha sends two messages in a row, or an album: A5.1 says every photo is its own message and its own draft, so an album of 10 photos starts 10 simultaneous flows, 10 parallel API calls, 10 interleaved writers to the "last 10 messages" list. The memory list then holds `user, user, assistant, assistant`, and after truncation to 10 it can start with an assistant turn, which the API can refuse with a 400 (the skill's error table lists "messages not alternating user/assistant"; I did not test the current rule for a leading assistant turn). The same burst can hit the new organization's rate limits (429, then the uncapped wait of finding 2).
Also: `dispatcher.py:322-330` logs `str(e)` of any unhandled exception and the user gets no reply. The AI flow has many new failure points (photo download, base64, JSON, tool input, sqlite).

Spec change, new A2.7 (or A8):
"AI messages are handled one at a time: one `asyncio.Lock` around the whole AI flow (model calls, tool execution, memory update). Memory is a `collections.deque(maxlen=10)`; the user turn and the bot turn are appended together after the flow succeeded, so a failed flow leaves no half pair and the list always starts with `user`. Tool code and DB code of the AI flow run in the event-loop thread (the shared `sqlite3` connection is bound to it; no `to_thread`) and never `await` between the first write and the commit. The AI flow is wrapped in one `try/except Exception`: the user gets the A9.3 reply, the log gets the exception class name only (no `exc_info`, no message text)."
Test: two messages sent with `asyncio.gather` produce memory `[user, bot, user, bot]`; a tool that raises produces one reply and no traceback containing the message text.

### 4. [should fix] A6.1/A6.3: "Pressing Save twice can never save twice" needs a stated mechanism; `add_transaction` commits per entry

Evidence: `ledger.py:56` `with conn:` commits after each entry. A Save that flips the draft to `saved` first and then calls `add_transaction` for 3 entries commits after entry 1; a failure on entry 2 leaves a `saved` draft with one entry, and a concurrent second tap sees `saved`. If the status is flipped last, two concurrent taps (two tasks) can both pass the `open` check before either commits, only if an `await` sits between check and commit.

Spec change, A6.1, add: "Save is one transaction: `BEGIN IMMEDIATE`, then `UPDATE drafts SET status='saved' WHERE id=? AND status='open'`; if no row changed, answer by the A6.3 rule and stop; otherwise insert all entries without committing in between (the existing typed-entry path gets a no-commit variant), commit once, then send the replies. No `await` inside the transaction. Test: two Save callbacks run with `asyncio.gather` produce exactly one set of entries; a forced error on the second entry leaves the draft `open` and no entry saved."

### 5. [should fix] A10.2: the existing log filter takes one token, breaks on an empty value, and matches only the exact string

Evidence: `session.py:8-33`: `_TokenFilter(token)` replaces one exact string; `redact_token_in_logs(token)` takes one value; `__main__.py:21` and `jobs.py:75` pass only `bot_token`. `str.replace("", "***")` on an empty secret inserts `***` between every character (checked: `"abc".replace("","***")` gives `'***a***b***c***'`), so wiring the optional key as `redact_token_in_logs(settings.anthropic_api_key)` with no key configured would garble the whole log. `config.py:14-18`: `Settings` is a plain dataclass, so its auto `repr()` prints `bot_token` and the new key if a `Settings` object is ever logged or lands in an assertion message.

Spec change, A10.2, replace with: "The log filter hides every configured secret (bot token, API key). Empty or missing secrets are skipped. In addition it hides anything that looks like an Anthropic key: pattern `sk-ant-[A-Za-z0-9_-]{8,}`. In `Settings`, the token and the key fields are declared with `field(repr=False)`." Tests: (a) key in a message, in a traceback, and in a chained exception is hidden; (b) with no key, log text is unchanged; (c) `repr(Settings(...))` contains neither value.
Note: the AI flow's own rule (log the class name only) is the main defence; the filter is the second one.

### 6. [should fix] A2.6/A10: an `ANTHROPIC_LOG=debug` line in `.env` would write every message and receipt photo into the journal

Evidence (probe, anthropic 2.3.0, httpx2 2.16.0): with root level INFO as today, a failed call logs one line, `INFO:anthropic._base_client:Retrying request to /v1/messages in 0.48 seconds`, no key, no text; the exception text is `Connection error.`. With `ANTHROPIC_LOG=debug` in the environment, the probe printed "user text in logs: True" (the SDK logs `Request options: ...` including the messages, `_base_client.py:602`; the key itself did not appear). systemd passes the whole `.env` into the process (`finance-bot.service` `EnvironmentFile=`), and the SDK reads `ANTHROPIC_LOG` at import time (`_utils/_logs.py`). A successful call also logs `HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"` from the `httpx2` logger at INFO (harmless, but a second line per call next to A2.6).

Spec change, A2.6, add: "After `import anthropic`, `main()` sets the level of the `anthropic` logger to INFO and of `httpx2` and `httpcore2` to WARNING, whatever `ANTHROPIC_LOG` says, so the SDK can never write message content or photos to the journal." Test: with `ANTHROPIC_LOG=debug` set and a call to a closed local port, the captured log does not contain the message text.

### 7. [should fix] A5.1: say that the photo goes to the API as base64, never as a Telegram file URL

Evidence: aiogram downloads photos from `https://api.telegram.org/file/bot<BOT_TOKEN>/...` (the project already knows URLs carry the token, `agent-team-tool-limits.md`). The API accepts an image by URL. If the implementer passes that URL as the image source, the bot token goes to Anthropic and the file is fetched from outside the server. The spec says only "downloaded" (A9.4) and "sends it ... as JPEG".

Spec change, A5.1, add: "The bot downloads the file itself and sends the bytes as a base64 `image` block with media type `image/jpeg`. The Telegram file URL is never sent to the API. A file larger than 5 MB (the API limit) is refused with the A9.4 reply."

### 8. [should fix] Cost: no cap on the bot side; the spec's cost section covers only the typical case

Numbers (my estimates, prices from the claude-api skill: Sonnet 5.5 $2 / $10 per million tokens; the spec's typical message of 3,000 in / 300 out is about $0.009, which matches):
- Worst case for one message: 4 model calls; input grows as tool results are appended (system + tools about 2,000, history up to about 2,500, message about 300, a receipt about 1,600, `list_entries` up to 100 lines about 4,000 per call). Roughly 44,000 input tokens and 4 x 1,024 output tokens in total, about $0.09 + $0.04 = about $0.13, thirteen times the typical one-cent message.
- Retries multiply HTTP requests (up to 12 per message) but only generated responses are billed, so no change to the estimate.
- Nothing in the bot limits the number of messages per day. Tool loops are capped (A2.4); the count of messages is not.
- The hard stops that exist: (1) no payment method on the Anthropic account, so spend cannot exceed the promotional credits and nothing can be charged (HANDOFF, key section); (2) the $20 monthly limit set on the whole organization (`shared/decisions.md`, 01.11 row), which only matters if a card is added later. $20 equals about 150 worst-case messages or about 2,000 typical ones. So the question "is $20 plus the 4-call cap enough?": for money, yes (today the money at risk is zero); for availability, no: a bug or a burst can spend the month's credits in an hour and the AI is dead until the next grant.
- Who can trigger spend: only the owner. `OwnerOnly` is an outer middleware on `dispatcher.message` and `dispatcher.callback_query` (`app.py:27-29`), it wraps the sub-router, and `_is_owner_in_private` requires owner id and a private chat for both `Message` (photos are `Message`) and `CallbackQuery` (`access.py:24-33`). A foreign user's photo or Save press never reaches a handler. Other update types have no handlers.
- Spec versus HANDOFF: HANDOFF (20:10) says the workspace $20 limit is "not yet confirmed"; `decisions.md` (later) says it is set on the organization, the workspace has none. There is no screenshot or date for it in the repo.

Spec change, new A2.8: "The bot counts model calls per Vienna day in the existing `meta` table (key `ai_calls:YYYY-MM-DD`, no new table). At 100 calls the AI is off until midnight: `Daily AI limit reached. Nothing saved. Write it as 25 coffee; it resets at midnight.` The check runs before every model call, so the tool loop also stops. The same row family may keep input and output token sums per month (`ai_tokens:YYYY-MM`) so the real cost is readable without searching the journal." At 100 calls the worst case is about $3 a day, normal use (10 messages, 15-25 calls) is far below.
Cost section, add: "Real money at risk today: none (no card). The $20 limit becomes the guard only if a card is added; adding a card needs a re-check of the limit first."
Release checklist: a Console screenshot of the spend limit and of the credit expiry date, saved in the release record.

### 9. [should fix] A9: credits expire on 08.11; the failure buckets hide the cases Misha must act on

Evidence: HANDOFF: "$100 promotional credit, granted 01.11.2026, expires 08.11.2026 ... the next $100 arrives after the plan renews". `api-key-setup-ru.md`: unspent credits burn at the end of the period. The spec's Cost section says "inside the $100 Max credits" with no date, and A9.1 says "used up for this month". Acceptance ("a week of logs", "9 of 10 messages") straddles 08.11. On 08.11 credits expire, they are not "used up"; there may be a gap before the next grant.
The skill's error table lists 402 `billing_error` next to 400 `invalid_request_error`; the spec says only "the API says the credit balance is too low", with no way to detect it. A real exhausted-credit response cannot be tested without spending everything; the fake-client test will use a made-up shape.
A9.2 puts "spend limit reached" and "invalid key" into the same reply as a transient outage ("AI is not available right now"), which tells Misha to wait when he must act.

Spec change, A9, replace items 1-2 with three buckets:
1. Money: status 402, or 400 with a message containing `credit balance` or `usage limit`: `AI credits are used up or expired. Nothing saved. Write it as 25 coffee.` Log at ERROR: status, error type, request id.
2. Access: status 401 or 403 (key revoked, wrong workspace, not allowed): `AI key problem, ask the agent to check it. Nothing saved. Write it as 25 coffee.` Log at ERROR.
3. Everything else from the API (timeout, connection, 429, 5xx, 529, deadline): `AI is not available right now. Nothing saved. Write it as 25 coffee.`
"Detection is by status code and error type first; the message text is only a fallback for bucket 1. An unknown shape falls into bucket 3."
Cost section, add: "Credits granted 01.11 expire 08.11; the next grant arrives when the plan renews. Misha checks the expiry on platform.claude.com/settings/billing before acceptance."
Checklist: a zero-cost check of bucket 2 with the real SDK, by starting a local copy of the bot with a deliberately wrong key (`sk-ant-wrong`): the reply is the access message, the log shows `AuthenticationError 401`, no spend.

### 10. [should fix] Testing section: where the live run happens, how it gets the key, and a network guard for the unit tests

Evidence: Testing 2 says "one live run ... on a copy of the server database" but not where. The key exists only in the server `.env` (HANDOFF; Misha was told "put it nowhere else", `api-key-setup-ru.md`). `_config/storage-rules.md`: "Runtime data never leaves the server, except the CSV export Misha asks for". The only existing precedent is the `iterdump` simulation on the Mac (memory `finance-bot-build-process`). `deploy.sh` step 4 runs `pytest` on the server with `cwd=/opt/finance-bot`, where the real `.env` sits; the cwd-relative `Path(".env")` in `__main__.py:13` and `jobs.py:23` would read it if a test called `main()`. `test_runner.py:20` copies the whole environment into subprocesses (removing only BOT_TOKEN and OWNER_ID).

Spec change, Testing:
- 2: "The live run executes on the server in a separate directory (`/opt/finance-bot-livetest`), not in `/opt/finance-bot`, not through the service, with a database copy made by the sqlite backup API (mode 700 directory). The script reads the key from `/opt/finance-bot/.env` inside the process and never prints it. It prints only drafts, answers and the token log lines. It stops after the 13 messages (about $0.20, Misha's yes). The copy is removed only with Misha's yes. The run must include at least one tool loop (a question) and one `propose_entries`."
- 1: add "A `conftest.py` autouse fixture (a) blocks `socket.socket.connect` for every address except loopback, (b) deletes `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_LOG` from the environment, so a mistaken real client call fails at once and costs nothing. `test_runner.run_python` also drops those variables."

### 11. [should fix] Deploy and rollback: `.env` check, rollback wording, first-live-call checklist

Evidence:
- `deploy.sh:79` step 5 checks only `BOT_TOKEN`, `OWNER_ID` and mode 600, and fails without a message (HANDOFF note). A10.1 says the check "stays as is". If the key line is missing or empty, the bot starts normally and free text silently gets the old "Start with the amount" reply (A1.3); nothing tells Misha the AI is off.
- Rollback: `db.py:12-17` only acts on versions 0, 1, 2; an old binary opening a version-4 database falls through all three branches and works (the `drafts` table is ignored). So after this release the correct rollback is code only (deploy the previous commit; this was already the practice, release record 1.3: "deploy `96b0137` again"). The printed rollback line restores the database copy, which would throw away every entry made after the deploy and is right only if the migration itself damaged the data.
- Step order (`deploy.sh:65-90`): new code and `pip install` land in the live venv (steps 1, 3) before the server tests (step 4) and before the restart (step 7). If tests fail, the old process keeps running, but a reboot of the VPS would start new code and migrate the database. Existing behaviour, but the migration makes it matter more.
- Server: Python 3.12.3, x86_64, pip 24.0; a dry run for `x86_64-manylinux_2_28`, cp312, `--only-binary :all:` resolves all 28 packages as wheels (no compiler needed). `anthropic==2.3.0` adds 10 packages: anyio, docstring-parser, h11, httpcore2, httpx2, jiter, opentelemetry-api, sniffio, truststore (plus anthropic). Only `anthropic` is pinned; the other nine float, and the server tests run in a fresh temporary venv that may resolve different versions than the live venv.

Spec change, A10.1, replace "The deploy check of `.env` stays as is" with: "The deploy check of `.env` gets one more informational step that never fails the deploy and never prints a value: it prints `AI key: present` or `AI key: MISSING (AI input will be off)`. At startup the bot logs one line `AI input: on (model claude-sonnet-5-5)` or `AI input: off (no key)`."
Add a "Release and rollback" section to the spec:
- "Rollback of this release is code only: deploy the previous commit. The version-4 database works with the old code (test: open a copy of a version-4 database with the previous release's `db.connect`). Restore the database backup only if the migration damaged data, and say that this loses entries made since."
- "Release checklist additions: (1) `AI key: present` in the deploy output; (2) the journal for the first minute shows `AI input: on`, no traceback; (3) one real message from Misha (`вчера 25 на кофе`) gives a draft; afterwards the agent checks the journal: exactly one A2.6 line per model call, `grep -c 'sk-ant'` is 0, and the message words (`кофе`) do not appear; (4) `systemctl show -p MemoryCurrent finance-bot.service` before and after (baseline 151 MB, RSS 170 MB); (5) `pip freeze` of the live venv saved in the release record; (6) neighbours `job-digest-bot.service` and `other-service.timer` active, crontab md5 unchanged, as in 1.3; (7) if the key leaks: revoke it in the Console, put a new line in `.env`, `systemctl restart finance-bot.service`."
- The step 5 silent failure (HANDOFF) can be fixed in the same change: print which key is missing.

### 12. [minor] Failure visibility for a one-person bot

Answer to the question: with findings 9 and 11 the chat reply at the moment of use is enough for the failure itself, because the AI is only called when Misha writes, so there is no moment when it fails unseen. What is still missing: (a) a silent "off" state when the key is missing (fixed by the startup line and the deploy line in finding 11); (b) early warning before expiry (08.11 is known; put it in the release record and in Misha's calendar, since the bot cannot read the credit balance without an Admin key, which should not be put on the server); (c) real usage numbers: the token log lines in the journal are the only source in the spec (A2.6), and Misha does not read the journal; the `ai_tokens:YYYY-MM` counters from finding 8 make a one-line "AI this month: N calls, about $X" possible in the monthly summary later (optional, not needed for the first version). A proactive alert message is not needed.

### 13. [minor] A10.3 privacy list is incomplete; retention not verified

What leaves the server per call, from the code: the message text and caption; the photo; the system prompt (date, currencies, all category names including his own); the last 10 turns including the bot's earlier replies (amounts, notes, category names); every tool result. `month_summary` returns the full `/month` report, which includes the savings pots block (names, balances, goals) and top entries (`reports.py:80-95`, `_savings`), but A7.1 lists only "totals, categories, budgets, top entries". `list_entries` returns the free-text notes of up to 100 entries. A receipt can carry card digits, a name, a loyalty number, the store address; Telegram strips photo metadata, so no GPS. No telemetry was found in the SDK source (logging only; `opentelemetry-api` is a no-op without a configured exporter). Prompt injection through a receipt or an old note cannot write anything: the only write path is `propose_entries`, which needs the Save press, and the only output channel is the reply to Misha; no URL is fetched.
Not verified by me: Anthropic's current API data-retention period and training policy for this account type. The record of Misha's "4 - ага" should carry the vendor's retention sentence copied from Anthropic's privacy page.
Spec change, A10.3: list the items above; A7.1: add "savings pots" to the `month_summary` content; A8: memory is dropped after 2 hours without a message (a day-old conversation is not sent again and costs nothing); drafts keep the entries JSON on disk after Save and Cancel (state it; optional cleanup of saved and cancelled drafts older than 30 days in the daily job).

### 14. [minor] A2.6, A4.5, A2.5: small gaps

- A2.6 log line: add the request id (`message._request_id`, no content), the call number (1 of 4), elapsed milliseconds, source (`text` or `photo`), and for failures the error class and status. Never `str(error)`.
- A4.5 / reply length: A3 asks for under 800 characters but nothing enforces it; Telegram refuses over 4096 and the failure would be silent. Add: "a reply is cut to 4000 characters and sent without `parse_mode`" (also draft text: notes may contain `<`).
- A2.5: "typing" lasts about 5 s in Telegram; for a 20-60 s call it disappears. The `send_chat_action` call must not be able to fail the flow (wrap, ignore `TelegramAPIError`).
- Restart during a call: aiogram has already advanced the update offset, so a message in flight when the bot restarts gets no reply and no draft. Nothing is saved; mention in Known risks.

### 15. [minor] CSV formula cells now have an untrusted source (Q-9)

Q-9 (CSV formula cells) was accepted as backlog for typed notes. AI notes come from receipts (store names read from a photo), so a hostile receipt can put `=HYPERLINK(...)` into a note that later lands in the monthly CSV Misha opens in a spreadsheet. Low probability. Proposed: A4.2 note rule, "a note starting with `=`, `+`, `-` or `@` gets a leading apostrophe or is stripped of that character" (or fix Q-9 in the export for all notes).

### 16. [minor] Server resources: no concern

`the server`: 6 CPUs, 11.7 GB RAM with 10.9 GB available, no swap, load 0.01, 174 GB free disk; Python 3.12.3. `finance-bot.service`: RSS about 170 MB, cgroup 151 MB, `NRestarts=0`, no memory limit. `job-digest-bot.service`: 19 MB. The probe measured +25 MB after `import anthropic` on top of aiogram (175 to 200 MB RSS on the Mac). Image handling is a base64 string of a few hundred kilobytes. Journal 1.5 GB, content-free if findings 3 and 6 are applied. Outbound: `curl -sI https://api.anthropic.com` returns `HTTP/2 404` from Cloudflare (reachable); both `-4` and `-6` work (connect 10 ms and 4 ms), so the Telegram IPv6 trap does not apply to this host; no IPv4 pin is needed for the Anthropic client today. A 60 s model call does not block other Telegram messages or the daily job (async client, separate processes), provided the DB code stays synchronous and short (finding 3).

## Checked and fine

- Key from `.env` to the client: `EnvironmentFile=` puts `ANTHROPIC_API_KEY` into the bot's environment, and the SDK reads it from there. Still, `Settings` should carry it and the client should get `api_key=` explicitly, so the "key configured?" check in A1.3 and the client use the same source, and `ANTHROPIC_AUTH_TOKEN`, a profile on disk or a stray `ANTHROPIC_BASE_URL` in `.env` cannot change where the key goes. Consider also passing `base_url="https://api.anthropic.com"` explicitly.
- The SDK's default logs (INFO) carry no key and no text; exception strings (`Connection error.`, status errors) carry no key (probe).
- Old code on a version-4 database: works (finding 11).
- Migration pattern: the 3 to 4 step must copy the `BEGIN IMMEDIATE` plus re-check pattern of `db.py:30-48`, because the bot and the daily job both call `connect()`.
- No model-controlled SQL: `list_entries` arguments must stay parameterized (engineering rules).
- Tests: the A10.2 test needs a key-shaped string like `TOKEN = "123456:SECRET"` in `test_runner.py:14`.
- The daily job (09:00) does not use the AI and does not need the key; it receives it only because it shares `.env`. No action.

## Proposed order for v2

1 (thinking), 2 and 3 (deadline, lock, catch-all), 4 (Save transaction), 5 and 6 (log filter, SDK loggers), 7 (base64), 8 (daily cap), 9 (buckets, expiry), 10 (live run, test guard), 11 (deploy and rollback section). Then the minor items 12-15 as one short list.
