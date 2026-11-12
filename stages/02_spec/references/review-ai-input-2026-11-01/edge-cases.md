# Review: AI input spec v1 — edge cases, failure modes, real product flow

Reviewed: `stages/02_spec/output/spec-ai-input-2026-11-01.md` against `shared/decisions.md` (rows 01.11), `HANDOFF.md`, `_config/engineering-rules.md`, `_config/telegram-rules.md`, `stages/05_qa/output/qa-phase1-2026-10-31.md` and the code in `app/finbot/` at HEAD `2e42add`. Read-only; no repo file changed, no server touched, no `.env` read.

Evidence gathered by running code locally (no network):
- `parse_entries(text, date(2026, 11, 1))` on 26 realistic inputs (results quoted in F1).
- `texts.saved_text`, `last_button_text`, `entry_line` rendered for a Record with an empty keyword and empty note (F3).
- aiogram 3.31.0 source in `app/.venv`: `Dispatcher.start_polling(..., handle_as_tasks=True)` is the default (dispatcher.py line 359), so updates are handled as parallel tasks; `utils/chat_action.ChatActionSender` exists with a 5 s interval.

Severity: **blocker** = must change in the spec before the plan; **should fix** = change the spec text, the plan cannot settle it alone; **minor** = worth one line in v2.

---

## Part A. Spec is wrong or missing

### F1. Number-first free text is saved at once with wrong data, and the "Known risks" line about it is false — BLOCKER
Sections: A1.1, Known risks (bullet 2), Goal.

Scenario. A1.1 sends any text whose first word starts with an amount to the plain parser, which saves immediately with no draft. Real output of `parse_entries` today (01.11.2026):

| Input | Saved as | What he meant |
|---|---|---|
| `2025 total?` | expense 2,025.00 EUR, note `total?` | a question |
| `1 сентября сколько потратил` | expense 1.00 EUR | a question |
| `300 грн такси` | 300.00 EUR, note `грн такси` | 300 UAH (about 6 EUR) |
| `50 баксов такси` | 50.00 EUR | 50 USD |
| `1000 рублей` | 1,000.00 EUR | unsupported currency |
| `25 на кофе вчера` | 25 EUR dated today, keyword `на` | yesterday; a category pick then teaches `на` for every later `25 на ...` |
| `10 октября 25 кофе` | 10.00 EUR, note `октября 25 кофе` | 25 EUR on 10.10 |
| `3 кофе и 2 круассана` | 3.00 EUR | two items |

Why wrong: the spec's Known risks says `2025 total?` "goes to the plain parser and gets its usual error" — it does not, it is saved as a 2,025 EUR expense. The goal is "writes the way he talks" in Russian; number-first Russian phrases (`300 грн такси`, `25 на кофе вчера`) are the most natural form and they bypass the AI and the confirm button, landing as silent wrong entries. Misha's approval of v1 rests on the false risk line.

Proposed A1.1 text:
> 1. Text whose first word starts with an amount (an optional `+`, an optional currency symbol from `money.SYMBOLS`, then a digit), or whose first word is `save` or `take` (any case) followed by an amount: the existing parser first. With the key configured, the message goes to the AI instead, and the parser saves nothing, when the parser refuses it, or when any parsed note contains a digit, a `?`, or a word from the fixed list in the plan (currency words: грн, гривна/гривны/гривен/гривень/гривня/гривні, бакс/бакса/баксов, доллар/доллара/долларов, евро, руб/рубль/рубля/рублей, bucks, dollars, euros, hryvnia; date words: вчера, позавчера, сегодня, завтра, вчора, сьогодні, today, tomorrow; month names января…декабря and січня…грудня). Otherwise the parser saves it exactly as in phase 1.3. Without the key: phase 1.3 behaviour in full.

Proposed Known risks replacement:
> A number-first text that the parser accepts and that has none of the A1.1 warning signs is saved at once: `2025 total` becomes a 2,025.00 EUR expense, `50 bucks` without a note word becomes 50.00 EUR. The reply shows what was saved and Undo is one tap.

