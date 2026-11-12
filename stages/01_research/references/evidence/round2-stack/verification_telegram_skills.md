# Verification: Telegram group bots, input UX references, agent skills

Checked: 31 Oct 2026. Checker: fact-check pass on the three notes files (group_split_bots.md, bot_input_ux.md, agent_skills.md). The notes were not modified.

Method:
- Telegram docs: exact text read through a text mirror (r.jina.ai) and matched with grep. Quotes in section 1 are exact. The "/tutorial" page was read the same way.
- Owerly, Lightsplit, Cointry: WebFetch only. These quotes are as returned by a fetch model, not grep-matched. Re-check the live page before quoting externally.
- GitHub: `gh api` metadata and README reads (beancounter README read in full via `gh api repos/KidCoderT/beancounter/readme`). Nothing cloned, installed or run.
- Anthropic paths: `gh api repos/.../contents/...`.
- Prices: official pricing pages (claude.com/pricing and platform.claude.com/docs/en/about-claude/pricing), table rows read from the page text.
- WebSearch: 1 call (budget 10).

Verdict key: CONFIRMED / WRONG / CONFLICT (sources disagree) / UNVERIFIABLE (not found in the sources read).

## 1. Telegram official docs

| Claim | Verdict | Correct value | Quote | Source URL |
|---|---|---|---|---|
| Privacy mode is on by default for bots in groups | CONFIRMED | On by default for all bots, except bots added to a group as admins (admins receive all messages). | "Privacy mode is enabled by default for all bots, except bots that were added to a group as admins" | https://core.telegram.org/bots/features#privacy-mode |
| What a privacy-mode bot receives in a group | CONFIRMED | Commands aimed at it (`/command@this_bot`); `/start` only if it was the last bot to post; inline messages sent via the bot; replies to its messages. Always receives service messages and private-chat messages, regardless of mode. | "Replies to any messages implicitly or explicitly meant for this bot." | https://core.telegram.org/bots/features#privacy-mode ; https://core.telegram.org/bots/faq |
| Bot receives @mentions in groups under privacy mode | CONFLICT | The features page and the FAQ lists omit mentions. The Bot API ForceReply example includes them. Do not rely on mentions reaching a privacy-mode bot until tested. | "only receives commands, replies to its messages and mentions" (Bot API, ForceReply example) | https://core.telegram.org/bots/api#forcereply ; https://core.telegram.org/bots/features#privacy-mode |
| Turn privacy mode off: BotFather /setprivacy, then re-add the bot | CONFIRMED | Set it with BotFather `/setprivacy`. The bot must be re-added to the group for the change to apply. Telegram recommends force reply for the bot's own messages instead: "In most cases, using the force reply option for the bot's messages should be more than enough." | "the bot will need to be re-added to the group for this change to take effect" | https://core.telegram.org/bots/features#privacy-mode |
| No method lists all group members | CONFIRMED | Bot API has `getChatMemberCount`, `getChatAdministrators` and `getChatMember`. There is no `getChatMembers` method (grep of the full API text). The FAQ has no member-list section. | "Use this method to get information about a member of a chat." (getChatMember) | https://core.telegram.org/bots/api ; https://core.telegram.org/bots/faq |
| `getChatMember` works for other users only if the bot is an admin | CONFIRMED | Guaranteed for other users only when the bot is an administrator in the chat. | "The method is only guaranteed to work for other users if the bot is an administrator in the chat." | https://core.telegram.org/bots/api#getchatmember |
| Group limit: 20 messages per minute | CONFIRMED | 20 per minute in a group. The FAQ sentence contains the original typo "are not be able". | "In a group, bots are not be able to send more than 20 messages per minute." | https://core.telegram.org/bots/faq |
| Chat limit: 1 message per second | CONFIRMED (soft limit) | Telegram says "avoid" more than one per second. Short bursts are allowed; after that, 429 errors follow. | "In a single chat, avoid sending more than one message per second." | https://core.telegram.org/bots/faq |
| `callback_data` is 1-64 bytes | CONFIRMED | 1-64 bytes. | "Data to be sent in a callback query to the bot when the button is pressed, 1-64 bytes" | https://core.telegram.org/bots/api (InlineKeyboardButton) |
| `deleteMessage` works only within 48 hours | CONFIRMED | Only messages sent less than 48 hours ago. Bots can delete their own outgoing messages in private chats, groups and supergroups. | "A message can only be deleted if it was sent less than 48 hours ago." | https://core.telegram.org/bots/api#deletemessage |
| A bot cannot send the first private message to a user who never started it | CONFIRMED on the tutorial page only | Not stated on bots/api, bots/faq or bots/features (grep). The tutorial says the user must have contacted the bot first. Exception: a join request to a group where the bot is an admin. The error text "bot can't initiate conversation" was not found in the pages read; do not cite it. | "The user must have contacted your bot first." | https://core.telegram.org/bots/tutorial |

