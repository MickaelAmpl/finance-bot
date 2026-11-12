# Verification of open_source_finance_engines.md (as of 31 October 2026)

Scope: Part A verifies the claims in open_source_finance_engines.md. Part B fills three gaps (Enable Banking free tier and Erste, Sure and Securo APIs, Monobank and Telegram importers). The source file was read in full and not modified.

## Method and evidence labels

- GitHub numbers: `gh api` on 31 Oct 2026 (UTC). Values are as read at check time, so stars and push times can differ from the notes by a few hours.
- Web pages: WebFetch first. Where WebFetch returned only a title, a 403 or a 404, the reader proxy (`https://r.jina.ai/URL`) was used and is named in the source column. "Extracted" = WebFetch summary, re-check before quoting verbatim.
- Search: 5 WebSearch calls in total. Search excerpts are labelled as such.
- Nothing was cloned, run, logged into, or created. No accounts were opened on Enable Banking, GoCardless or Monobank.
- Verdicts: CONFIRMED, WRONG (correct value given), UNVERIFIABLE (reason given).

## Part A: verification

### A.1 Repository numbers

| Repo | Claim in notes | Verdict | Correct value (gh api, 31 Oct 2026) | Source |
|---|---|---|---|---|
| firefly-iii/firefly-iii | 25,046 stars; pushed 2026-10-31 03:01; latest v6.7.9 (2026-10-11); AGPL-3.0; not archived | CONFIRMED (stars off by 1) | 25,045 stars; pushed 2026-10-31T03:01:35Z; latest v6.7.9 published 2026-10-11T19:16:51Z; AGPL-3.0; archived false | https://github.com/firefly-iii/firefly-iii |
| actualbudget/actual | 29,877 stars; pushed 2026-10-30 23:53; latest v26.10.0 (2026-10-02); MIT | CONFIRMED (stars and push time drifted) | 29,879 stars; pushed 2026-10-31T09:15:08Z; latest v26.10.0 published 2026-10-02T15:32:36Z; MIT; archived false | https://github.com/actualbudget/actual |
| ghostfolio/ghostfolio | 9,622 stars; pushed 2026-10-31 08:36; latest 3.94.0 (2026-10-28); AGPL-3.0 | WRONG (latest release is newer) | 9,623 stars; pushed 2026-10-31T09:56:00Z; latest release 3.95.0 published 2026-10-31T09:56:00Z; AGPL-3.0; archived false | https://github.com/ghostfolio/ghostfolio |
| wealthfolio/wealthfolio | 9,294 stars; pushed 2026-10-30 22:18; latest v3.11.0 (2026-10-23); AGPL-3.0; afadil path redirects | CONFIRMED (stars off by 1; redirect confirmed) | 9,293 stars; pushed 2026-10-30T22:17:59Z; latest v3.11.0 published 2026-10-23T01:12:36Z; AGPL-3.0; `afadil/wealthfolio` resolves to `wealthfolio/wealthfolio` | https://github.com/wealthfolio/wealthfolio |
| maybe-finance/maybe | 54,206 stars; last push 2025-07-24; latest v0.6.0; archived | CONFIRMED | 54,206 stars; archived true; pushed 2025-07-24T22:20:44Z; latest v0.6.0 published 2025-07-24T22:05:26Z; AGPL-3.0 | https://github.com/maybe-finance/maybe |
| we-promise/sure | 10,736 stars; pushed 2026-10-31 07:02; latest v0.7.6 (2026-10-31); AGPL-3.0; created 2025-07-23; "Maybe fork" | CONFIRMED (the "fork" is conceptual) | 10,736 stars; pushed 2026-10-31T07:02:01Z; latest v0.7.6 published 2026-10-31T03:37:06Z; created 2025-07-23T04:13:55Z; AGPL-3.0; GitHub fork flag false, no parent. The README calls it a "community fork" of Maybe Finance, which is a description, not a GitHub fork relation | https://github.com/we-promise/sure |
| mayswind/ezbookkeeping | 5,893 stars; pushed 2026-10-29 15:21; latest v2.1.1 (2026-10-23); MIT | CONFIRMED | 5,893 stars; pushed 2026-10-29T15:20:54Z; latest v2.1.1 published 2026-10-23T16:04:22Z; MIT; archived false | https://github.com/mayswind/ezbookkeeping |
| securo-finance/securo | 4,151 stars; created 2026-03-08; pushed 2026-10-30 20:49; latest v0.16.6 (2026-10-26); AGPL-3.0 | CONFIRMED (repo exists at this path; not a fork) | 4,152 stars; created 2026-03-08T19:58:11Z; pushed 2026-10-30T20:48:51Z; latest v0.16.6 published 2026-10-26T20:18:19Z; AGPL-3.0; fork false, no parent or source. Its docs repo `securo-finance/securo-docs` was created 2026-03-14. A GitHub search for "securo" shows no older personal-finance project with this name. | https://github.com/securo-finance/securo |
| Ivy-Apps/ivy-wallet | 3,184 stars; archived; latest v2026.10.22-207 (2026-10-22); GPL-3.0 | CONFIRMED | 3,184 stars; archived true; pushed 2026-10-22T14:04:48Z; latest v2026.10.22-207 published 2026-10-22T14:14:22Z; GPL-3.0 | https://github.com/Ivy-Apps/ivy-wallet |