Alternative if Misha wants number-first text untouched: keep A1.1 as is, but the Known risks line must list the real effects above (silent wrong currency, wrong date, questions saved as expenses).

### F2. Corrections create a second open draft; a correction after Save creates a duplicate entry — BLOCKER
Sections: A3, A4, A6, A8; decisions row 38 ("no draft editor: Cancel and retype, or fix after saving with the existing buttons").

Scenario (a). `кофе с другом 25 вчера` → draft 1 (Eating out). He writes `нет, это продукты`. Memory holds draft 1's text, so the model proposes draft 2 (Groceries). Both stay `open` with live Save buttons; nothing closes draft 1. Save on both (or on draft 1 days later while scrolling) → two 25 EUR entries.

Scenario (b). He presses Save on draft 1, then writes `нет, это продукты`. A8 remembers the draft text but not that it was saved; A3 has no rule about saved entries. The model proposes draft 2 → Save → duplicate. "Editing entries through AI" is out of scope, but nothing tells the model, so it "edits" by re-drafting.

Same class: typed `сохрани` / `save it` after a draft, `отмени последнюю` — the model cannot act and the spec gives it no instruction.

Proposed changes:
- A8 add: `Save and Cancel add a line to memory right after that draft's text: [draft saved] or [draft cancelled].`
- A3 rules add: `Saved entries cannot be changed or deleted in chat: for a saved entry, point to the buttons under it, /last and /undo, and never propose it again. Draft buttons are pressed by him; typing "save" does nothing. A correction of a draft that is still open proposes the whole corrected draft with replaces_open_draft set to true.`
- A4.1 add field `replaces_open_draft` (boolean) to `propose_entries`.
- A4 new item: `When a draft is stored with replaces_open_draft true, the newest open draft becomes replaced: its message becomes "Replaced by the draft below. Nothing saved." without buttons, and its buttons answer "Replaced by a newer draft."` The `drafts` table (A4.3) gains status `replaced` and the Telegram message id of the draft message.

Alternative (no model flag): any new draft from text replaces every open draft from text; photo drafts are never replaced. Simpler, but `кофе 3` then `и такси 10` before Save drops the coffee draft. Misha's call.

### F3. A6.1 "same path as typed entries" contradicts the code: the AI category is lost and the reply says `New word ""` — SHOULD FIX
Sections: A6.1, A4.2.

Scenario. `ledger.add_transaction` takes the category only from `category_for_keyword(conn, entry.keyword, ...)`; an AI entry has keyword `""`, so saved "through the same path" it gets no category, whatever the draft said. When the category is empty, `saved_text` renders (verified):
```
Saved 31.10: -25.00 EUR · 
New word "" - pick a category:
```
An empty note (receipt with an unreadable store name; the model may return `""`) gives the `/last` button `1.  -25.00 EUR` and record view `31.10 -25.00 EUR `. A note with a line break (`REWE\nWien Mitte`) breaks the one-line reply, `/last` and the month report's top list; typed notes never contain line breaks (`" ".join(tokens)`).

Proposed A6.1 sentence: `Each entry is saved with the category from the draft, or with none. Its reply is the reply a typed entry gets (date, rate line, budget line, buttons), except the category question reads "Pick a category:" instead of "New word "…" - pick a category:".`
Proposed A4.2 addition: `Line breaks and repeated spaces in a note become single spaces. A note that is empty after that becomes the category name, or "receipt" for a photo with no category.`

### F4. "Pressing Save twice can never save twice" is not guaranteed by the described save — SHOULD FIX
Sections: A6.1, A6.3.

