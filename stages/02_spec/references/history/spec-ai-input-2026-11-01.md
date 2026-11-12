# Spec: AI input (phase 1.4), 01.11.2026

Status: draft for Misha's approval. After approval it is the authority for the phase 1.4 plan; the base spec `spec-2026-10-31.md` still governs everything this file does not change (its out-of-scope line "LLM parsing, voice, receipt photos" is lifted here for LLM parsing and receipt photos only; voice stays out).

## Source decisions (`shared/decisions.md`, 01.11)

- Chat inside the bot answers questions about his money; his data may go to the Anthropic API: "4 - ага", "5 - внутри бота".
- Free text and receipt photos, each confirmed with a button; voice later as a separate step: "3 - записывать в свободном формате, голосовые записывать, фотки чеков", "Да давай на все ок. Стартуй".
- Runs on his Max plan API credits; model Claude Sonnet 5.5: "2 - ставь соннет".
- One entry per receipt; questions in this phase; English replies; memory of the last 10 messages; the `anthropic` library approved; no draft editor: "1 - одна запись 2 - по рекомендации 3 - так как будет легче для системы 4 - да по рекомендации 5 - да ставь 6 - да хорошо".

## Goal and success

Misha writes the way he talks ("вчера 25 на кофе с другом") or sends a receipt photo; the bot shows a draft and saves only after he presses Save. He can also ask about his money ("how much did I spend on eating out in October", "how much is left in the Rent budget") and get an answer computed from his own entries.

Success at acceptance (Misha in Telegram, after deploy): at least 9 of 10 ordinary free-text messages and 4 of 5 receipts give a correct draft without changes; every answer to a money question matches `/month` for the same month. Each miss is recorded and becomes a prompt fix.

## Out of scope

Voice messages; pot moves through AI (pots stay `save 200 emergency`); editing or deleting entries through AI; a draft editor; several entries from one receipt; learning keywords from AI choices; prompt caching; group bill splitting.

## Requirements

### A1. Which messages go to the AI

