# Group bill-splitting bot for Telegram: live bots, open-source repos, reference apps, Bot API constraints

Research date: 31 Oct 2026.

How to read the source labels:
- "(verified)" = exact wording confirmed with a grep or text mirror of the official page on 31 Oct 2026.
- "(summary fetch)" = read through a summarizing WebFetch. Treat as paraphrase, not quote, unless marked verbatim.
- "(search snippet)" = taken from search result text only. The page itself was not opened.
- "(gh)" = GitHub API data from `gh` on 31 Oct 2026.

Tool use: WebSearch 10 calls, WebFetch 11 calls, plus gh and curl checks. This went past the ~15 guideline because the brief covered six areas.

---

## 1. Live Telegram bots and Mini Apps for group splitting

### Takeaway
Live products are few, and most are EN vendor products. Two entry patterns exist: (a) slash commands typed in the group chat (Lightsplit, SplitMate), and (b) a button posted in the group that opens a Telegram Mini App form (Owerly; Lightsplit uses a Mini App for unequal splits). None of the products read accepts free-text expense entry. Pricing is mostly not published. RU/UA coverage is thin: only Owerly and SplitMate matched group-debt bots.

### Cited Findings

**Lightsplit (@lightsplit_bot), EN, vendor tutorial dated 1 May 2026** (summary fetch)
- Handle: @lightsplit_bot, per [Lightsplit home](https://lightsplit.com/).
- Setup: add the bot to a group, or use it in private chat. `/newgroup Tokyo Trip JPY` creates a group; the second word is the settlement currency, default USD. `/link <group url>` attaches an existing Lightsplit group. Source: [tutorial](https://lightsplit.com/blog/telegram-bot-split-expenses-tutorial), published May 1, 2026 per the page.
- Members: existing Telegram group members are imported automatically as default members when the group is created. People without Telegram are added through the Mini App and included in settlement. Source: same tutorial.
- Entry: commands only, e.g. `/add 3000 ramen` or `/add 3000 JPY ramen`. Tutorial: "The bot only handles messages that start with `/`." Default split is equal among all members. A "View Details" button opens the Mini App for changes. Source: same tutorial.
- Unequal splits: done in the Mini App (exclude people, split by ratio). Source: same tutorial.
- Multi-currency: expenses in several currencies, converted automatically into the group's settlement currency (examples JPY, THB, EUR). Source: same tutorial. Homepage: "automatic exchange rate conversion", no currency list. Source: [home](https://lightsplit.com/).
- Transfers: `/transfer 5000 @bob` records money movements such as floats or paybacks, not expenses. No separate "mark as paid" action described. Source: same tutorial.
- Balances: `/balances` shows net amount per person (positive = owed to them). Tutorial: "Lightsplit collapses everything into the fewest transfers possible." Homepage section "Simplify Debts": "Automatically minimize the number of transfers needed." Sources: same tutorial; [home](https://lightsplit.com/).
- Other commands: `/stats` (totals by category); `/unlink` detaches the chat and keeps data, `/link` re-attaches. Mini App: AI receipt scanning, edit history. Source: same tutorial.
- Not found: pricing, free-tier limits (homepage has an "Is Lightsplit free to use?" heading with no answer in the fetched text), CSV/PDF export, a changelog or "last updated" date.

**Owerly (@owerlybot), RU market, Telegram Mini App, article dated 16 Dec 2025** (summary fetch of [devby.io](https://devby.io/ru/news/owerly))
- Handle: @owerlybot, plus a link t.me/OwerlyBot in the article.
- Setup: add the bot to a group chat. The bot posts one message with a button that opens the Mini App; the article suggests pinning it. Russian original: "Добавили бота в чат — и всё." (add the bot to the chat and that's it).
- Entry: a form inside the Mini App with fields amount, category, payer, participants, split method. Text or bot-command entry: not found.
- Participants: picked in the form. Chat members get access automatically. An expense can name people who have not opened the bot yet; they see it when they join.
- Splits: equal ("поровну"), by shares, by percentages, custom amounts.
- Debt calculation: pairwise netting is always on. Example in article: chain of 50, 30, 20 becomes 20 and 10. Group-wide optimization can be turned on in group settings to reduce transfers. No explicit settle-up button wording in the article.
- Currencies: examples GEL and PLN. Automatic exchange rates are a paid feature; debt repayment in any currency is a paid feature. Full currency list: not found.
- Pricing: basic version "полностью бесплатна" (completely free). Paid price and billing period: not found. Article claims it is "дешевле аналогов" (cheaper than comparable products).
- CONFLICT: the search snippet attributed a "$6-7 per month" premium figure to Owerly. The fetched article text says that figure refers to Splitwise's premium plan. Not resolved. Do not use that figure for Owerly.
- Data: cloud storage, so data survives device change. Article: the app stores amounts, categories and descriptions, and no information is passed to third parties. Bot reads only join/leave notifications from group chats. Storage provider: not found.
- Export: not found.

**SplitMate (@party_calc_bot), RU market, article dated 19 Aug 2025** (summary fetch of [vc.ru](https://vc.ru/services/2160473-splitmate-udobnyj-delyoz-raskhodov-v-telegram); article is promotional)
- Handle: @party_calc_bot, from the t.me link in the article.
- Setup: a group member creates an event with `/up <name>`, e.g. "/up Пятница у Сережи".
- Entry: command only, e.g. `/add 1200`. Refunds: `/subtract 500 возврат`. Free-text entry: not found.
- Participants: late joiners are added to the calculation with one message (no dedicated command named). `/include @user1` and `/exclude @user2` adjust the group; per the article, an excluded person's share is recalculated.
- Settlement: `/calc` returns total spent, each person's share, and a transfer list in the form "@А -> @B = 350".
- Equal per-person split; article says the bot splits "по справедливости" (fairly), adjusting kopecks so totals match to the cent.
- Custom splits, currencies, pricing, export: not found.

**SplitFast (hunted.space / Product Hunt), EN** (summary fetch of [listing](https://www.hunted.space/product/splitfast); claims are from the maker's own comment, not verified)
- Maker: "you add the bot to any group chat"; expenses entered by "drop a receipt or an amount"; AI receipt scanning; "Multi-currency with date-locked rates"; can "settle debts"; "Free forever, no ads, no expense caps."
- Bot handle, participant selection, equal vs custom split, launch date: not found.

**Other EN bots, listings only (search snippets; pages not opened)**
- Budget Splitter: standalone app with a Telegram bot to add and manage expenses in group chats; supports multiple payers. Source: [mwm.ai listing](https://mwm.ai/apps/budget-splitter-split-bills/6760643673) (search snippet).
- Tyzenhaus: AlternativeTo describes it as a shared-expense Telegram bot for travelers, roommates and friends. Source: [AlternativeTo](https://alternativeto.net/software/tyzenhaus/?p=3) (search snippet). Handle, pricing: not found.
- SplitEasy Agent: hackathon-style project. Parses bill messages in Telegram or WhatsApp; equal, itemized or custom shares; settlement via ERC-20 transfers on Celo Alfajores (a testnet). Source: [karmahq](https://www.karmahq.xyz/project/spliteasy-agent/about) (search snippet).
- Splitman: an app, not a bot. Described as reducing group debts to the fewest payments. Source: [Product Hunt](https://www.producthunt.com/products/splitman-2) (search snippet).
- Housematee (open-source bot, see section 2): /splitbill and /splitbill_add. Source: [GitHub](https://github.com/tasszz2k/housematee-tgbot) (search snippet).

**RU/UA market**
- RU search: Owerly and SplitMate are the only group-debt bots that matched. Other hits were personal-expense trackers or a Splitall Android app. Splitall is an app, not a bot: [RuStore](https://www.rustore.ru/catalog/app/app.splitall) (search snippet).
- UA search: one service matched, Owerly (same article as above). Other hits were personal trackers and academic papers on building Telegram expense bots with aiogram or python-telegram-bot (search snippets).

**Pricing summary**
- Lightsplit: not found.
- Owerly: basic free; paid price not found.
- SplitFast: "Free forever" (maker's claim).
- SplitMate, Budget Splitter, Tyzenhaus, SplitEasy: not found.

### Inferences
- Live products use one of two patterns: a command ledger (Lightsplit, SplitMate) or a Mini App form opened from a group button (Owerly). Command-only bots run into Telegram privacy mode (section 4), which is why both products say "/" commands.
- Both products import chat members, which implies the bot learns members through join events or from the group itself (see the Bot API constraints in section 4; the API has no member list).
- Two multi-currency models appear: convert to one group currency when the expense is entered (Lightsplit; SplitFast "date-locked rates"), or keep per-currency balances and charge for conversion (Owerly; Splitwise API per-currency balances in section 3).

### Gaps
- Pricing: not found for Lightsplit, SplitMate, Budget Splitter, Tyzenhaus, SplitEasy.
- Handles not found: SplitFast, Tyzenhaus, Budget Splitter.
- No user reviews of the live bots were read (App Store, Google Play, Reddit): not searched in depth; no Telegram-bot-specific review text found in the results.
- Official Splitwise Telegram integration: not searched.

---

## 2. Open-source repos on GitHub

Metadata from `gh api repos/OWNER/REPO` (gh) on 31 Oct 2026. Stars = stargazers count as returned. "Last push" = `pushed_at`. License = SPDX as returned; "none" = GitHub returned no license.

| Repo | Lang | Stars | License | Last push | What it is |
|---|---|---|---|---|---|
| [zovo-one/telegram-split-bill-bot](https://github.com/zovo-one/telegram-split-bill-bot) | TypeScript | 0 | MIT | 2026-09-09 | Bot for group expenses. Repo description: "group expense ledger: add expenses, see balances, minimal settlement, CSV export." (gh; README not read) |
| [tasszz2k/housematee-tgbot](https://github.com/tasszz2k/housematee-tgbot) | Go | 6 | MIT | 2026-01-28 | Housemate bot: home bills, chore reminders, and /splitbill and /splitbill_add (search snippet) |
| [Alvaritobg/telsplit](https://github.com/Alvaritobg/telsplit) | not reported | 0 | MIT | 2026-04-07 | Description "Splitwise telegram bot chat" (gh) |
| [krnbatra/SplitwiseTelegramBot](https://github.com/krnbatra/SplitwiseTelegramBot) | Python | 13 | MIT | 2022-12-08 | "Telegram Bot for managing Splitwise" (gh). Front-end to Splitwise; data lives in Splitwise. |
| [irvinseet/splitwise-telegram-bot](https://github.com/irvinseet/splitwise-telegram-bot) | Python | 0 | none | 2026-04-16 | No description (gh) |
| [BishalJena/splitwise-fastapi](https://github.com/BishalJena/splitwise-fastapi) | Python | 0 | none | 2025-06-14 | "A FastAPI-based Splitwise Telegram bot and MCP proxy" (gh) |
| [bsolf/telegram-debt-bot](https://github.com/bsolf/telegram-debt-bot) | Python | 0 | none | 2025-11-22 | Description "telegram-debt-bot" (gh); nothing else read |
| [ngeeyonglim/telegram-SplitBillBot](https://github.com/ngeeyonglim/telegram-SplitBillBot) | Python | 0 | none | 2026-06-18 | Upload an image, describe the allocation in natural language (gh) |
| [danjaniell/aspire-splitwise-telegram-bot](https://github.com/danjaniell/aspire-splitwise-telegram-bot) | Python | 0 | MIT | 2023-11-06 | No description (gh) |
| [bambuchaAdm/splitwise-telegram-bot](https://github.com/bambuchaAdm/splitwise-telegram-bot) | not reported | 0 | none | 2020-06-12 | "Telegram bot to use splitwise on groups" (gh) |
| [shawyl/Billy](https://github.com/shawyl/Billy) | Python | 0 | none | 2026-06-21 | "Local-first Telegram bill splitting bot that reads receipts, understands split rules, and calculates shared payments ... built-in validation to remove AI hallucination risk." (gh) |
| [Amenediel/Dirshayen](https://github.com/Amenediel/Dirshayen) | not checked | not checked | not checked | 2026-04-24 (search) | "A telegram bill splitting bot with tax and service charge." gh API call timed out; only search metadata. |
| [sz-sudo/TelegramBot-Splitwise](https://github.com/sz-sudo/TelegramBot-Splitwise) | C++ | 0 | none | 2021-02-11 | "does what Splitwise does ... developed for educational purposes" (gh) |

Reference apps (not bots):

| Repo | Lang | Stars | License | Last push | What it is |
|---|---|---|---|---|---|
| [spliit-app/spliit](https://github.com/spliit-app/spliit) | TypeScript | 3,032 | MIT | 2026-10-22 | "Free and Open Source Alternative to Splitwise." (gh) |
| [oss-apps/split-pro](https://github.com/oss-apps/split-pro) | TypeScript | 1,481 | MIT | 2026-10-20 | "Open source alternative to Splitwise." (gh). Per an AlternativeTo snippet: self-hostable, imports from Splitwise, simplifies group debts (search snippet; README not read). |

Notes on the reference app spliit (summary fetch of the README, [repo](https://github.com/spliit-app/spliit)):
- Stack: "Next.js for the web application"; "TailwindCSS for the styling"; "shadcn/UI for the UI components"; "Prisma to access the database"; PostgreSQL (Compose sample uses postgres:17.3); hosting example "Vercel for hosting (application and database)".
- Groups: "Create a group and share it with friends." Identity: "Tell the application who you are when opening a group." No accounts or invite-link mechanism described.
- Splits: "Split expenses unevenly" and "Select all/no participant for expenses." Equal, shares, percentage and amount modes are not named in the README.
- Currency: `DEFAULT_CURRENCY_CODE` pre-selects a currency on the new-group form; default USD. No conversion described.
- Balances: README lists "Display group balances" and "Create reimbursement expenses." The word "simplify" does not appear, and the simplification method is not explained.
- Self-hosting documented: "Run locally", "Run in a container", "Run with Docker compose."

### Takeaway
The GitHub group-splitting bot space is small and mostly hobby-grade. The most-starred bots are Splitwise front-ends where the data lives in Splitwise, not in the bot. The one self-contained group-ledger bot with a recent push is zovo-one/telegram-split-bill-bot (TypeScript, MIT, pushed 2026-09-09, 0 stars, description claims balances, minimal settlement, CSV export). The strongest open reference for data model is spliit (MIT, 3,032 stars), but it is a web app, not a bot.

### Cited Findings
- Most Splitwise-bot repos last pushed between 2020 and 2023 or have no license (gh table above).
- Only zovo-one (2026-09-09) and Housematee (2026-01-28) have a self-contained ledger and a 2026 push among the bots listed, plus Billy (2026-06-21) and ngeeyonglim (2026-06-18), which are no-license projects (gh).
- Billy's own description emphasizes validation of parsed receipts "to remove AI hallucination risk" (gh description).
- spliit README and stack: see above (summary fetch).

### Inferences
- Pattern A: Splitwise front-end bot. Keeps no ledger of its own. Simple, but inherits Splitwise's rules and limits. Examples: krnbatra, BishalJena, irvinseet.
- Pattern B: self-contained ledger in the bot's own database. zovo-one and Housematee. This is the pattern a new product would need.
- Pattern C: LLM receipt parsing with a validation layer. Billy, ngeeyonglim, Dirshayen.
- No repo found that implements a Mini App split UI.

### Gaps
- Not read: READMEs or code of zovo-one, Billy, ngeeyonglim, Dirshayen, bsolf. Stack and commands for those are not verified.
- Star counts are very low for every bot repo, so popularity says little about quality.
- Repos were not cloned or run (per brief).

---

## 3. Reference apps: Splitwise, Tricount, Settle Up

### Takeaway
Splitwise's public API is the best primary data model available. It stores each expense with per-user paid and owed shares, keeps per-currency balances, and returns both original and simplified debts per group. Tricount and Settle Up say simplification minimizes payments or transfers, but neither documents an algorithm. The common third-party description is net balance followed by greedy matching. Splitwise's rule for odd cents is not in its API documentation.

### Cited Findings

**Splitwise API data model** (summary fetch of [dev.splitwise.com](https://dev.splitwise.com/); page read to about 100,000 of about 101,300 characters)
- Expense `cost`: string, "limited to 2 decimal places" (sample "25.0").
- Expense `currency_code`: "Must be in the list from `get_currencies`."
- Expense `users`: array of `user_id`, `paid_share`, `owed_share`, `net_balance` (sample: paid "8.99", owed "4.5", net "4.49"; the summary says net = paid minus owed, from one sample).
- Shares: "Decimal amount as a string with 2 decimal places."
- Creating an equal split: `group_id` plus `split_equally: true`; the authenticated user is treated as payer. Alternatively, explicit `paid_share` and `owed_share` per user.
- Expense `repayments`: array of `from`, `to`, `amount` (sample amount "25.0"). The page does not define the term; the summary reads it as user-to-user amounts (inference).
- Group: `simplify_by_default` (boolean; sample true); `members`, each with `balance` as an array of `{currency_code, amount}`; `original_debts` and `simplified_debts` as arrays of `{from, to, amount, currency_code}`.
- Group types: `home`, `trip`, `couple`, `other`, `apartment`, `house`; docs recommend `home` in place of `house` or `apartment`.
- Notification type 11 is "Debt simplification."
- Currencies: `get_currencies` returns a list; "mostly ISO 4217 codes ... we do sometimes use pending codes or unofficial, colloquial codes."
- Rounding rule for odd cents: not stated on the page read.
- Simplification method: not explained on the page.

**Splitwise simplification, third-party descriptions (search snippets)**
- Simplification "leaves each person's total unchanged while cutting the number of payments" (wikiHow-derived guide, [kiwix mirror](https://kiwix.lema.org/wikihow_en_maxi_2023-03/Use-Splitwise)).
- Algorithm "works from each person's net balance"; greedy approach "works well for small groups and gives near-optimal results"; Splitwise shows both simplified debts and per-expense breakdown (system-design write-up, [techinterview.org](https://www.techinterview.org/post/3233474468/system-design-design-splitwise-expense-sharing-debt-simplification-group-balances-payment-integration-currency-conversion/)).
- Example: Arman owes Geoff RM30 and Geoff owes Fiona RM30; simplification has Arman pay Fiona directly (article, [The Edge Malaysia](https://theedgemalaysia.com/article/financial-hacks-splitwise-makes-it-easy-go-dutch)).

**Splitwise Pro price** (search snippets; no official annual price read)
- Apple App Store listing: Pro prices shown as $39.99, $29.99, $4.99, $2.99 without labels for period (source: [Splitwise on App Store](https://apps.apple.com/app/splitwise-bill-splitter/id458023433)).
- Competitor page (ShareCost): monthly $4.99; yearly "about $29.99-$39.99, depending on region"; says "accurate as of July 2026, per splitwise.com/pro" (source: [ShareCost vs Splitwise](https://budgetbakers.com/es/products/sharecost/vs-splitwise/)). Competitor-authored, so secondary.
- splitwise.com/pro was not opened.

**Tricount**
- Glossary: debt simplification is designed so "only the minimum number of payments is needed to settle up" ([Tricount glossary](https://tricount.com/glossary), search snippet).
- FAQ: the app works out each member's balance and "proposes a method to evenly distribute these balances. The goal is to limit the number of transactions between participants" ([Tricount FAQs](https://help.tricount.com/articles/tricount-faqs), search snippet).
- FAQ: "It might seem odd when tricount suggests you repay someone who hasn't made any payments on your behalf." (same FAQ, search snippet)
- Balances: suggested reimbursements can be marked as paid, and balances return to zero (search snippet; the exact page was not identified).
- Algorithm, currency handling, rounding, pricing, export: not found.

**Settle Up (Step Up Labs)**
- Store-listing aggregator text: a "Minimize the number of debts" toggle shows simplified transfers ([mwm.ai listing](https://mwm.ai/apps/settle-up-group-expenses/737534985), search snippet; secondary).
- Non-users can open a group link to check balances in a browser; data can be emailed as CSV; offline entries sync when back online; Premium reportedly removes ads and adds receipt photos (search snippets from the same listing and APKMirror pages; not verified).
- Official developer documentation: not opened.

**Currencies and rounding across apps**
- Splitwise API: per-currency balances per member; no conversion described in the API docs (see above).
- Lightsplit: converts to the settlement currency at entry (tutorial, section 1).
- SplitFast: "date-locked rates" (maker's claim).
- Owerly: automatic rates are a paid feature (article, section 1).
- Rounding, Splitwise rule: not found.
- Rounding, third-party design guidance:
  - HackerNoon: "let the group choose who receives the extra cent or by rotating the remainder"; "Whatever rule is used, it should be consistent and visible" ([HackerNoon](https://hackernoon.com/how-to-build-a-tip-calculator-that-doesnt-lose-a-cent), search snippet).
  - Shopify money library discussion: the leftover penny could go to "whichever chunk is nearest to the next whole penny" ([PR 284](https://redirect.github.com/Shopify/money/pull/284), search snippet; a proposal, not a decision).
  - Clemson procurement policy (accounting, not Splitwise): "The rounding takes place first, then the difference is applied to the last distribution" ([Clemson policy](https://www.clemson.edu/procurement/faculty-staff/policies/procurement/psv76pol.html), search snippet).
  - A design-interview write-up says the last person absorbs the difference, so $100 split three ways gives 33.33, 33.33, 33.34. The source URL was not identified in the search output; treat as unverified.

**Simplification algorithm in plain words** (inference from the third-party descriptions above; not from an official source)
1. For each person, net = total paid minus total owed (kept per currency).
2. Nets sum to zero. People with positive net are creditors; negative are debtors.
3. Take the largest debtor and largest creditor. Transfer the smaller of the two absolute amounts. Reduce both. Remove whoever reaches zero.
4. Repeat until all nets are zero.
Each transfer settles at least one person, so the count is at most (number of people minus one). Greedy is a heuristic: it does not guarantee the fewest possible transfers. The exact minimum is a harder problem; no source for that was found in this research.

### Inferences
- Store amounts as integers in minor units (cents) to match the API's two-decimal strings. Keep per-currency balances. Convert only if the product explicitly chooses a single group currency.
- Show both views, as Splitwise does: the per-expense list and the simplified transfers. Tricount's FAQ "odd suggestion" note is the reason.
- Pick and display one rounding rule per expense (last share takes the remainder, rotate, or nearest-penny). None of the sources gives Splitwise's rule.

### Gaps
- Splitwise rounding rule: not found in the API documentation read, and not found in search.
- Splitwise official simplification algorithm: not found in official docs.
- Tricount: currency handling, rounding, pricing, export: not found.
- Settle Up: pricing and official docs: not found.
- Splitwise Pro official price: not found on splitwise.com/pro (not opened).

---

## 4. Telegram Bot API constraints for group bots

### Takeaway
A bot in a group does not receive ordinary chat text by default (privacy mode). It cannot list group members at all: the API has no method for that. It can read a single member's status only if it is an admin, per the official wording "guaranteed to work for other users if the bot is an administrator." It learns about joins and leaves from service messages, which privacy mode does not block, and from `chat_member` updates, which require admin rights. Inline buttons do not post into the chat, but every callback must be answered. Group bots are limited to 20 messages per minute.

### Cited Findings

**Privacy mode** (verified, text mirror of [Telegram Bot features, Privacy Mode](https://core.telegram.org/bots/features#privacy-mode), 31 Oct 2026)
- "By default, **all bots** added to groups run in Privacy Mode and only see relevant messages and commands":
  - commands explicitly meant for them, e.g. `/command@this_bot`;
  - general commands such as `/start` if the bot was the last bot to send a message to the group;
  - inline messages sent via the bot;
  - replies to any messages implicitly or explicitly meant for this bot.
- "All bots will also receive, **regardless of privacy mode**": all service messages; all messages from private chats; all messages from channels where they are a member.
- "Privacy mode is **enabled by default** for all bots, except bots that were added to a group as admins (bot admins always receive **all messages**)."
- Turning it off: via BotFather `/setprivacy`; "the bot will need to be re-added to the group for this change to take effect." Telegram recommends force-reply in the bot's own messages instead: "In most cases, using the force reply option for the bot's messages should be more than enough."
- CONFLICT: the Bot API ForceReply example says "A poll bot for groups runs in privacy mode (only receives commands, replies to its messages and mentions)" (verified, [Bot API](https://core.telegram.org/bots/api)). The features page list above does not include mentions. Do not rely on mentions reaching the bot until this is tested.

**Member list and member status** (verified, [Bot API](https://core.telegram.org/bots/api))
- `getChatAdministrators`: returns an array of ChatMember objects.
- `getChatMemberCount`: returns an Integer.
- `getChatMember`: "Use this method to get information about a member of a chat. The method is only guaranteed to work for other users if the bot is an administrator in the chat. Returns a ChatMember object on success."
- The string "getChatMembers" does not appear on the Bot API page (grep, 31 Oct 2026). There is no method to list all members of a group.
- FAQ does not describe member listing (read via [Bot FAQ](https://core.telegram.org/bots/faq), summary fetch; the FAQ has no section on it).

**Learning about joins and leaves** (verified, [Bot API](https://core.telegram.org/bots/api))
- Message service fields `new_chat_members` and `left_chat_member` exist.
- Service messages reach all bots regardless of privacy mode ([features page](https://core.telegram.org/bots/features#privacy-mode), verified).
- `chat_member` update: "A chat member's status was updated in a chat. The bot must be an administrator in the chat and must explicitly specify "chat_member" in the list of allowed_updates to receive these updates."
- `allowed_updates`: "Specify an empty list to receive all update types except chat_member, message_reaction, and message_reaction_count (default)."

**Mentions** (verified, [Bot API](https://core.telegram.org/bots/api))
- "Unless the user is a member of the chat where they were mentioned, these mentions are only guaranteed to work if the user has contacted the bot in private in the past or has sent a callback query to the bot via an inline button and doesn't have Forwarded Messages privacy enabled for the bot."

**Inline keyboards and callbacks** (verified)
- "Unlike with custom reply keyboards, pressing buttons on inline keyboards **doesn't send messages to the chat**." ([features page](https://core.telegram.org/bots/features))
- `callback_data`: "Optional. Data to be sent in a callback query to the bot when the button is pressed, 1-64 bytes" ([Bot API](https://core.telegram.org/bots/api)).
- `answerCallbackQuery`: "After the user presses a callback button, Telegram clients will display a progress bar until you call answerCallbackQuery. It is, therefore, necessary to react by calling answerCallbackQuery even if no notification to the user is needed" ([Bot API](https://core.telegram.org/bots/api)).

**Messages, editing, deleting** (verified, [Bot API](https://core.telegram.org/bots/api))
- `sendMessage` text: "1-4096 characters after entities parsing."
- `editMessageText`: the 48-hour rule is stated only for "business messages that were not sent by the bot and do not contain an inline keyboard." No age limit for the bot's own messages appears in the text read.
- `deleteMessage`: "A message can only be deleted if it was sent less than 48 hours ago." "Bots can delete outgoing messages in private chats, groups, and supergroups."
- Pinning in a group needs the bot to be admin with `can_pin_messages` (or `can_edit_messages` for channels) ([Bot API](https://core.telegram.org/bots/api), pinChatMessage section).

**Rate limits** (verified, [Bot FAQ](https://core.telegram.org/bots/faq))
- Per chat: "In a single chat, avoid sending more than one message per second. We may allow short bursts that go over this limit, but eventually you'll begin receiving 429 errors."
- Group: "In a group, bots are not be able to send more than 20 messages per minute." (sic, as in the FAQ)
- Bulk: "about 30 messages per second", with paid broadcasts to raise it.

**Mini Apps** (summary fetch of [Telegram Mini Apps docs](https://core.telegram.org/bots/webapps); not grep-verified)
- Launch points: keyboard button (`web_app`), inline button, menu button, attachment menu.
- Attachment menu in groups: "Added the ability to use bots added to the attachment menu in group, supergroup and channel chats" (June 20, 2022 changelog entry).
- Attachment-menu availability: "currently only available for major advertisers on the Telegram Ad Platform," though "all bots can use it in the test server environment."
- Inline-button Mini App: receives "basic user information (ID, name, username, language_code)" plus a session query_id.
- Group chat info (`chat`): returned for supergroups and groups "only for Mini Apps launched via the attachment menu and chat join requests."
- Inline mode and direct links: "Inline Mini Apps have no access to the chat," and Mini Apps opened from a direct link "have no access to the chat."
- Member lists: no text on reading group members.
- `initDataUnsafe`: "Data from this field should not be trusted."
- `sendData`: only for Mini Apps launched from a keyboard button; sends a service message to the bot with data "up to 4096 bytes," and closes the Mini App.

### Inferences
- Free-text expenses ("I paid 500 for taxi") will not reach a privacy-mode bot unless the bot is admin. Design entry around commands, ForceReply, or inline buttons. Admin status makes the bot see all messages, which is a trust and privacy cost that must be disclosed.
- Member roster has no API source. Practical options, each to be tested: (a) make the bot admin and use `chat_member` plus `getChatMember` for known IDs; (b) have members press a "join" button or send /join, so the bot learns the user ID from the callback or command; (c) use `new_chat_members` and `left_chat_member` service messages to add or remove people.
- Mini App opened from an in-group inline button gets the user but not the group ID. The bot must bind the Mini App session to the group on its side, and treat any group ID passed in the URL as untrusted (inference from the docs above; not tested).
- Attachment-menu launch is restricted, so group-level Mini App entry should go through inline or keyboard buttons.
- Use one editable ledger or balance message where possible. The group limit of 20 messages per minute means a bot that posts one message per expense will hit the limit in an active group.

### Gaps
- Whether a non-admin bot receives callback queries under privacy mode: not stated on the official features page.
- Whether a bot can message a user who has not started it: not verified in this research. The mention-reliability text above is the only related source.
- Whether a Mini App launched from an inline button in a group can get the group ID: summary says chat info only via attachment menu and join requests. Not confirmed by a test.
- FAQ does not describe how bots learn group members beyond service messages: not found.
- Official "last updated" date for the Bot API and FAQ pages: not found on the pages read.

---

## 5. UX pitfalls reported by users

### Takeaway
Direct user complaints are thin in this search. One Lemmy post complains that Splitwise's group simplification is confusing and adds payments. Open GitHub feature requests in other projects ask for visible simplification and an explanation of automatic debt conversion. No Reddit threads surfaced. The strongest signals come from Tricount's own FAQ and from the design of existing bots.

### Cited Findings
- Tricount FAQ: it "might seem odd" when the app suggests you repay someone who has not paid anything on your behalf ([Tricount FAQs](https://help.tricount.com/articles/tricount-faqs), search snippet).
- Lemmy post: user says the "simplify group debts" feature is confusing and "creates a bunch of extra Venmo transactions" ([Lemmy post](https://lemmy.imagisphe.re/post/558369/1726799), search snippet; the quote is from the search summary, not from the page).
- Splitwise does not move money; settling up happens in another app. Source: [Gerald guide](https://joingerald.com/learn/money-basics/what-is-splitwise) (search snippet; commercial guide, secondary).
- Open issues, in other projects (titles and update dates from gh; these are feature requests, not confirmed complaints):
  - sw-carlos-cristobal/sharetab #328, "feat(groups): honor the simplify-debts setting, with a toggle showing the payments it saves", updated 2026-10-22: [issue](https://github.com/sw-carlos-cristobal/sharetab/issues/328)
  - ChipIn-one/chipin-frontend #277, "Explain Automatic Debt Conversion in Group and Settings UI", updated 2026-10-22: [issue](https://github.com/ChipIn-one/chipin-frontend/issues/277)
  - tanuja1521/Splitwise-API #3, "Add simplify debts option in group", updated 2025-03-15: [issue](https://github.com/tanuja1521/Splitwise-API/issues/3)
  - Cosmichomeless/TAB #44, "[Product] Export a group summary to PDF/CSV", updated 2026-10-13: [issue](https://github.com/Cosmichomeless/TAB/issues/44)
  - sw-carlos-cristobal/sharetab #393, "a balance alert when someone's balance passes a set amount", updated 2026-10-23: [issue](https://github.com/sw-carlos-cristobal/sharetab/issues/393)
- Rounding: a search result quotes a GitHub commenter on importing a Splitwise CSV: "a tiny difference in balances due to the rounding ... but it's a matter of cents." The issue URL was not identified, so the quote is not attributed.
- Telegram design: the Lightsplit tutorial states the bot "only handles messages that start with `/`" (section 1). Anyone who types a cost in chat gets no response. This is a consequence of privacy mode (section 4), not a reported complaint.
- Owerly: expenses can name people who have not opened the bot, and those people see them on joining (article, section 1). A design choice, not a complaint.

### Inferences
- The main pain is explanation rather than arithmetic. Users need to see why a simplified payment differs from the per-expense debts. Show both lists and a one-line reason per transfer.
- A group bot in privacy mode will look broken when users type free text. Put a visible command or button in the first message.
- Users are asking for control over simplification (on/off, see what it saves). Splitwise's API has a per-group `simplify_by_default` setting, so the control exists in the market leader.
- Member changes need a rule. SplitMate recalculates shares on exclude; the Splitwise system-design write-up suggests settling before a person leaves (not verified in a primary source).

### Gaps
- Reddit: no Reddit threads surfaced in the two searches that targeted it. Not found.
- App Store and Google Play reviews of the live Telegram bots: not read. Not found in this research.
- GitHub issues specific to Telegram split bots: none found by `gh search issues "splitwise telegram"` (returned no results).
- Attribution of the rounding complaint: not identified.

---

## Dates and conflicts for the report writer

- Dates: Lightsplit tutorial May 1, 2026 (summary fetch); Owerly article Dec 16, 2025; SplitMate article Aug 19, 2025; Mini App changelog June 20, 2022 and Nov 17, 2024; repo last pushes from gh (section 2); Telegram Bot API and FAQ "last updated" date: not found.
- Conflicts:
  1. Privacy mode: features page default list omits mentions; Bot API ForceReply example includes mentions (section 4).
  2. "$6-7 per month" premium figure: search snippet attributes it to Owerly; fetched article attributes it to Splitwise (section 1).
  3. Splitwise Pro price: Apple listing shows unlabeled prices; competitor page gives a monthly and yearly range; no official page read (section 3).
- Unverified claims flagged in place: SplitFast (maker's claims), Settle Up premium features, the design-interview rounding rule, Tricount "marked as paid" page.
