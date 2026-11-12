# Reference apps for a personal-finance tracker: UX, data model, APIs (as of 31 Oct 2026)

Scope and method (applies to all sections)
- Date of research: 31 Oct 2026. Prices and ratings are as seen on that day unless a different date is given.
- Ratings: Apple's public iTunes Search API, US storefront (country=us), queried 31 Oct 2026. Counts change daily. Store pages for AT and UA storefronts were also read where noted; their counts are far larger and are not comparable with US counts.
- Google Play: not collected.
- Reddit, Habr, vc.ru: no Reddit threads came up in search and Reddit was not fetched directly. Sentiment below is therefore thin and mostly from secondary blogs (labelled "secondary").
- Budget: 14 WebSearch calls used. About 40 WebFetch and Bash calls on primary pages, store pages and EUR-Lex.
- Several vendor pages returned 403, 404, or non-pricing content (Lunch Money site, Finary pricing, Wallet pricing, Monefy redirect, ZenMoney pricing numbers). Those are marked "not found", not estimated.
- EUR-Lex was fetched through a text proxy (r.jina.ai) because the direct fetch returned empty. Check the wording against EUR-Lex before quoting it in a legal document.
- One search snippet from a monobank API docs page contained text addressed to AI tools. It was ignored and not used.
- Secondary sources (getfinny.app, costbench.com, fincomparelab.com, unstar.app, subscribed.fyi) are labelled as secondary and are used only where no primary page was read.
- Text is paraphrased throughout; short quotes are kept only where the exact wording matters.

---

## 1. Which apps to study: candidate map and App Store ratings

### Takeaway
No candidate in the brief was confirmed as Telegram-first. The Telegram trackers found in search are open-source hobby projects known only from snippets. Strongest primary-source references: YNAB, Monarch, Copilot, ZenMoney, Toshl, Spendee, Kubera and getquin (model, API, net worth). Monefy is the simplest manual-entry reference. The bank apps for the two home markets are monobank (UA) and George (AT).

### Cited Findings

App Store ratings, US storefront, fetched 31 Oct 2026 (App Store link = public product page for that id):