Not re-checked in this pass: 12-month release counts, contributor counts, open-issue counts, and the repos not listed above (Fava, Beancount, hledger, Kresus, Cashew, Money Manager EX, Budget Board, WYGIWYH, Paisa, BeeCount, finanze, budgetzero, open-finance, Aurum). UNVERIFIABLE in this pass.

Note on Securo: the repo was created on 2026-03-08 and is not a fork, so it cannot be an older project renamed. Rename history was not checked, but the creation date rules out an older origin.

### A.2 Firefly III

| Claim | Verdict | Correct value | Source |
|---|---|---|---|
| REST API covering most of the product | CONFIRMED | README: "It features a REST JSON API that covers almost every part of Firefly III." | https://github.com/firefly-iii/firefly-iii (README) |
| Personal access tokens for the API | CONFIRMED | Section "Personal Access Tokens": if the app cannot use OAuth2, generate a token under "Options" > "Profile" > "OAuth" > "Personal Access Tokens". OAuth2 is also documented. The exact menu path is confirmed from the source file, not from the live page. | https://github.com/firefly-iii/docs/blob/main/docs/docs/how-to/firefly-iii/features/api.md (live: https://docs.firefly-iii.org/how-to/firefly-iii/features/api/) |
| Data importer lists Enable Banking | CONFIRMED | Section "Enable Banking": "Enable Banking offers a free restricted mode that allows you to access your own pre-authorized bank accounts without a paid subscription." Tutorial page exists (`docs/docs/tutorials/data-importer/eb.md`). The live tutorial page returned Cloudflare 403 to both tools, so the source file was used. | https://github.com/firefly-iii/docs/blob/main/docs/docs/how-to/data-importer/import/third-party-providers.md |
| GoCardless registration closed (quote) | CONFIRMED, with a caveat | Warning box: "GoCardless is sunsetting this free service and registration is unfortunately closed." Caveat: the same page still contains an older section, "You can sign up for the GoCardless API ... free for both commercial and personal use". The page contradicts itself. Last commit to the file: 2026-10-26. Which text is newer is an inference. | https://github.com/firefly-iii/docs/blob/main/docs/docs/how-to/data-importer/import/gocardless.md (live: https://docs.firefly-iii.org/how-to/data-importer/import/gocardless/) |
| Full list of importer providers (Basiq, Enable Banking, FinTS, GoCardless, Sophtron, Lunch Flow, OBG, SimpleFIN, teller.io) | PARTLY CONFIRMED | Enable Banking, GoCardless, SimpleFIN and teller.io sections seen. Basiq, FinTS, Sophtron, Lunch Flow and OBG were not re-read. | https://github.com/firefly-iii/docs/blob/main/docs/docs/how-to/data-importer/import/third-party-providers.md |

### A.3 Actual Budget

