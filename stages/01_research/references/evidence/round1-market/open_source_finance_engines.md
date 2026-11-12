# Open-source personal finance engines for a personal Telegram Mini App (as of 31 Oct 2026)

Scope: engines only (data model, API, reports). Telegram bridge bots excluded.
Snapshot date: 2026-10-31 (UTC). GitHub numbers from `gh api` run on that date; "last push" = GitHub `pushed_at`.
Evidence labels used below:
- "raw" = read from the page text or repo README directly (reader proxy or gh).
- "extracted" = read through a WebFetch summarizer; re-check before quoting verbatim.
- "search excerpt" = seen only in a search-result summary, page not opened.
- "not found" = searched, nothing usable in this session.

## 1. Candidate landscape and GitHub maturity

### Takeaway
Actual Budget (29,877 stars) and Firefly III (25,046) are the largest active engines; both were pushed on 30-31 Oct 2026. Maybe Finance is archived (last push 2025-07-24, README says "no longer maintained"); its AGPL fork Sure (we-promise/sure, 10,736 stars) is the active successor. The newest fast-moving entrant is Securo (created 2026-03-08, 4,151 stars, 87 releases in the 12 months to 31 Oct 2026). Ivy Wallet is archived; Cashew's last release is from 2024-07-01; budgetzero's last release is from 2021-06-06.

### Cited Findings

