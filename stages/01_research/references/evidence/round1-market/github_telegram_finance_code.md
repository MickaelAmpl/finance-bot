# Telegram personal-finance code on GitHub and GitLab: fork and study candidates (snapshot 2026-10-31)

Method and conventions:
- GitHub figures: GitHub REST API `repos/OWNER/REPO` (plus `contributors`, `releases/latest`, `contents`), read 2026-10-31. The linked repo is the source for its row.
- npm: registry.npmjs.org (latest tag, `time` field, deprecation field) and api.npmjs.org weekly downloads for 2026-10-23 to 2026-10-29.
- PyPI: pypi.org JSON API. GitLab: unauthenticated public project search (public projects only).
- "Stale" = no push in 12+ months, i.e. last push before 2025-10-31. Days since last push are computed from 2026-10-31.
- Contributor counts are capped at 100 by the API. "Root" = top-level file listing only; test folders inside subfolders were not checked.
- Nothing cloned, downloaded or run. READMEs and search summaries were read as data only. No credentials or `.env` contents were read.
- Search coverage: about 45 GitHub repo-search queries (Mini App, bot, bridge, LLM/voice/receipt, org listing, topic search). GitHub search hit its 30 requests/min limit once; those queries were re-run after reset. Queries that show no rows returned zero results. GitLab: 2 public API queries. Web: 3 WebSearch and 2 WebFetch calls. Habr and dev.to: no Habr results returned by search; dev.to not searched.

---

## Key question 1: Open-source Telegram Mini Apps for personal finance (expenses, income, budget, net worth)

### Takeaway
Real open-source finance Mini Apps are rare and low-adoption: every one found has 0 stars, 1-2 contributors, and no GitHub release. Only one has a broad feature set (xetus476/sofiy_qwen: expenses, income, goals, budget plan vs actual, analytics) and it has no license. The only MIT finance-specific Mini App code found is krybybit/finance-tracker-backend, a backend with thin docs. No open-source net-worth Mini App was found.

### Cited Findings

Mini App finance repos (GitHub API, 2026-10-31):

