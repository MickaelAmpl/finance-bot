# Telegram-native personal finance trackers: bots and Mini Apps (state as of 31 Oct 2026)

Method: 15 WebSearch calls, about 20 WebFetch calls on product, directory and article pages, and 16 GitHub API checks (run 31 Oct 2026). Telegram "monthly users" counts were not visible on any t.me page fetched. Reddit search returned no Reddit threads, so Reddit is not covered. Habr and vc.ru were seen only in search snippets; DOU was not searched. "Dated sign" means the date shown on the source page. "Relative" means the page shows only "Nmo ago". Items marked UNVERIFIED come from a search snippet, not from the page itself.

## KQ1. Which Telegram bots and Mini Apps exist and are active (EN, RU, UA; AI input)

### Takeaway
12 hosted Telegram finance products found (bot or Mini App). Five show a 2026 date: Cointry, Kopilo, Tabby, IGNIO, Expenselizer. Three Russian/Ukrainian bots (Finnik, Fiinny, PotBot) have only a 6 Sep 2025 article as their latest sign. FinNotes (RU) has a 21 Nov 2025 post. 13 open-source repos found; 11 have no push in the last 12 months (possibly dead). No hosted product showed a Telegram monthly-user count on its t.me page.

### Cited Findings

Hosted products (bots and Mini Apps):