| Claim | Verdict | Correct value | Source |
|---|---|---|---|
| No HTTP REST API; only the Node.js `@actual-app/api` client | CONFIRMED | "Actual **does not** expose HTTP endpoints that can be called." Official client: "We provide an official Node.js client in the `@actual-app/api` package. Other languages are not supported at this point." | https://actualbudget.org/docs/api/ |
| Supports Enable Banking | CONFIRMED | Bank-sync list: "Enable Banking (European Banks)". Same list: "GoCardless BankAccountData (European Banks, not accepting new accounts)". | https://actualbudget.org/docs/advanced/bank-sync/ |
| Browser build marked experimental | UNVERIFIABLE (attribution) | The page marks "an experimental feature" (full-page line 56). The text read did not show which feature it is, so the notes' "browser build" attribution was not confirmed. | https://actualbudget.org/docs/api/ |

### A.4 GoCardless Bank Account Data status

| Claim | Verdict | Correct value | Source |
|---|---|---|---|
| New sign-ups are closed | CONFIRMED by GoCardless (undated) | Official notice: "New signups for Bank Account Data are currently disabled." No date, no reason, no pricing or sales link. The notes said no GoCardless page states this; that is now wrong. | https://bankaccountdata.gocardless.com/new-signups-disabled |
| Closure happened "from July 2025" | UNVERIFIABLE as a GoCardless statement | Only Actual's docs say: "From July 2025 onwards, GoCardless has stopped accepting new Bank Account Data accounts." The Actual page is undated, and GoCardless's notice gives no date. | https://actualbudget.org/docs/advanced/bank-sync/gocardless/ |
| Existing users keep working | CONFIRMED (Actual docs only) | "if you are an existing user, your account should continue to work." | https://actualbudget.org/docs/advanced/bank-sync/gocardless/ |
| Free tier is gone, paid tier exists | PARTLY CONFIRMED (inference) | GoCardless developer docs: "Account verification is only offered to paying customers." Firefly: "sunsetting this free service". | https://docs.gocardless.com/bank-account-data/overview |
| GoCardless legacy notice | Not the same thing | "The product you are trying to access was discontinued on the 18th of December 2023 and is no longer available for use." The page does not say whether this is the free Bank Account Data tier. | https://gocardless.com/bank-account-data/announcement |
| "Free plan of 50 requisitions per month" (from search excerpt in notes) | UNVERIFIABLE | Not in the GoCardless pricing text read. That text covers general payment pricing and shows no Bank Account Data plan. Keep excluded. | https://gocardless.com/pricing |

### A.5 Monobank personal API

| Claim | Verdict | Correct value | Source |
|---|---|---|---|
| Statement period max 31 days + 1 hour | CONFIRMED | Ukrainian original "31 доба + 1 година (2682000 секунд)", translated: maximum period 31 days + 1 hour (2,682,000 seconds). Check: 31 x 86400 + 3600 = 2,682,000 s, which matches. | https://api.monobank.ua/docs/ (endpoint `/personal/statement`), read via https://r.jina.ai/https://api.monobank.ua/docs/ |
| 1 request per 60 seconds | CONFIRMED | Statement (translated from "не частіше ніж 1 раз у 60 секунд"): not more than once per 60 seconds. Client-info (`/personal/client-info`): the same limit. | https://api.monobank.ua/docs/ (reader) |
| Webhook support | CONFIRMED | Endpoint `/personal/webhook` (Ukrainian heading "Встановлення WebHook", translated: setting a webhook). Events are POSTed as `{type:"StatementItem", data:{...}}`. The service must answer HTTP 200 within 5 seconds. Retries after 60 and 600 seconds. Disabled after the third failed attempt. | https://api.monobank.ua/docs/ (reader) |
| Personal token | CONFIRMED | Token for personal use (translated from "отримати токен для персонального використання"), obtained in the personal cabinet at https://api.monobank.ua/ | https://api.monobank.ua/docs/ (reader) |
| Corporate (service-provider) API is optional for personal use | CONFIRMED (extracted) | Summary of the page: corporate API use is "optional" for personal or family use where client data does not pass through your servers. Re-check the Ukrainian text before quoting. | https://api.monobank.ua/docs/ (WebFetch, extracted) |

### A.6 Ghostfolio Premium

| Claim | Verdict | Correct value | Source |
|---|---|---|---|
| Premium costs USD 48 per year | CONFIRMED | Premium plan on the pricing page: "USD 48 per year". Direct WebFetch returned only the page title, so the page was read via the reader proxy. | https://ghostfol.io/en/pricing (via https://r.jina.ai/https://ghostfol.io/en/pricing) |

## Part B: gap fills

### B.7 Enable Banking: free tier for personal use, conditions, Erste Bank