1. Text whose first word starts with an amount (an optional `+`, an optional currency symbol from `money.SYMBOLS`, then a digit: `25`, `+3000`, `€5`), or whose first word is `save` or `take` (any case): the existing parser, exactly as today (phase 1.3 behaviour, replies and errors unchanged). It never reaches the AI, costs nothing and answers at once.
2. Text starting with `/`: as today (known commands run, unknown ones get the existing "Start with the amount" reply).
3. Any other text: the AI, when the key is configured. Without the key: the existing "Start with the amount, e.g. 25 coffee" reply (today's behaviour).
4. Text longer than 1000 characters is refused before any AI call: `Keep it under 1000 characters, or split it into two messages.`
5. A photo, with or without a caption: the AI receipt flow (A5). Every photo of an album is its own message and its own draft. Without the key: `Receipt photos need the AI. Write it as 25 coffee.`
6. Other message types (voice, stickers, files) stay ignored as today.

### A2. The model call

1. Official `anthropic` Python library, async client, pinned to one exact version in `app/requirements.txt` (latest at build time; 2.3.0 on 01.11.2026).
2. Model `claude-sonnet-5-5`, `max_tokens` 1024, no extended thinking. Client timeout 60 s, library retries 2 (connection errors, 429, 5xx are retried by the library).
3. Tools are declared with `strict: true` and `tool_choice` stays automatic: forcing a tool returns an error on Sonnet 5.5.
4. The bot runs the tool loop itself: at most 4 model calls for one user message. More than that is a failure (A8).
5. While waiting, the bot shows "typing" in the chat once per model call.
6. After every model call the log gets one line: model, input tokens, output tokens, stop reason. Never the message text, the photo, the answer or the key.

### A3. What the model is told

The system prompt is built for every call from the database and contains:
- today's date in Europe/Vienna with the weekday, so "yesterday" and "on Friday" resolve;
- allowed currencies EUR, USD, UAH, EUR when none is named;
- the current expense and income category names;
- the rules: entries are created only through `propose_entries`; never invent an amount; if a message is unclear, ask one short question in text instead of guessing; a receipt is one entry (A5); answers about money come only from the read tools, never from memory or guesses; answers in English, plain text without Markdown, under 800 characters, amounts with two decimals and the currency; pots are changed only by typing `save 200 emergency` or `take 50 emergency`, and the model says so when asked to move money between pots.

### A4. Drafts

1. `propose_entries` takes 1 to 10 entries. Each entry: `kind` (`expense` or `income`), `amount` (text like `25` or `12.50`), `currency` (`EUR`, `USD`, `UAH`), `category` (a category name), `note` (the words that describe it, in his language), `date` (`YYYY-MM-DD`).
2. The bot checks every entry with the manual-input rules: amount above zero and at most the existing maximum, two decimals at most, currency allowed, date valid and not in the future. One bad entry refuses the whole draft: `I could not draft that. Nothing saved. Write it as 25 coffee.` A note longer than 100 characters is cut to 99 plus `…`. A category name that is not his category of that kind (case-insensitive) is kept empty: after saving, the usual category buttons ask him.
3. A valid draft is stored in a new `drafts` table (database version 3 to 4, backup taken by the deploy as always): id, the entries as JSON, source `text` or `photo`, status `open`, `saved` or `cancelled`, created time.
4. The bot replies with the draft and two buttons:

   ```
   Draft:
   1. 25.00 EUR · Eating out · кофе с другом · 31.10.2026
   2. 3000.00 EUR · Salary · зарплата · 01.11.2026 (income)
   ```
   Buttons: `Save` (or `Save 2 entries` for more than one) and `Cancel`.
5. A text the model writes next to the tool call is not shown. When the model answers with text and no tool call, that text is the reply (a question back or an answer).

### A5. Receipt photos

1. The bot takes the largest size Telegram offers for the photo and sends it to the model as JPEG, with the caption if there is one.
2. One receipt is one expense entry: the total paid, the currency printed on it, the store name as the note, one category, the receipt date when it is readable and not in the future, otherwise today.
3. Not a receipt, or no readable total: the model says so in one sentence; nothing is drafted.

### A6. Save and Cancel

1. Save on an `open` draft: every entry is saved through the same path as typed entries, all saves first, then the replies. Each saved entry gets exactly the reply a typed entry gets today (date, budget line, category or entry buttons). An AI entry carries no keyword, so pressing a category under it does not teach a keyword. Then the draft message becomes `Saved 2 entries.` without buttons and the draft is `saved`.
2. Cancel on an `open` draft: the message becomes `Cancelled. Nothing saved.` without buttons, the draft is `cancelled`.
3. Any button on a draft that is no longer `open`, or a draft id that does not exist, changes nothing and answers `Already saved.`, `Already cancelled.` or `This draft is gone.`. Pressing Save twice can never save twice.
4. Drafts do not expire. Every callback is answered exactly once.

### A7. Questions about money (read only)

The model gets three read tools. None of them writes anything.
1. `month_summary(month: "YYYY-MM")`: the same text `/month` shows for that month (totals, categories, budgets, top entries).
2. `list_entries(start: "YYYY-MM-DD", end: "YYYY-MM-DD", category?: name)`: live entries in that range, one line each (date, kind, amount and currency, EUR amount, category, note), at most 100 lines; when there are more, the last line says `first 100 of N`.
3. `savings()`: the same text `/savings` shows.
A bad argument (unknown month, end before start, unknown category) returns an error text to the model, which may correct itself within the 4-call limit.

### A8. Conversation memory

The bot keeps the last 10 messages (his and its own, as plain text) in memory and sends them with every call, so "and in September?" works. A photo is remembered as `[receipt photo]`, a draft as its draft text. Messages that went to the plain parser are not remembered. Memory is lost on restart; nothing of it is written to disk.

### A9. Failures

Nothing is ever saved on a failure; every failure gets one plain reply.
1. Credits used up (the API says the credit balance is too low): `AI credits are used up for this month. Nothing saved. Write it as 25 coffee.`
2. Anthropic unreachable, timeout, overloaded, rate-limited after the library retries, spend limit reached, invalid key, or any other API error: `AI is not available right now. Nothing saved. Write it as 25 coffee.` The log gets the error class and status code only.
3. The model refuses, runs out of tokens, exceeds 4 calls, or returns neither text nor a draft: `I could not make sense of that. Write it as 25 coffee, or ask again.`
4. The photo cannot be downloaded from Telegram: `Could not read the photo. Send it again.`

### A10. Secrets and privacy

1. `ANTHROPIC_API_KEY` is optional in `.env`; the bot starts without it and then works as today (A1.3, A1.5). The deploy check of `.env` stays as is.
2. The key never appears in logs: the existing token log filter also hides the key.
3. His message text, receipt photos and the rows the read tools return are sent to Anthropic (agreed: "4 - ага"). Nothing else leaves the server.

### A11. Help text

`/help` gains three lines after the several-entries line:
- `coffee with a friend yesterday 25 - free text: the bot drafts it, you press Save`
- `a receipt photo - one entry for the total, after you press Save`
- `how much did I spend on eating out in October? - ask about your money`

## Cost

Estimate, not measured: a text message is about 3,000 input and 300 output tokens, about 1 cent; a receipt about 1.2 cents; a question with one or two tool calls about 2 cents. At 10 messages a day this is about $3–6 a month, inside the $100 Max credits. Hard cap: the $20 monthly spend limit set on the Console organization. The token log lines (A2.6) give the real numbers after a week.

## Testing and acceptance

1. Unit and bot tests use a fake model client with scripted replies; no test touches the network (engineering rules). Covered: routing (A1), draft checks (A4.2), Save and Cancel twice and in any order (A6), read tools output (A7), memory length (A8), every failure reply (A9), the key hidden in logs (A10.2), `/help` (A11).
2. One live run before the deploy, on a copy of the server database, through the real Sonnet 5.5: 10 free-text messages and 3 questions, about $0.20, only with Misha's yes for that spend. Receipt photos are checked by Misha in Telegram, since the agent has no receipts of his.
3. Acceptance by Misha after the deploy, as in "Goal and success".

## Known risks

- A draft can be wrong (wrong category, wrong date). Mitigation: nothing is saved without Save; after saving, category and Undo buttons work as today.
- A text that starts with a number but is a question ("2025 total?") goes to the plain parser and gets its usual error. Rewording without a leading number sends it to the AI.
- Answers come from a model: a wrong sum is possible in principle. The read tools return the same numbers as `/month`, and the prompt forbids answering money questions without them.