| Repo | Stars | Last push (days ago) | License | Stack (from README or root files) | Contributors | Declared homepage (not opened) | Notes |
|---|---|---|---|---|---|---|---|
| [xetus476/sofiy_qwen](https://github.com/xetus476/sofiy_qwen) | 0 | 2026-10-03 (28) | none | React 18, TypeScript, Vite, Tailwind, Recharts, Framer Motion, React Router v6, Supabase (PostgreSQL), "Telegram Web App API" (README) | 2 | https://sofiy-qwen.vercel.app | README feature list: expenses by category, income, goals, budget plan vs fact, analytics charts. Root has `.env` and `.env.example`; `.env` contents not read. Root also holds many AI-generated setup docs (DEPLOYMENT.md, FIX_EDGE_FUNCTION.md, REAL_VERSION_SETUP.md). No tests folder at root. |
| [krybybit/finance-tracker-backend](https://github.com/krybybit/finance-tracker-backend) | 0 | 2026-04-16 (198) | MIT | Python (requirements.txt), Dockerfile, docker-compose.yml; root also has a folder named `fronted` | 1 | https://finance-tracker-weld-theta.vercel.app | README is a title and one line: "Backend для Telegram Mini App Finance Tracker". Framework not stated in README. No tests folder at root. |
| [AdoniasMulugeta/quicktrack-expenses-mini-app](https://github.com/AdoniasMulugeta/quicktrack-expenses-mini-app) | 0 | 2026-02-13 (260) | none | Vanilla HTML/CSS/JS; repo description: IndexedDB and Telegram CloudStorage sync; `api/` folder; vercel.json | 1 | none | Expense tracker, no framework. Smallest stack of the group. No tests at root. |
| [zhandos717/tgfinance](https://github.com/zhandos717/tgfinance) | 0 | 2026-03-15 (230) | none | HTML frontend; Go backend (go.mod, cmd/, internal/); Makefile; deploy/; docs/ | 1 | none | Description: "finance & task tracker with ZeroClaw integration". Mixes finance and tasks. |
| [Nati7396/fintrack-birr](https://github.com/Nati7396/fintrack-birr) | 0 | 2026-06-01 (152) | none | TypeScript pnpm workspace (artifacts/, lib/, scripts/); replit.md | 1 | none | Description: personal finance tracker in Ethiopian Birr. Replit-style project layout. |

Other finance-tool repos found in search, not verified via API:
- [tvolezka-ux/frontend](https://github.com/tvolezka-ux/frontend): description "telegram finance mini app", 0 stars, search row shows last push 2025-11-06. Not inspected.
- [Oghma/Sparagne](https://github.com/Oghma/Sparagne): Rust budget tracker with a Telegram bot front end, early alpha, not a Mini App (WebSearch summary).
- [Oghma/hodlTracker](https://github.com/Oghma/hodlTracker): bot plus server, early alpha (WebSearch summary).
- [ymdatta/DollarBot](https://github.com/ymdatta/DollarBot): MIT, multi-currency balance and threshold alerts, bot not Mini App (WebSearch summary).
- [xpenser (hunted.space)](https://www.hunted.space/dashboard/xpenser-2): search summary says open source, self-hostable, Telegram workflows, API and MCP; no repo link found. Unverified.
- [Kopilo (Indie Hackers)](https://www.indiehackers.com/product/kopilo): described as a premium Telegram Mini App for personal and shared finance, 7-day trial. Appears closed-source per search summary. Not verified.
- [TeleExpense (Product Hunt)](https://www.producthunt.com/p/teleexpense-tracker/teleexpense-tracker-2): commercial, stores data in Google Sheets (search summary).

Topic and keyword searches: `telegram mini app expense`, `telegram mini app finance`, `telegram webapp budget`, `twa expense tracker`, `telegram mini app budget tracker`, `telegram mini app personal finance`, `telegram miniapp money tracker`, `telegram mini app wallet tracker`, `telegram web app expenses react`, `tma finance tracker`, `telegram finance mini app`, `telegram mini app expenses`, and `--topic telegram-mini-app` (top 60 by stars). Most returned zero finance rows. The topic list is dominated by games, bots and SDK tooling.

GitLab (unauthenticated public project search, 2026-10-31):
- Query "telegram expense" returned 7 public projects, all bots, 0 stars: kishikai/grocerbender_bot (last activity 2026-03-29), wonderful_python/financial-assistant (2023-03-26), tankruslan/telegrammoneysaverbot (2021-04-06), jiserra/gastos-telegram-bot (2021-02-08), mixa2130/tg_finance_bot (2021-02-23), georgemarkosian/emilia-expenses-bot (2020-11-29), categulario/walletbot (2019-01-04). Source: https://gitlab.com/api/v4/projects?search=telegram%20expense&visibility=public&order_by=star_count&sort=desc&per_page=10
- Query "telegram mini app finance" returned no public results. Source: https://gitlab.com/api/v4/projects?search=telegram%20mini%20app%20finance&visibility=public&order_by=star_count&sort=desc&per_page=10
- GitLab: no Mini App finance project found.

### Inferences
- sofiy_qwen is the best feature reference for a finance Mini App UI, but without a license GitHub's default terms grant no reuse rights. Reading it for ideas is fine; copying code needs the author's permission. Inference, not verified against GitHub's licensing guide.
- Before anyone works in sofiy_qwen, the committed `.env` must be checked for secrets by someone who can read it safely. Do not paste its contents into chat.
- krybybit/finance-tracker-backend is the only MIT finance-specific Mini App code found, but its README is one line. The code has to be read before it is trusted.
- None of the five has a root-level tests folder, and none has a GitHub release. Quality signals are weak across the board.

### Gaps
- No open-source net-worth Mini App found. Queries "telegram bot net worth" and "telegram mini app budget tracker" returned zero repo rows.
- No Mini App was found with EUR, UAH or PrivatBank/Erste support. Currency and bank support was not checked in any repo, and no search for bank import repos was run.
- Habr and dev.to articles were not found through search. No article-linked repos verified.
- tvolezka-ux/frontend and the WebSearch-only tools (Sparagne, hodlTracker, DollarBot, xpenser, Kopilo) were not verified through the API.

---

## Key question 2: Open-source Telegram expense bots (Python, Node, Go), including LLM, voice and receipt-photo bots

### Takeaway
Bots outnumber Mini Apps by a wide margin, but nearly all have 0-13 stars. Active LLM or voice bots: miguel-bm/firefly-iii-telegram-bot (MIT, pushed 2026-09-13; natural-language and voice input per README), smkbdh/finance-ai-buddah-bot (AI and voice per description, 2 stars, no license), and alhajbaig/Expense-Tracker-Telegram-bot (AI natural language per description, no license). The only receipt-scanning bot found explicitly says "No LLMs": bbharathbala/actual-budget-telegram-bot. No open-source receipt-photo LLM bot with real adoption was found.

### Cited Findings

Active bots (GitHub API, 2026-10-31):

| Repo | Stars | Last push (days ago) | License | Language and stack | Contributors | What it does (source) |
|---|---|---|---|---|---|---|
| [Ythosa/minuki](https://github.com/Ythosa/minuki) | 13 | 2026-10-22 (9) | Apache-2.0 | Python; Dockerfile, Makefile, createdb.sql, server.py | 3 | "Telegram Bot for Tracking Expenses" (description). Categories module. No LLM visible in root. |
| [apuignav/expense-bot](https://github.com/apuignav/expense-bot) | 1 | 2026-10-06 (25) | none per API; no LICENSE file in root | Python; setup.py, Dockerfile, compose.yml, tests/ | 2 | "Telegram bot for expense tracking" (description). Conflict: a WebSearch summary says BSD 3-Clause, but the API reports no license. Treat as unlicensed until checked. |
| [miguel-bm/firefly-iii-telegram-bot](https://github.com/miguel-bm/firefly-iii-telegram-bot) | 0 | 2026-09-13 (48) | MIT | TypeScript; Cloudflare Workers (wrangler.toml); pnpm; vitest.config.ts; `webapp/` (Vite, React, index.html) | 2 | README: natural-language entry ("15€ at Mercadona for groceries"), voice notes transcribed and processed, smart categorization, charts, edit and delete, Firefly III API. LLM provider not named in README head. Whether `webapp/` is a Mini App was not checked. |
| [smkbdh/finance-ai-buddah-bot](https://github.com/smkbdh/finance-ai-buddah-bot) | 2 | 2026-03-26 (219) | none | Python; Dockerfile, fly.toml, bot/, config.py | 1 | Description: "AI-powered personal finance Telegram bot — expense tracking, multi-currency (THB/RUB/USD/USDT), voice input". No EUR or UAH in description. |
| [alhajbaig/Expense-Tracker-Telegram-bot](https://github.com/alhajbaig/Expense-Tracker-Telegram-bot) | 1 | 2026-07-05 (118) | none | Python; SQLite (database.py), export.py, visualization.py, parser.py | 1 | Description: "AI-powered expense tracker that understands natural language, stores expenses in SQLite". |
| [arsalan-19/ai-expense-tracker-telegram-v1](https://github.com/arsalan-19/ai-expense-tracker-telegram-v1) | 1 | 2026-05-01 (183) | none | Root holds only README.md | 1 | Description: "Voice-first expense tracker". No code visible at root, so likely incomplete. Not inspected further. |
| [KidCoderT/beancounter](https://github.com/KidCoderT/beancounter) | 0 | 2026-08-08 (84) | none | Python; uv.lock; Alembic migrations; Dockerfile; tests/; website/; futureplan.md | 1 | README: "A Telegram bot that tracks your spending in the time it takes to type 'purse 5.2'." Homepage: https://beancounter-gamma.vercel.app. A WebSearch summary (unverified) says it has a Mini App at `/app`. Beancount as the ledger engine not confirmed. |
| [botlabz/telegram-bot-expense-tracker](https://github.com/botlabz/telegram-bot-expense-tracker) | 0 | 2026-08-21 (71) | MIT | JavaScript; Cloudflare Worker (worker.js, wrangler.toml); README in English and Persian | 1 | Description: records personal or business expenses, categorizes them, daily, weekly and monthly summaries. No LLM mentioned. |
| [ceelikonur/jarvis-home](https://github.com/ceelikonur/jarvis-home) | 0 | 2026-07-01 (122) | MIT | JavaScript; src/, test/, config/, web/ | 1 | Description: self-hosted home assistant with "Telegram bot + budget manager + web dashboard in a single Node" app. Has its own budget engine; not a bridge. |
| [justpiple/expense-tracker-telegram-bot](https://github.com/justpiple/expense-tracker-telegram-bot) | 5 | 2026-02-14 (259) | MIT | TypeScript on Bun (bun.lock); Dockerfile | 1 | Description: records expenses and saves them to Notion automatically. See Key question 3. |

Stale or older bots (over 12 months without a push):
- [haaris272k/ExpenseGenie](https://github.com/haaris272k/ExpenseGenie): 4 stars, MIT, Python, last push 2023-09-10. Chat commands, PDF export (WebSearch summary).
- [kaiimran/Expenses-Tracker-Telegram-Bot](https://github.com/kaiimran/Expenses-Tracker-Telegram-Bot): 13 stars, last push 2020-05-24, Google Sheets (search row).
- [R3D4NG3L/PersonalExpenseReport](https://github.com/R3D4NG3L/PersonalExpenseReport): 79 stars, Apache-2.0, JavaScript (Google Apps Script), 22 forks, last push 2022-03-24. Google Sheets plus Telegram bot.
- [vinoajay/telegram-voice-expense-bot](https://github.com/vinoajay/telegram-voice-expense-bot): 0 stars, last push 2025-07-03 (search row).

Node and TypeScript bot frameworks, npm (2026-10-23 to 2026-10-29 downloads):
- [grammy](https://www.npmjs.com/package/grammy): latest 1.46.0, published 2026-08-26, 3,924,629 weekly downloads. Sources: https://registry.npmjs.org/grammy and https://api.npmjs.org/downloads/point/last-week/grammy
- [telegraf](https://www.npmjs.com/package/telegraf): latest 4.16.3, npm `time` for that version 2024-02-29 (stale by the 12-month rule), 326,194 weekly downloads. Source: https://registry.npmjs.org/telegraf

Python bot frameworks, PyPI:
- [aiogram](https://pypi.org/project/aiogram/): latest 3.31.0, uploaded 2026-08-26.
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/): latest 22.8, uploaded 2026-06-12.

Go: the only Go expense bot found is mesuutt/ledger-cli-telegram-bot (see Key question 3, stale).

### Inferences
- The three AI or voice bots (miguel-bm, smkbdh, alhajbaig) are the closest references for "free-text and voice in, structured expense out". None has more than 2 stars, so quality must be checked in code.
- grammY has about 12 times the weekly downloads of telegraf (3.92M vs 0.33M) and a 2026 publish, so it is the safer Node default. Inference from download counts and publish dates only.
- Receipt-photo parsing is effectively absent from open source in this sample. Only bbharathbala has receipt handling, and it explicitly avoids LLMs.

### Gaps
- No receipt-photo LLM bot found. These queries returned zero repo rows: "telegram receipt ocr expenses", "telegram expense bot openai", "telegram expense bot gemini", "personal finance telegram bot llm", "expense tracker telegram llm".
- The LLM provider used by miguel-bm, smkbdh and alhajbaig was not confirmed. Only README heads and descriptions were read.
- Test coverage was not checked for most bots, beyond the root listing.

---

## Key question 3: Bridges from Telegram to existing finance engines (Firefly III, Actual Budget, Beancount, ledger, Google Sheets, Notion)

### Takeaway
Firefly III has the most active bridges: cyxou/firefly-iii-telegram-bot (70 stars, GPL-3.0, pushed 2026-10-23, v3.0.0 released the same day). Actual Budget has three repos with 2025-2026 pushes, none above 18 stars. Beancount and ledger bridges are small and mostly stale. Google Sheets has one popular bridge (79 stars) but no push since 2022. hledger, YNAB and Monarch bridges returned zero rows. All bridges are bots, not Mini Apps.

### Cited Findings

| Repo | Engine | Stars | Last push (days ago) | License | Stack and files | Contributors | What it does (source) |
|---|---|---|---|---|---|---|---|
| [cyxou/firefly-iii-telegram-bot](https://github.com/cyxou/firefly-iii-telegram-bot) | Firefly III | 70 | 2026-10-23 (8) | GPL-3.0 | TypeScript; release v3.0.0 published 2026-10-23; 13 forks; root: AGENTS.md, CLAUDE.md, .openapi-generator-config.yaml, Earthfile, Makefile, .github/ | 6 | "Firefly III Telegram bot for faster interaction with the service" (description). |
| [miguel-bm/firefly-iii-telegram-bot](https://github.com/miguel-bm/firefly-iii-telegram-bot) | Firefly III | 0 | 2026-09-13 (48) | MIT | TypeScript, Cloudflare Workers, vitest | 2 | See Key question 2. Connects to the Firefly III API directly; the Data Importer is not needed (README). |
| [may-cat/firefly-iii-telegram-bot](https://github.com/may-cat/firefly-iii-telegram-bot) | Firefly III | 27 | 2020-02-13 (stale) | GPL-3.0 | n/a | 5 | Stale. |
| [streusselhirni/firefly-iii-telegram-bot](https://github.com/streusselhirni/firefly-iii-telegram-bot) | Firefly III | 0 | 2019-01-02 (stale) | MIT | n/a | 0 | Stale. |
| [bbharathbala/actual-budget-telegram-bot](https://github.com/bbharathbala/actual-budget-telegram-bot) | Actual Budget | 18 | 2026-06-01 (152) | MIT | JavaScript; Dockerfile, fly.toml, parser.js, receipt.js | 1 | Description: "Telegram bot for household expense tracking with Actual Budget. No LLMs, no AI costs. Receipt scanning". 4 forks. |
| [p0tt8r/actual-budget-assistant](https://github.com/p0tt8r/actual-budget-assistant) | Actual Budget | 0 | 2026-07-10 (113) | MIT | Python; release v1.0.1 published 2026-07-10; actual-bridge/, assistant/, docker-compose.yml, ROADMAP.md, DECISIONS.md | 1 | Description: "Local-first family finance assistant for Actual Budget — Telegram approvals, voted merchant memory, cashflow". |
| [kunalkeshan/actual-budget-telegram-bot](https://github.com/kunalkeshan/actual-budget-telegram-bot) | Actual Budget | 0 | 2025-12-28 (307) | none | TypeScript, NestJS (nest-cli.json), Dockerfile, bruno/ (API collection), test/ | 1 | Description: "A secure, AI-powered Telegram bot for managing your Actual Budget finances using natural language." Homepage https://actual-budget-telegram-bot.vercel.app. Not stale by the 12-month rule, but close. |
| [mesuutt/ledger-cli-telegram-bot](https://github.com/mesuutt/ledger-cli-telegram-bot) | ledger-cli | 12 | 2024-12-22 (~22 months, stale) | none | Go; bot/, db/, ledger/ | 1 | "ledger-cli telegram bot". Homepage https://t.me/telegderbot. |
| [blinkstu/beancount-telegram-bot](https://github.com/blinkstu/beancount-telegram-bot) | Beancount | 7 | 2026-01-13 (291) | none | Python; pdm; Dockerfile; app/; tests/ | 1 | No description in API. Beancount role inferred from the repo name only. |
| [KidCoderT/beancounter](https://github.com/KidCoderT/beancounter) | Beancount (name suggests; not confirmed) | 0 | 2026-08-08 (84) | none | Python; Alembic; tests/ | 1 | See Key question 2. |
| [justpiple/expense-tracker-telegram-bot](https://github.com/justpiple/expense-tracker-telegram-bot) | Notion | 5 | 2026-02-14 (259) | MIT | TypeScript on Bun | 1 | Description: saves expenses to Notion automatically. |
| [R3D4NG3L/PersonalExpenseReport](https://github.com/R3D4NG3L/PersonalExpenseReport) | Google Sheets | 79 | 2022-03-24 (stale) | Apache-2.0 | JavaScript (Google Apps Script, TelegramBotIntegration.js); 22 forks | 2 | Google Sheets report plus Telegram bot for add, delete, totals (WebSearch summary). Stale. |
| [kaiimran/Expenses-Tracker-Telegram-Bot](https://github.com/kaiimran/Expenses-Tracker-Telegram-Bot) | Google Sheets | 13 | 2020-05-24 (stale) | none | n/a | n/a | Description: "Send your expenses to a telegram bot and it will automatically insert the data to your google spreadsheet". Stale. |
| [Sumanth1501/Telegram-Bot-Expense-Tracker](https://github.com/Sumanth1501/Telegram-Bot-Expense-Tracker) | Google Sheets | 0 | 2026-01-05 (299) | none | n/a | n/a | Description: "Bot to track expense to google sheets" (search row). |
| [wujunchuan/telegram-bot](https://github.com/wujunchuan/telegram-bot) | Beancount | 3 | 2021-08-12 (stale) | none | n/a | n/a | Description: minimum viable product for a Beancount Telegram bot (search row). Stale. |
| [nonPointer/beancounter_telegram](https://github.com/nonPointer/beancounter_telegram) | Beancount | 1 | 2026-10-15 | none | n/a | n/a | No description (search row). Not inspected. |

Searches returning zero rows: "hledger telegram", "ynab telegram bot", "notion expense telegram bot" (only justpiple surfaced via another query), "telegram bot net worth", "telegram bot personal finance self-hosted", "actual budget bot". Source: GitHub search API, 2026-10-31.

### Inferences
- Firefly III is the best-supported engine for a Telegram bridge: the most active repo (cyxou, versioned), plus MIT alternative miguel-bm with voice and tests.
- Actual Budget: three repos; two pushed in 2026 (bbharathbala 2026-06-01, p0tt8r 2026-07-10) and one in 2025-12 (kunalkeshan). Firefly III is more recent (cyxou 2026-10-23, miguel-bm 2026-09-13). Adoption is small for both.
- Beancount and ledger bridges are small and mostly stale. Choosing one of them means maintaining an unmaintained bot.
- None of the bridges expose a Mini App. A Mini App over these engines would have to be built.

### Gaps
- No bridge to a Mini App found. All bridges are bots.
- No repos found for hledger or YNAB.
- Firefly bridge API compatibility and Actual Budget bridge license obligations for personal use were not checked.
- Bank-specific imports (Erste, PrivatBank) were not searched.

---

## Key question 4: Starter templates and SDKs for Telegram Mini Apps (official org, SDKs, UI kits, npm status)

### Takeaway
The official Telegram-Mini-Apps org is active around the tma.js monorepo (1,209 stars, MIT, pushed 2026-10-28). The current SDK scope is @tma.js/* (@tma.js/sdk 3.3.0, published 2026-07-14). The @telegram-apps/* scope is legacy: several packages are flagged deprecated, and the docs label them "Legacy". The four current official templates were last pushed 2025-11-12 to 2025-12-08, so they are approaching the 12-month line. The @telegram-apps/telegram-ui kit has no repo in the org. @twa-dev/sdk and react-telegram-web-app are stale.

### Cited Findings

Official Telegram-Mini-Apps org, GitHub API 2026-10-31:

| Repo | Stars | Forks | Last push (days ago) | License | Stack | Contributors | Notes |
|---|---|---|---|---|---|---|---|
| [Telegram-Mini-Apps/tma.js](https://github.com/Telegram-Mini-Apps/tma.js) | 1,209 | 393 | 2026-10-28 (3) | MIT | TypeScript monorepo (apps/, packages/, .changeset, eslint, CONTRIBUTING.md, V4_CHANGES.md in root) | 40 | Latest release tag: @tma.js/sdk-react@3.0.23, 2026-07-14. Docs: https://docs.telegram-mini-apps.com/ |
| [Telegram-Mini-Apps/reactjs-template](https://github.com/Telegram-Mini-Apps/reactjs-template) | 430 | 165 | 2025-11-12 (353) | MIT | React, tma.js, TypeScript, Vite | 5 | Description: uses tma.js. Homepage: https://t.me/tmajsbot/react_example. No release. |
| [Telegram-Mini-Apps/nextjs-template](https://github.com/Telegram-Mini-Apps/nextjs-template) | 370 | 124 | 2025-12-08 (327) | none | Next.js, TypeScript, TON Connect, tma.js | 5 | Description includes TON Connect. |
| [Telegram-Mini-Apps/vuejs-template](https://github.com/Telegram-Mini-Apps/vuejs-template) | 34 | 11 | 2025-11-12 (353) | none | Vue, TypeScript, Vite | 2 | Demo: https://telegram-mini-apps.github.io/vuejs-template/ |
| [Telegram-Mini-Apps/solidjs-template](https://github.com/Telegram-Mini-Apps/solidjs-template) | 37 | 8 | 2025-11-12 (353) | none | Solid, TypeScript, Vite | 1 | Demo: https://telegram-mini-apps.github.io/solidjs-template/ |
| [Telegram-Mini-Apps/init-data-golang](https://github.com/Telegram-Mini-Apps/init-data-golang) | 117 | 19 | 2026-09-10 (51) | MIT | Go | 6 | Validation library for Mini App init data. Latest release v2.0.1, 2025-08-22. |

Legacy org templates (2025-01-07 batch): typescript-template (18 stars), vanillajs-template (15), reactjs-tsdk-template (8), nextjs-tsdk-template (8), and others are archived (`archived: true`). Source: https://github.com/Telegram-Mini-Apps (org listing, read 2026-10-31).

Telegram-Mini-Apps/telegram-ui: GitHub API returns 404 for this repo name, and the org listing (100 repos) does not include it. The npm package is still published (see below). Repo location not found.

Community starters and libraries:

| Repo | Stars | Last push (days ago) | License | Stack | Status |
|---|---|---|---|---|---|
| [AHTOOOXA/gramkit](https://github.com/AHTOOOXA/gramkit) | 10 | 2026-10-29 (2) | MIT | Monorepo: FastAPI, Next.js or Vue, Postgres, Redis, aiogram; description: "Telegram Mini App + web monorepo starter". Homepage https://react.antonchaynik.ru/ . Root has CLAUDE.md, .claude/, .mcp.json. 2 forks, 1 contributor. | Active. Only licensed starter in this search that combines Mini App, Python backend and aiogram bot. |
| [nimaxin/init-data-py](https://github.com/nimaxin/init-data-py) | 45 | 2026-10-18 (13) | MIT | Python library for validating Mini App init data (description) | Active (search row). |
| [vkruglikov/react-telegram-web-app](https://github.com/vkruglikov/react-telegram-web-app) | 613 | 2024-12-24 (676) | MIT | React components; latest release v2.1.9, 2023-12-09 | Archived (`archived: true`) and stale. |
| [twa-dev/SDK](https://github.com/twa-dev/SDK) | 332 | 2025-02-05 (633) | MIT | JavaScript; release v8.0.2, 2025-02-05 | Stale. |
| [Vishal-1756/Telegram-Miniapp-Boilerplate](https://github.com/Vishal-1756/Telegram-Miniapp-Boilerplate) | 12 | 2025-05-31 (518) | Apache-2.0 | React 18, TypeScript, Tailwind (description) | Stale. |
| [liect/tma-nextjs-starter](https://github.com/liect/tma-nextjs-starter) | 19 | 2024-11-26 (704) | MIT | Next.js, TON Connect UI (search row) | Stale. |
| [st-matskevich/tg-mini-app-template](https://github.com/st-matskevich/tg-mini-app-template) | 35 | 2023-10-15 (stale, over 3 years) | MIT | Go + React, CI/CD to GCP (search row) | Stale. |
| [usernein/react-mini-app](https://github.com/usernein/react-mini-app) | 18 | 2023-10-04 | MIT | React, TypeScript, Vite (search row) | Stale. |

npm packages (registry.npmjs.org, api.npmjs.org; downloads for 2026-10-23 to 2026-10-29):

| Package | Latest | Published | Deprecated flag | Weekly downloads | Status |
|---|---|---|---|---|---|
| [@tma.js/sdk](https://www.npmjs.com/package/@tma.js/sdk) | 3.3.0 | 2026-07-14 | none | 32,876 | Current scope, active |
| [@tma.js/sdk-react](https://www.npmjs.com/package/@tma.js/sdk-react) | 3.0.23 | 2026-07-14 | none | 16,396 | Current, active |
| [@tma.js/bridge](https://www.npmjs.com/package/@tma.js/bridge) | 2.3.3 | 2026-06-20 | none | 34,418 | Current, active |
| [@tma.js/init-data-node](https://www.npmjs.com/package/@tma.js/init-data-node) | 2.0.8 | 2026-06-20 | none | 12,732 | Current, active |
| [@tma.js/sdk-solid](https://www.npmjs.com/package/@tma.js/sdk-solid) | 3.0.23 | 2026-07-14 | none | 406 | Current, active |
| [@tma.js/sdk-vue](https://www.npmjs.com/package/@tma.js/sdk-vue) | 1.0.23 | 2026-07-14 | none | 626 | Current, active |
| [@tma.js/create-mini-app](https://www.npmjs.com/package/@tma.js/create-mini-app) | 1.0.1 | 2025-10-18 | "Package no longer supported" | 5 | Abandoned |
| [@telegram-apps/sdk](https://www.npmjs.com/package/@telegram-apps/sdk) | 3.11.8 | 2025-10-08 (388 days) | none | 79,980 | Legacy scope, no publish in 12+ months |
| [@telegram-apps/sdk-react](https://www.npmjs.com/package/@telegram-apps/sdk-react) | 3.3.9 | 2025-10-08 (388 days) | none | 37,961 | Legacy scope, stale |
| [@telegram-apps/telegram-ui](https://www.npmjs.com/package/@telegram-apps/telegram-ui) | 2.1.13 | 2025-10-14 (382 days) | none | 12,359 | Stale; repo not found |
| [@telegram-apps/init-data-node](https://www.npmjs.com/package/@telegram-apps/init-data-node) | 2.0.10 | 2025-06-27 | "not supported anymore. Use @tma.js/init-data-node" | 12,383 | Deprecated |
| [@telegram-apps/bridge](https://www.npmjs.com/package/@telegram-apps/bridge) | 2.11.0 | 2025-08-25 | "not supported anymore. Use @tma.js/bridge" | 107,449 | Deprecated |
| [@telegram-apps/sdk-solid](https://www.npmjs.com/package/@telegram-apps/sdk-solid) | 3.0.31 | 2025-08-25 | "unsupported anymore. Use @tma.js/sdk-solid" | 366 | Deprecated |
| [@telegram-apps/sdk-vue](https://www.npmjs.com/package/@telegram-apps/sdk-vue) | 2.0.31 | 2025-08-25 | "unsupported anymore. Use @tma.js/sdk-vue" | 758 | Deprecated |
| [@twa-dev/sdk](https://www.npmjs.com/package/@twa-dev/sdk) | 8.0.2 | 2025-02-05 (633 days) | none | 23,179 | Stale |
| [@tonconnect/ui-react](https://www.npmjs.com/package/@tonconnect/ui-react) | 5.0.1 | 2026-10-11 | none | 39,711 | Active (TON wallet UI, for reference) |

Sources: registry.npmjs.org/PACKAGE and api.npmjs.org/downloads/point/last-week/PACKAGE for each row.

Telegram's own client script: the Mini App API is loaded from `https://telegram.org/js/telegram-web-app.js?64`, placed in `<head>`. The page does not mention an npm package for the Mini App JS API. Source: https://core.telegram.org/bots/webapps (WebFetch, 2026-10-31).
- npm package named `telegram-web-app`: version 0.0.0, last published 2022-04-18, 150 weekly downloads. It is a placeholder and not the official client. Source: https://registry.npmjs.org/telegram-web-app

docs.telegram-mini-apps.com (WebFetch, 2026-10-31): the page lists navigation labels "Latest" (packages/tma-js-sdk) and "Legacy" (packages/legacy/tma-js-sdk). It names no npm packages and no versions. Source: https://docs.telegram-mini-apps.com/

### Inferences
- For a React Mini App, the official reactjs-template (MIT, tma.js) is the lowest-risk base. Its 353-day gap since last push is close to the 12-month stale line.
- Use the @tma.js/* scope for new code. The @telegram-apps/* packages are deprecated (several explicitly), and the docs label them "Legacy".
- Legacy @telegram-apps/sdk still has more weekly downloads (79,980) than @tma.js/sdk (32,876). Inference: many projects have not migrated. Migration status of individual starters was not checked.
- tma.js root contains V4_CHANGES.md, but npm latest for @tma.js/sdk is 3.3.0. No v4 is published as of 2026-10-31. Whether a v4 pre-release exists was not checked.
- The UI kit (@telegram-apps/telegram-ui) has no visible maintained repo, so picking it carries risk. Inference from the 404 and the org listing.

### Gaps
- Telegram-Mini-Apps/telegram-ui repo location not found.
- Whether reactjs-template uses @tma.js or legacy @telegram-apps packages was not checked (only the description "tma.js").
- Telegram-Mini-Apps/tma.js docs were not read beyond the navigation page (WebFetch returned navigation text only).
- Test coverage and CI status of the starters were not checked.

---

## Key question 5: Top 5 candidates to fork for a personal finance Mini App, and top 5 to study

Ranking criteria: license allows reuse, recent push, Mini App or finance fit, and reading effort for a non-programmer working with AI agents. Scores are not computed; order is a judgment from the data above.

### Takeaway
Fork candidates are mostly foundations: the official React template, a full-stack monorepo, and an MIT finance backend. The best feature reference, sofiy_qwen, has no license, so it is study-only unless the author agrees to reuse. Study candidates cover the feature set, the UX of logging, and SDK practice.

### Cited Findings

Top 5 to fork (ranked):
1. [Telegram-Mini-Apps/reactjs-template](https://github.com/Telegram-Mini-Apps/reactjs-template): MIT, 430 stars, 165 forks, React plus tma.js plus Vite. Reason: official, licensed frontend base; finance screens are added on top. Watch: last push 2025-11-12 (353 days).
2. [AHTOOOXA/gramkit](https://github.com/AHTOOOXA/gramkit): MIT, 10 stars, pushed 2026-10-29. Reason: only licensed monorepo that covers Mini App, FastAPI backend, Postgres and an aiogram bot in one repo; built with agent-oriented files (CLAUDE.md, .mcp.json). Watch: one contributor, 10 stars.
3. [krybybit/finance-tracker-backend](https://github.com/krybybit/finance-tracker-backend): MIT, pushed 2026-04-16, Python with Dockerfile and docker-compose, live homepage. Reason: only MIT finance-specific Mini App backend found. Watch: README is one line; read before use.
4. [xetus476/sofiy_qwen](https://github.com/xetus476/sofiy_qwen): React, TypeScript, Vite, Supabase; pushed 2026-10-03. Reason: the closest match to the target feature set (expenses, income, goals, budget plan vs fact, analytics). Condition: no license, so fork only with the author's permission. Check the committed `.env` first.
5. [ceelikonur/jarvis-home](https://github.com/ceelikonur/jarvis-home): MIT, pushed 2026-07-01, Node, has src/, test/, web/. Reason: one MIT codebase with a Telegram bot, a budget manager and a web dashboard. Watch: 0 stars, 1 contributor, self-hosted home-assistant framing.

Conditional forks if an engine is chosen: cyxou/firefly-iii-telegram-bot (GPL-3.0, see study list) or miguel-bm/firefly-iii-telegram-bot (MIT, Firefly, voice input, vitest) for Firefly III; bbharathbala/actual-budget-telegram-bot (MIT, Actual Budget, receipt scanning, no LLM) for Actual Budget.

Top 5 to study (ranked):
1. [xetus476/sofiy_qwen](https://github.com/xetus476/sofiy_qwen): best finance UI feature reference (budget plan vs fact, goals, analytics on React and Supabase). No license, so read for ideas only.
2. [cyxou/firefly-iii-telegram-bot](https://github.com/cyxou/firefly-iii-telegram-bot): 70 stars, 13 forks, 6 contributors, v3.0.0 released 2026-10-23. Most-used bridge to an engine. AGENTS.md and CLAUDE.md show how the author works with AI agents. GPL-3.0 means derived code must be GPL.
3. [KidCoderT/beancounter](https://github.com/KidCoderT/beancounter): README's single-line logging idea ("purse 5.2") is the clearest UX reference for friction-free entry. Python with Alembic migrations and tests. No license, so study only. Mini App claim not verified.
4. [AdoniasMulugeta/quicktrack-expenses-mini-app](https://github.com/AdoniasMulugeta/quicktrack-expenses-mini-app): a Mini App with no framework (vanilla JS), IndexedDB and Telegram CloudStorage. Short enough to read in one sitting. No license, so study only.
5. [Telegram-Mini-Apps/tma.js](https://github.com/Telegram-Mini-Apps/tma.js): reference for SDK usage, init-data validation and the @telegram-apps to @tma.js migration. 1,209 stars, pushed 2026-10-28. Its own docs are the source for the SDK choice.

### Inferences
- Two stack shapes stand out from the data:
  - Frontend-first: reactjs-template (React, tma.js, Vite) plus a backend such as krybybit (Python) or gramkit (FastAPI, Postgres).
  - Engine-first: a Telegram bot bridge to Firefly III (cyxou or miguel-bm) or Actual Budget (bbharathbala), with a Mini App added later.
- Nothing in the sample is production-proven by adoption. All finance-specific repos have 0-5 stars. Treat them as references to read, not as products to deploy.
- Deployments: homepages were declared but not opened, so live status is unverified.

### Gaps
- No code was cloned or run. Security, test coverage, data-model quality and multi-currency handling (EUR, UAH, USD) are not verified for any top-10 candidate.
- The `.env` file in xetus476/sofiy_qwen was not read. Its risk is inferred only from its presence at the repo root.
- The Mini App status of KidCoderT/beancounter and miguel-bm/firefly-iii-telegram-bot `webapp/` is unverified.
- Bank integrations for Erste (Austria) and PrivatBank (Ukraine): not searched.
- Habr and dev.to write-ups were not found.