Answer: yes. Enable Banking's own Terms make the Control Panel and API free of charge, and allow production use for linked accounts for the personal use of private individuals. Limits: the number of linked accounts per application "may be limited", and no number is published.

Official Terms (https://enablebanking.com/terms/, "Last updated: January 9, 2026"):
- Pricing: "Use of the Control Panel and the API under these Terms is free of charge."
- Sandbox: "available to all users for evaluation and development purposes" (mock data and a limited number of bank sandboxes).
- Production: "limited to Linked Accounts and is available solely for evaluation purposes or for the personal use of private individuals. The number of Linked Accounts per Application may be limited."
- Linked Account: a payment account that the user associates with an application in the Control Panel, through the bank's SCA and consent flows.
- Not covered: "any business or professional purpose", including business accounts and accounts that do not belong to the Control Panel user. Business users may activate production only "solely for evaluation purposes" until Enable Banking gives written notice of deactivation.
- Outside these Terms: "a separate agreement with Enable Banking covering the intended use case and applicable pricing is required."
- AISP: "For communications with ASPSPs in the Production Environment, the API relies on Enable Banking acting as an authorised AISP." Under current Terms a personal app does not need its own AISP registration. The notes' November 2022 changelog claim (apps need AISP approval) is not repeated in the Terms and is now superseded for this purpose.

Other sources:
- Firefly III docs (source file): "free restricted mode ... without a paid subscription", with a sign-up through "Get Started" on enablebanking.com.
- Securo README: the free plan needs the accounts to be pre-linked in the Enable Banking portal before connecting from Securo, otherwise no accounts are returned. Securo also cites "PSD2 four-access-per-day limits" for polling. That is a bank-side rule; it was not checked in Enable Banking docs.
- Commercial pricing: https://enablebanking.com/pricing/ returns HTTP 404 (checked on 31 Oct 2026 via reader and WebFetch). The homepage mentions a "Get a Quote" tool (March 2026 changelog), so commercial pricing is quote-based. A third-party guide (search excerpt, not opened) says volume-based with a minimum monthly invoice. UNVERIFIABLE on an official page.
- Coverage: homepage says "2,700+ banks across 30 European countries". July 2025 changelog says "over 2,500 ASPSPs". Firefly tutorial says "2500+ banks across 29 European countries". Securo says "~2500". The homepage figure is the current one.

Erste Bank Austria (George):
- Enable Banking AT market page (https://enablebanking.com/docs/markets/at/, extracted): Erste Bank (Sparkasse) is listed first among Austria's main banks "in order of significance". "Erste Bank uses s Identity mobile application for SCA." "Users are required to input their user ID for the 'George' online/mobile banking." The only sandbox listed is Oberbank's. The page has no production-status line.
- Changelog, June 2026 (https://enablebanking.com/blog/2026/07/08/enable-banking-changelog-june-2026): "Erste Bank (AT, HU)" under fixed and improved integrations (line 136 of reader text).
- Changelog, October 2025 (https://enablebanking.com/blog/2025/11/05/enable-banking-changelog-october-2025): Erste Bank (AT) in a list (heading not read), and "all our integrations now default to 180 days" for consent validity.
- Verdict: the Erste integration is documented and maintained by Enable Banking (CONFIRMED). Live access for a personal Erste/George account is UNVERIFIABLE: it needs a Control Panel application, which requires an account. Not done, because account creation is outside this task.
- Practical implication (inference): plan for consent renewal about every 180 days. The notes' Sparkasse FAQ excerpt (not re-checked in this pass) says "180 calendar days" for a regional Sparkasse page, not Erste Bank Oesterreich.

### B.8 Sure and Securo: API, auth, multi-currency, net worth, investments

| Item | Sure (we-promise/sure) | Securo (securo-finance/securo) |
|---|---|---|
| Documented API | CONFIRMED. OpenAPI spec in repo at `docs/api/openapi.yaml` (paths `/api/v1/...`), plus endpoint guides (categories, chats, imports, merchants, tags, transactions, users). Source: https://github.com/we-promise/sure/tree/main/docs/api | NOT PUBLISHED as a docs page. The repo `docs/` folder holds feature docs and RFCs; https://docs.usesecuro.com/ describes features only (its only "API" matches are "FastAPI" mentions). The backend generates an OpenAPI schema at `/api/openapi.json` with Swagger at `/api/docs` when running (`backend/app/main.py`, lines 116-117). Not a published spec. |
| Auth | CONFIRMED. `securitySchemes`: `apiKeyAuth` (header `X-Api-Key`), `bearer` (opaque credential), `oauth2` (`/oauth/authorize`, `/oauth/token`). Source: openapi.yaml lines 13-30. | REST: fastapi-users `BearerTransport` with `tokenUrl="/api/auth/login"` (`backend/app/core/auth.py`, line 84). That implies a bearer token from a user login. Not tested. Separate MCP tokens: `POST /api/agents/mcp-tokens` (`backend/app/agents/api/mcp_tokens.py`), with bearer checks in `backend/mcp_server/auth.py`. |
| Other protocol | MCP endpoint for AI clients, JSON-RPC 2.0 (`docs/hosting/mcp.md`). | MCP server (`backend/mcp_server`) with tools for accounts, budgets, transactions, reports, rules and others. |
| Multi-currency | CONFIRMED at schema level: `enabled_currencies` and `custom_enabled_currencies` in family settings, and `currency` fields on accounts and balances (openapi.yaml, around lines 599-650). | CONFIRMED: README "Multi-currency support with automatic FX conversion". Without an Open Exchange Rates key, cross-currency amounts fall back to a 1:1 rate with a warning (README and docs site). Caveat for the Mini App. |
| Net worth | CONFIRMED: `GET /api/v1/balance_sheet`, "Returns the family balance sheet including net worth, total assets, ..." (openapi.yaml, line 5405). | CONFIRMED: README "Reports: Net Worth and Income vs Expenses". Docs site: "net worth tracking". |
| Investments | CONFIRMED at API level: `/api/v1/holdings` and `/api/v1/trades` (openapi.yaml, lines 7279 and 9773). | PARTIAL. README lists "Asset management with valuation tracking and growth rules" and does not claim a portfolio with trades. RFC #235 (`docs/rfc-235-investment-ledger.md`) is "Status: in progress" for ticker grouping, average price and a buy/sell ledger. Inference: a consolidated investment ledger is not shipped yet. |
| Maturity signal | 10,736 stars; last push 2026-10-31 (section A.1). | 4,152 stars; created 2026-03-08; last push 2026-10-30 (section A.1). |

Sure's API is documented well enough for a Mini App backend (X-Api-Key or OAuth2, plus balance sheet, holdings and trades). Securo's API is not documented as a published reference; its REST auth is a login-based bearer token, so a long-lived service token needs confirmation by a live test. Neither was tested live.

### B.9 Monobank and Telegram importers for Firefly III and Actual (gh search, 31 Oct 2026)

Searches were run as requested: "firefly monobank", "monobank firefly iii", "monobank actual budget", "privatbank firefly". Three extra searches were run: "monobank importer", "monobank" (keyword) and "firefly telegram" (for the Telegram angle).

| Repo | What it does | Stars | Created | Last push | License (GitHub) | Notes |
|---|---|---|---|---|---|---|
| mariko357/fireflyiii-monobank-importer | Monobank to Firefly III transactions (Python) | 1 | 2023-11-27 | 2024-01-14 | none detected | Uses a personal Monobank token and a Firefly token. Maps accounts, tags, budgets and categories in `config.yaml`. Run with `python main.py`. Stale for about 33 months. https://github.com/mariko357/fireflyiii-monobank-importer |
| mariko357/fireflyiii-monobank-importer-docker | Docker wrapper for the above | 0 | 2023-11-28 | 2023-11-29 | none detected | Stale. https://github.com/mariko357/fireflyiii-monobank-importer-docker |
| dnullproject/mono-to-actualbudget | Monobank to Actual Budget sync (JS, Docker) | 6 | 2024-01-17 | 2025-05-26 | Apache-2.0 | Env vars include `MONO_TOKEN`, `ACTUAL_URL`, `ACTUAL_SYNC_ID`, and card-to-budget mapping. Personal use. The README calls the author's JS "brutally bad" (self-assessment, treated as data). https://github.com/dnullproject/mono-to-actualbudget |
| holywag/ynab-monobank-importer | Monobank to YNAB | 0 | n/a | 2026-10-04 | n/a | Not Firefly or Actual. |
| smaugfm/monobudget | Monobank to YNAB or Lunch Money | 11 | n/a | 2025-01-06 | none detected | Not Firefly or Actual. |
| akutishevsky/monobank-mcp-server | MCP server for Monobank | 11 | n/a | 2026-10-06 | n/a | Not reviewed in detail. |
| vtopc/go-monobank | Go client, personal and corporate Monobank API | 24 | n/a | 2026-07-19 | n/a | Client library only. |

Searches with no results: "monobank firefly iii", "monobank actual budget", "privatbank firefly". No PrivatBank importer for Firefly III or Actual was found on GitHub.

Telegram (Firefly III bots, not importers; bridge bots are out of scope per the notes):
- AndresRzCh/firefly-telegram-bot: 1 star, last push 2026-08-30, "create expenses, revenues, and transfers with simple text commands". https://github.com/AndresRzCh/firefly-telegram-bot
- rodrigoaguilar96/fireflyiii-telegram-bot: 0 stars, last push 2026-06-01.
- qvanphong/fireflyiii-telegram-agent: 0 stars, last push 2025-11-15, "A Agent that help manage your Firefly III through Telegram chat".
- dkotama/firefly-telegram-assistant: 0 stars, last push 2025-03-23.
- RedRubyDev/FireflyTelegramBot: 0 stars, last push 2024-01-27.
- alejorodriguez96/firefly-telegram-bot: 1 star, last push 2022-11-07.

Impact on the notes: section 6 says that one search "found none" for a Monobank importer for Firefly III. That is now corrected: a Firefly importer exists (stale, 2024) and an Actual script exists (2025). Neither is native to the engine, so "each shortlisted engine needs a custom Monobank importer" still holds.

## Corrections to open_source_finance_engines.md

1. Ghostfolio latest release is 3.95.0 (2026-10-31), not 3.94.0 (2026-10-28).
2. GoCardless now has an official notice: "New signups for Bank Account Data are currently disabled." Section 5 said no such page exists.
3. Enable Banking free personal tier is now confirmed by its own Terms (Jan 2026). Section 4 and 6 rely on third-party sources for this.
4. Enable Banking AISP-approval claim (Nov 2022 changelog) is superseded: the current Terms say Enable Banking acts as the authorised AISP.
5. Enable Banking coverage: homepage says 2,700+ banks, 30 countries (notes say 2,500).
6. Sure API, multi-currency, net worth and holdings/trades are now confirmed from its OpenAPI spec (notes said API unverified).
7. Securo API is not a published reference; its REST auth is a login-based bearer token; investments are partial (RFC #235 in progress). Notes said "API not verified".
8. Monobank importers exist for Firefly III (stale, 2024) and Actual Budget (2025), both third-party. Notes said none found.
9. Sure is a "community fork" by description. GitHub does not list it as a fork.

## Not verified (follow-up)

- Erste Bank (AT) live access for a personal George account: needs a Control Panel application. Not done.
- The date GoCardless closed sign-ups: GoCardless has not stated it. The notes suggest asking GoCardless support directly; not done.
- Number of linked accounts allowed per Enable Banking application: not published.
- Securo: whether REST accepts a long-lived API token (only login bearer found in code). Not tested live.
- Live tests of any engine (create user, EUR/UAH/USD accounts, FX): not done.

## Overall reliability

- Part A (repo numbers, Monobank, Ghostfolio, Firefly and Actual API facts): HIGH. Repo records confirmed or updated; Monobank limits and webhook confirmed from the Monobank docs; Ghostfolio price confirmed from the pricing page. One wrong value (Ghostfolio release) and three claims unverifiable (GoCardless July 2025 date, GoCardless 50-requisition plan, Actual "browser build" attribution).
- Part B.7 (Enable Banking) and A.4 (GoCardless status): MEDIUM. Free personal tier confirmed by Enable Banking's Terms; GoCardless closure confirmed by GoCardless's own notice but undated; Erste integration documented and maintained, but personal live access and pricing unverified.
- Part B.8 and B.9 (Sure and Securo APIs, importers): MEDIUM-LOW. Sure's API is confirmed from its OpenAPI spec; Securo's API is not published and its investment support is partial; importers found are small and stale (last push 2024 and 2025).