| Engine | Repo (source) | Stars | Last push (UTC) | Latest release | Releases since 2025-10-31 | License | Archived | Open issues (incl. PRs) | Contributors (GitHub API) | Language |
|---|---|---|---|---|---|---|---|---|---|---|
| Firefly III | [firefly-iii/firefly-iii](https://github.com/firefly-iii/firefly-iii) | 25,046 | 2026-10-31 03:01 | v6.7.9 (2026-10-11) | 49 | AGPL-3.0 | no | 179 | 180 | PHP |
| Actual Budget | [actualbudget/actual](https://github.com/actualbudget/actual) | 29,877 | 2026-10-30 23:53 | v26.10.0 (2026-10-02) | 16 | MIT | no | 207 | 465 | TypeScript |
| Ghostfolio | [ghostfolio/ghostfolio](https://github.com/ghostfolio/ghostfolio) | 9,622 | 2026-10-31 08:36 | 3.94.0 (2026-10-28) | 155 | AGPL-3.0 | no | 332 | 312 | TypeScript |
| Wealthfolio | [wealthfolio/wealthfolio](https://github.com/wealthfolio/wealthfolio) (old path afadil/wealthfolio redirects) | 9,294 | 2026-10-30 22:18 | v3.11.0 (2026-10-23) | 34 | AGPL-3.0 | no | 539 | 96 | Rust |
| Maybe Finance | [maybe-finance/maybe](https://github.com/maybe-finance/maybe) | 54,206 | 2025-07-24 22:20 | v0.6.0 (2025-07-24) | 0 | AGPL-3.0 | YES | 0 | 124 | Ruby |
| Sure (Maybe fork) | [we-promise/sure](https://github.com/we-promise/sure) (created 2025-07-23) | 10,736 | 2026-10-31 07:02 | v0.7.6 (2026-10-31) | 18 | AGPL-3.0 | no | 799 | 432 | Ruby |
| ezBookkeeping | [mayswind/ezbookkeeping](https://github.com/mayswind/ezbookkeeping) | 5,893 | 2026-10-29 15:21 | v2.1.1 (2026-10-23) | 13 | MIT | no | 20 | 46 | Go |
| Securo | [securo-finance/securo](https://github.com/securo-finance/securo) (created 2026-03-08) | 4,151 | 2026-10-30 20:49 | v0.16.6 (2026-10-26) | 87 | AGPL-3.0 | no | 284 | 118 | Python |
| Fava | [beancount/fava](https://github.com/beancount/fava) | 2,598 | 2026-10-29 20:42 | no GitHub release object; latest tag v1.30.16 (tag date not read) | not counted | MIT | no | 90 | 130 | Python |
| Beancount | [beancount/beancount](https://github.com/beancount/beancount) | 6,137 | 2026-08-23 20:18 | no GitHub release object | not counted | GPL-2.0 | no | 248 | not counted | Python |
| hledger | [hledgerorg/hledger](https://github.com/hledgerorg/hledger) (old simonmichael/hledger redirects) | 4,801 | 2026-10-30 17:58 | 1.52.4 (2026-09-10) | 17 | GPL-3.0 | no | 316 | 182 | Haskell |
| Kresus | [kresusapp/kresus](https://github.com/kresusapp/kresus) | 344 | 2026-10-21 12:48 | no GitHub release object; latest tag 0.26.0 (date not read) | not counted | AGPL-3.0 | no | 125 | 35 | TypeScript |
| Cashew | [jameskokoska/Cashew](https://github.com/jameskokoska/Cashew) | 4,770 | 2026-03-09 01:35 | 5.3.4+396 (2024-07-01) | not counted | GPL-3.0 | no | 13 | not counted | Dart |
| Ivy Wallet | [Ivy-Apps/ivy-wallet](https://github.com/Ivy-Apps/ivy-wallet) | 3,184 | 2026-10-22 14:04 | v2026.10.22-207 (2026-10-22) | not counted | GPL-3.0 | YES | 69 | not counted | Kotlin |
| Money Manager EX | [moneymanagerex/moneymanagerex](https://github.com/moneymanagerex/moneymanagerex) | 2,278 | 2026-10-31 03:28 | v1.9.4 (2026-08-31) | not counted | GPL-2.0 | no | 438 | not counted | C++ |
| Budget Board | [teelur/budget-board](https://github.com/teelur/budget-board) | 894 | 2026-10-31 02:02 | v3.9.0 (2026-10-31) | 31 | AGPL-3.0 | no | 12 | 11 | C# |
| WYGIWYH | [eitchtee/WYGIWYH](https://github.com/eitchtee/WYGIWYH) | 906 | 2026-10-25 15:11 | 0.24.0 (2026-10-24) | 17 | AGPL-3.0 | no | 19 | 43 | Python |
| Paisa | [ananthakumaran/paisa](https://github.com/ananthakumaran/paisa) | 3,230 | 2026-10-21 16:19 | v0.7.8 (2026-10-21) | 4 | AGPL-3.0 | no | 94 | 9 | TypeScript |
| BeeCount | [TNT-Likely/BeeCount](https://github.com/TNT-Likely/BeeCount) (created 2025-09-06) | 2,696 | 2026-10-30 03:36 | 3.9.0 (2026-10-20) | 104 | NOASSERTION (GitHub could not detect; LICENSE not read) | no | 147 | 11 | Dart |
| finanze | [finanze/finanze](https://github.com/finanze/finanze) | 66 | 2026-10-30 18:43 | v0.10.1 (2026-09-28) | 15 | AGPL-3.0 | no | 7 | not counted | Python |
| budgetzero | [budgetzero/budgetzero](https://github.com/budgetzero/budgetzero) | 657 | 2026-10-31 02:11 | v0.1.21 (2021-06-06) | not counted | AGPL-3.0 | no | 75 | not counted | Vue |
| open-finance | [openfinance-app/open-finance](https://github.com/openfinance-app/open-finance) (created 2026-01-21) | 9 | 2026-10-30 08:04 | v0.5.8-beta (2026-10-18) | not counted | NOASSERTION | no | 1 | not counted | Java |
| Aurum | [Zproger/Aurum](https://github.com/Zproger/Aurum) (created 2026-08-16) | 263 | 2026-10-30 07:40 | no release | not counted | NOASSERTION | no | 7 | not counted | TypeScript |

Notes on the table:
- "Open issues" is GitHub's `open_issues_count`, which includes pull requests.
- "Contributors" = number of entries returned by `repos/OWNER/REPO/contributors` (count via pagination), default branch. Not counted = not retrieved.
- "Releases since 2025-10-31" = GitHub releases published in the 12 months to 31 Oct 2026 (paginated `gh api`). High release counts can mean many small patch tags; this is not a quality measure.

Topic discovery (GitHub topic search, sorted by stars, run 31 Oct 2026; topic search only finds repos tagged with the topic, so the list is not exhaustive): [topics/personal-finance](https://github.com/topics/personal-finance), [topics/budgeting](https://github.com/topics/budgeting), [topics/expense-tracker](https://github.com/topics/expense-tracker), [topics/net-worth](https://github.com/topics/net-worth). Further names that surfaced and were not assessed in depth (stars as returned by GitHub search): Volmarg/personal-management-system 4,192 (pushed 2026-10-29); kevinschaich/mintable 1,634 (2026-10-29); Tanq16/ExpenseOwl 1,526 (last push 2025-10-18); RIP-Comm/sossoldi 1,415 (2026-10-20); whisper-money/whisper-money 1,143 (2026-10-29); TheAxelander/OpenBudgeteer 974 (2026-10-27); budgetzero 657 (2026-10-31); hisabi-app/hisabi 460 (2026-09-28); kedder/ofxstatement 368 (last push 2026-08-22, release 0.9.2 on 2024-11-25; GitHub description: converts proprietary bank statements to OFX). Wallos (ellite/Wallos, 8,769 stars, 2026-10-23) is a subscription tracker, not a full engine. Sources: the topic pages above, GitHub search output.

### Inferences
- By releases in the last 12 months, the most active engines are Ghostfolio (155), BeeCount (104), Securo (87), Firefly III (49), Wealthfolio (34), Budget Board (31). Activity is high for Firefly, Securo and Actual alike, but Actual's 16 releases and Sure's 18 are lower in count.
- Maybe Finance (archived) should not be the base of a new build; Sure is the active AGPL continuation (its README says it is based on Maybe but not affiliated with it).

### Gaps
- Release counts not retrieved for Ivy Wallet, Money Manager EX, Cashew, budgetzero, open-finance, Aurum, Fava, Beancount, Kresus (latest release dates for Fava and Kresus not read as GitHub release objects).
- Contributor counts not retrieved for Beancount, finanze, budgetzero, open-finance, Aurum, Cashew, Ivy, MMEX.
- Stars and pushes are GitHub-only; no independent usage numbers found.

## 2. Engine profiles: stack, hosting, API, data model, import

### Takeaway
Firefly III is the only engine here with a documented REST API that covers most of the product, with OAuth2 or personal-access-token auth, and it lists Enable Banking as an import source. Actual Budget has no HTTP API (Node.js client only). Wealthfolio, ezBookkeeping, Securo and WYGIWYH state multi-currency with FX in their READMEs. hledger is a multi-currency double-entry engine with CLI, HTTP and API access, but it is plain text. No candidate README shows a native Monobank or PrivatBank connector.

### Cited Findings

Firefly III ([repo](https://github.com/firefly-iii/firefly-iii), PHP, AGPL-3.0):
- README (raw): "It features a REST JSON API that covers almost every part of Firefly III." Also: "It is completely self-hosted and isolated, and will never contact external servers until you explicitly tell it to." Supports budgets, categories, tags and piggy banks (raw).
- Hosting (raw README): run with Docker; Docker docs at [docs.firefly-iii.org/how-to/firefly-iii/installation/docker](https://docs.firefly-iii.org/how-to/firefly-iii/installation/docker/). Database and RAM minimums: not found.
- API auth (raw, [API docs](https://docs.firefly-iii.org/api/)): OAuth2 authorization-code flow (client created on /profile) or a Personal Access Token sent as bearer token (Options > Profile > OAuth > Personal Access Tokens, per [How to use the API](https://docs.firefly-iii.org/how-to/firefly-iii/features/api/)). The API reference explains currency fields, configuration values and webhooks ([API reference guide](https://docs.firefly-iii.org/references/firefly-iii/api/), linked from the API docs; not opened).
- Import (raw, Data Importer nav on [docs.firefly-iii.org/how-to/data-importer/import/gocardless](https://docs.firefly-iii.org/how-to/data-importer/import/gocardless/)): data providers listed are Basiq, Enable Banking, FinTS, GoCardless, Sophtron, Lunch Flow, Open Banking/HBCI (OBG), SimpleFIN and teller.io; file imports are CSV and CAMT.05x.
- GoCardless entry (raw, same page): "GoCardless is sunsetting this free service and registration is unfortunately closed." (see section 5).
- Double-entry status, FX rate handling and investments coverage: not verified in this session.

Actual Budget ([repo](https://github.com/actualbudget/actual), TypeScript, MIT):
- README (raw): self-hosted via Docker image. Docs: [actualbudget.org/docs/install/docker](https://actualbudget.org/docs/install/docker).
- API ([API docs](https://actualbudget.org/docs/api/), extracted): official Node.js client `@actual-app/api`; "Actual does not expose HTTP endpoints that can be called." `init` needs server URL, server password and budget sync ID; the browser build is marked experimental.
- Bank sync providers ([bank sync docs](https://actualbudget.org/docs/advanced/bank-sync/), extracted): Akahu (New Zealand), Enable Banking (European banks), GoCardless BankAccountData (European banks, "not accepting new accounts"), SimpleFIN Bridge (North American banks), Pluggy.ai (Brazil). Users supply their own API credentials; works only with actual-server.
- Hosting cost: see section 4 (PikaPods).
- Multi-currency, double-entry and FX: not verified in this session.

Ghostfolio ([repo](https://github.com/ghostfolio/ghostfolio), TypeScript, AGPL-3.0):
- Description (GitHub topic search): "Open Source Wealth Management Software. Angular + NestJS + Prisma + Nx + TypeScript."
- README (raw): NestJS backend, PostgreSQL via Prisma, Redis for caching; official Docker images for amd64, arm/v7, arm64; self-hosting FAQ at [ghostfol.io/en/faq/self-hosting](https://ghostfol.io/en/faq/self-hosting).
- Config (raw): optional CoinGecko API keys for market data; no bank connection provider appears in the README.
- Scope: portfolio and wealth tracking. Expense and income tracking, API docs and bank import: not verified.
- Security (search excerpt, not opened): [osv.dev CVE-2026-47127](https://osv.dev/vulnerability/CVE-2026-47127) reports versions before 3.4.0 allowed self-granted Premium. Check the version before any self-hosting.

Wealthfolio ([repo](https://github.com/wealthfolio/wealthfolio), Rust, AGPL-3.0):
- README (raw): "open-source, private portfolio tracker - investments, net worth, spending, and simulations." Multi-currency: "Support for multiple currencies with exchange rate..." Platforms: desktop (Windows, macOS, Linux), iOS, and self-hosted Docker/web.
- Docker docs: [wealthfolio.app/docs/guide/self-hosting/docker](https://wealthfolio.app/docs/guide/self-hosting/docker) (link in README; not opened).
- API, bank import and data model: not verified.

Maybe Finance and Sure ([maybe repo](https://github.com/maybe-finance/maybe), [sure repo](https://github.com/we-promise/sure), Ruby, AGPL-3.0):
- Maybe README (raw): "This repo is no longer maintained. You're free to fork it under the AGPLv3..."; self-host requires PostgreSQL >9.3 (raw).
- Sure README (raw): "Sure is a fully working personal finance app that can be self hosted with Docker"; "Sure can be accessed from a browser, the macOS desktop app, the mobile app, API..."; PostgreSQL >9.3; Render deploy variants "Sure - No AI" and "Sure - Simple AI" (raw). Team statement (raw, truncated): the app had "nearly $1 million" development spend; goal was self-hosting "and eventually launch a hosted v[ersion]". Hosted launch status: not found.
- Sure must keep the AGPL license and a non-affiliation statement (raw README).
- API scope, multi-currency detail, bank sync: not verified.

ezBookkeeping ([repo](https://github.com/mayswind/ezbookkeeping), Go, MIT):
- README (raw): self-hosted; Docker; SQLite, MySQL and PostgreSQL; "Agent Skill and API command-line script tools for AI integration"; "Multi-language and multi-currency support"; "Multiple exchange rate sources with automatic updates"; imports CSV, Excel, OFX, QFX, QIF, IIF, Camt.052, Camt.053, MT940, GnuCash, Firefly III, Beancount and more.
- Bank connection: none listed in the README.
- Docs site (from README): https://ezbookkeeping.mayswind.net (not opened). REST API docs: not verified.

Securo ([repo](https://github.com/securo-finance/securo), Python, AGPL-3.0, created 2026-03-08):
- README (raw): file import (OFX, QIF, CAMT, CSV); bank sync via Pluggy (Brazil), Enable Banking (about 2,500 European PSD2 banks) and SimpleFIN (US and international); "Multi-currency support with automatic FX conversion"; optional self-hosted AI agents with tool use and RAG.
- Hosting (raw): `docker compose up --build`; Linux and macOS via Docker or Podman; Windows via Docker Desktop.
- Enable Banking setup (raw): "Sign up at enablebanking.com, create a Production application, and download its PEM private key."
- PSD2 limit (raw): polling settings mention "PSD2 four-access-per-day limits".
- API, double-entry status, net-worth features: not verified.

WYGIWYH ([repo](https://github.com/eitchtee/WYGIWYH), Python with manage.py commands, AGPL-3.0):
- README (raw): principles-first, no-budget finance tracker; multiple accounts including "banks, wallets, investments"; "Out-of-the-box multi-currency support"; "Automation-ready API"; Docker and docker-compose.
- Demo caveat (raw): demo data is wiped within 24 hours; API, Rules, automatic exchange rates and import/export are disabled in the demo.
- Bank connection: not in README. Monobank: no.

hledger ([repo](https://github.com/hledgerorg/hledger), Haskell, GPL-3.0):
- README (raw): "lightweight, cross platform, multi-currency, double-entry accounting software"; "Scriptable by CLI, HTTP or API"; "A robust, general, well-specified multi-currency accounting engine."
- Storage: plain text journal files (raw examples in README). Hosting: no server needed for CLI; HTTP mode details not read.
- Bank connection: none in README.

Beancount and Fava ([beancount repo](https://github.com/beancount/beancount), [fava repo](https://github.com/beancount/fava)):
- Fava repo (raw): MIT license, Python, PyPI badge; homepage [beancount.github.io/fava](https://beancount.github.io/fava/). Beancount: GPL-2.0, Python.
- Double-entry and API details: not verified in this session. Plain-text based (not verified in-session).

Kresus ([repo](https://github.com/kresusapp/kresus), TypeScript, AGPL-3.0):
- README (raw): "open-source libre self-hosted personal finance manager... track your banking history, check your overall balance."
- Bank connector mechanism and country coverage: not verified.

Cashew ([repo](https://github.com/jameskokoska/Cashew), Dart, GPL-3.0):
- README (raw): Flutter app with Drift SQL and Firebase. Mobile-first app, not a server engine.

Ivy Wallet ([repo](https://github.com/Ivy-Apps/ivy-wallet), Kotlin, GPL-3.0, archived):
- README (raw): Room DB (SQLite ORM); "you are encouraged to fork this repository" under GPL-3.0; a private Telegram community group link (see section 7).
- Archived flag set on GitHub (gh), yet a release dated 2026-10-22 exists. Treat as read-only.

Money Manager EX ([repo](https://github.com/moneymanagerex/moneymanagerex), C++, GPL-2.0):
- README (raw): "Nonproprietary SQLite database with Advanced Encryption Standard (AES)"; built with wxWidgets (gh description). Desktop application; no HTTP API found in README.

Budget Board ([repo](https://github.com/teelur/budget-board), C#, AGPL-3.0):
- README (raw): self-hosted alternative to Mint; "Sync Providers: ... SimpleFIN and LunchFlow"; localized date and number formats; Docker build workflow (badge).
- Coverage of Erste or Ukrainian banks: not found. SimpleFIN is listed by Actual docs as North American banks (extracted).

Paisa ([repo](https://github.com/ananthakumaran/paisa), TypeScript, AGPL-3.0): GitHub description "Paisa - Personal Finance Manager" with demo at paisa.fyi; README not read.

BeeCount ([repo](https://github.com/TNT-Likely/BeeCount), Dart): GitHub description (raw): "Local-first bookkeeping for iOS/Android/Web - Self-hosted cloud + iCloud/WebDAV/S3 sync - AI capture - MCP". License not detected by GitHub (NOASSERTION); LICENSE file not read.

finanze ([repo](https://github.com/finanze/finanze), Python, AGPL-3.0): GitHub description "Self-hosted personal finance & net worth tracker. Aggregate banks, investments, crypto & real estate. Privacy-first." Method used to aggregate banks: not read.

budgetzero ([repo](https://github.com/budgetzero/budgetzero), Vue, AGPL-3.0): GitHub description "Open-source, self-hosted, zero-based budgeting." Latest release 2021-06-06 despite 2026-10-31 push.

open-finance ([repo](https://github.com/openfinance-app/open-finance), Java): GitHub search description "Local-first, self-hosted personal finance manager - assets, budgets, QIF/OFX import, multi-currency, AI assistant (Docker + SQLite/Postgres)". 9 stars, created 2026-01-21, beta release.

### Inferences
- Only Firefly III in this set combines a documented REST API with auth methods (OAuth2 or bearer token) and an import route to Enable Banking. For a Mini App backend this is the least custom glue.
- Actual has a Node.js client, so a Mini App backend would need a small Node wrapper around @actual-app/api to expose endpoints. This is an inference from "does not expose HTTP endpoints".
- Multi-currency is stated in the READMEs of Wealthfolio, ezBookkeeping, Securo, WYGIWYH and hledger; Firefly and Actual mention currency fields or other currency support only indirectly (not verified).

### Gaps
- RAM and database minimums: not found in any README read. Firefly, Actual, Ghostfolio, Sure, ezBookkeeping and WYGIWYH hosting docs were not opened in full.
- API docs not read for: Ghostfolio, Wealthfolio, Sure, ezBookkeeping, Securo, Budget Board, Kresus, Fava/Beancount.
- Data model (double-entry or not, accounts, transfers, budgets, investments) not verified for Actual, Ghostfolio, Securo, Sure, ezBookkeeping, Firefly III (beyond budgets, piggy banks and currency fields), Budget Board, Kresus.
- Import details not verified for Actual (CSV/OFX), Wealthfolio, Sure, ezBookkeeping (bank API absent), WYGIWYH import formats.

## 3. Best-fit shortlist: EUR, UAH, USD; one user; expenses + income + assets

### Takeaway
Shortlist of four: Firefly III (API-first backend with Enable Banking route), Securo (Erste route via Enable Banking, multi-currency with FX, but young), ezBookkeeping (lightweight, MIT, multi-currency with FX sources, file-based imports), and Wealthfolio (multi-currency assets and net worth, investments-first; API unverified). Actual Budget is mature and has an Enable Banking route, but without an HTTP API it needs a wrapper. Each shortlisted engine needs a custom Monobank importer; none has one natively.

### Cited Findings
Fit evidence per requirement:
- Multi-currency with FX: ezBookkeeping ([README](https://github.com/mayswind/ezbookkeeping), raw: multi-currency; multiple exchange rate sources with automatic updates); Securo ([README](https://github.com/securo-finance/securo), raw: multi-currency with automatic FX conversion); WYGIWYH ([README](https://github.com/eitchtee/WYGIWYH), raw: out-of-the-box multi-currency, automatic exchange rates in the feature list); Wealthfolio ([README](https://github.com/wealthfolio/wealthfolio), raw: multiple currencies with exchange rates); hledger ([README](https://github.com/hledgerorg/hledger), raw: multi-currency engine). Firefly: currency fields documented in the API reference ([API docs](https://docs.firefly-iii.org/api/)); FX handling not verified.
- API for a Mini App backend: Firefly III (documented REST API, OAuth2 or bearer token, [API docs](https://docs.firefly-iii.org/api/)); WYGIWYH ("Automation-ready API", README, demo disables API); ezBookkeeping (API command-line tools, README); hledger (HTTP/API, README); Actual (Node.js client only, [API docs](https://actualbudget.org/docs/api/), extracted).
- Erste Bank route (George): Enable Banking is listed by Actual docs (extracted), by Firefly docs (raw nav) and in the Securo README (raw). Enable Banking lists Erste Bank (Sparkasse) as a top Austrian ASPSP ([Enable Banking AT](https://enablebanking.com/docs/markets/at/), extracted). See section 6.
- Ukrainian route (Monobank): no native connector in Firefly, Actual, Securo, Budget Board or ezBookkeeping READMEs/docs read. Monobank personal API exists ([api.monobank.ua docs](https://api.monobank.ua/docs/), raw). See section 6.
- Assets and net worth: Wealthfolio README (raw: "investments, net worth, spending, and simulations"); Firefly (asset accounts; piggy banks in README); WYGIWYH (multiple accounts incl. investments, README); finanze (GitHub description: net worth, banks, investments, crypto; not read in depth).
- Licenses: Firefly AGPL-3.0; Securo AGPL-3.0; Wealthfolio AGPL-3.0; ezBookkeeping MIT (repo license field).
- Maturity: see section 1 table.

Shortlist and reasons:
1. Firefly III (AGPL-3.0, 25,046 stars, pushed 2026-10-31, release v6.7.9 on 2026-10-11, 49 releases in 12 months, 180 contributors). Best fit for a Mini App backend: documented REST API with OAuth2 or bearer token, multi-currency accounts, budgets, piggy banks, Enable Banking import route (raw nav). Gap: no Monobank route; double-entry status and FX handling not verified.
2. Securo (AGPL-3.0, 4,151 stars, created 2026-03-08, release v0.16.6 on 2026-10-26, 87 releases in 12 months, 118 contributors, 284 open issues). Best bank-sync coverage for Erste among the candidates (Enable Banking, raw README) plus automatic FX. Risk: about 7 months old; API, data model and maturity of the finance logic not verified.
3. ezBookkeeping (MIT, 5,893 stars, pushed 2026-10-29, release v2.1.1 on 2026-10-23, 13 releases in 12 months, 46 contributors, 20 open issues). Most permissive license and strong multi-currency with exchange-rate sources (raw README); many file import formats including Firefly III and Beancount (raw). No bank connection, so Erste data would come from George exports (format not verified) or a custom Enable Banking script.
4. Wealthfolio (AGPL-3.0, 9,294 stars, pushed 2026-10-30, release v3.11.0 on 2026-10-23, 34 releases in 12 months, 96 contributors, 539 open issues). Best for the assets and net-worth layer with multi-currency FX (raw README). Investments-first; expense tracking exists per the README tagline but depth and API not verified.

Also considered (not in the top 4):
- Actual Budget: strongest community (29,877 stars, 465 contributors, MIT, pushed 2026-10-30, release v26.10.0 on 2026-10-02) and an Enable Banking route; excluded for the backend because it exposes no HTTP endpoints (extracted, [API docs](https://actualbudget.org/docs/api/)). A Node wrapper would fix this but adds a layer.
- Ghostfolio: 155 releases in 12 months, but portfolio-first; expense/income features and API not verified; Premium cloud offering exists (section 4).
- hledger or Beancount + Fava: double-entry plain-text accounting with strong multi-currency (hledger raw README). Excluded for a Mini App backend because data lives in text journals; a good choice only if Misha wants accounting correctness and accepts building the API layer. Beancount double-entry status: not verified in session.
- Sure: active AGPL successor to Maybe (18 releases in 12 months, 432 contributors); its README lists an API, but features and API details were not read. Worth a follow-up read as a fifth option.
- Budget Board: SimpleFIN and LunchFlow providers only (raw README); SimpleFIN covers North American banks (extracted, Actual docs). Not an Erste route.
- Kresus, Money Manager EX, Cashew, Ivy Wallet: desktop or mobile apps, or archived, or bank connector not verified; not recommended as an engine.
- Maybe Finance: archived since 2025-07-24. Do not build on it.

Licence note (inference, not legal advice): AGPL-3.0 obligations trigger when modified versions are offered to other users over a network. A private Mini App used only by Misha creates no such obligation. If the solution is later sold to clients, any modified Firefly, Securo or Wealthfolio code would need AGPL source publication. Calling an unmodified engine's HTTP API from a separate app is a different case; confirm before selling. Source for AGPL text: [gnu.org AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html) (linked from the Firefly README, raw).

### Inferences
- For one user with EUR, UAH and USD, the shortlist depends on two things: a reliable Erste feed (Enable Banking) and a custom Monobank script. Engines with a documented API and a clean FX model reduce custom glue; Firefly is the strongest on API, Securo on Erste feed, ezBookkeeping on FX and license, Wealthfolio on net worth.
- The engine choice does not change the Monobank effort: all four need a custom importer, because none has one natively (verified for Firefly, Securo, Budget Board, Actual by their documented provider lists; ezBookkeeping and WYGIWYH have no bank connector in their READMEs).

### Gaps
- Hands-on test of each engine (create user, add EUR/UAH/USD accounts, FX rate) not done. This is a research pass from docs and READMEs only.
- API depth for Securo, ezBookkeeping, Wealthfolio, Sure not verified.
- Net-worth and investment support for Firefly and Securo not verified.

## 4. Hosted versions and prices

### Takeaway
Only one hosted price is confirmed from an official page: Ghostfolio Premium at USD 48 per year. Actual Budget via PikaPods is said to be "a little more than $1 per month" in an Actual deploy-preview page (may be stale). Enable Banking production pricing is not public. Managed hosting for Firefly, Securo, Sure and ezBookkeeping: not found.

### Cited Findings
- Ghostfolio Premium: "USD 48 per year" with a "Premium" plan on the official pricing page ([ghostfol.io/en/pricing](https://ghostfol.io/en/pricing), raw). Page text: "Our official Ghostfolio Premium cloud offering is the easiest way to get started." Third-party listings (search excerpts, not opened) gave USD 40/yr and "up to $40 per month"; discarded as unverified.
- Actual Budget on PikaPods: "a little more than $1 per month" (search excerpt of [Actual PikaPods docs, deploy preview](https://deploy-preview-390.www.actualbudget.org/docs/install/pikapods); the page itself says the price may have changed). PikaPods' own price page not retrieved.
- Firefly III on PikaPods: README says the project is sponsored by "Hostinger and PikaPods" with a kickback program (raw README, [github.com/firefly-iii/firefly-iii](https://github.com/firefly-iii/firefly-iii)); a pod page exists at [pikapods.com/pods?run=firefly-iii](https://www.pikapods.com/pods?run=firefly-iii) (not opened). Price: not found.
- Actual managed hosting by the Actual team: not found.
- Enable Banking: official pricing page path /pricing returned 404 and /pricing/ returned no matching lines (reader proxy). Search excerpts (third-party, not opened): free sandbox and free production for accounts you link yourself ("Restricted Production", [openbankingtracker free APIs guide](https://www.openbankingtracker.com/guides/free-open-banking-apis)); paid production volume-based with a minimum monthly invoice that is not public.
- GoCardless Bank Account Data: the search excerpt of GoCardless pricing (not opened) lists a free plan of 50 requisitions per month and pay-as-you-go at £100 / €100 monthly plus £0.25 / €0.25 per requisition. This conflicts with the closure evidence in section 5. Not used.
- Monobank personal API: no fee stated on the docs page ([api.monobank.ua/docs](https://api.monobank.ua/docs/), raw). Not a price claim.
- Securo: a homepage exists ([usesecuro.com](https://usesecuro.com/)); hosted offer not checked.
- Sure: README says the team plans to "eventually launch a hosted v[ersion]" (raw, truncated). Hosted price: not found.

### Inferences
- The only hosted price usable as a comparison point is Ghostfolio (USD 48/year), and it is portfolio-focused.
- For a personal setup, self-hosting on a small VPS is the realistic path; hosting cost per engine is not established by sources here.

### Gaps
- Official Enable Banking production pricing: not found.
- PikaPods exact current prices for Actual and Firefly: not verified.
- Managed hosting prices for Firefly III, Securo, Sure, ezBookkeeping, Wealthfolio: not found.
- VPS sizing (RAM, CPU) per engine: not found.

## 5. GoCardless Bank Account Data status (ex-Nordigen)

### Takeaway
Two integrators' docs say GoCardless closed free Bank Account Data sign-ups in July 2025 (Actual dates it to "July 2025 onwards"; Firefly says "registration is unfortunately closed"). No GoCardless page found states the closure or a date, and GoCardless's own pages are inconclusive. Treat GoCardless as unavailable for a new account and use Enable Banking for Erste.

### Cited Findings
- Actual Budget GoCardless docs (extracted from [actualbudget.org/docs/advanced/bank-sync/gocardless](https://actualbudget.org/docs/advanced/bank-sync/gocardless/)): "From July 2025 onwards, GoCardless has stopped accepting new Bank Account Data accounts." Existing users "should continue to work"; the sign-up steps on the page are outdated. Undated page.
- Actual bank-sync provider list (extracted, [bank sync docs](https://actualbudget.org/docs/advanced/bank-sync/)): "GoCardless BankAccountData (European Banks, not accepting new accounts)".
- Firefly III GoCardless docs (raw, [docs.firefly-iii.org/how-to/data-importer/import/gocardless](https://docs.firefly-iii.org/how-to/data-importer/import/gocardless/)): "GoCardless is sunsetting this free service and registration is unfortunately closed." Page undated; also says "GoCardless is a commercial organisation. They may revoke your access or charge money at any moment."
- GoCardless announcement page (extracted, [gocardless.com/bank-account-data/announcement](https://gocardless.com/bank-account-data/announcement)): the page is titled "Bank Account Data legacy wind down" and says "The product you are trying to access was discontinued on the 18th of December 2023 and is no longer available for use." It then points to the current Bank Account Data page and to sales ([contact-sales link](https://gocardless.com/contact-sales?interest=bankaccountdata)). It does not mention Nordigen, sign-ups or existing users. Unclear whether this legacy product is the free Nordigen-era tier.
- GoCardless Bank Account Data page (extracted, [gocardless.com/bank-account-data](https://gocardless.com/bank-account-data/)): has a "Sign up" button; no pricing tiers shown; no closure statement; "Pricing" link points to gocardless.com/pricing.
- GoCardless developer docs (extracted, now at [docs.gocardless.com/bank-account-data/overview](https://docs.gocardless.com/bank-account-data/overview); developer.gocardless.com redirects there): "Account verification is only offered to paying customers"; no closure statement; no date shown.
- Search excerpts (not opened): GoCardless' developer docs described portal sign-up as the route to user secrets, with no closure mentioned.

### Inferences
- Most likely status: closed for new free sign-ups since July 2025, with existing users kept working (two integrator docs agree; GoCardless' own pages do not confirm). Paid access may still exist; not verified.
- The GoCardless announcement page does not mention the Nordigen free tier, so it cannot be used as the official statement for this question.

### Gaps
- No official GoCardless statement naming the closure date or the free-tier end was found.
- GoCardless pricing page (gocardless.com/pricing) returned "not found" per one search excerpt; not verified directly.
- Whether an enterprise or paid Bank Account Data sign-up is open in October 2026: not found.
- Recommended check (not done): ask GoCardless sales via the contact link above, and read the Bank Account Data portal sign-up screen (do not create an account without the user's approval).

## 6. Erste Bank Austria (George) and Ukrainian banks (Monobank, PrivatBank)

### Takeaway
Erste: Enable Banking is the live PSD2 route; it names Erste Bank (Sparkasse) first among Austria's main banks and is already supported by Actual, Firefly and Securo. Its public Austrian sandbox covers only Oberbank. Monobank: official personal API with rate limits; no candidate engine has it natively. PrivatBank: no personal API found; business-only sources found.

### Cited Findings

Erste Bank (George):
- Enable Banking, Austria market page (extracted, [enablebanking.com/docs/markets/at](https://enablebanking.com/docs/markets/at/)): the four major ASPSPs "in order of significance" are Erste Bank (Sparkasse), Raiffeisen Bank, BAWAG (incl. easybank) and UniCredit Bank Austria. Erste uses the "s Identity" app for SCA; the George user ID must be entered. Only Oberbank has a sandbox. No mention of AISP approval or personal-use pricing on that page.
- Enable Banking Europe scale (search excerpt, [changelog July 2025](https://enablebanking.com/blog/2025/08/22/changelog-july-2025)): coverage over 2,500 ASPSPs. Erste-specific listing not confirmed on the live list (not opened).
- Enable Banking AISP approval (search excerpt, [changelog Nov 2022](https://enablebanking.com/blog/2022/12/07/changelog-november-2022)): apps relying on Enable's own AISP registration need approval before going live. Relevance to a personal setup unverified.
- Securo README (raw): Enable Banking "for ~2500 European PSD2 banks"; production application and PEM key required; PSD2 four-access-per-day limits in polling.
- Actual docs (extracted): Enable Banking (European banks) is a provider.
- Firefly docs (raw nav): "Import from Enable Banking" tutorial at [docs.firefly-iii.org/tutorials/data-importer/eb](https://docs.firefly-iii.org/tutorials/data-importer/eb/).
- Sparkasse open-banking FAQ (search excerpts only, regional Sparkasse pages, not Erste Bank Oesterreich; [example](https://www.sparkasse.at/noe/open-banking/public)): third-party access only with the customer's explicit consent; account must be online-accessible via George or Business Banking (one page names Telebanking Pro instead); consent renewal every 180 calendar days; each payment still needs customer approval. Sources conflict on access channel.
- Erste Group developer portal ([developers.erstegroup.com](https://developers.erstegroup.com), search link, not opened): search summary says a sandbox account-information endpoint exists and contact is openbanking@erstebank.at. Not verified.

Monobank (Ukraine):
- Official docs ([api.monobank.ua/docs](https://api.monobank.ua/docs/), raw, Ukrainian): the API gives statements and the state of personal accounts; access requires signing in to the personal cabinet at api.monobank.ua and getting "a token for personal use".
- Limits (raw): client info: at most once per 60 seconds. Statement: at most 31 days + 1 hour (2,682,000 seconds) per request, once per 60 seconds. Webhook: events are POSTed as `StatementItem`; the service must answer HTTP 200 within 5 seconds; retries after 60 and 600 seconds; disabled after the third failure.
- Currency rates (raw): public rates endpoint, cached and updated at most once per 5 minutes.
- Corporate (service-provider) API (raw): required for services that offer the account data to clients through a central connection; optional for personal or family use where client data does not pass through your servers, and for personal-use libraries or apps.
- Age (raw): not available to clients under 16; children's accounts through the parent's account.
- No native Monobank provider in: Firefly data-provider list (raw nav), Actual bank-sync list (extracted), Securo README (raw), Budget Board README (raw). One search for a Monobank importer for Firefly III, ezBookkeeping or Actual found none (search summary); ezBookkeeping and Actual importers not searched.

PrivatBank (Ukraine):
- Fintable (search excerpt, [fintable PrivatBank page](https://fintable.io/coverage/banks/Ukraine/21389549_privatbank-business-fintable-direct-api)): PrivatBank connection is for the business product ("Приват24 для бізнесу").
- Buxfer (search excerpt, [buxfer PrivatBank page](https://content.buxfer.com/banks/62582/ПриватБанк-api-(ua)-online-money-management-software)): lists a "ПриватБанк API (UA)" sync; whether it covers personal accounts is not stated.
- 1C tool page from 2017 (search excerpt, [infostart.ru](https://infostart.ru/1c/tools/650664)): a personal-customer tool that requests card balance via api.privatbank.ua. Old; scope limited to balance.
- api.privatbank.ua (reader proxy): keyword grep for personal or statement terms returned no lines; not conclusive.
- Verdict: personal PrivatBank API for transaction history: not found.

### Inferences
- Erste: an Enable Banking production application with a personal account link is the only route found that three candidate engines already support. Its personal-use cost and approval steps are unverified; check Enable Banking directly.
- Monobank: the personal token and statement endpoint are enough for a single-user backend (the docs say corporate API is optional for personal use with no client data on your servers). Build a small Monobank importer that writes to the chosen engine's API. Not legal advice; a personal-use reading of the Monobank text.
- PrivatBank: plan for manual export or a separate import until a personal API is confirmed.

### Gaps
- George export formats (CSV, MT940, camt) for personal accounts: not verified.
- Erste live listing on Enable Banking (production coverage for consumer accounts): not confirmed.
- Enable Banking production pricing and approval for a personal linked account: not found on Enable's own pages.
- Monobank importers for Firefly III, ezBookkeeping, Actual, Securo: not found (only Firefly searched).
- PrivatBank consumer transaction export or API: not found.

## 7. Telegram mentions (note only, bridges excluded)

### Takeaway
No official Telegram bot or integration found in the candidate READMEs read. The only Telegram reference is a community group link in the Ivy Wallet README (archived app).

### Cited Findings
- Ivy Wallet README (raw): links a private Telegram community group ("Join our private Telegram community"); a community chat, not an integration. [github.com/Ivy-Apps/ivy-wallet](https://github.com/Ivy-Apps/ivy-wallet).
- The other READMEs were scanned with keyword grep (first 14 matching lines each; Firefly, Actual, Ghostfolio, Wealthfolio, Sure, Maybe, ezBookkeeping, Kresus, Cashew, MMEX, Budget Board, Securo, WYGIWYH, Fava, hledger). No Telegram integration line appeared.

### Inferences
- A Telegram Mini App would need its own bot or front end; none of these engines offers one out of the box, per these READMEs.

### Gaps
- Full READMEs and docs sites not read for Telegram mentions (scan was keyword-based and partial). BeeCount, Securo's docs and Budget Board docs not scanned for Telegram.

## Source and verification summary
- GitHub numbers: `gh api` and `gh search repos` on 2026-10-31 (UTC).
- Raw page reads: Firefly III API docs (auth methods), Firefly GoCardless how-to (closure sentence and data-provider nav), Ghostfolio pricing page (USD 48/year), Monobank API docs (token and limits), GitHub READMEs of the candidates.
- Extracted via WebFetch summarizer (re-check before quoting verbatim): Actual API and bank-sync docs, Actual GoCardless docs, GoCardless announcement and Bank Account Data pages, GoCardless developer docs, Enable Banking Austria page.
- Search excerpts only (pages not opened): Sparkasse FAQ, Enable Banking changelog and third-party pricing guides, Fintable and Buxfer PrivatBank pages, Ghostfolio CVE, PikaPods Actual deploy-preview page.
- Not found: RAM minimums, Firefly/Securo/Sure/ezBookkeeping/Wealthfolio API depth, double-entry status for most engines, official GoCardless closure date, Enable Banking official pricing, PrivatBank personal API, Monobank importers outside Firefly search.
