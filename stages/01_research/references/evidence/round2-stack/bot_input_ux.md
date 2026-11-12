# Telegram expense bots: fast text input, parsing, savings tracking, reports, reminders (as of 31 Oct 2026)

Method note: Cointry, Tabby and the QuickChart, Telegram and Claude pricing pages were read through WebFetch, which returns a model-written summary, not raw HTML. Quotes are as returned and should be re-checked on the live page before they go into anything public. The firefly-iii piggy-bank explanation page was read through the r.jina.ai proxy after a direct 403. Items marked "(search snippet)" were seen only in a WebSearch result and were not opened. Roughly 21 tool calls were used, above the 15 target, to cover the breadth of questions.

## Cointry deep dive (@cointrybot, cointry.io)

### Takeaway
Cointry takes "amount, optional currency code, description", with an optional date word and a leading "+" for income. It assigns categories automatically (per-title memory on the guide, "AI" on the homepage). Editing, export, budgets and multi-currency are Premium. No savings goals, reminders or savings snapshots appear on any Cointry page read.

### Cited Findings
- **Expense format (amount first, then description):** "20 cinema" - https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot ; "20 McDonald's" - https://cointry.io#features
- **Currency code after the amount:** "30000 JPY Japanese whiskey" - https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot . Homepage: "969 EUR iPhone" is saved as 969 EUR (1140 USD) - https://cointry.io#features . Currency symbols appear only in narrative text ("You've spent $20 on a cinema") in the guide. Symbol as input is not documented.
- **Income marker:** "Simply add leading plus «+» to the amount, and it will be saved as income." Example "+400 bicycle sale" - https://cointry.io#features . The guide has no income section.
- **Dates:** "40 barbershop yesterday" and "80 theatre 23.09.2023" - guide URL above. Homepage lists "yesterday", "1.12.20", "2020-12-01" and says arbitrary dates are Premium - https://cointry.io (homepage).
- **Voice input (Premium):** dictate entries such as "spent $20 on taxi yesterday" - https://cointry.io (homepage).
- **Categories:** for a new title "Cointry would ask you to choose a category for it"; for repeat titles it assigns the category "automatically without any questions" - guide URL above. Homepage: "the AI will automatically pick the right category, so you don't have to" with a claimed 94% accuracy (vendor claim) - https://cointry.io#features . Ability to change a category later: not found.
- **Editing and deleting:** "/delete removes the latest record from the chat" - https://cointry.io#faq . "Editing and removing any records, as well as exporting your data to CSV/Excel" is Premium - https://cointry.io#faq ; "editing" is listed under Premium - https://cointry.io#pricing . The Mini App is said to hold "graphs, settings, and editing" - https://cointry.io#faq (tier wording conflicts, see Gaps).
- **Multi-currency and base currency:** exchange rates "update twice a day from CurrencyBeacon" - https://cointry.io#faq . Guide: conversion uses "the exchange rate from the transaction date" - guide URL above. Reports convert to "your main currency" - https://cointry.io#features . Free plan lists "Support for any currency"; Premium lists "Multicurrency" - https://cointry.io#pricing . How to set the main currency: not found.
- **Reports:** "/stats" gives "detailed statistics for the month or year" by category and user - https://cointry.io#features . Monthly reports are sent automatically: "Cointry also sends you monthly reports on every first day of the month." - guide URL above. Free monthly reports compare with earlier months; Premium adds AI analysis - https://cointry.io#pricing (summary). Visual graphs: "Telegram mini app gives full visibility of your budget with visual graphs." - https://cointry.io#features . Chart images in chat: not found. Period commands other than /stats: not found.
- **Budgets:** overall or per-category monthly budgets with a notification when exceeded; "Monthly budget" is Premium - https://cointry.io#pricing .
- **Savings goals:** not found on the cointry.io page (its #faq and #pricing sections included) or in the guide.
- **Reminders:** not found. "Recurring transactions" is listed as "coming soon" under Premium - https://cointry.io#pricing .
- **Export:** CSV/Excel is Premium - https://cointry.io#pricing and https://cointry.io#faq .
- **Shared and family use:** add @cointrybot to a group; "There's no limit on participants." - https://cointry.io#features . "The Cointry chatbot works perfectly in group chats" - guide URL above. Separate chats are isolated; a Premium subscription bought in a group covers all members - https://cointry.io#faq . Premium adds recording expenses for other users; Business is multiple chats under one subscription - https://cointry.io (summary, no anchor).
- **Mini App / web dashboard:** "Graphs, settings, and editing are in a Telegram Mini App inside the bot." - https://cointry.io#faq . A separate web dashboard: not found.
- **Plans:** Free "$0 forever": unlimited records, categories and chat users; AI categorization, statistics, monthly reports. Premium "$2.5/month, billed annually": AI reports, voice input, monthly budgets, editing, advanced search, hashtags, CSV/Excel export; activated with /subscription. Business: no price shown - https://cointry.io#pricing .
- **Market signals (search snippets, not fetched):** Gumroad listing "$20 a year" - https://cointry.gumroad.com/l/cointry ; Capterra description "reads a free-text entry, assigns a category with AI, converts currencies" - https://www.capterra.com/p/10049958/Cointry/ ; Product Hunt page exists - https://www.producthunt.com/products/cointry . Bot link: https://t.me/cointrybot .

### Inferences
- The grammar is "amount [currency code] description [date word]", with "+" as the income switch. This is the same shape the user's examples use ("25 eur coffee", "+3000 salary", "1200 uah taxi"). Cointry's own "969 EUR iPhone" is a direct match for "25 eur coffee".
- Per-title memory (repeat titles auto-assigned) is a keyword-to-category dictionary in effect. The mechanism is not documented; the homepage's "AI" claim may describe the same thing or a model call. Not resolvable from the pages read.
- Savings is absent from Cointry's feature set as read, so Cointry is a reference for input and categorization only, not for savings.

### Gaps
- Conflicts not resolved:
  - Category: homepage says the AI "picks the right category" automatically; the guide says the bot "would ask you to choose" for a new title.
  - Price: pricing page gives $2.5/month billed annually (about $30 per year); Gumroad snippet says "$20 a year". Could be an old listing; not verified.
  - Editing tier: FAQ and pricing place editing in Premium; the FAQ also says the Mini App holds "editing". Tier of the Mini App edit is unclear.
  - Dates: homepage says arbitrary dates are Premium; the guide shows a dated example ("23.09.2023") without a tier note.
  - FX timing: FAQ says rates update twice a day; guide says the rate of the transaction date.
- Not found: how income vs expense is shown in the guide; how to change a category; how to set the main currency; savings goals; reminders; text charts in chat; period commands other than /stats; whether category choice uses inline buttons (the guide says "ask you to choose" but shows no UI).
- No Cointry help-center page beyond the FAQ and the guide was located.

## Other bots, briefer: Tabby, miguel-bm and cyxou Firefly III bots, beancounter, DollarBot

### Takeaway
Tabby and beancounter are the two UX extremes: Tabby is AI-first with categories and tags, while beancounter keeps a deterministic fast path with wallet nicknames and calls an LLM only when the line is ambiguous. The Firefly III bots depend on a Firefly server and add bank imports and household transfers. DollarBot is the only one read that has a savings account type with low-balance alerts.

### Cited Findings
**Tabby** (https://tabbyfinance.app ; bot https://t.me/tabbyfinancebot ; pages /pricing, /guides, /blog/why-listen-mode - from fetch summary)
- Input: "150 omakase dinner" logs $150 under Food; "+2500 biweekly salary" logs income; past date as DD/MM at the end, e.g. "10 lunch 30/5". AI picks amount, category and tags.
- Currency: any currency can be logged and is converted at live rates; example "300 USD" becomes about SGD 384.
- Categories: defaults include Food, Transport, Shopping, Fun, Salary; custom categories up to 3 on Free, unlimited on Pro.
- Edit or delete any entry from chat or the mini app. Accounts (cash, credit, bank) with transfers and net worth; 2 accounts on Free.
- Reports: monthly report in chat with a summary, budget performance and plain-language explanation; weekly reports on Free; yearly wrap-up in January; dashboard in the mini app.
- Budgets: per category with alerts; Free gives 1 budget category with an alert at 100%; Pro gives alerts at 50/75/100% and payday-to-payday cycles.
- Savings goals: not found. The monthly report shows the percentage of income saved.
- Reminders: daily reminder at a time you choose, with streaks; on Free; Pro adds budget pacing to reminders.
- Recurring: rent and subscriptions logged on schedule; repeat charges are spotted in history. Free: 1 recurring income schedule and 2 subscriptions.
- Groups: unlimited group chats. Listen Mode on = auto-log expenses; off = mention the bot to log. "/context" separates trips or budgets inside one chat.
- Voice notes (Pro) can log several entries. Receipt scanning: 3 scans a month on Free, unlimited on Pro.
- Pricing: Free $0; Pro $24.99 per year with a 14-day trial, no card; monthly price not listed.
- Export to Excel/CSV: Pro per the pricing page and FAQ. The features list gives no tier (conflict noted by the summary).

**miguel-bm/firefly-iii-telegram-bot** (README via gh api - https://github.com/miguel-bm/firefly-iii-telegram-bot)
- Input: "15€ at Mercadona for groceries", "Coffee 3.50". Voice notes are transcribed. Categories come from existing Firefly III categories. Edit and delete "via conversation". Requires an OpenAI key for NLP and voice.
- Queries: "How much did I spend on food this month?"; pie, bar and line charts; links to Firefly web reports.
- Bank import from Excel/CSV (BBVA, CaixaBank, ImaginBank, Revolut). "Records the monthly €850 contributions once as transfers, from either statement side."
- Web dashboard as a Telegram Mini App: account balances, doughnut chart by category, transaction list, custom date ranges.
- Automation: monthly spending summary on the 1st; import reminders when no account upload has happened for N days.
- Stack: Cloudflare Worker, Durable Object, KV; default currency set by env variable.
- Not found in the README: category choice UI (buttons or not), savings goals, budgets.

**cyxou/firefly-iii-telegram-bot** (README via gh api - https://github.com/cyxou/firefly-iii-telegram-bot)
- Purpose: "facilitates creating Firefly III transactions" and manages Accounts, Categories and Reports.
- Setup: credentials entered in the bot's Settings or as env variables; Redis for sessions in v3; optional ALLOWED_TG_USER_IDS whitelist.
- Input grammar, command list, charts, savings and reminders: not found in the README (it points to a screenshot and to the code).

**KidCoderT/beancounter** (README via gh api - https://github.com/KidCoderT/beancounter)
- Input: "purse 5.2" gets a thumbs-up reaction on the user's own message. "paid xyz for chingchong 3.2 credit" logs -3.20 from credit with the note kept. "got +50 from dad!" logs +50 (asks which wallet if there is more than one). "5 in purse and 20 from credit" and "4.35cred" go to the AI fallback. "hello" (no digits) is ignored.
- Bare number = spend (negative); explicit + or - is respected.
- Wallets have nicknames: "/newwallet cash money purse". Nicknames are unique per user in the database.
- Commands with no arguments show inline buttons (pick wallet, preset, count).
- "/setwalletamnt <wallet> <amount>" corrects a balance; the gap is stored as "untracked drift".
- Mini App at /app: ledger (In/Out/Net by day), patterns (weekday, hour of day, 6-month trend), stat tiles.
- Limits listed by the author: currency hardcoded to $; no categories, budgets or recurring entries; wallets cannot be deleted; Mini App is read-only.
- Stack: python-telegram-bot, SQLite, AWS Bedrock (Amazon Nova Micro, eu-north-1) for the fallback.

**ymdatta/DollarBot** (README via gh api - https://github.com/ymdatta/DollarBot ; MIT license)
- Features: add spending; sums for day and month; history; edit or delete; recurring monthly expense; custom categories; budget per category; pie and bar charts; daily reminder to track expenses "for either the current day or the current month".
- v2.0: Checking and Savings account types; "Change type of account before making a purchase"; alerts when balance falls below a threshold; error if spending exceeds the account balance; multi-currency (USD, INR, GBP, EUR, CAD, JPY); CSV/PDF export and email.
- Command syntax was not read (README was truncated at 150 lines).

### Inferences
- Tabby and Cointry share the same input shape (amount first, then the note; "+" for income). Beancounter uses the same idea with a wallet nickname in place of a category.
- Firefly-based bots rely on a Firefly server plus an LLM key, so they are not a model for a standalone bot.

### Gaps
- Cointry-style command names for period switching and edit flows were not found in the other bots' READMEs.
- Tabby facts are from a fetch summary, not raw HTML.

## Parsing approaches: deterministic, keyword dictionaries, LLM

### Takeaway
Beancounter documents the hybrid that fits this brief: a deterministic parser for the common line, and an LLM fallback only for ambiguous or multi-transaction lines. Keyword or title memory is the documented way to categorize without an LLM (Cointry guide, Statement, paytext). LLM cost per message is small with a cheap model but depends on assumed token counts.

### Cited Findings
- **Deterministic fast path:** "Simple messages are parsed instantly by plain Python — no API call, no latency, no cost." - https://github.com/KidCoderT/beancounter
- **Fallback:** messages that are "genuinely ambiguous" go to an LLM that "can split it into multiple transactions and hand them back structured" - same URL. Without AWS credentials, "only ambiguous messages fail, with an apology" - same URL.
- **Examples of ambiguous input the author routes to the LLM:** "5 in purse and 20 from credit", "4.35cred" - same URL.
- **Currency and decimal parsing library:** price-parser. Per search snippet, `Price.fromstring("22,90 €")` returns Decimal 22.90 with currency €; handles thousands and decimal separators; `decimal_separator` override; `currency_hint` for strings without a currency; BSD-3; 900+ test strings - https://github.com/scrapinghub/price-parser/ (search snippet) and https://pypi.org/project/price-parser/ (search snippet). Not fetched.
- **Related open-source examples (search snippets, not fetched):**
  - receipt-parser-ocr: OCR receipt text to merchant, total, date and category buckets; cleans euro, pound and rupee symbols - https://pypi.org/project/receipt-parser-ocr/1.0.8/
  - paytext: reduces a bank transaction string to a merchant name so repeat purchases share a category (built on Norwegian bank strings) - https://github.com/yhoiseth/paytext
  - Statement: CSV bank statement tool with JSON keyword rules tagged income or expense - https://github.com/ReyonaD/Statement
  - punchagan/expense-tracker: counterparty-based auto-categorization; lists NLP/ML suggestions as a feature - https://www.github.com/punchagan/expense-tracker
- **Keyword and title memory:** repeat titles are assigned automatically; new titles prompt a choice - https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot
- **LLM use in sources:** miguel-bm uses OpenAI for NLP and voice transcription - https://github.com/miguel-bm/firefly-iii-telegram-bot ; beancounter uses a forced tool call on Bedrock Nova Micro that returns structured JSON - https://github.com/KidCoderT/beancounter . Tabby and Cointry say "AI" without naming a model - https://tabbyfinance.app and https://cointry.io#features .
- **Claude pricing (per million tokens, USD), as shown on the page:** Haiku 5.5 with prompts up to 100K tokens: input $0.10, output $0.50, cache read $0.01, cache write $0.125 (5-minute TTL); Sonnet 5.5: input $2, output $10; Opus 5.5: input $4, output $20; "Save 50% with batch processing." - https://claude.com/pricing (the anthropic.com/pricing URL redirects here).

### Inferences
- Cost estimate (my arithmetic, token counts assumed, not measured):
  - Haiku 5.5, 400 input + 60 output tokens per message: about $0.00007 per message, about $0.07 per 1,000 messages.
  - Haiku 5.5, 1,500-token system prompt (categories and rules) + 60 output, uncached: about $0.18 per 1,000 messages. With the prompt prefix served from cache at $0.01 per MTok: about $0.045 per 1,000.
  - Sonnet 5.5, 400 + 60 tokens: about $1.40 per 1,000 messages.
  - Excludes cache-write cost, hosting and Telegram costs.
- Recommended grammar (inferred from the sources above): [+ or -] amount [3-letter currency code or symbol] free-text note [date word or DD/MM]. Sign gives income vs expense; currency is optional and falls back to the base currency; category comes from a dictionary keyed by note words or merchant; anything the regex cannot place goes to an LLM or to a "which category?" button.
- Decimal comma vs dot: price-parser handles both automatically and allows an override (search snippet). Cointry and beancounter examples use the dot ("5.2", "3.50").
- Failure modes documented in sources: fallback only on ambiguity (beancounter); user prompted for new titles (Cointry). LLM failure rates and wrong-category rates: not found in sources read (Cointry's 94% is a vendor claim).

### Gaps
- No open-source library found that parses one free-text line into amount + currency + category + income sign. One search only; the closest tool is price-parser for amount and currency.
- Date words ("yesterday") and date-parsing libraries: not searched.
- Telegram message and callback limits relevant to a regex parser: not verified (see Reports section).

## Savings tracking patterns: goals, contribution log, balance snapshots

### Takeaway
No released bot read combines a goal with a target and deadline, a contribution log and monthly balance snapshots. The documented pieces are: a savings account type with threshold alerts (DollarBot); a balance correction that stores the gap (beancounter); household contributions recorded as transfers (miguel-bm); and piggy banks as sub-allocations of one savings account (Firefly III). A goal with target and progress appears only in a freelance spec (Cashy).

### Cited Findings
- **Firefly III piggy banks:** "You can use 'piggy banks' to organize your savings. A piggy bank is a way to divide your money in a number of parts." Each piggy bank is "tied to an asset account on which its money is saved." Money "can be added and removed to piggy banks freely"; a transfer can select a piggy bank - https://docs.firefly-iii.org/explanation/financial-concepts/piggy-banks/ (read through the r.jina.ai proxy; page "Last updated June 21, 2024").
- **Piggy bank target amount:** the docs treat the goal amount as optional but useful, with a €300 camera as the example (paraphrase from search snippet, not a verbatim quote) - https://docs.firefly-iii.org/how-to/firefly-iii/finances/piggy-banks/ (direct fetch returned 403, not read in full).
- **Piggy bank limit:** "You can't add more money to your piggy banks than you have on your savings account." - same how-to URL (search snippet).
- **Target date:** not confirmed. Not in the fetched explanation page; not seen in any snippet. Treat as unknown.
- **Balance snapshot with gap:** beancounter's "/setwalletamnt <wallet> <amount>" corrects a balance, and "that gap is stored and surfaced later as 'untracked drift'". Balances are not stored; they are "always SUM(amnt)" - https://github.com/KidCoderT/beancounter
- **Savings account type and alerts:** Checking and Savings account types; "Get alerts when your balance falls below a threshold value." - https://github.com/ymdatta/DollarBot
- **Contribution log via transfers:** "Records the monthly €850 contributions once as transfers, from either statement side" - https://github.com/miguel-bm/firefly-iii-telegram-bot
- **Goal with progress (spec only):** Telegram bot "Cashy" freelance spec describes goals with progress display, e.g. saving 10,000 UAH, and a balance display - https://freelancehunt.com/en/project/telegram-bot-cashy/1538756.html (search snippet; a freelance listing, not a released bot).
- **Savings share in report (Tabby):** the monthly report shows the percentage of income saved - https://tabbyfinance.app (fetch summary). No goals.
- **Cointry:** savings goals not found - https://cointry.io (homepage, FAQ, guide, pricing read).

### Inferences
- A workable model for this brief, built from the patterns above: each savings account is a balance the user snapshots (beancounter-style correction with stored gap) plus a contribution log of signed entries (DollarBot-style account type). A goal is a target amount with an optional date; progress = balance / target. No source read implements all three together, so this is a build, not a copy.
- Piggy banks suggest goals can be labels on one savings account rather than separate accounts. Firefly's model shows the split is allowed; it does not show a progress UI.
- Progress display options (text bar, chart image) are not documented in the sources beyond the Cashy spec. See Reports section for chart options.

### Gaps
- Target date in Firefly III: not confirmed.
- Released Telegram bots with goal, deadline and progress: not found in one search.
- Rabobank and Payzy piggy banks with an end date appeared in a search summary only (not fetched). Not cited as facts.
- Beancount "balance" assertions for monthly snapshots: not searched.

## Reports in Telegram without a Mini App: text, charts, period switchers

### Takeaway
Text reports in chat are the norm (Tabby's monthly report, Cointry /stats). Chart images in chat are described in the Firefly bots and DollarBot, but delivery format is not stated. QuickChart's free quota is not published; its paid tier is EUR 39 per month for 10,000 images. Inline keyboards are documented for wizard flows (beancounter), not for period switching.

### Cited Findings
- **Text report in chat (Tabby):** "a summary, budget performance, and a plain-language explanation of what changed" - https://tabbyfinance.app (fetch summary).
- **Text stats (Cointry):** "/stats" returns "detailed statistics for the month or year" by category and user - https://cointry.io#features ; charts only in the Mini App - https://cointry.io#features .
- **Charts (miguel-bm):** pie, bar and line charts; links to Firefly web reports - https://github.com/miguel-bm/firefly-iii-telegram-bot . Delivery format not stated in the README part read.
- **Charts (DollarBot):** "pie charts, bar graphs with and without budget lines"; "bar graph in the /history command" - https://github.com/ymdatta/DollarBot . Delivery format not stated.
- **Inline keyboards (beancounter):** commands with no arguments show inline buttons for choosing a wallet, a preset or a count - https://github.com/KidCoderT/beancounter . Period switching with inline keyboards: not found.
- **QuickChart pricing:** Community EUR 0/month, "No watermarks", "Rate limit enforced" (no figure). Professional EUR 39/month: "10,000 images/month", "50,000 short URLs/month", "No rate limits". Enterprise: "Contact Us". Source: https://quickchart.io/pricing/ (the page itself gave no URL; the fetch used this one).
  - Derived: Professional at full quota is about EUR 0.0039 per image (39 / 10,000).
  - Not found: free-tier request count, chart size limits, GET vs POST support.
- **Telegram Bot API (partial read; the page is about 580K characters and only the first 100K were read):**
  - Uploads use multipart/form-data; JSON is used "except for uploading files" - https://telegram.org/bots/api#making-requests
  - Voice notes arrive as a message with a Voice object: file_id, file_unique_id, duration - https://telegram.org/bots/api#voice
  - editMessageText: "allowing bots to edit rich messages" - https://telegram.org/bots/api#editmessagetext
  - editMessageMedia: live photo support mentioned; whether a new upload can replace the photo: not confirmed in the excerpt.

### Inferences
- A period switcher can be built with inline buttons that call editMessageText to swap a text table. Swapping a chart needs editMessageMedia with a new upload; that was not confirmed.
- Cheapest chart path, pending checks: render a PNG through QuickChart (paid tier about EUR 0.004 per image) or keep reports as text tables in chat. The free tier's limits need checking before relying on it.

### Gaps
- QuickChart free quota, chart size limits, GET vs POST: not found.
- Telegram sendPhoto (URL vs upload), callback_data length limit, message text length, caption length: not verified. The fetch did not reach those sections. Check https://telegram.org/bots/api before building.
- Text table formatting options (monospace/pre blocks, parse modes): not verified in sources read.
- Period-switcher examples in other bots: not found.

## Monthly reminder patterns

### Takeaway
Documented pattern: a cron job sends a monthly summary on the 1st (Cointry, miguel-bm); a daily or monthly "track your expenses" reminder (DollarBot); a daily reminder with streaks (Tabby). Stale-data reminders exist only as import reminders (miguel-bm). No bot read prompts for a monthly savings balance snapshot.

### Cited Findings
- **Cointry:** "Cointry also sends you monthly reports on every first day of the month." - https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot
- **miguel-bm:** Cloudflare Cron Triggers run monthly reports and import reminders (README table). Settings in README: `ENABLE_MONTHLY_REPORT = "true"` (report on the 1st); `BANK_IMPORT_REMINDER_DAYS = "10"` (days without an account upload before a reminder); `BANK_IMPORT_REMINDER_REPEAT_DAYS = "3"` (minimum days before the reminder repeats) - https://github.com/miguel-bm/firefly-iii-telegram-bot
- **DollarBot:** "Set a daily reminder to track your expenses for either the current day or the current month." - https://github.com/ymdatta/DollarBot
- **Tabby:** daily reminder at a time you choose; streaks; available on Free; Pro adds budget pacing to reminders - https://tabbyfinance.app (fetch summary).
- **beancounter:** no reminders found in the README - https://github.com/KidCoderT/beancounter

### Inferences
- Savings snapshot reminder (not found in any source): a monthly scheduled message on the last day or the 1st, with inline buttons "Enter balance: [account]" for each savings account, writing a snapshot through the same path as beancounter's balance correction. This combines the cron pattern (miguel-bm) with the balance-correction pattern (beancounter).
- Stale-snapshot alert: if a savings account has no snapshot for N days, send a reminder - the miguel-bm import-reminder logic, applied to balances.

### Gaps
- No bot read sends a savings or balance snapshot reminder. Design is an inference.
- Reminder wording and timing research: not searched.
- Telegram scheduling limits: not verified.