| App (publisher as shown in the store) | App Store id | Avg | Ratings | Last version date shown | Link |
|---|---|---|---|---|---|
| YNAB (You Need A Budget LLC) | 1010865877 | 4.79 | 62,012 | 2026-10-28 | [App Store](https://apps.apple.com/app/id1010865877) |
| Monarch Money (Monarch Money, Inc.) | 1459319842 | 4.89 | 116,173 to 116,321 (two calls) | 2026-10-29 | [App Store](https://apps.apple.com/app/id1459319842) |
| Copilot Money (Copilot Money, Inc.) | 1447330651 | 4.75 | 30,784 to 30,812 (two calls) | 2026-10-27 | [App Store](https://apps.apple.com/app/id1447330651) |
| Zenmoney: expense tracker (Zenmoney OU) | 905934786 | 4.44 | 161 | 2026-10-05 | [App Store](https://apps.apple.com/app/id905934786) |
| Lunch Money (Lunchbag Labs Inc) | 6739028463 | 4.76 | 59 | 2026-10-08 | [App Store](https://apps.apple.com/app/id6739028463) (publisher not cross-checked with vendor site) |
| Toshl Finance (Toshl Inc) | 921590251 | 4.75 | 1,787 | 2024-12-13 | [App Store](https://apps.apple.com/us/app/id921590251) |
| Spendee (CLEEVIO s.r.o. per store; site copyright says SPENDEE a.s.) | 635861140 | 4.61 | 6,267 | 2026-10-27 | [App Store](https://apps.apple.com/app/id635861140) |
| Wallet by BudgetBakers (BudgetBakers s.r.o.) | 1032467659 | 4.56 | 5,931 | 2026-10-15 | [App Store](https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659) |
| Money Lover (Finsify Joint Stock Company) | 486312413 | 4.61 | 2,275 | 2026-10-22 | [App Store](https://apps.apple.com/us/app/money-lover-money-manager/id486312413) |
| Monefy (Reflective Technologies ApS) | 1212024409 | 4.72 | 6,795 to 6,803 (several calls) | 2026-10-30 | [App Store](https://apps.apple.com/app/id1212024409) |
| Money Manager Expense & Budget (Realbyte Inc.) | 560481810 | 4.82 | 19,677 to 19,693 (several calls) | 2026-10-26 | [App Store](https://apps.apple.com/app/id560481810) |
| Buddy: Budget Planner App (Buddy Budgeting AB) | 936422955 | 4.71 | 9,606 | 2026-10-18 | [App Store](https://apps.apple.com/app/id936422955) |
| Finary: Budget & Money Tracker (FINARY) | 1569413444 | 4.49 | 98 | 2026-10-29 | [App Store](https://apps.apple.com/app/id1569413444) |
| getquin - Portfolio Tracker (QUIN Technologies GmbH) | 1513629447 | 4.35 | 361 | 2026-10-30 | [App Store](https://apps.apple.com/app/id1513629447) |
| CoinKeeper 3 (Dizrapp OOO) | 1335547405 | 4.34 | 131 | 2026-10-27 | [App Store](https://apps.apple.com/app/id1335547405). Older listing id 849747345: 4.63, 1,600 ratings, last updated 2024-06-10 |
| Bluecoins Finance & Budget (GEOPRO GLOBAL SOLUTIONS INC. as shown) | 1590297575 | 3.77 | 78 | 2026-07-18 | [App Store](https://apps.apple.com/app/id1590297575) (publisher name not cross-checked) |
| Kubera | not found | - | - | - | Search returned only an unrelated "BMD Kubera" (id 6667113898) |
| 1Money | not found | - | - | - | No match in search |
| George Österreich (Erste Bank der oesterreichischen Sparkassen AG) | 947829367 | 4.85 (US) | 4,370 (US) | 2026-10-19 (US) | [App Store AT](https://apps.apple.com/at/app/george-%C3%B6sterreich/id947829367). AT storefront page read 31 Oct 2026: avg 4.8, 430,413 ratings, version 26.34.35 dated 19 Oct |
| monobank (UNIVERSAL BANK, PRAT) | 1287005205 | 4.88 (US) | 18,026 (US) | 2026-10-25 (US) | [App Store UA](https://apps.apple.com/ua/app/monobank/id1287005205). UA storefront page read 31 Oct 2026: 4.9 from 972k ratings, version 9.17 |
| Privat24 (PrivatBank) | 1333984846 | 4.87 | 8,542 | 2026-10-16 | [App Store](https://apps.apple.com/app/id1333984846) |
| Finanzguru (dwins GmbH) | 1214803607 | 4.65 | 95 | 2026-10-23 | [App Store](https://apps.apple.com/app/id1214803607) |

What each candidate is, from the sources read:
- YNAB: plan-first budgeting. Homepage says you decide what money is for before spending it; lists goals and a "Build a Buffer" option. Bank connections via Plaid. Source: [ynab.com](https://www.ynab.com/)
- Monarch: net worth and budgeting. Core is $14.99/month or $99.99/year. Plus tier is described for forecasting, multiple income sources and deeper investment tools (price not shown). Source: [monarch.com/pricing](https://www.monarch.com/pricing)
- Copilot: Apple-only (iPhone, iPad, Mac, Web). No Android. Households feature announced as "coming this fall" (year not stated). Source: [copilot.money/pricing](https://www.copilot.money/pricing)
- ZenMoney: free "Basic" manual budget; paid "Full Zen" (monthly, yearly or lifetime) adds reports, spending plans with trend comparison and bank connections. Company footer: ZenMoney OU, Tallinn, Estonia. Source: [zenmoney.app](https://zenmoney.app/)
- Spendee: wallet-based tracker with bank-account sync on all tiers; shared wallets on Premium and Plus; budgets on iOS and Android, web "coming soon". Source: [spendee.com/premium](https://www.spendee.com/premium)
- Toshl: entry-based tracker. Free tier: 2 financial accounts, 2 budgets, CSV export only. Bank sync only on the paid Medici tier. Source: [toshl.com/pricing](https://toshl.com/pricing)
- Monefy: manual tracker. Core app free; optional upgrade adds unlimited accounts, recurring transactions and advanced filters. Sync through Google Drive or Dropbox, not a vendor server. 150+ currencies. Site copyright 2025. Source: [monefy.com](https://www.monefy.com/) (monefy.me redirects here)
- Money Lover: multi-wallet tracker. App Store lists "Linked Wallet" (bank link) and "Budget Plus" subscriptions plus a lifetime Premium. Source: [App Store](https://apps.apple.com/us/app/money-lover-money-manager/id486312413)
- Wallet (BudgetBakers): "personal and family finance manager" per its site. App Store lists bank sync, multiple currencies and shared budgets. Source: [budgetbakers.com](https://budgetbakers.com/), [App Store](https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659)
- Kubera: net worth on one page; manual asset valuation by ticker; an AI appraiser for real estate, jewelry and watches; multi-currency "through every layer"; nested portfolios on the Black tier. Source: [kubera.com](https://kubera.com/)
- getquin: net worth tracking as core feature; retirement planning with scenarios; portfolio KPIs, asset allocation, dividend tracker, monthly cash-flow analysis; conversational assistant. Homepage marketing figures ("+20 B EUR tracked", "500k users") not verified. Source: [getquin.com](https://getquin.com/)
- Money Manager (Realbyte): free main app; separate paid listing "Money Manager (Remove Ads)" at $5.99 (id 564730202). Feature set not verified. Source: [App Store](https://apps.apple.com/app/id560481810)
- Lunch Money: API-first budgeting product. Marketing site returned 403, so no features were read. Source: [lunchmoney.dev](https://lunchmoney.dev)
- Buddy, CoinKeeper, Bluecoins, Finary, 1Money: identity and rating only; features not verified.

### Inferences
- Monarch and YNAB have the largest US review bases (116k and 62k), so their UX is the most stress-tested in public. Money Manager (Realbyte, 19.7k ratings) has the highest rating count among the manual-entry apps in the list.
- Rating counts are storefront-specific. AT and UA counts for George and monobank are far larger than the US counts, so they cannot be compared with US figures.

### Gaps
- Google Play ratings and counts: not collected.
- Quick-add flow (taps per transaction), widgets, SMS or push parsing, rules engine, envelope vs limit budgeting: not verified for any app. Verifying needs installing and using the apps, which was not done (no logins allowed).
- Kubera and 1Money: no App Store match found under these names.
- No candidate confirmed as Telegram-first. No commercial Telegram interface was found in search, but the search was not exhaustive.

---

## 2. Pricing in 2026 (dated, as seen on 31 Oct 2026)

### Takeaway
Prices are in USD as displayed on each primary page. No EUR or UAH prices were verified for any app, so none are converted. Single-user annual costs on primary pages range from about $20 (Toshl Pro, Money Lover lifetime) to $250 (Kubera Essentials). Where a primary page and aggregator disagree (Copilot, YNAB, Money Lover, Wallet), the primary page is used and the conflict is noted.

### Cited Findings
- YNAB: $14.99/month; $109/year billed annually (about $9.08/month). 34-day free trial, no card required. No free plan. One subscription covers up to 6 people in total. Prices in USD, "Copyright 2026" in footer. Source: [ynab.com/pricing](https://www.ynab.com/pricing), read 31 Oct 2026.
  - Conflict: one search summary mentioned a $99/year figure in an April 2026 article (article not identified). Primary page says $109; primary is used.
- Monarch (Core): $14.99/month or $99.99/year. Promo on the page: 30% off Core for one year with a code, for new users, annual Core only, code may expire. Plus price not shown. Household price not shown. Trial length not stated ("first week on us" headline; terms not shown). Source: [monarch.com/pricing](https://www.monarch.com/pricing), read 31 Oct 2026.
  - Secondary only: Plus about $199.99/year, per [getfinny.app](https://getfinny.app/blog/monarch-money-pricing-2026).
- Copilot: $9/month; $109/year billed yearly ("instead of $119", labelled a limited-time offer). Platforms: iPhone, iPad, Mac, Web. Source: [copilot.money/pricing](https://www.copilot.money/pricing), read 31 Oct 2026.
  - Conflict: secondary sites give $13/month or $95/year and a 1-month trial in one review and 7 days in another. Verify on the live page before using these numbers.
- ZenMoney: Basic free, Full Zen paid (monthly, yearly or lifetime) with a trial. Page says prices vary by country and gives no numbers. Source: [zenmoney.app](https://zenmoney.app/). Numbers: not found.
- Toshl: Free: 2 accounts, 2 budgets, CSV export. Pro: $2.99/month or $19.99/year. Medici (adds bank sync): $4.99/month or $39.99/year. Pro and Medici have a 30-day trial. Sources: [toshl.com/pricing](https://toshl.com/pricing) (trial and free tier), [App Store US](https://apps.apple.com/us/app/toshl-finance-best-budget/id921590251) (prices), both read 31 Oct 2026.
- Spendee: Premium $5.99/month or $35.99/year. Plus $1.99/month or $14.99/year. Basic free (1 cash wallet, 1 budget). 7-day trial on all plans. Page says prices may differ by country; currency is not named (dollar sign shown). Page copyright reads 2018, so may be stale. Source: [spendee.com/premium](https://www.spendee.com/premium), read 31 Oct 2026.
- Wallet (BudgetBakers): website shows no prices. App Store US shows unlabelled in-app prices: $5.99, $14.99, $29.99 (lifetime) and $49.99 (3-year), with no billing period. Free trial offered, length not stated. Sources: [budgetbakers.com](https://budgetbakers.com/), [App Store](https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659).
- Money Lover: App Store US lists Linked Wallet $2.99/month or $2.49/month, Budget Plus $2.99/month, lifetime Premium $19.99, 7-day trial on Linked Wallet. Source: [App Store US](https://apps.apple.com/us/app/money-lover-money-manager/id486312413), read 31 Oct 2026.
  - Conflict: an earlier search snippet of a US listing gave $2.49/month, $14.49/6 months, $19.99/year and a 3-day trial. Snippet source: [appfollow.io](https://appfollow.io/ios/money-lover-expense-manager/486312413?country=us). Not reconciled; the page read directly is used.
- Monefy: core free; upgrade price not shown. Source: [monefy.com](https://www.monefy.com/). Numbers: not found.
- Kubera: Essentials $250/year; Black $2,500/year (adds ownership tags, nested portfolios, AI setup and support, 1:1 calls); 14-day trial; no monthly price shown. Source: [kubera.com](https://kubera.com/), read 31 Oct 2026.
- getquin: prices not found on homepage. Source: [getquin.com](https://getquin.com/).
- Finary: pricing page returned 404. Source: [finary.com/pricing](https://finary.com/pricing). Numbers: not found.
- Lunch Money: site returned 403. Numbers: not found.
- Monobank, George, Privat24: free apps in the App Store (US and AT/UA storefronts). Sources: store links in section 1.
- Money Manager (Realbyte): main app free; separate paid listing "Money Manager (Remove Ads)" at $5.99 (App Store US, id 564730202).
- Secondary, Monarch Plus: about $199.99/year per [getfinny.app](https://getfinny.app/blog/monarch-money-pricing-2026).

### Inferences
- For a single user at primary-page USD list prices: YNAB $109/year, Monarch Core $99.99/year, Copilot $109/year (primary page), Spendee Premium $35.99/year, Toshl Medici $39.99/year, Kubera Essentials $250/year. Real costs in EUR or UAH will differ and need checking.
- Multi-user pricing: YNAB is per subscription (up to 6). Spendee has shared wallets on Premium and Plus. Copilot's households feature is not yet live per its page.

### Gaps
- EUR and UAH prices: not verified for any app.
- Lunch Money, Finary, getquin, Monefy, ZenMoney, Wallet, Money Lover (one primary source): exact current prices not found on primary pages.
- Trial length for Monarch and Copilot: conflicting or not stated.

---

## 3. Public APIs and exports

### Takeaway
Documented, official public APIs exist for YNAB, ZenMoney (OAuth2 with manual registration), Toshl, Lunch Money (v2) and monobank's personal API (partly read). Erste Group has a developer portal, but no George-specific personal API was found. No personal PrivatBank API was found. For the other candidates, no public API was found, but they were not searched one by one.

### Cited Findings

YNAB (official API docs at [api.ynab.com](https://api.ynab.com/), read 31 Oct 2026):
- Base URL https://api.ynab.com/v1. The older youneedabudget.com host still works but the docs say to switch.
- Authentication: personal access tokens (only for the account owner; the docs say to treat them like the account password and not to share them), or OAuth apps. OAuth access tokens expire after 2 hours; the Authorization Code grant includes refresh tokens. New OAuth apps are "restricted" to 25 authorizations until YNAB reviews them.
- Rate limit: 200 requests per hour per access token, rolling window; HTTP 429 when exceeded.
- Resources: plans (replacing budgets; the /budgets paths still work but are not documented), accounts, categories, months, payees, transactions, money movements and money movement groups, scheduled transactions. Mostly read-only with some POST, PATCH and DELETE endpoints.
- Not verified: whether API access requires a paid subscription, and whether the API is available during the trial.

ZenMoney (official-looking wiki, Russian, last edited 4 Aug 2023: [ZenMoney API wiki](https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API), read 31 Oct 2026):
- OAuth 2.0 authorization code flow against api.zenmoney.ru. Access tokens expire after 86,400 seconds (24 hours); refresh tokens are issued but refresh is not documented.
- Client registration: a Google Form. Only "real projects" that implement OAuth 2.0 get a consumer key and secret; review is manual.
- Personal token without registration: the wiki points to zerro.app, a third-party service.
- Main sync endpoint: diff (sends local changes plus last server timestamp; server returns its changes). Conflict rule: the server keeps its own copy if its change timestamp is newer.
- Suggest endpoint: given partial transaction data, returns suggested category, merchant or payee.
- Entities listed: instrument (currencies), company (banks and payment providers), user, account (types: cash, credit card, checking, loan, deposit, e-money, debt), tag (categories), merchant (counterparties), reminder and reminder marker (planned operations), transaction, budget. User entities can be created, changed and deleted; system entities are read-only.
- No rate limits, terms, licence or fees stated on the wiki page.
- Community clients (unofficial, not checked for maintenance): zenmoney-py and zenmoney-api on PyPI, zenmoney-rs on docs.rs, zenmoney-api on npm (search results only).

Toshl (official docs at [developer.toshl.com/docs](https://developer.toshl.com/docs), read 31 Oct 2026):
- Base URL https://api.toshl.com. HTTPS only, JSON only.
- Authentication: OAuth2 bearer tokens (separate OAuth page) or long-lived tokens generated in account settings. Users can revoke access at any time.
- Resources: entries (main object, including location, amount, timeline, review and "split undo"), accounts, categories, tags, budgets (with history), currencies, exports, images, reports, bank institutions, bank connections, bank imports, planning.
- Rate limit headers: X-RateLimit-Limit and X-RateLimit-Remaining. The example limit is 1000. Behaviour when exceeded not stated.
- Pagination: lists return 200 most recent items per page by default; per_page changes this; Link header with first, previous, next, last.
- Notes: the docs page does not describe the API as beta (last modified 8 Jan 2024). A search summary had said "beta"; the page read directly is used. Toshl does not provide exchange rates and suggests an external service (Open Exchange Rates). Data in the extra field stays private to the user and your app. Updates must not change the read-only modified field (400 if they do); conflicts return 409.
- Exports: CSV on the free plan ([toshl.com/pricing](https://toshl.com/pricing)).

Lunch Money (developer site [lunchmoney.dev](https://lunchmoney.dev), read 31 Oct 2026):
- v2 API at https://api.lunchmoney.dev/v2. Not backwards compatible with v1. Bearer token from the developers page.
- Rate-limit guide linked but not read. Write support not confirmed on the page.
- Legacy v1 changelog (search snippet only, [support.lunchmoney.app](https://support.lunchmoney.app/importing-transactions/developer-api)) mentions a transaction group endpoint, filters on tag, category and asset, and a skip_balance_update flag. Snippet only, not read in full.
- A Python SDK, lunchable, wraps the developer API (search result, [PyPI](https://pypi.org/p/lunchable)).

monobank personal API (docs at [api.monobank.ua/docs](https://api.monobank.ua/docs/), partly read; read 31 Oct 2026):
- Endpoints: client info (GET), set webhook (POST), statement (GET).
- Token: obtained by logging into the personal cabinet on the monobank API site.
- Not available to clients under 16. Under-16 child accounts are reachable through the parent's account.
- Statement returns at most 500 transactions per call, sorted backwards from the end of the period; paginate by moving the to-time back. Source: [monobank community docs](https://github.com/andrew-demb/monobank-api-community-docs), which describes itself as an unofficial personal initiative provided as-is.
- Rate limit: the official page was truncated and no numeric limit was captured. The community doc says to keep request frequency to the docs and that excessive use can trigger a 403 block for about 24 hours. An older community README (search snippet, [hackage](https://hackage-content.haskell.org/package/api-monobank-0.1.0.1/src/README.md)) reports a one-call-per-60-seconds cap and a 31-day statement limit; unverified.
- Auth header name: not confirmed in the text read. The community doc names an auth token but no header for the personal API.

monobank open banking, third-party access (program, not live as of read; [monobank.ua/en/openbanking](https://monobank.ua/en/openbanking)):
- Status: page says interfaces will be available after technical implementation completes. No launch date given.
- Scope: account balance and transaction history (31 days) with consent; payment initiation.
- Consent per account, up to 180 days, confirmed by push in the app. Up to 4 requests a day without re-confirmation.
- Sandbox available; production only after two testing stages.

Erste Group / George:
- Erste's 2019 press release names its developer portal as the central access point for PSD2 APIs (documentation, access, sandbox). Source: [erstebank.hr press release](https://www.erstebank.hr/en/press/press-releases/2019/6/11/ready-for-psd2-and-open-banking-erste-group-provides-unified-access-to-the-apis-of-all-its-subsidiary-banks-in-the-eastern-part-of-the-eu).
- [developers.erstegroup.com](https://developers.erstegroup.com/) returned only its heading when read. Current status and access terms not verified.
- A third-party listing ([Open Banking Tracker](https://www.openbankingtracker.com/provider/erste-bank-and-sparkassen)) lists Erste under a Berlin Group 1.3 standard with an aggregator. Auto-generated listing, low confidence.
- No George-specific personal API found.

PrivatBank:
- No official personal API found. Third-party clients (e.g. [python-privatbank-client](https://pypi.org/project/python-privatbank-client/)) get tokens from "Privat24 for Business" Autoclient, a product for companies and sole proprietors.

Other candidates: no public API found in search, and no API mention on the primary pages read (Kubera's page does not mention API or export; Monefy's page does not mention one). Spendee, Monarch, Copilot, Money Lover, Wallet, getquin, Finary, Money Manager were not searched individually.

### Inferences
- For a Telegram bot that writes to a tracker, YNAB (write endpoints with PAT) and Toshl (write, with conflict handling) are the most plug-in-ready. Lunch Money v2 is also a candidate but write support is not confirmed.
- Bank data for the user's own George and PrivatBank accounts: no personal API is available. Realistic routes are official exports or a licensed aggregator (see section 7 on PSD2).

### Gaps
- Exports other than Toshl CSV: not verified for any candidate.
- Erste/George developer portal current status and terms: not verified.
- Monobank rate limits and auth header: not captured from official docs.
- YNAB API access on trial or free plan: not verified.
- Lunch Money write support and rate limits: not verified.

---

## 4. Bank-sync coverage for Austria (Erste/George) and Ukraine (PrivatBank, monobank)

### Takeaway
No candidate was confirmed to sync Erste/George or PrivatBank accounts from a primary source. ZenMoney's bank-plugin repo has no Austrian bank and no PrivatBank or monobank folder among the folders visible in its listing. Monobank is the only UA bank with an open personal API. George and PrivatBank have no personal API found.

### Cited Findings

Austria:
- ZenMoney: site says it connects "any UK, European and many international banks" and "over 3,300 banks worldwide". No Austrian bank named. Source: [zenmoney.app](https://zenmoney.app/).
- ZenPlugins repo (GPL-3.0 licence per repo page; TypeScript; plugins run on the user's device and call the bank's service): the visible folder listing (first 100 folders) has no erste, george, sparkasse, bawag, bank-austria or bks folder. A raiffeisen-rs folder exists but its suffix points to Serbia. Full listing not checked. Source: [ZenPlugins repo](https://github.com/zenmoney/ZenPlugins), [plugin folders](https://github.com/zenmoney/ZenPlugins/tree/master/src/plugins).
- Spendee: bank-account sync listed on all tiers; no list of banks or countries on the page. Source: [spendee.com/premium](https://www.spendee.com/premium).
- Wallet (BudgetBakers): website says "15K+ bank connections"; App Store says "about 4,000 banks worldwide". Countries not named. Conflicting counts. Sources: [budgetbakers.com](https://budgetbakers.com/), [App Store](https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659).
- Toshl: bank sync only on Medici tier; regions not stated. Source: [toshl.com/pricing](https://toshl.com/pricing).
- getquin: connects accounts through "thousands of providers"; Austria not mentioned. Source: [getquin.com](https://getquin.com/).
- YNAB: connects via Plaid, which provides account information services through YNAB as its agent (UK FCA cited in footer). Countries not listed; Austria not mentioned. Source: [ynab.com](https://www.ynab.com/).
- Monarch: pricing page links to bank connections but the content was not read; Europe and Austria not mentioned on pricing page. Source: [monarch.com/pricing](https://www.monarch.com/pricing).
- Money Lover (Linked Wallet): regions not verified.
- Finanzguru: App Store listing exists (dwins GmbH). Austrian bank list not found in search. Source: [App Store](https://apps.apple.com/app/id1214803607).
- Erste itself: the George AT App Store page describes an overview of all accounts and cards. Source: [App Store AT](https://apps.apple.com/at/app/george-%C3%B6sterreich/id947829367).

Ukraine:
- ZenPlugins visible folder names with UA suffix or Ukrainian bank names: alfabank-ua, kredobank-ua, otpbank-ua, oschadbank, pumb, ukrsibbank. No privatbank or monobank folder in the visible listing. Direct paths src/plugins/privatbank and src/plugins/monobank both returned HTTP 404. Full listing (truncated at 100) not checked.
- monobank: own personal API (see section 3). Open banking for third parties not live as of read.
- PrivatBank: no personal API found; third-party clients target Privat24 for Business.
- None of the other candidates' primary pages read list Ukrainian bank support.

### Inferences
- For Erste/George and PrivatBank the realistic data path is manual or official export (no personal API found), a licensed aggregator, or the bank's own app. Screen-scraping logins is not recommended (see section 7).
- The ZenMoney plugin model (bank connector as a per-bank plugin, with a diff-based sync) is the closest existing pattern for Austria or Ukraine if coverage is added later, but there is no evidence of an existing AT or PrivatBank plugin.

### Gaps
- Erste/George coverage in any candidate: not confirmed.
- PrivatBank coverage in any candidate: not confirmed.
- Full ZenPlugins folder list, including folders after the first 100: not checked.
- Monarch bank-connections page: not read.

---

## 5. Built-in analytics in monobank and George

### Takeaway
Neither bank app's store page describes spending categories, budgets or spend analysis. Monobank's categories appear only in the monthly cashback selection. George focuses on overview, savings goals and payments. This needs confirming by using the apps, which was not done.

### Cited Findings

monobank (UA App Store, version 9.17, read 31 Oct 2026; [store page](https://apps.apple.com/ua/app/monobank/id1287005205)):
- Spending analysis, budgets, charts and savings jars: not described.
- Categories: monthly cashback categories are chosen by the user (grocery, taxi, fuel, cafes, books named). Source: same page.
- Group expenses with friends and accepting payments from the phone: mentioned, no detail.
- Currency: buy and sell currency in the app with exchange rate shown before confirmation; a EUR card can show amounts in UAH or EUR by tapping the currency symbol (developer reply).
- Statements: extended statement allows photo attachments on payments (release notes).
- Fees, limits and rates are shown before a transaction is confirmed.
- Other: favourite payments, blocking a user from seeing transfer details (release note), marketplace and installments, Diia.Card, business portal.

George (Austrian App Store page, read 31 Oct 2026; [store page](https://apps.apple.com/at/app/george-%C3%B6sterreich/id947829367)):
- Quick financial overview; all accounts and cards in one place; personal insights and tips (no detail).
- Savings goals in the George FIT section: target amounts and periods, can link products.
- Split a card transaction and share a QR code so others can pay their share.
- Scan and pay, Apple Pay, investing (stocks, funds, ETFs), credit offers, advisor chat.
- Spending categories, expense analysis and budgets: not described on the page.
- Language count: 17. Accessibility options listed.
- Rating (AT store): 4.8 from 430,413 ratings; version 26.34.35 dated 19 Oct (year not shown).

### Inferences
- Neither store listing describes spending analysis. That may leave room for an external tracker that imports their statements.
- The monobank "photo attachments on statement items" note is a useful pattern for receipt capture in a tracker.

### Gaps
- Spending categories and charts in George and monobank in-app: not verified (requires login, not allowed).
- Monobank's in-app analytics screen: not found in the store page.

---

## 6. Data-model patterns worth copying

### Takeaway
Use ZenMoney's entity split (instrument, company, account type, tag, merchant, reminder), YNAB's plan-scoped resources (accounts, categories, months, payees, transactions, money movements), and Toshl's entry model (extra field for app-private data, read-only modified field, conflict handling). Store original amount and currency and convert through your own FX table, because Toshl provides none. Keep net-worth assets with manual valuations (Kubera model).

### Cited Findings
- Entity split: ZenMoney separates currencies (instrument), banks (company), accounts with types, categories (tags), counterparties (merchants), and planned operations (reminders). Source: [ZenMoney API wiki](https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API).
- Account types in ZenMoney: cash, credit card, checking, loan, deposit, e-money, debt. Source: same.
- Sync: diff with server timestamp; server copy wins if its change time is newer. Source: same.
- Suggest endpoint: returns category, merchant or payee for a partial transaction. Source: same.
- YNAB resources: plans contain accounts, categories, months, payees, transactions, money movements (and money movement groups), scheduled transactions. Source: [api.ynab.com](https://api.ynab.com/).
- Toshl entries: the main object, with location, amount, timeline, review and split undo. Tags are a separate resource from categories. Budgets have history. Source: [developer.toshl.com/docs](https://developer.toshl.com/docs).
- Toshl extra field: data stored there stays private to the user and the app that wrote it. Source: same.
- Toshl concurrency: the modified field is read-only, updates that change it return 400, and conflicts return 409. Source: same.
- Multi-currency: Kubera says multi-currency runs through every layer of the product. Source: [kubera.com](https://kubera.com/). Toshl leaves FX rates to an external provider. Source: [developer.toshl.com/docs](https://developer.toshl.com/docs).
- Asset valuation: Kubera tracks manual positions by ticker and uses an AI appraiser for real estate, jewelry and watches. Source: [kubera.com](https://kubera.com/). getquin tracks net worth alongside portfolio KPIs and retirement scenarios. Source: [getquin.com](https://getquin.com/).
- Shared budgets: Spendee has shared wallets on Premium and Plus ([spendee.com/premium](https://www.spendee.com/premium)); YNAB covers up to 6 people per subscription ([ynab.com/pricing](https://www.ynab.com/pricing)); Copilot households not yet live ([copilot.money/pricing](https://www.copilot.money/pricing)); Wallet lists shared budgets on the App Store ([App Store](https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659)).
- Original currency with reporting currency (open-source Telegram tracker, snippet only): LimeBalance keeps each entry in its original currency and converts to USD for reporting. Source: [github.com/Alexi-creator/limebalance](https://github.com/Alexi-creator/limebalance) (search snippet, repo not read).
- Automatic FX updates (snippet): Scrooge, a self-hosted assets and expenses service, updates exchange rates automatically. Source: [github.com/maximten/scrooge](https://github.com/maximten/scrooge) (snippet).
- Receipt capture (bank app): monobank extended statements allow photo attachments per payment. Source: [App Store UA](https://apps.apple.com/ua/app/monobank/id1287005205).
- Split transactions: Toshl has a split-undo operation on entries. George can split a card payment for sharing. Sources: [developer.toshl.com/docs](https://developer.toshl.com/docs), [App Store AT](https://apps.apple.com/at/app/george-%C3%B6sterreich/id947829367).

### Inferences
- The entity split in ZenMoney is the cleanest reference for a tracker that wants accounts, categories, counterparties, currencies and banks as separate tables.
- A tracker should store the original amount and currency per transaction and keep a dated FX table for net-worth conversion. No candidate's primary page documents historical FX handling, so this is inference from the Toshl and LimeBalance patterns.
- Single-entry (transactions with transfers) looks like the model in YNAB and ZenMoney from their resource lists. This is inference only.

### Gaps
- Double-entry vs single-entry: no primary source examined.
- Historical FX rates in any commercial candidate: not verified.
- Net-worth snapshot history (time series of asset valuations) in any candidate: not verified.
- Tags as a separate concept in YNAB and Monarch: not verified.

---

## 7. Reverse engineering in the EU: what is allowed

### Takeaway
Studying how a program functions, while using it legitimately, is permitted by Directive 2009/24/EC Article 5(3). Ideas and principles, including those behind interfaces, are not protected by that Directive (Article 1(2)), so UX patterns and features are not protected as such. Decompiling code is allowed only for interoperability and under strict conditions in Article 6. Copying code, UI graphics, text or databases is outside these exceptions. Calling private APIs against a provider's terms is a contractual and practical risk. Bank-account access is regulated under PSD2.

### Cited Findings (paraphrased)
- Directive 2009/24/EC, Article 1(2): only the expression of a computer program is protected; ideas and principles behind any element, including interfaces, are not protected under the Directive. Source: [EUR-Lex, CELEX:32009L0024](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024) (read via text proxy).
- Recital 11 says the same and extends it to logic and algorithms insofar as they are ideas. Same source.
- Article 5(3): a person entitled to use a copy may observe, study or test how the program works, to determine the ideas and principles behind it, while doing acts they are entitled to do (loading, displaying, running, transmitting, storing). Same source.
- Recital 14: such study is allowed provided it does not infringe copyright in the program. Same source.
- Article 6(1): reproducing code and translating its form (decompilation) is allowed only if indispensable to get information needed for interoperability with an independently created program, if the information was not readily available before, and if the acts are confined to the necessary parts of the original. Same source.
- Article 6(2): information obtained this way may not be used for other goals, given to others (except for interoperability), or used to develop a substantially similar program. Same source.
- Article 6(3): the Article must not be applied so as to unreasonably prejudice the rightholder. Same source.
- Recital 16: contract terms that override the decompilation or observation exceptions are void. The Directive's closing contractual-override provision (printed after Article 8 in the text read) says the same for Article 6 and Article 5(2)-(3). Article number not confirmed in the rendering. Same source.
- PSD2, Directive (EU) 2015/2366: defines an account information service (consolidated information on payment accounts held with one or more providers) and an account information service provider as a regulated payment-service provider. Recitals describe these services as provided with the account holder's consent, under a licensing and registration regime. Source: [EUR-Lex, CELEX:32015L2366](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366) (read via text proxy; article numbers not confirmed).

### Inferences
- Allowed: reading and documenting an app's features and UX from your own use, public docs, store listings and screenshots; using official APIs and exports; designing your own data model from public docs.
- Not allowed or high risk: copying code, icons, illustrations, copy text, layouts closely enough to be a copy, or datasets such as merchant or category lists without a licence; calling undocumented private APIs against a provider's terms.
- Bank accounts: reading George or PrivatBank accounts with stored logins is a regulated activity under PSD2 and a terms-of-service risk. Use official exports or a licensed aggregator.
- Austrian implementation (UrhG) and the database right were not checked; both should be checked before copying any dataset.

### Gaps
- Austrian UrhG text (for national implementation of the Software Directive) not fetched.
- Database Directive 96/9/EC not fetched.
- GDPR rules for financial data not researched.
- George and monobank API terms of use not read.

---

## 8. Best 3 to 5 references for a Telegram-first, fast-input, multi-currency, net-worth-aware tracker

### Takeaway
Use ZenMoney, YNAB, Kubera and Toshl as the primary references, Monefy as the fast manual-entry baseline, and open-source Telegram bots (LimeBalance, SmartExpenseBot, Scrooge) for bot architecture and FX handling at snippet-level confidence.

### Cited Findings

1. ZenMoney: data model and sync.
   - Take: entity split (currency, bank, account type, category, counterparty, planned operations); diff sync with server timestamps; suggest endpoint for auto-category or merchant. Sources: [ZenMoney API wiki](https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API).
   - Plugin model for banks (per-bank connector) from [ZenPlugins](https://github.com/zenmoney/ZenPlugins). Licence GPL-3.0. Study the architecture, do not copy code.
   - Caveat: no Austrian or PrivatBank support seen. Basic free manual tier vs Full Zen paid tier is a clear model.

2. YNAB: account, category and month model; personal-token API.
   - Take: plan-first UX ("decide what money is for before spending"); API resources (plans, accounts, categories, months, payees, transactions, money movements); personal access token for a single-user bot; rate limit 200 requests per hour per token. Sources: [ynab.com](https://www.ynab.com/), [api.ynab.com](https://api.ynab.com/).
   - Caveat: bank connection via Plaid with no country list (UK FCA cited in footer); $109/year; no envelope method described on the homepage.

3. Kubera: net-worth model.
   - Take: manual valuation by ticker, AI-assisted valuation for illiquid assets (real estate, jewelry, watches), multi-currency through every layer, nested portfolios. Source: [kubera.com](https://kubera.com/).
   - Caveat: Essentials $250/year; Black $2,500/year; no monthly price.

4. Toshl: entries API and concurrency.
   - Take: entries as main object with split undo; extra field for app-only metadata; read-only modified field with 400 and 409 conflict rules; 200-item pages with Link header; FX delegated to an external provider. Source: [developer.toshl.com/docs](https://developer.toshl.com/docs).
   - Caveat: free tier 2 accounts and 2 budgets; bank sync only on Medici tier ($39.99/year, US App Store).

5. Monefy: fast manual entry baseline (UX not verified).
   - Take: core free, optional upgrade for unlimited accounts and recurring entries; sync via Google Drive or Dropbox with no vendor server. 6.8k App Store ratings, 4.72 average. Source: [monefy.com](https://www.monefy.com/), [App Store](https://apps.apple.com/app/id1212024409).
   - Caveat: the entry-flow speed and tap count are not measured.

Telegram-first open-source references (snippet only, licence and maintenance not verified):
- SmartExpenseBot: natural-language entry that extracts amount, currency and category; voice input; multi-currency including EUR, USD, RUB and UZS. Source: [GitHub release 1.1.0](https://github.com/BotirBakhtiyarov/SmartExpenseBot/releases/tag/1.1.0).
- LimeBalance: NestJS, grammY, Prisma, PostgreSQL, REST API, Docker; original currency kept, USD reporting. Source: [GitHub](https://github.com/Alexi-creator/limebalance).
- SpendSnap: logs expenses from text and receipt screenshots, handles EUR and other currency formats; LangGraph and Groq. Source: [GitHub](https://github.com/Kusagra9308/SpendSnap).
- Scrooge: self-hosted assets and expenses through a Telegram bot; automatic FX rates. Source: [GitHub](https://github.com/maximten/scrooge).
- DollarBot: Python, MIT licence, daily expense logging; multi-currency not shown in snippet. Source: [GitHub](https://github.com/ymdatta/DollarBot).

### Inferences
- Patterns to combine: ZenMoney's entity split and diff sync; YNAB's token model and resource list; Kubera's net-worth valuation; Toshl's conflict rules and external FX; LimeBalance's original-currency storage with a reporting currency.
- The quick-add flow (taps per transaction), widgets and SMS or push parsing were not measured for any app. Measuring them needs Misha or someone with access to install and use the apps. No logins were attempted.

### Gaps
- Telegram-first commercial product: not found in this session.
- Quick-add flow, widgets, SMS or push parsing, rules, shared-budget mechanics beyond the listed facts: not verified.
- Reddit and vc.ru user sentiment: not collected. Secondary blog only: a promotional roundup at [unstar.app](https://unstar.app/it/blog/ynab-vs-rocket-money-vs-monarch-budgeting-apps-ranked-2026) says bank connections break often and that reviewers resent Monarch's roughly $100 yearly price; not reliable.
- Google Play ratings: not collected.
