# Fact-check of github_telegram_finance_code.md (as of 2026-10-31)

Method: GitHub REST API via gh (repo facts, latest release, contributors, root file names only); npm registry and api.npmjs.org for download counts; READMEs and package.json read as data; docs source read from the apps/docs folder of Telegram-Mini-Apps/tma.js; docs.telegram-mini-apps.com fetched once. Nothing cloned, downloaded or run. No .env or secrets file opened (names only). Temporary files written to /tmp during the check were deleted.
Verdict key: CONFIRMED = notes are right. WRONG = notes are wrong; correct value given. UNVERIFIABLE = not settled by the sources above. ANSWERED = a question from the brief that the notes did not settle.

## Table

| Claim | Verdict | Correct value | Source |
|---|---|---|---|
| reactjs-template: 430 stars, 165 forks, MIT, 5 contributors, last push 2025-11-12, no release | CONFIRMED | Same. releases/latest returns 404. 353 days before 2026-10-31 | https://github.com/Telegram-Mini-Apps/reactjs-template |
| reactjs-template stack "React, tma.js, TypeScript, Vite" | CONFIRMED | Repo description: "React, tma.js, TypeScript and Vite" | https://github.com/Telegram-Mini-Apps/reactjs-template |
| gramkit: 10 stars, 2 forks, MIT, 1 contributor, last push 2026-10-29 | CONFIRMED | Same | https://github.com/AHTOOOXA/gramkit |
| gramkit root has CLAUDE.md, .claude/, .mcp.json | CONFIRMED | All three present in root | https://github.com/AHTOOOXA/gramkit |
| krybybit/finance-tracker-backend: 0 stars, MIT, 1 contributor, last push 2026-04-16 | CONFIRMED | Same | https://github.com/krybybit/finance-tracker-backend |
| krybybit README is a title and one line | CONFIRMED | Two lines: title plus "Backend для Telegram Mini App Finance Tracker" | https://github.com/krybybit/finance-tracker-backend |
| krybybit root has Dockerfile, docker-compose.yml, requirements.txt, folder "fronted" | CONFIRMED | All present | https://github.com/krybybit/finance-tracker-backend |
| xetus476/sofiy_qwen: 0 stars, no license, 2 contributors, last push 2026-10-03 | CONFIRMED | License null (no LICENSE file in root) | https://github.com/xetus476/sofiy_qwen |
| sofiy_qwen root has .env and .env.example | CONFIRMED | Both present. Names only, contents not opened | https://github.com/xetus476/sofiy_qwen |
| sofiy_qwen features and stack | CONFIRMED | README title "FinanceBot Mini App": expenses by category, income, goals, budget plan vs fact, analytics. Stack: React 18, TypeScript, Vite, Tailwind, Recharts, Framer Motion, React Router v6, Supabase | https://github.com/xetus476/sofiy_qwen |
| sofiy_qwen has no tests folder at root | CONFIRMED | No tests entry in root listing | https://github.com/xetus476/sofiy_qwen |
| ceelikonur/jarvis-home: 0 stars, MIT, 1 contributor, last push 2026-07-01 | CONFIRMED | Same | https://github.com/ceelikonur/jarvis-home |
| jarvis-home as a Mini App fork candidate | CONFIRMED (caveat) | Facts match, but it is not a Mini App. README: Telegram bot plus a web dashboard that is PIN-protected and open on the local WiFi. Weak fit for a Mini App | https://github.com/ceelikonur/jarvis-home |
| cyxou/firefly-iii-telegram-bot: 70 stars, 13 forks, GPL-3.0, 6 contributors, last push 2026-10-23 | CONFIRMED | Same | https://github.com/cyxou/firefly-iii-telegram-bot |
| cyxou release v3.0.0 published 2026-10-23 | CONFIRMED | Latest release v3.0.0, published 2026-10-23 | https://github.com/cyxou/firefly-iii-telegram-bot/releases |
| cyxou root has AGENTS.md, CLAUDE.md, Earthfile, Makefile, .openapi-generator-config.yaml, .github | CONFIRMED | All present | https://github.com/cyxou/firefly-iii-telegram-bot |
| KidCoderT/beancounter: 0 stars, no license, 1 contributor, last push 2026-08-08, homepage beancounter-gamma.vercel.app | CONFIRMED | License null. Homepage as stated (not opened) | https://github.com/KidCoderT/beancounter |
| beancounter stack: Python, Alembic migrations, tests, website, futureplan.md | CONFIRMED | Root has alembic.ini, migrations/, tests/, website/, futureplan.md, pyproject.toml, uv.lock | https://github.com/KidCoderT/beancounter |
| beancounter has a Mini App at /app (WebSearch claim, unverified in notes) | CONFIRMED | README: "/app opens a Telegram Mini App". The Mini App is read-only, no editing from the web | https://github.com/KidCoderT/beancounter |
| beancounter uses Beancount as its ledger engine | UNVERIFIABLE | README mentions Beancount only in the project name. Storage engine not stated | https://github.com/KidCoderT/beancounter |
| AdoniasMulugeta/quicktrack-expenses-mini-app: 0 stars, no license, 1 contributor, last push 2026-02-13 | CONFIRMED | License null | https://github.com/AdoniasMulugeta/quicktrack-expenses-mini-app |
| quicktrack: vanilla HTML/CSS/JS, IndexedDB, Telegram CloudStorage, api/ folder, vercel.json | CONFIRMED | Description matches. Root has api/, vercel.json, app.js, storage.js, ui.js. Repo has no README (API returns 404) | https://github.com/AdoniasMulugeta/quicktrack-expenses-mini-app |
| Telegram-Mini-Apps/tma.js: 1,209 stars, 393 forks, MIT, 40 contributors, last push 2026-10-28 | CONFIRMED | Same | https://github.com/Telegram-Mini-Apps/tma.js |
| tma.js latest release tag @tma.js/sdk-react@3.0.23, 2026-07-14 | CONFIRMED | Same | https://github.com/Telegram-Mini-Apps/tma.js/releases |
| tma.js root contains V4_CHANGES.md | CONFIRMED | Present | https://github.com/Telegram-Mini-Apps/tma.js |
| miguel-bm/firefly-iii-telegram-bot: 0 stars, MIT, 2 contributors, last push 2026-09-13 | CONFIRMED | Same | https://github.com/miguel-bm/firefly-iii-telegram-bot |
| miguel-bm root has wrangler.toml, vitest.config.ts, webapp/, pnpm lockfile | CONFIRMED | All present | https://github.com/miguel-bm/firefly-iii-telegram-bot |
| bbharathbala/actual-budget-telegram-bot: 18 stars, 4 forks, MIT, 1 contributor, last push 2026-06-01 | CONFIRMED | Same | https://github.com/bbharathbala/actual-budget-telegram-bot |
| bbharathbala description says "No LLMs, no AI costs. Receipt scanning" | CONFIRMED | Same. Full description adds auto-learning categories, tags, transfers, daily nudge | https://github.com/bbharathbala/actual-budget-telegram-bot |
| p0tt8r/actual-budget-assistant: 0 stars, MIT, 1 contributor, last push 2026-07-10, release v1.0.1 on 2026-07-10 | CONFIRMED | Same | https://github.com/p0tt8r/actual-budget-assistant |
| p0tt8r is written in Python | UNVERIFIABLE | Language field not checked. Root has actual-bridge/, assistant/, docker-compose.yml, ROADMAP.md, DECISIONS.md | https://github.com/p0tt8r/actual-budget-assistant |
| apuignav/expense-bot: no license per API; no LICENSE file in root | CONFIRMED | License null. The WebSearch "BSD 3-Clause" is not supported | https://github.com/apuignav/expense-bot |
| The 19 repos the notes call "no license" | CONFIRMED | License null for all 19. Apps: xetus476/sofiy_qwen, AdoniasMulugeta/quicktrack-expenses-mini-app, Telegram-Mini-Apps/nextjs-template, Telegram-Mini-Apps/vuejs-template, Telegram-Mini-Apps/solidjs-template, Nati7396/fintrack-birr, zhandos717/tgfinance. Bots: KidCoderT/beancounter, apuignav/expense-bot, smkbdh/finance-ai-buddah-bot, alhajbaig/Expense-Tracker-Telegram-bot, arsalan-19/ai-expense-tracker-telegram-v1, kunalkeshan/actual-budget-telegram-bot, blinkstu/beancount-telegram-bot, mesuutt/ledger-cli-telegram-bot, kaiimran/Expenses-Tracker-Telegram-Bot, Sumanth1501/Telegram-Bot-Expense-Tracker, wujunchuan/telegram-bot, nonPointer/beancounter_telegram | Each repo at https://github.com/OWNER/REPO (license read via https://api.github.com/repos/OWNER/REPO) |
| Four official templates: stars, last push, license (reactjs 430 / nextjs 370 / vuejs 34 / solidjs 37; pushed 2025-11-12, 2025-12-08, 2025-11-12, 2025-11-12; nextjs, vuejs and solidjs have no license) | CONFIRMED | Same. reactjs-template is MIT | https://github.com/Telegram-Mini-Apps (per repo) |
| Templates moved into the tma.js monorepo? | ANSWERED | No. tma.js packages/: bridge, init-data, sdk, sdk-react, sdk-solid, sdk-svelte, sdk-vue, tsconfig. apps/: docs, playground. The four templates stay in separate repos | https://github.com/Telegram-Mini-Apps/tma.js/tree/master/packages |
| reactjs-template dependency scope | ANSWERED | Mixed. @tma.js/sdk-react ^3.0.8 (current), @telegram-apps/telegram-ui ^2.1.9 (older scope, no repo found), @tonconnect/ui-react ^2.2.0 (TON Connect) | https://github.com/Telegram-Mini-Apps/reactjs-template (package.json) |
| nextjs-template dependency scope | ANSWERED | Mixed. @tma.js/sdk-react ^3.0.11, @telegram-apps/telegram-ui ^2.1.13, @tonconnect/ui-react ^2.3.1 | https://github.com/Telegram-Mini-Apps/nextjs-template (package.json) |
| vuejs-template dependency scope | ANSWERED | Current scope only: @tma.js/sdk-vue ^1.0.8. Also @tonconnect/ui ^2.0.9 | https://github.com/Telegram-Mini-Apps/vuejs-template (package.json) |
| solidjs-template dependency scope | ANSWERED | Current scope only: @tma.js/sdk-solid ^3.0.8. Also @tonconnect/ui ^2.0.5 | https://github.com/Telegram-Mini-Apps/solidjs-template (package.json) |
| Telegram-Mini-Apps org listing has 100 repos | WRONG | 24 repos in the full listing | https://github.com/Telegram-Mini-Apps |
| Legacy 2025-01-07 batch archived: typescript-template 18 stars, vanillajs-template 15, reactjs-tsdk-template 8, nextjs-tsdk-template 8 | CONFIRMED | Stars 18 / 15 / 8 / 8. All four archived | https://github.com/Telegram-Mini-Apps |
| Telegram-Mini-Apps/telegram-ui returns 404 and is not in the org listing | CONFIRMED | 404 on the repos API. Not among the 24 org repos. Not a package in telegram-mini-apps-dev/telegram-apps/packages either | https://github.com/Telegram-Mini-Apps |
| twa-dev/SDK: 332 stars, MIT, last push 2025-02-05, release v8.0.2 on 2025-02-05 | CONFIRMED | Same. Stale | https://github.com/twa-dev/SDK |
| vkruglikov/react-telegram-web-app: 613 stars, MIT, archived, last push 2024-12-24, release v2.1.9 on 2023-12-09 | CONFIRMED | Same | https://github.com/vkruglikov/react-telegram-web-app |
| @tma.js/sdk: latest 3.3.0, published 2026-07-14, 32,876 weekly downloads | CONFIRMED | Same. Not deprecated | https://www.npmjs.com/package/@tma.js/sdk |
| @telegram-apps/sdk: latest 3.11.8, published 2025-10-08, 79,980 weekly downloads | CONFIRMED | Same. 388 days since publish | https://www.npmjs.com/package/@telegram-apps/sdk |
| Is @telegram-apps/sdk marked deprecated? | ANSWERED | No. The deprecated field is empty on 3.11.8 | https://registry.npmjs.org/@telegram-apps%2Fsdk |
| @telegram-apps/telegram-ui: latest 2.1.13, published 2025-10-14, 12,359 weekly downloads | CONFIRMED | Same. Not deprecated. No repo found | https://www.npmjs.com/package/@telegram-apps/telegram-ui |
| @twa-dev/sdk: latest 8.0.2, published 2025-02-05, 23,179 weekly downloads | CONFIRMED | Same. Not deprecated | https://www.npmjs.com/package/@twa-dev/sdk |
| @tma.js/create-mini-app is abandoned (notes) | CONFIRMED | Deprecated: "Package no longer supported". 5 weekly downloads. Published 2025-10-18 | https://www.npmjs.com/package/@tma.js/create-mini-app |
| Several @telegram-apps packages are deprecated | CONFIRMED | Four are flagged: bridge 2.11.0, init-data-node 2.0.10, sdk-solid 3.0.31, sdk-vue 2.0.31. Each message points to the @tma.js replacement | https://www.npmjs.com/package/@telegram-apps/bridge |
| "The @telegram-apps/* packages are deprecated" (general, Key Q4 inference) | WRONG | Only the four above are flagged. @telegram-apps/sdk 3.11.8, sdk-react 3.3.9 and telegram-ui 2.1.13 are not | https://registry.npmjs.org/@telegram-apps%2Fsdk-react |
| "No v4 is published as of 2026-10-31" | WRONG | No stable 4.x. 4.0.0-rc.0 (2026-10-11) and 4.0.0-rc.1 (2026-10-28) are published under the "rc" dist-tag. "latest" is still 3.3.0 | https://registry.npmjs.org/@tma.js%2Fsdk |
| docs.telegram-mini-apps.com nav labels "Latest" and "Legacy" | CONFIRMED | "Latest" leads to /packages/tma-js-sdk. "Legacy" leads to /packages/legacy/tma-js-sdk | https://docs.telegram-mini-apps.com/ |
| The docs "Legacy" label covers the @telegram-apps packages (Key Q4 takeaway) | WRONG | "Legacy" holds previous versions of @tma.js packages (sidebar "Previous Versions"). The @telegram-apps packages are covered by "migrate-from-telegram-apps" guides instead | https://github.com/Telegram-Mini-Apps/tma.js/blob/master/apps/docs/.vitepress/packages.ts |
| What official docs recommend for new projects | ANSWERED | Entry point is @tma.js. Install with `pnpm i @tma.js/sdk`; bindings such as @tma.js/sdk-react install next to it. No page found that says "for new projects use X". No starter or CLI is named in the docs | https://docs.telegram-mini-apps.com/packages/tma-js-sdk |
| Docs CDN example uses @tma.js/sdk@4 | ANSWERED | jsDelivr returns 404 for @tma.js/sdk@4 because there is no stable 4.x. The docs source (main branch) already uses @4 | https://github.com/Telegram-Mini-Apps/tma.js/blob/master/apps/docs/packages/tma-js-sdk.md |
| Official project generator CLI | ANSWERED | Two on npm. @telegram-apps/create-mini-app 1.3.3 (published 2025-10-06, 48 weekly downloads, not deprecated). Its source is in telegram-mini-apps-dev/telegram-apps (25 stars, MIT, last push 2025-10-08). @tma.js/create-mini-app 1.0.1 is deprecated. The official docs have no CLI page: the docs link in the npm README redirects to /packages/tma-js-sdk | https://www.npmjs.com/package/@telegram-apps/create-mini-app |
| Templates the CLI offers | ANSWERED | From its template map (source read, not run). TypeScript with the telegramApps SDK option: reactjs-template, solidjs-template, nextjs-template, vuejs-template, plus a jQuery typescript-template (archived). TypeScript with the tsdk option: archived *-tsdk-template repos. JavaScript and jQuery templates are deprecated per CHANGELOG 1.3.0 | https://github.com/telegram-mini-apps-dev/telegram-apps/tree/master/packages/create-mini-app |
| cyxou: natural-language input | ANSWERED | Not in README. No natural-language or AI mention | https://github.com/cyxou/firefly-iii-telegram-bot |
| cyxou: voice input | ANSWERED | Not in README. No voice mention | https://github.com/cyxou/firefly-iii-telegram-bot |
| cyxou: Firefly III actions supported | ANSWERED | README: create transactions (incl. transfers and deposits), edit, list, math in amounts, accounts management, liabilities accounts, reports. Categories are named in the intro. Tags not yet (unchecked TODO). v3 needs Redis and Bun | https://github.com/cyxou/firefly-iii-telegram-bot#readme |
| miguel-bm: natural-language input ("15€ at Mercadona for groceries") | CONFIRMED | README: "Natural language input" with that example | https://github.com/miguel-bm/firefly-iii-telegram-bot#readme |
| miguel-bm: voice input | CONFIRMED | README: voice notes are transcribed and processed automatically. Needs an OpenAI key | https://github.com/miguel-bm/firefly-iii-telegram-bot#readme |
| miguel-bm: LLM provider not named in README head | WRONG | README Requirements name it: "OpenAI API key (for natural language processing and voice transcription)" | https://github.com/miguel-bm/firefly-iii-telegram-bot#readme |
| miguel-bm: Firefly III actions | CONFIRMED | Create, edit and delete transactions; natural-language queries; sum, count, average by category, period, merchant or tag; pie, bar and line charts; report links; account balances; bank statement import (BBVA, CaixaBank, ImaginBank, Revolut); monthly report; import reminders | https://github.com/miguel-bm/firefly-iii-telegram-bot#readme |
| miguel-bm: webapp/ is a Mini App (notes gap) | CONFIRMED | README section "Web Dashboard (Telegram Mini App)": account balances, doughnut charts, transaction list, custom date ranges. Not run | https://github.com/miguel-bm/firefly-iii-telegram-bot#readme |
| Erste and PrivatBank bank imports (notes gap) | ANSWERED | Not supported by miguel-bm. Supported: BBVA, CaixaBank, ImaginBank, Revolut | https://github.com/miguel-bm/firefly-iii-telegram-bot#readme |
| smkbdh/finance-ai-buddah-bot: LLM provider (notes: not confirmed) | ANSWERED | Description: "Powered by GPT-4o-mini" | https://github.com/smkbdh/finance-ai-buddah-bot |
| alhajbaig/Expense-Tracker-Telegram-bot: LLM provider (notes: not confirmed) | ANSWERED | Description: "Built with Python, Groq API, and the Telegram Bot API" | https://github.com/alhajbaig/Expense-Tracker-Telegram-bot |
| smkbdh description: voice input and multi-currency THB/RUB/USD/USDT | CONFIRMED | Same. Description also lists screenshot recognition, goals, charts | https://github.com/smkbdh/finance-ai-buddah-bot |
| "No open-source net-worth Mini App was found" | CONFIRMED (caveat) | Still no net-worth Mini App. But dompetku (see Missed candidates) is an MIT net-worth tracker with a Telegram bot | https://github.com/ilramdhan/dompetku |
| "Receipt-photo parsing is effectively absent from open source" | WRONG | dompetku has AI receipt OCR in its web app and Telegram bot (any OpenAI-compatible API). 26 stars | https://github.com/ilramdhan/dompetku |
| "The only receipt-scanning bot found explicitly says 'No LLMs'" | WRONG | bbharathbala does say that, but it is not the only receipt bot. dompetku (AI receipt OCR) and smkbdh (screenshot recognition) also handle receipt-like input | https://github.com/bbharathbala/actual-budget-telegram-bot |
| Zero-row query "telegram bot net worth" | CONFIRMED (caveat) | Re-run returns 0 rows. The same words reordered ("net worth telegram") return dompetku. Zero rows do not prove absence | https://github.com/search |
| Telegram's client script (telegram.org/js/telegram-web-app.js) and the telegram-web-app npm placeholder | UNVERIFIABLE | Not checked in this pass | https://core.telegram.org/bots/webapps |