| # | Product | Handle / t.me link | Type | Pricing (as shown) | Dated sign | Sources |
|---|---|---|---|---|---|---|
| 1 | Cointry | @cointrybot / https://t.me/cointrybot | Bot + Mini App | Free $0 forever; Premium $2.5/month when paid annually; Business by contact | Site copyright "2020-2026" (fetched 31 Oct 2026); no last-updated date | [cointry.io](https://cointry.io); [t.me](https://t.me/cointrybot) |
| 2 | Kopilo | @KopiloAppBot / https://t.me/KopiloAppBot | Mini App (bot entry) | "Free Options" tag; 7-day free trial, no card (maker comment); no paid price found | "Launched in 2026" (PH) | [PH](https://www.producthunt.com/products/kopilo); [t.me](https://t.me/KopiloAppBot) |
| 3 | Tabby | @tabbyfinancebot / https://t.me/tabbyfinancebot (from site; t.me page not opened) | Bot + web dashboard | Free $0; Pro $24.99/year; 14-day Pro trial, no card | Site "(c) 2026"; "Launched in 2026" (PH) | [site](https://tabbyfinance.app); [PH](https://www.producthunt.com/posts/tabby-10) |
| 4 | FinTrack (AI Expense Tracker) | @PersonalFinTrackerBot / https://t.me/PersonalFinTrackerBot | Bot | not found | no date shown | [t.me](https://t.me/PersonalFinTrackerBot) |
| 5 | Finnik - Money Tracker | @Finnik1Bot / https://t.me/Finnik1Bot | Bot | not found | article 6 Sep 2025 | [t.me](https://t.me/Finnik1Bot); [tproger](https://tproger.ru/articles/top-20-prilozhenij-po-finansam-v-2025-godu) |
| 6 | Fiinny (bot name shown as "ChatGPT 5.4 \| Finny") | @Fiinny_bot / https://t.me/Fiinny_bot | Bot | not found | article 6 Sep 2025 | [t.me](https://t.me/Fiinny_bot); [tproger](https://tproger.ru/articles/top-20-prilozhenij-po-finansam-v-2025-godu) |
| 7 | PotBot (tproger name: PotTeleBot) | @PotTeleBot / https://t.me/PotTeleBot | Bot | not found | article 6 Sep 2025 | [t.me](https://t.me/PotTeleBot); [tproger](https://tproger.ru/articles/top-20-prilozhenij-po-finansam-v-2025-godu) |
| 8 | FinNotes | not found (not in article) | Mini App | not stated by author; a commenter claims 50 Stars/month (UNVERIFIED) | post 21 Nov 2025 | [t-j.ru](https://t-j.ru/we-started-telegram-mini-app-for-financial-accounting/) |
| 9 | IGNIO | not found (ignio.app redirects to leocardz.com, then a7t.ai; not fetched) | Bot-led, web dashboard | "Freemium from $7.99"; currency not stated, tiers not listed | PeerPush listing 2 May 2026; maker comment 7 Apr 2026 | [PeerPush](https://peerpush.com/p/ignio) |
| 10 | Expenselizer | not found | Web app + Telegram bot | 7-day trial; Basic $1/mo; Premium $5/mo (currency not stated) | "Launched in 2026" (PH) | [PH](https://www.producthunt.com/products/expenselizer) |
| 11 | TeleExpense Tracker | not found | Telegram bot writing to the user's Google Sheet | not stated | relative "4mo ago" only | [PH](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2) |
| 12 | Spendly | not found | Bot; status "Now in BETA" | not stated | relative "4mo ago" only | [PH](https://www.producthunt.com/p/spendly-6/spendly-7) |

Mini App directories:
- tapps.center (fetched 31 Oct 2026): wallet and TON/DeFi apps only (Tonkeeper, Wallet in Telegram, My Wallet, STON.fi, DeDust and others). No expense or budget app found. Footer year 2026. Source: [tapps.center](https://tapps.center/)
- findmini.app: search returned only game listings (PAWS, Donot). No finance listing found. Source: search result only; not fetched.

Seen in search, not profiled (snippet only, not verified):
- MonySi, an AI family-budgeting Mini App: [Indie Hackers](https://www.indiehackers.com/product/monysi)
- Smart Budget Bot: snippet says free tier with shared chats, premium $1.99/mo or $15.99/yr: [AlternativeTo](https://alternativeto.net/software/smart-budget-bot/about/)
- Receipt-photo bots: [Receiptist](https://peerpush.com/p/receiptist), [Receipta](https://hunted.space/product/receipta), [Receiptix](https://www.alternativeto.net/software/receiptix/about/)
- SmartExpenseBot (self-hosted, DeepSeek parsing, multi-currency per snippet): [Ready Tensor](https://app.readytensor.ai/publications/smartexpensebot-Lar8MYmfnXPQ)
- SplitKit: bill splitting only, not a tracker: [AlternativeTo](https://alternativeto.net/software/splitkit/about/)
- Copilka (Russian): Android app on RuStore, not a Telegram product: [RuStore](https://www.rustore.ru/catalog/app/app.kopilka)

### Inferences
- Most hosted products are expense-first. Accounts and assets do not appear in any hosted product found.
- Several launches name an individual maker on their pages (Kopilo, IGNIO, Spendly, TeleExpense); Expenselizer and Cointry's operator are not named as individuals. Abandonment risk for individual-run products is higher than for a company product; this is an inference from the maker names, not a measured fact.

### Gaps
- Pricing not found for FinTrack, Finnik, Fiinny, PotBot, TeleExpense, Spendly.
- Handles not found for FinNotes, IGNIO, Expenselizer, TeleExpense, Spendly.
- Ukrainian and Russian products beyond the four bots and FinNotes not found within the search budget.

## KQ2. Per-product details (features, pricing, usage, operator, data, activity)

### Takeaway
Income and expenses are common. Accounts and assets are not offered by any product found. Multi-currency with FX conversion is in the free tiers of Cointry and Tabby. CSV/Excel export and voice input are mostly paid. The only stated data location is Cointry (EU). No product showed a visible Telegram user count.

### Cited Findings

Feature matrix ("not found" = no mention on the pages checked; "not mentioned" = page lists features but this one is absent). Sources for each cell are in the product notes below.

| Product | Income | Accounts | Assets / net worth | Multi-currency + FX | Budgets | Recurring | Charts | Shared / family | CSV/Excel export | Bank import | AI / input |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Cointry | yes (command) | not mentioned | not mentioned | yes, free; rates updated twice a day | yes, free and Premium | Premium, "upcoming" | Mini App graphs | yes; free "unlimited users in a chat" | Premium | not mentioned | AI categories; voice (Premium); photo not mentioned |
| Kopilo | not stated | not found | not found | 50+ currencies (PH) | yes | not found | not found | yes ("Shared Spaces") | not found | not found | AI assistant; receipt scanning |
| Tabby | yes (salary as recurring) | not mentioned | not mentioned | yes, free, live rates | yes (free: 1 category) | yes (subscriptions, rent, salary) | yes | yes (group split) | Pro | no ("does not connect to banks") | text; receipt photos (3/month free); voice (Pro) |
| FinTrack | yes (t.me description) | not found | not found | UNVERIFIED (several currencies) | not found | not found | not found | UNVERIFIED (family budget) | UNVERIFIED (Google Sheets) | not found | "AI" in name only |
| Finnik | yes (tproger) | not found | not found | not found | not found | payment reminders | reports | not found | not found | not found | not stated |
| Fiinny | not found | not found | not found | not found | yes (suggests budgets) | not found | analytics | families, small business | not found | not found | name suggests GPT-based (UNVERIFIED) |
| PotBot | not found | not found | not found | not found | not found | not found | visual reports (tproger) | "joint funds" (t.me) | not found | not found | not stated |
| FinNotes | no (expenses only) | not found | not found | not found | not mentioned | payment reminders | charts | yes (couples, families, friends) | Excel export; Notion sync | not found | voice entry; AI tips |
| IGNIO | not stated | not found | not found | not found | not found | recurring and installments | dashboard | not found | not found | not found | receipts, voice notes, text; AI extraction |
| Expenselizer | not stated | not found | not found | not mentioned | not mentioned | not found | dashboard, trends | not found | not mentioned | not found | Telegram bot logging; categories |
| TeleExpense | not stated | not found | not found | not mentioned | not found | recurring entries | monthly reports | shared tracking with partner | Google Sheets (CSV not listed) | "bank alerts" (banks not named) | AI categorisation; receipt scanning |
| Spendly | not stated | not found | not found | not found | yes (tracks against budget) | not found | not found | not found | not found | not found | chat-message entry |

Per-product notes:

- Cointry: features and prices from [cointry.io](https://cointry.io) (fetched 31 Oct 2026). Free: "$0 / forever", unlimited records, categories and users in a chat. Premium: "$2.5 / month", "when paid annually". Business: contact hi@cointry.io. FX rates update twice a day (CurrencyBeacon; Belarusian ruble rates from the National Bank of Belarus). Data: "stored in the EU"; "not end-to-end encrypted by design" (same page). Usage: monthly users not shown on [t.me/cointrybot](https://t.me/cointrybot). Capterra lists "Rated by 0 users" ([Capterra India](https://www.capterra.in/software/1105371/Cointry), search snippet). Product Hunt shows one review (search summary, [PH](https://www.producthunt.com/products/cointry)). Conflict: [Capterra US](https://www.capterra.com/p/10049958/Cointry/) lists CSV/Excel export and recurring transactions in the free plan; cointry.io places export on Premium and recurring as "upcoming". The vendor site is used here. An older [Gumroad listing](https://cointry.gumroad.com/l/cointry) is titled "$20 a year"; not verified as current.
- Kopilo: Product Hunt tagline "Your money's copilot, right inside Telegram"; AI assistant, receipt scanning, 50+ currencies, joint family budgets, bill splitting ([PH](https://www.producthunt.com/products/kopilo)). Bot description: "Track personal and shared expenses, budgets, goals, and debts with AI" ([t.me/KopiloAppBot](https://t.me/KopiloAppBot)). Maker: Alexander Polozhnov, solo developer (PH). PH shows 0 reviews and 7 followers. Maker status note: "phase 9 - domain, scaling, getting real people to use it" (PH), which suggests early stage. Usage on t.me: not shown. Data location: not found.
- Tabby: [tabbyfinance.app](https://tabbyfinance.app) (fetched). Free: one budget category, one alert at 100%, two suggestions per month, three receipt scans per month, multi-currency at live rates. Pro: $24.99/year, 14-day trial without card; unlimited budgets; alerts at 50/75/100%; payday-to-payday budget cycles; voice logging; unlimited scans; Excel/CSV export. FAQ: "does not connect to banks". Data: "I don't sell or share your data" (site); storage location not stated. Operator not named on fetched pages. Usage on PH: 2 points, 9 followers, no reviews ([PH](https://www.producthunt.com/posts/tabby-10)). Conflict: PH lists pricing as "Free"; site lists Pro tiers. Site used.
- FinTrack: [t.me/PersonalFinTrackerBot](https://t.me/PersonalFinTrackerBot) shows name "FinTrack - AI Expense Tracker" (emoji removed), Ukrainian description "Облік витрат і доходів у Telegram" (expense and income tracking in Telegram), support contact @fintrackbot_support. Monthly users not shown. UNVERIFIED claims from a Ukrainian-language search summary (source article not identified): records to Google Sheets, Ukrainian and Russian UI, several currencies, shared family budget. The same summary cites an article author who says the sheet is created in the developer's account, so the developer may see all entries. Pricing not found.
- Finnik: [t.me/Finnik1Bot](https://t.me/Finnik1Bot) shows "Finnik - Money Tracker", description "Manage your money with ease", support @FinnikSupport. Monthly users not shown. [tproger](https://tproger.ru/articles/top-20-prilozhenij-po-finansam-v-2025-godu) (6 Sep 2025): quick entry of expenses and income, reports, reminders about scheduled payments. Pricing not stated.
- Fiinny: [t.me/Fiinny_bot](https://t.me/Fiinny_bot) shows "ChatGPT 5.4 | Finny", description "pocket financial expert", contact @mon_tti1. Monthly users not shown. [tproger](https://tproger.ru/articles/top-20-prilozhenij-po-finansam-v-2025-godu) (6 Sep 2025): budget suggestions, hidden-spending flags, analytics for families and small businesses. Pricing not stated.
- PotBot: [t.me/PotTeleBot](https://t.me/PotTeleBot) shows "PotBot", description "Joint funds manager", monthly users not shown. [tproger](https://tproger.ru/articles/top-20-prilozhenij-po-finansam-v-2025-godu) (6 Sep 2025) describes "PotTeleBot" as an expense and income tracker with visual reports. The two descriptions differ; tproger gives no handle, so the match is by name. Pricing not found.
- FinNotes: [t-j.ru post](https://t-j.ru/we-started-telegram-mini-app-for-financial-accounting/), 21 Nov 2025, by Yuliana Shilko (T-Journal community post; author describes her own launch). Runs inside Telegram, no login or download. Features per post: categories, totals, voice entry, shared expenses for couples/families/friends, analytics, AI tips, charts, payment reminders, Excel export, Notion sync, period filters, backdated entries. Income not offered ("this was an expense tracker, not income"). Accounts, currencies, bank import: not found. Self-reported: launch cost about 500,000 RUB; net revenue 30,000-50,000 RUB/month; the author says most revenue comes from Germany. Commenters dispute the figures. Price: not stated by author; a commenter claims "50 stars per month or about 100 rubles" (UNVERIFIED). Handle not given.
- IGNIO: [PeerPush](https://peerpush.com/p/ignio): tagline "Track your finances via Telegram using AI". Inputs: receipts, voice notes, text. Also installments, recurring transactions, web dashboard. "Freemium from $7.99"; no tier breakdown. Maker: @leocardz (individual). 9 upvotes, 6 follows, no reviews. X handle @ignio (PeerPush). Website ignio.app redirects to leocardz.com and then to a7t.ai (not fetched). Telegram handle, data location: not found.
- Expenselizer: [PH](https://www.producthunt.com/products/expenselizer): web app for tracking expenses with a Telegram bot for logging and reports. Pricing from maker comment: 7-day trial, Basic $1/mo, Premium $5/mo; currency not stated on page. PH: 0 points, 2 followers, no reviews. Launched in 2026 (PH). Handle, operator, data location: not found.
- TeleExpense Tracker: [PH](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2): tagline "Auto-track expenses from bank alerts in Telegram"; records to the user's own Google Sheet; no bank login (PH); AI categorisation; monthly reports; shared tracking with a partner. Maker: Bruce Wang. Multi-currency not mentioned; pricing not stated. Which banks send the alerts is not named. Also listed at [TrustMRR](https://trustmrr.com/startup/teleexpense-tracker) (not fetched). Usage: two unlabelled counts ("2", "4") on PH.
- Spendly: [PH](https://www.producthunt.com/p/spendly-6/spendly-7): "a simple budgeting assistant that works entirely inside Telegram"; status "Now in BETA"; maker Nour Imen Bousaid; pricing not stated; Telegram handle not on page. Unlabelled counts "8" and "5" on the PH thread.

### Inferences
- Where sources disagree, the vendor site is used over directory pages: Cointry (export on Premium), Tabby (Pro tiers).
- Usage signals are weak across the set: Product Hunt followers range from 2 to 9 for the launches checked, GitHub stars from 0 to 11. These are not user counts.

### Gaps
- Telegram monthly-user counts: not visible on the t.me pages fetched (@PersonalFinTrackerBot, @cointrybot, @KopiloAppBot, @Finnik1Bot, @Fiinny_bot, @PotTeleBot). Not checked: @tabbyfinancebot, @fStatisticsBot.
- Data storage location: not found for Tabby, Kopilo, IGNIO, Expenselizer, FinNotes.
- Operator: not found for Tabby, Expenselizer, FinTrack, Finnik, Fiinny, PotBot, FinNotes.
- Last activity after Sep 2025 (Finnik, Fiinny, PotBot): not found. Possibly dead, not verified.
- Stars pricing: no product confirmed as priced in Telegram Stars. The FinNotes figure is an unverified comment.

## KQ3. Does any product import from Austrian banks (Erste Bank / George) or Ukrainian banks (PrivatBank, monobank)?

### Takeaway
No Telegram product found that imports from Erste Bank / George or PrivatBank. The only bank import found is monobank, through the self-hosted open-source project monobudget, which writes to YNAB or Lunch Money rather than to a Telegram tracker. George does offer transaction export as CSV, Excel or JSON per Sparkasse Austria help pages (George Business), which a custom build could read; private-account availability is not verified.

### Cited Findings
- Erste / George: no Telegram bot or Mini App found importing George data (one English and one German search). Neither search returned a relevant product.
- George export options: Sparkasse Austria help (George Business) says the full transaction history can be exported, with CSV, Excel or JSON as file options; PDF uses the print function. Source: [George Business export](https://www.sparkasse.at/en/george-help/george-business/transactions-and-search/print-and-export/download---export-your-account-history); [Account history export (George Business, German)](https://www.sparkasse.at/de/george-help/george-business/transaktionen-und-suche/drucken-und-exportieren/export-ihrer-kontohistorie) (title and page seen in search results; not fetched).
- Electronic statement format: camt.053 XML, per Sparkasse Austria help page for George Business, revised 03.03.2026 (search snippet): [Kontoauszuege](https://www.sparkasse.at/de/george-help/george-business/konten-und-finanzierungen/ihre-konten/kontoauszuege).
- Private George pages also appeared in results (not fetched): [Export your search results](https://www.sparkasse.at/en/george-help/george/search-and-find/your-search-results/export-your-search-results). The summary of that page lists CSV, Excel and JSON.
- monobank: [monobudget](https://github.com/smaugfm/monobudget) (11 stars, last push 2025-01-06, no license returned). Pulls monobank transactions via webhook into YNAB or Lunch Money; per-account monobank token; Telegram bot for notifications and category fixes (search summary of repo).
- monobank: a Telegram bot "Cashy" appears only as a freelance job spec for automatic monobank transaction retrieval, not a released product: [Freelancehunt](https://freelancehunt.com/en/project/telegram-bot-cashy/1538756.html).
- monobank: [financyka-bot](https://github.com/iYasha/financyka-bot) lists scraping of MonoBank mobile-banking data as a planned item, not built (search summary).
- monobank API docs at https://api.monobank.ua were named in a search summary as the place to check rate limits and webhooks; not fetched, so no limits are stated here.
- PrivatBank: no product found in one Ukrainian-language query that included "privatbank".
- TeleExpense Tracker reads "bank alerts" ([PH](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2)); the banks it supports are not named.
- Tabby: explicitly does not connect to banks ([tabbyfinance.app](https://tabbyfinance.app)).

### Inferences
- An Erste/George import would need a custom build or a manual CSV upload into a tool; no existing Telegram product covers it.
- monobudget is a usable reference for a Monobank path, but its output is YNAB/Lunch Money, not a Telegram tracker.

### Gaps
- Whether private Erste accounts can export CSV in George: not verified. The pages found are Sparkasse Austria pages for George Business.
- PrivatBank: not found.
- A third-party "george" agent skill on [eliteai.tools](https://eliteai.tools/agent-skills/george) automates George in a browser and stores a login session locally. Not evaluated and not used; it would require the user's bank login, so it needs a separate security review.

## KQ4. Which products are open source (repo links)

### Takeaway
13 open-source repos found. Two were pushed within the last 12 months: SpendSnap (23 Aug 2026) and teferdet/finances (26 Oct 2026). The rest (last push 2021 to 2025) are flagged as possibly dead. Only monobudget covers a bank import, and only for Monobank. None combines Telegram, accounts, assets, multi-currency and bank import with recent activity.

### Cited Findings

"Last push" = GitHub pushed_at timestamp, checked 31 Oct 2026 with gh API. "Possibly dead" = no push since 31 Oct 2025. "None reported" = GitHub API returned no SPDX license.

| Repo | Telegram handle | Stars | Last push | License | What it does | Possibly dead |
|---|---|---|---|---|---|---|
| [s4lat/GoSavingsBot](https://github.com/s4lat/GoSavingsBot) | not found | 5 | 2024-11-28 | MIT | Go; entries as "amount name"; day/month/year stats; CSV/Excel export; timezones ([pkg.go.dev](https://pkg.go.dev/github.com/s4lat/gosavingsbot), search summary) | yes |
| [DrVisual/FinancialT_Bot](https://github.com/DrVisual/FinancialT_Bot) | not found | 1 | 2025-08-30 | MIT | 3 expense categories; USD and EUR to RUB rates; SQLite (search summary) | yes |
| [smaugfm/monobudget](https://github.com/smaugfm/monobudget) | not found | 11 | 2025-01-06 | None reported | Monobank to YNAB or Lunch Money via webhook; Telegram notifications (search summary) | yes |
| [iYasha/financyka-bot](https://github.com/iYasha/financyka-bot) | not found | 0 | 2024-09-23 | MIT | Telegram finance manager; MonoBank scraping on roadmap, not built (search summary) | yes |
| [Kusagra9308/SpendSnap](https://github.com/Kusagra9308/SpendSnap) | not found | 0 | 2026-08-23 | None reported | Telegram expense bot; LangGraph + Groq Llama 3.3 70B; text and receipt screenshots; no voice (search summary) | no |
| [teferdet/finances](https://github.com/teferdet/finances) | @fStatisticsBot ([repo page](https://github.com/teferdet/finances)) | 2 | 2026-10-26 | MIT | Fiat, crypto and stock prices; portfolio; price alerts; needs CoinMarketCap and Financial Modeling Prep API keys and MongoDB (repo page, search summary). No expenses. | no |
| [maximten/scrooge](https://github.com/maximten/scrooge) | not found | 2 | 2023-01-14 | None reported | Self-hosted Telegram bot for assets and expenses; multiple currencies; stocks and crypto; USD totals; automatic FX updates (search summary) | yes |
| [rarepepi/alfred](https://github.com/rarepepi/alfred) | not found | 4 | 2022-11-22 | Apache-2.0 | Telegram bot for assets across platforms (repo description) | yes |
| [mtkumar123/MyDollarBot](https://github.com/mtkumar123/MyDollarBot) | not found | 0 | 2021-11-25 | MIT | Student project; per-category budgets with alerts (search summary) | yes |
| [ymdatta/DollarBot](https://github.com/ymdatta/DollarBot) | not found | 0 | 2023-11-28 | MIT | Student project; balances in USD, INR, GBP, EUR, CAD, JPY; low-balance alert (search summary) | yes |
| [MilaEgoshina/expense-tracker-bot](https://github.com/MilaEgoshina/expense-tracker-bot) | not found | 0 | 2024-04-24 | None reported | Income and expenses with history; aiogram + sqlite3 (repo description, search summary) | yes |
| [kkkooolllyyyaaa/finance-bot](https://github.com/kkkooolllyyyaaa/finance-bot) | not found | 0 | 2022-11-12 | None reported | Expense tracker bot (repo description) | yes |
| [AS-1312/Fin-Bot](https://github.com/AS-1312/Fin-Bot) (search result showed UltimateRoman/Fin-Bot; redirects here) | not found | 1 | 2021-04-18 | None reported | Personal finance tracker bot (repo description) | yes |

Listed but not verified: github.com/aronsx/telegram-finance-bot (gh API returned 404; listed in search) and github.com/Nash-Well/inspensebot (gh API returned 404).

### Inferences
- The only recently active self-hosted expense bot is SpendSnap, which has no voice input and no accounts. Using it means building on it, not reusing it.
- teferdet/finances is active but tracks prices, not expenses or bank accounts.

### Gaps
- No open-source repo found that combines Telegram, multiple accounts, assets, multi-currency and bank import with activity in the last 12 months.

## KQ5. What needs are poorly served (assets/net worth, multi-currency, bank sync, privacy)

### Takeaway
Free multi-currency with FX conversion exists (Cointry, Tabby). Poorly served: accounts plus assets/net worth in one Telegram tool; any Austrian or PrivatBank import; bank sync outside Monobank (self-hosted only); clear privacy terms (only Cointry states a storage location). Shared and family use is common. Accounts are not.

### Cited Findings
- Multi-currency with FX: Cointry free plan, FX rates updated twice a day ([cointry.io](https://cointry.io)). Tabby free plan, multi-currency at live rates ([tabbyfinance.app](https://tabbyfinance.app)). Kopilo lists 50+ currencies ([PH](https://www.producthunt.com/products/kopilo)); not verified beyond the listing.
- Assets / net worth: no hosted Telegram product with accounts and assets found. Closest: teferdet/finances, which tracks fiat, crypto and stock prices and a portfolio, with no expenses and no bank accounts ([repo](https://github.com/teferdet/finances)). Scrooge covered assets plus expenses but was last pushed 2023-01-14 ([repo](https://github.com/maximten/scrooge)).
- Bank sync: Monobank only, through self-hosted monobudget ([repo](https://github.com/smaugfm/monobudget)). Tabby explicitly has no bank connection ([site](https://tabbyfinance.app)). TeleExpense reads bank alerts; banks not named ([PH](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2)).
- Privacy: Cointry states "stored in the EU", not end-to-end encrypted ([cointry.io](https://cointry.io)). TeleExpense stores in the user's own Google Sheet ([PH](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2)). Self-hosted repos run on the user's own server. FinTrack's Google Sheet is reportedly in the developer's account (UNVERIFIED). No privacy statement found for Kopilo, IGNIO, Expenselizer, FinNotes.
- Shared and family use: Cointry (group chats, [cointry.io](https://cointry.io)); Tabby (group split, [PH](https://www.producthunt.com/posts/tabby-10)); Kopilo ("Shared Spaces", [PH](https://www.producthunt.com/products/kopilo)); FinNotes (couples, families, friends, [t-j.ru](https://t-j.ru/we-started-telegram-mini-app-for-financial-accounting/)); TeleExpense (shared tracking, [PH](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2)).
- Export: paid in most products. Cointry Premium, Tabby Pro (Excel/CSV) and FinNotes (Excel, price not stated). Not found in any free tier.
- Income tracking: Cointry and Tabby (recurring salary entries) ([site](https://cointry.io), [site](https://tabbyfinance.app)). FinNotes explicitly excludes income.
- Pricing currency: most hosted products price in USD. No product confirmed as priced in Telegram Stars.
- Activity and scale: all Product Hunt signals are small (2 to 9 followers for the launches checked). The only revenue figure is self-reported by FinNotes and disputed in its comments ([t-j.ru](https://t-j.ru/we-started-telegram-mini-app-for-financial-accounting/)).

### Inferences
- Fit for the user's case (judging only): no product found covers EUR, UAH and USD together with accounts, assets and bank import.
- Closest for the expense part: Cointry (free multi-currency with FX, budgets, group chats, EU storage). It lacks accounts, assets and bank import, and CSV/Excel export costs $2.5/month on the annual Premium plan ([cointry.io](https://cointry.io)).
- Closest for the asset-price part: teferdet/finances, but it is self-hosted and needs API keys and MongoDB.
- Based on this scan, accounts plus assets plus bank import in one place is not available off the shelf in Telegram. This is an inference from the products found.

### Gaps
- Erste/George private export and any Erste import: not verified.
- PrivatBank import: not found.
- Reddit, Habr and vc.ru user experiences: not covered (Habr article 726622 seen in search only, not fetched).
- Telegram monthly-user counts for most products: not visible.
- Pricing for six products and handles for five products: not found (see KQ1 gaps).