Scenario. `add_transaction` commits each entry in its own `with conn` (and Python's sqlite3 `with conn` commits an outer transaction too, so it cannot simply be nested). A 5-entry draft where entry 3 fails to insert leaves entries 1-2 committed and the draft still `open`; the next Save writes 1-2 again. Phase 1.3 accepted per-entry commits for typed messages because there is no Save button to press twice; drafts have one.

Proposed A6.1 sentence: `The draft's status change and all its entries are written in one transaction: either every entry is saved and the draft is saved, or nothing is written and the reply is "Could not save. Nothing saved. Press Save again."`

### F5. Two AI messages at once: memory interleaves, albums hit the API in parallel — SHOULD FIX
Sections: A1.5, A2, A8.

Scenario. aiogram 3.31.0 handles each update as its own task by default (`handle_as_tasks=True`). (a) `кофе 25` then, 3 s later, `нет, это продукты`: the second call starts before draft 1 exists, its memory lacks the draft, the model answers nonsense or drafts `продукты` with no amount. (b) An album of 8 receipts = 8 model calls at the same second, each ~2-5k input tokens; the organisation's rate-limit tier is unknown, so some photos fail with A9.2 after the retries. Memory order follows finish order, not send order.

Proposed A2 item: `One AI request at a time: AI messages wait their turn in the order they arrived. Typed entries, commands and draft buttons never wait for it.` A1.5 add: `Album photos are drafted one after another, in order.`

### F6. A single message can wait up to ~12 minutes, with "typing" visible for 5 seconds — SHOULD FIX
Sections: A2.2, A2.4, A2.5, A9.2.

Scenario. 60 s timeout × (1 + 2 retries) per call × up to 4 calls, plus backoff, is about 12 minutes before the A9.2 reply. Telegram shows a chat action for about 5 s, and A2.5 sends it once per call, so he sees nothing for most of a 10-30 s receipt call and sends the photo again (a second draft). With F5's queue, one stuck call also blocks every later AI message.

Proposed A2 text: `Each message has 90 seconds in total for all its model calls; past that the reply is A9.2. "typing" is repeated every 5 seconds until the reply is sent.`

### F7. "Drafts do not expire" vs buttons older than 48 hours — SHOULD FIX
Section: A6.4. Known item Q-5 (QA report): Telegram sends an InaccessibleMessage for buttons on messages older than 48 hours; the existing handlers wrap their work in `isinstance(callback.message, Message)` and act silently or not at all.

Scenario. Save on a 3-day-old draft: built like the other handlers, it either saves with no reply and no edit (a later tap on the same old message gets "Already saved." with no trace of what was saved), or skips the save. A stale open draft is also the main source of accidental double entries (F2).

Proposed A6.4: `A draft older than 48 hours is not saved: its buttons answer "This draft is too old. Nothing saved. Send it again." and the draft becomes cancelled. Every callback is answered exactly once.`
Alternative: save it anyway and send the replies by chat id. Misha's call; expiry is simpler and safer.

### F8. Money answers depend on the model adding up rows; pending and pot rows are undefined — SHOULD FIX
Sections: A7.2, A3, Goal ("answer computed from his own entries").

Scenarios.
- `how much did I spend on groceries this year` → more than 100 rows → the model sees `first 100 of N` and returns a partial or guessed sum. Even under 100 rows, adding 60 amounts by the model is the likeliest wrong-number source.
- `how much on coffee in October` → coffee is a note, not a category; no text filter, so the model lists all of October (possibly over 100) and filters itself.
- USD/UAH entries without a rate have no EUR amount (`/month` leaves them out: "Not counted: N pending"); the line format says "EUR amount" without saying what a pending row shows, so UAH amounts can get summed as EUR.
- `ledger.records_between` returns pot moves (`save`/`take`) too; they would appear as entries with no category and get counted as spending or income.

Proposed A7.2: `list_entries(start, end, category?, text?)`: expenses and incomes only (pot moves are in `savings()`); `text` matches notes, any case. The first line is computed by the bot over ALL matching entries: `Spent X EUR, income Y EUR, N entries; M pending without a rate, not counted (amounts per currency)`. Then up to 100 lines, newest first, a pending one shown as `no rate`; when there are more, `first 100 of N`.
A3 rule add: `Totals come from the totals line or month_summary; never add amounts up yourself.`

### F9. Acceptance criteria are not measurable as written — SHOULD FIX
Sections: Goal and success, Testing and acceptance 2-3.

- "correct draft" is undefined (is a different but reasonable category a miss? the note?). Proposed: `Correct = amount, currency, kind and date exactly right and the category he would pick; the note is not judged.`
- "ordinary free-text messages" — who picks them? Proposed: `the first 10 messages he sends after deploy that go to the AI, not written for the test; every miss goes to the release record as message, expected, got.`
- "every answer matches /month for the same month": questions about a date range, a note (`coffee`) or uncategorized entries cannot be checked against `/month`. Proposed: `matches /month, or for a range or a note, the sum from the /export file; "I can't tell" is a pass, a wrong number is a fail; at least 5 questions.`
- Live run (Testing 2): "a copy of the server database" holds almost nothing (test data cleared 01.11), so 3 questions on it prove little; copying it to the Mac moves real data; and the key lives only on the server (HANDOFF), so the spec must say where the run happens and how the key is used without printing it. Proposed: `The live run uses a synthetic database built by a script: one month of about 60 entries with known totals, two pending USD/UAH entries, one budget and one pot; every answer is compared with the totals the script prints. It runs where the key is (on the server in a separate process, or with a second key Misha creates), only with his yes for the spend.`
- Timing: HANDOFF says the $100 credits expire 08.11.2026. Acceptance and "the token log lines give the real numbers after a week" (Cost) straddle that date; state that acceptance finishes before 08.11 or after the new credits arrive.

### F10. The tool loop end is not defined for drafts — SHOULD FIX
Sections: A2.4, A4.2, A4.5, A9.3.

Scenarios. After `propose_entries` the API expects a `tool_result` to continue — does the bot call the model again? A response may hold two `propose_entries` calls (parallel tool use) or `propose_entries` plus a read tool. `25 coffee tomorrow` → the model proposes 02.11 → A4.2 refuses the whole draft with a generic `I could not draft that` (dead end, no reason), where the parser would have said `That date is in the future`.

Proposed A4 text: `A valid propose_entries ends the turn: no further model call; only the first propose_entries in a response counts and other tool calls in that response are ignored. Several read tools in one response count as one model call. A draft that fails the A4.2 checks goes back to the model as a tool error naming the entry and the reason (e.g. "entry 1: 2026-11-02 is in the future"), so it can ask him or correct it within the 4 calls; only then the A4.2 reply.`

### F11. Currencies other than EUR, USD, UAH — SHOULD FIX
Sections: A3, A4.2, A5.2-A5.3.

Scenario. A receipt from Bratislava is EUR, but Prague (CZK), Budapest (HUF), Kraków (PLN), Zurich (CHF) are a train ride from Vienna; `потратил 500 крон`. The schema's enum leaves the model three bad options: label it EUR, convert it with an invented rate, or answer something unplanned. A5.3 covers only "not a receipt / no total".

Proposed A3 rule and A5.3 addition: `An amount in any other currency is not drafted; the reply is one sentence: "Only EUR, USD and UAH for now. Write it as 25 coffee in one of them." The model never converts between currencies.`

### F12. What counts as a receipt; images sent as files; duplicates — SHOULD FIX (first two), MINOR (last two)
Sections: A1.5, A1.6, A5.

- Bank app screenshots (a Monobank payment, a card push, an online order confirmation) are the commonest "receipt" for a Kyiv/Vienna user; A5.3 "not a receipt → nothing drafted" may refuse them. Proposed A5.2 addition: `A screenshot of one card payment or bank transaction counts as a receipt (amount, currency, merchant as the note, its date); an incoming payment is drafted as income. A screenshot listing several payments is not drafted: "One payment per photo, please."`
- An image sent with "Send as file" (iOS, uncompressed) or a PDF e-receipt arrives as a document; A1.6 ignores it with no reply at all. Proposed A1.6: `An image sent as a file (jpg, png, webp) is handled as a photo; any other file gets "Send the receipt as a photo."`
- Album: Telegram attaches the caption to one photo only; the other photos are drafted without it. State it in A1.5. (minor)
- The same photo sent twice gives two drafts and, after two Saves, a duplicate. Store Telegram's `file_unique_id` in the draft; a draft from a photo already saved shows `This photo was saved before, on 31.10.` (minor)

### F13. The server's IPv6 trap may hit api.anthropic.com too — SHOULD FIX
Section: A2. `_config/telegram-rules.md`: IPv6 from the VPS server to api.telegram.org stalls, so the Telegram session is IPv4-only. The anthropic library uses httpx, which does not fall back to IPv4 quickly; HANDOFF's `GET /v1/models returned 200` does not say which tool or IP family was used. If IPv6 stalls, every AI call waits for the timeout and ends in A9.2.

Proposed A2 item: `Before the build, check from the server that Python's httpx reaches api.anthropic.com at once; if IPv6 stalls, the Anthropic client connects over IPv4 only, like the Telegram session.`

### F14. Failure texts will mislead in the likeliest failures — MINOR
Section: A9.1-A9.2. The $20 spend limit is lower than the $100 credits, so it is the likelier stop, yet it falls under "AI is not available right now" — for the rest of the month he sees "right now" and thinks the bot is broken. Credits expire 08.11 (HANDOFF), so "for this month" can be inaccurate. A revoked key also reads "right now", and he never learns to fix it.

Proposed: A9.1 `The credit balance is too low or the spend limit is reached: "The AI budget is used up for now. Nothing saved. Write it as 25 coffee."` New A9 item: `The API rejects the key (401, 403): "The AI key does not work. Nothing saved. Write it as 25 coffee."` The exact API error strings are checked at build time.

### F15. Model text is not capped for Telegram — MINOR
Sections: A3, A4.5. "Under 800 characters" is only a request to the model; `max_tokens` 1024 can come close to Telegram's 4096 limit. Proposed A4.5 addition: `The bot cuts the model's text to 4000 characters. Text that is empty or only spaces counts as no text (A9.3).`

### F16. "Today" is processing time, so "вчера" near midnight is off by one — MINOR
Section: A3. Known item 2 in HANDOFF: entries are dated when processed. An AI call adds 5-30 s, and the F5 queue more. `вчера кофе 4` sent at 23:59:50 is drafted for the day before yesterday. Proposed A3: `today's date is the date the message was sent (Telegram message time, Europe/Vienna); the A4.2 future-date check uses the same date.`

### F17. Memory boundaries — MINOR
Section: A8.
- A follow-up the next morning still sees yesterday's drafts and questions ("and in September?" latches onto stale context). Proposed: `Messages older than 2 hours are forgotten.` (Misha's call on the number.)
- Which of the bot's replies are remembered is unclear: the 1000-character refusal, A9 failures, no-key replies. Proposed: `Only messages that reached the model and the model's own replies are remembered; failure replies are not.`
- When he uses Telegram's Reply on a bot message (`это продукты` as a reply to a saved entry), the replied-to text is lost. Proposed: `A reply to a bot message is sent with that message's text in front: [reply to: …].`