Count: 76 checks. CONFIRMED 50, WRONG 7, UNVERIFIABLE 3, ANSWERED 16.

## Missed candidates

Four searches run with gh search repos (sorted by stars). Only repos with 5+ stars or a 2026 push are listed.

- "telegram mini app budget": 0 rows.
- "tma finance": 2 rows, both not finance apps:
  - ivlogv/tma-finances: 0 stars, no license, last push 2026-01-19, TypeScript. README title "Telegram Mini Apps Vue Template". A copy of the official Vue template, not a finance app. Exclude. https://github.com/ivlogv/tma-finances
  - slyshenko-ai/tma-finance-affiliate: 0 stars, no license, last push 2026-06-25, HTML. One page titled "TMA Finance - Affiliate Partnerships" that sells bookkeeping services. Exclude. https://github.com/slyshenko-ai/tma-finance-affiliate
- "telegram webapp expense tracker": 0 rows.
- "net worth telegram": 1 row, worth adding:
  - ilramdhan/dompetku: MIT, 26 stars, last push 2026-10-30. Self-hosted personal finance tracker: budgets, goals, recurring and split transactions, net worth (accounts, gold, receivables), Telegram bot (chat entries such as "kopi 25rb" and receipt photos, with a preview and /undo), AI receipt OCR through any OpenAI-compatible provider, 2FA, backups. Currencies IDR and USD (no EUR). Not a Mini App: the README says "web app" plus a Telegram chat bot and never "Mini App". Root has Vite config, supabase/, n8n/, Dockerfile. Good reference for net worth and receipt OCR. Declared homepage https://dompetku.ilramdhan.dev (not opened). https://github.com/ilramdhan/dompetku

## Overall reliability

1. Repo metadata (stars, forks, licenses, last push, contributors, releases): high. Every value checked against the API matched; no wrong repo fact found.
2. Narrative claims: medium. Five WRONG statements (org size 100 vs 24, "no v4" vs 4.0.0-rc.1, docs "Legacy" label, general deprecation claim, miguel-bm LLM provider) and two gap claims contradicted (receipt OCR absent, only receipt bot).
3. Coverage: low to medium. The notes' search missed dompetku, zero-row results depend on phrasing, and no code was read, so stack and quality claims rest on READMEs and package.json only.