## 2. Owerly and Lightsplit (WebFetch, fetch-model quotes)

| Claim | Verdict | Correct value | Quote | Source URL |
|---|---|---|---|---|
| Owerly: a group button opens a Mini App form | CONFIRMED (fetch) | The bot posts one message with a button that launches the app. The expense form is inside the Mini App. No text or command entry found. | "Бот присылает одно сообщение с кнопкой запуска приложения." (The bot sends one message with a button that launches the app.) | https://devby.io/ru/news/owerly |
| Owerly: equal / shares / percent / custom splits | CONFIRMED with correction | The form offers four methods: equal, by shares, by percentages, custom amounts. The features section lists three (amounts, percentages, shares). "Equal" appears only in the form. | "Как делить: поровну / по долям / по процентам / кастомные суммы" (How to split: equally / by shares / by percentages / custom amounts) | https://devby.io/ru/news/owerly |
| Owerly: debt chain 50, 30, 20 collapses to 20 and 10 | WRONG (the article's arithmetic does not reconcile) | Starting debts: you owe Anya 50; Anya owes Boris 30; Boris owes you 20. Net positions: you -30, Anya +20, Boris +10. The simplified result is therefore: you pay Anya 20 and Boris 10 (two transfers, total 30). The article's result (you owe Anya 20; Anya owes Boris 10) gives you -20 and Anya +10, which does not match the starting nets. Do not reuse the article's example as a correct illustration. | "приложение схлопнёт эту цепочку: вы должны Ане 20 злотых, Аня должна Борису 10 злотых" (the app will collapse this chain: you owe Anya 20 zloty, Anya owes Boris 10) | https://devby.io/ru/news/owerly |
| Owerly: pairwise netting always on; group-wide optimization in settings | CONFIRMED (fetch) | Pairwise netting always works. Global optimization can be enabled in group settings. | "Между любой парой пользователей оптимизация работает всегда" (Optimization always works between any pair of users) | https://devby.io/ru/news/owerly |
| Owerly: automatic exchange rates and debt repayment in any currency are paid | CONFIRMED (fetch) | Listed among paid-version features in the article. | "автокурсы валют, погашение долгов в любой валюте" (auto exchange rates, debt repayment in any currency) | https://devby.io/ru/news/owerly |
| Owerly pricing: basic version free; $6-7 figure | CONFIRMED free basic; paid price UNVERIFIABLE; $6-7 attribution UNVERIFIABLE | Basic version is free. Paid price not found. The "$6-7 a month" sentence is in the article, but the claim that it refers to Splitwise is the fetch model's reading. Do not attribute the figure to Owerly. | "Базовая версия - полностью бесплатна" (The basic version is completely free); "премиум-функции стоят около $6-7 в месяц" (premium features cost around $6-7 a month) | https://devby.io/ru/news/owerly |
| Owerly article date: 16 Dec 2025 | CONFIRMED (fetch) | 16 December 2025, 13:00. Page metadata shows dateModified 2025-12-08, which is earlier than the publication date; not used. | "16 декабря 2025, 13:00" | https://devby.io/ru/news/owerly |
| Lightsplit: bot handles only messages starting with "/" | CONFIRMED (fetch) | Only slash commands are handled; plain chat text gets no response. | "The bot only handles messages that start with `/`." | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit commands: /newgroup, /link, /add, /transfer, /balances, /stats, /unlink | CONFIRMED (fetch) | `/newgroup Tokyo Trip JPY`; `/link <group url>`; `/add 3000 ramen` and `/add 3000 JPY ramen`; `/transfer 5000 @bob` and `/transfer 5000 JPY Alice`; `/balances`; `/stats`; `/unlink` detaches the chat. | "Type `/unlink` in the group to detach the chat from the split group." | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit: second word of /newgroup is the settlement currency, default USD | UNVERIFIABLE | The tutorial shows JPY as the currency argument. "Default USD" was not in the fetched text. | - | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit: /link re-attaches after /unlink | UNVERIFIABLE | The tutorial text describes /unlink. Re-attach wording was not found in the fetched text. | - | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit: unequal splits in the Mini App | CONFIRMED (fetch) | Opened with the "View Details" button under the expense reply; the Mini App adjusts the split (skip people, split by ratio). | "adjust the split (skip people who didn't eat, or split by ratio" | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit: existing group members imported as default members | CONFIRMED (fetch) | Existing Telegram group members are pulled into the roster as default members. | "pulls the existing Telegram group members into the roster as default members" | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit: fewest transfers | CONFIRMED (fetch) | Balances are reduced to the fewest transfers. | "Lightsplit collapses everything into the fewest transfers possible." | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |
| Lightsplit tutorial date: 1 May 2026 | CONFIRMED (fetch) | "May 1, 2026" | "May 1, 2026" | https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial |

## 3. GitHub repos (gh api, 31 Oct 2026)

Path check: the notes used the right path for spliit. The "split-pro" repo is `oss-apps/split-pro`.

| Repo | Verdict | Correct value (stars, license, pushed, other) | Quote (gh JSON) | Source URL |
|---|---|---|---|---|
| spliit-app/spliit | CONFIRMED | 3,032 stars; MIT; pushed 2026-10-22; not archived | `"stars":3032,"license":"MIT","pushed":"2026-10-22T09:11:32Z"` | https://github.com/spliit-app/spliit |
| split-pro (correct path oss-apps/split-pro) | CONFIRMED with path | 1,481 stars; MIT; pushed 2026-10-20 | `"stars":1481,"license":"MIT","pushed":"2026-10-20T19:20:11Z"` | https://github.com/oss-apps/split-pro |
| zovo-one/telegram-split-bill-bot | CONFIRMED | 0 stars; MIT; pushed 2026-09-09; created 2026-09-04 | `"stars":0,"license":"MIT","pushed":"2026-09-09T08:56:35Z"` | https://github.com/zovo-one/telegram-split-bill-bot |
| KidCoderT/beancounter | CONFIRMED stars/dates; NEW: no license | 0 stars; license null (GitHub reports none); pushed 2026-08-08; created 2026-08-06 | `"license":null,"pushed":"2026-08-08T03:49:38Z"` | https://github.com/KidCoderT/beancounter |
| ymdatta/DollarBot | CONFIRMED licence; NEW: stale | MIT; 0 stars; last push 2023-11-28 (almost three years before this check) | `"license":"MIT","pushed":"2023-11-28T05:20:37Z"` | https://github.com/ymdatta/DollarBot |
| grammyjs/tgcloud | CONFIRMED | 9 stars; MIT; created 2026-10-11; pushed 2026-10-18 | `"stars":9,"license":"MIT","created":"2026-10-11T15:24:28Z"` | https://github.com/grammyjs/tgcloud |
| Nitish-bot/grammy-skill | CONFIRMED | 0 stars; license null (no LICENSE file, GitHub reports none); created and pushed 2026-06-14 | `"license":null,"created":"2026-06-14T13:22:30Z"` | https://github.com/Nitish-bot/grammy-skill |
| ballisarium/aiogram-skills | CONFIRMED | 2 stars; MIT; created 2026-07-11; pushed 2026-10-27 | `"stars":2,"license":"MIT","pushed":"2026-10-27T07:15:45Z"` | https://github.com/ballisarium/aiogram-skills |
| Rithprohos/telegram-mini-app-skills | CONFIRMED | 14 stars; license null (no LICENSE file; README shows an MIT badge); created 2026-02-20; pushed 2026-02-21 | `"stars":14,"license":null,"pushed":"2026-02-21T15:42:08Z"` | https://github.com/Rithprohos/telegram-mini-app-skills |

Extra, not asked: grammyjs/awesome-grammY, 283 stars, CC0-1.0, pushed 2026-10-29 (matches the notes).

## 4. Anthropic plugin and skill paths

| Path | Verdict | Correct value | Quote (listing) | Source URL |
|---|---|---|---|---|
| external_plugins/playwright | CONFIRMED | Exists (`.claude-plugin`, `.mcp.json`). | folder listing | https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/playwright |
| external_plugins/context7 | CONFIRMED | Exists (`.claude-plugin`, `.mcp.json`, `README.md`). | folder listing | https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/context7 |
| external_plugins/telegram | CONFIRMED | Exists (`server.ts`, `ACCESS.md`, `LICENSE`, `README.md`, `skills`). | folder listing | https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/telegram |
| anthropics/skills webapp-testing | CONFIRMED | Exists under `skills/`. | skills listing | https://github.com/anthropics/skills/tree/HEAD/skills/webapp-testing |
| anthropics/skills mcp-builder | CONFIRMED | Exists under `skills/`. | skills listing | https://github.com/anthropics/skills/tree/HEAD/skills/mcp-builder |
| "security-guidance" plugin | CONFIRMED path | Real path is `plugins/security-guidance` (not `external_plugins`). | folder listing | https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins/security-guidance |
| Other plugin paths in the notes (claude-md-management, mcp-server-dev, feature-dev, code-review) | CONFIRMED | All exist under `plugins/`. | plugins listing | https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins |

## 5. Cointry (WebFetch, fetch-model quotes)

| Claim | Verdict | Correct value | Quote | Source URL |
|---|---|---|---|---|
| Amount first, then note ("20 cinema") | CONFIRMED (fetch) | Format is amount, then description. Example in the guide. | "Then all you need to tell the bot is:" followed by `20 cinema` | https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot |
| Currency code after the amount ("30000 JPY Japanese whiskey") | CONFIRMED (fetch) | Currency code goes after the amount. Homepage example "969 EUR iPhone". | "All you need to do is just specify that currency:" followed by `30000 JPY Japanese whiskey` | https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot ; https://cointry.io |
| "+" prefix means income | CONFIRMED (fetch) | Leading "+" saves the entry as income. Example "+400 bicycle sale". The guide has no income section. | "Simply add leading plus «+» to the amount, and it will be saved as income." | https://cointry.io |
| `/delete` removes the latest record | CONFIRMED (fetch) | Removes the latest record from the chat. Editing and removing any record is Premium. | "remove the latest record from the chat with /delete" | https://cointry.io (FAQ) |
| `/stats` | CONFIRMED (fetch) | Statistics for the month or year, by category and by user. Charts are in the Mini App. | "Send a /stats command to the bot and get detailed statistics for the month or year." | https://cointry.io (features) |
| Monthly report on the 1st | CONFIRMED (fetch) | Sent on every first day of the month (guide). The homepage says only "every month" for the previous month's spending. | "Cointry also sends you monthly reports on every first day of the month." | https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot |
| Groups supported | CONFIRMED (fetch) | Works in group chats. No participant limit. | "works perfectly in group chats" and "There's no limit on participants." | https://cointry.io/how-to-record-your-expenses-with-cointry-telegram-chatbot ; https://cointry.io |
| Premium $2.5/month, billed annually | CONFIRMED (fetch) | "$2.5 / month" when paid annually (about $30 a year). Premium lists editing, CSV/Excel export, voice input and arbitrary dates. | "$2.5 / month" with the note "when paid annually" | https://cointry.io (pricing section) |

Not re-checked in this pass: the homepage's AI "picks the right category" wording and the 94% accuracy claim; the Gumroad "$20 a year" snippet (conflict with $30 a year on the pricing page is unresolved).

## 6. beancounter README (gh api, first 150 lines plus limits section at lines 178-190)

| Claim | Verdict | Correct value | Quote | Source URL |
|---|---|---|---|---|
| Deterministic parser first; LLM only for ambiguous lines | CONFIRMED | Plain Python parses simple messages. An LLM fallback runs only for "genuinely ambiguous" messages. | "Simple messages are parsed instantly by plain Python" | https://github.com/KidCoderT/beancounter |
| `/setwalletamnt` balance correction | CONFIRMED | Correcting a balance stores the gap, surfaced later as "untracked drift". | "that gap is stored and surfaced later as" ... "untracked drift" | https://github.com/KidCoderT/beancounter |
| Balances are stored | CONFIRMED (correction to nuance) | Balances are never stored; they are always computed as SUM(amnt). | "balances are never stored, always `SUM(amnt)`" | https://github.com/KidCoderT/beancounter |
| Limits: Mini App read-only; no categories, budgets or recurring; currency fixed to $; wallets cannot be deleted | CONFIRMED | Mini App is read-only; no categories, budgets or recurring transactions; currency hardcoded to `$`; wallets can be renamed but not deleted. These lines are at README lines 186-189, outside the head -150 range. | "The Mini App is **read-only**" | https://github.com/KidCoderT/beancounter |
| Stack: python-telegram-bot; SQLite; Bedrock Amazon Nova Micro in eu-north-1 | CONFIRMED | Also FastAPI, SQLModel, Alembic (not in the notes). Region eu-north-1 is stated for Bedrock access. | "AWS Bedrock (Amazon Nova Micro)"; "Bedrock access in `eu-north-1`" | https://github.com/KidCoderT/beancounter |
| License (not in the notes) | NEW | GitHub reports no license (`license: null`). Do not copy code without a license decision. | `"license":null` | https://github.com/KidCoderT/beancounter |

## 7. Claude Haiku 5.5 price (official pricing pages)

| Claim | Verdict | Correct value | Quote (table row) | Source URL |
|---|---|---|---|---|
| Haiku 5.5: input $0.10 and output $0.50 per million tokens | CONFIRMED only for prompts up to 100,000 tokens | Input $0.10 (up to 100K) and $0.50 (over 100K). Output $0.50 (up to 100K) and $2.50 (over 100K). Cache read $0.01 (up to 100K) and $0.05 (over 100K). Cache write, 5-minute: $0.125 and $0.625. Cache write, 1-hour: $0.20 and $1. The notes' figures are right for prompts under 100K tokens only. | "Claude Haiku 5.5 (for prompts up to 100,000 tokens)" - "$0.10 / MTok" base input (pipes in the table replaced by colons) | https://claude.com/pricing ; https://platform.claude.com/docs/en/about-claude/pricing |
| Sonnet 5.5 $2 / $10; Opus 5.5 $4 / $20 | CONFIRMED | Sonnet 5.5 input $2, output $10. Opus 5.5 input $4, output $20. No prompt-size tiers. | "Claude Opus 5.5": "$4 / MTok" input, "$20 / MTok" output | https://claude.com/pricing |
| Batch processing saves 50% | CONFIRMED | 50% off input and output on the Batch API. Haiku 5.5 batch rates for prompts up to 100K: $0.05 input, $0.25 output. | "The Batch API allows asynchronous processing of large volumes of requests with a 50 percent discount on both input and output tokens." | https://platform.claude.com/docs/en/about-claude/pricing |

Impact on the notes' cost estimates: they hold for prompts under 100K tokens. Any prompt above 100K is priced at five times the base rate for input and for output.

## Reliability rating

1. Telegram official rules (section 1): High. Checked by grep of the official text. One claim (first private message) is only on the tutorial page; one conflict (mentions) is recorded.
2. Owerly, Lightsplit, Cointry (sections 2 and 5): Medium. Fetch-model summaries, not grep-matched. The Owerly 50/30/20 example is arithmetically wrong.
3. GitHub numbers, Anthropic paths, Haiku 5.5 price (sections 3, 4, 7): High. Read from gh API and official pages. The notes' Haiku figures are right only below 100K prompt tokens.

## Gaps and open items

- Lightsplit: "default USD" and "/link re-attaches" not found in the tutorial text.
- Owerly: the $6-7 attribution (Splitwise or Owerly) is the fetch model's reading; check the full article.
- Cointry: homepage AI-category wording and the Gumroad $20/year price were not re-checked.
- Telegram: the exact error text for a bot starting a private conversation is not in the official pages read.
- ymdatta/DollarBot: last push Nov 2023; the README's v2.0 features (account types, alerts) were not re-verified in this pass.