### F18. Draft format does not match the bot's own formats; empty category not shown — MINOR
Section: A4.4. The example shows `3000.00 EUR`; `money.format_cents` prints `3,000.00`. Existing replies use `31.10` (keeping the year in drafts is good: a receipt can carry last year's date). The draft does not say how an entry with no category looks. Proposed: amounts through `format_cents`; an empty category shows as `no category yet`.

### F19. Smaller routing gaps — MINOR
Section: A1.
- `save`/`take` as the first word without an amount (`Save`, `Take a look at October`) goes to the parser and gets `Use: save 200 emergency`. Covered by F1's "followed by an amount".
- Edited messages are ignored (Q-4, accepted backlog); state it: `Editing a sent message changes nothing, including a draft; send a new message.`
- Forwarded text (a friend's "you owe me 20", a bank SMS) is treated as if he typed it; state it.
- A1.4's 1000-character limit: state that it applies only to text going to the AI (the parser path has no limit today).

### F20. Help advertises AI without the key — MINOR
Section: A11. With no key, `/help` still offers free text and receipts. Proposed: `The three lines appear only when the key is configured.` (or accept.)

### F21. The model does not know the words he already taught — MINOR
Sections: A3, Goal. He taught `rewe → Groceries` by pressing buttons; the AI may pick Shopping for a REWE receipt, which counts against the 9 of 10. Proposed A3 addition: `the learned words and their categories` in the system prompt (his data, already agreed to leave the server under A10.3; a few hundred tokens).

---

## Part B. Plan and implementation details to remember (no spec change needed)

1. Store the category id (not only the name) in the draft JSON; categories can be renamed between draft and Save and are never deleted. Check the kind matches.
2. Save handler order: answer the callback first, then send up to 10 entry replies (a `retry_after` sleep can outlast Telegram's callback window), then edit the draft message. Register the draft callback before `on_unknown_callback`. `d:s:<id>` is far under 64 bytes.
3. `callback.message` can be an InaccessibleMessage; do not wrap the save itself in `isinstance(callback.message, Message)` (F7 decides the behaviour).
4. Migration 3 → 4 locked and re-checked with `BEGIN IMMEDIATE` like `_add_budgets`: the daily job also calls `connect()`. Old code runs fine on version 4 (rollback safe).
5. The key comes from `read_env_file` (a dict), not `os.environ`; the anthropic client must get `api_key` explicitly. Keep the key out of `Settings.__repr__` (the phase 1 ledger noted the token is in it).
6. The token filter sits on root handlers, so it covers the anthropic and httpx loggers; httpx logs one INFO line per request (no key, but noise): consider WARNING for `httpx`.
7. Parse the model's `amount` text with `money.parse_amount` (accepts `12,50`, rejects `1,200.00`); check the entry count 1-10 in code, not only in the schema.
8. Budget line per entry computed right after its own insert (phase 1.3 rule); with F4's single transaction the same connection sees its uncommitted rows, so this still works.
9. `/undo` after a saved draft removes only the newest entry; each reply's Undo removes its own entry. Save after `/clear` brings entries back into the cleared month (he pressed Save, acceptable). A Save between the `/clear` question and its confirm makes the confirm refuse ("changed since you asked") through the existing count/last_id pin — correct as is.
10. Send model text with no `parse_mode` (the bot has no default parse mode), so `<`, `*` and `_` in answers are harmless.
11. Memory keeps text only; tool calls and tool results are not stored. Trim the window so it starts with his message.
12. A restart during an in-flight AI call loses that message with no reply (the update is acknowledged on the next poll). Only deploys restart the bot; note it in the release steps.
13. AI USD/UAH entries without a rate get the usual `No USD rate yet` line and are converted by the next `/rate` (`set_rate` converts every pending row) — works unchanged.
14. The `drafts` table grows forever (a few rows a day) and is in the daily backup; it holds his notes, on his server.

## Part C. Checked and fine

- `set_category` teaches a keyword only `if entry.keyword:` — AI entries teach nothing, as A6.1 wants.
- `category_for_keyword(conn, "", kind)` never matches: no empty keyword is ever stored.
- Drafts live in the database, so Save works after a restart (only memory is lost).
- `/clear` confirmation stays safe against a draft saved in between (count and last id pinned).
- The monthly summary job and CSV export need no change; CSV quoting handles commas and quotes in AI notes.
- Unknown `/commands` and edited messages behave as the spec says today.

## Questions for Misha (numbered, for the v2 decision)

1. Number-first text (F1): send it to the AI when it shows warning signs (recommended), or keep the parser as is and only correct the risk line?
2. Corrections (F2): the model marks a corrected draft and the old one closes (recommended), or every new text draft closes the older open ones?
3. Old drafts (F7): expire after 48 hours (recommended), or save anyway?
4. Memory (F17): forget after 2 hours (recommended), or keep until a restart?
5. Receipts (F12): bank app screenshots count as receipts and images sent as files are read (recommended)?
