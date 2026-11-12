# Verification: reference_apps_reverse_engineering.md

Checked on 31 October 2026. Input file not modified.

Method: WebFetch on official pages and App Store product pages; iTunes Lookup and Search API (country=us); text proxy (r.jina.ai) for the monobank docs and EUR-Lex; 4 WebSearch calls.

Notes on method:
- The iTunes Search and Lookup endpoints disagree on Monefy's last-update date (Search: 2026-08-26; Lookup: 2026-10-30). Lookup is used below.
- Toshl prices come from the US App Store product list. toshl.com/pricing shows no prices.
- ZenMoney ruble prices come from zenmoney.ru/a/. A search snippet of the same page gave the same figures.
- Rating counts move daily. The values below are the 31 October readings.

## 1. Prices

| # | Claim (from notes) | Verdict | Correct value | Source URL |
|---|---|---|---|---|
| A1 | YNAB: $14.99/month | CONFIRMED | $14.99 USD per month | https://www.ynab.com/pricing |
| A2 | YNAB: $109/year | CONFIRMED | $109 USD paid annually (shown as $9.08/month) | https://www.ynab.com/pricing |
| A3 | YNAB: 34-day free trial | CONFIRMED | 34 days; no card needed when signing up directly with YNAB (app stores may ask for one) | https://www.ynab.com/pricing |
| A4 | YNAB: no free plan; up to 6 people per subscription | UNVERIFIABLE | Not stated in the page text read | https://www.ynab.com/pricing |
| A5 | Monarch: $14.99/month (Core) | CONFIRMED | $14.99 USD per month. Tier not labelled on the page; the promo names the "annual Core plan", so the price is Core's | https://www.monarch.com/pricing |
| A6 | Monarch: $99.99/year (Core) | CONFIRMED | $99.99 yearly. Promo: 30% off Core for one year with code WELCOME, new users, annual plan only | https://www.monarch.com/pricing |
| A7 | Monarch: trial length not stated | CONFIRMED (partly) | Headline "Your first week is on us". Terms were not read, so the length is not confirmed beyond that | https://www.monarch.com/pricing |
| A8 | Monarch Plus about $199.99/year | UNVERIFIABLE | No Plus price on monarch.com/pricing. The only figure is from getfinny.app (secondary source) | https://www.monarch.com/pricing |
| A9 | Copilot: $9/month or $109/year (primary page) | CONFIRMED | $9 per month. $109 billed yearly, "instead of $119", tagged "limited time offer" | https://www.copilot.money/pricing |
| A10 | Copilot: conflict with $13/month and $95/year | WRONG (secondary sites) | The $13 and $95 figures are not on the primary page. Current primary values: $9/month or $109/year | https://www.copilot.money/pricing |
| A11 | Copilot: 1-month or 7-day trial | UNVERIFIABLE | Trial length is not stated on the page | https://www.copilot.money/pricing |
| A12 | Spendee Premium $5.99/month | CONFIRMED | $5.99/Month. Dollar sign shown, no currency code. Page says prices "might differ based on the country" | https://www.spendee.com/premium |
| A13 | Spendee Premium $35.99/year | CONFIRMED | $35.99/Year | https://www.spendee.com/premium |
| A14 | Spendee: 7-day trial on all plans | CONFIRMED | "All plans come with 7-day free trial period!" | https://www.spendee.com/premium |
| A15 | Spendee: page copyright 2018 | UNVERIFIABLE | Not checked | https://www.spendee.com/premium |
| A16 | Toshl Pro $19.99/year | CONFIRMED (source differs) | toshl.com/pricing shows no prices. US App Store product "Toshl Pro $19.99" (yearly). Pro monthly is $2.99. Period taken from the plan description on the store page | https://apps.apple.com/us/app/toshl-finance-best-budget/id921590251 |
| A17 | Medici $39.99/year | CONFIRMED (source differs) | US App Store product "Toshl Medici $39.99" (yearly). Medici monthly is $4.99 | https://apps.apple.com/us/app/toshl-finance-best-budget/id921590251 |
| A18 | Toshl: 30-day trial (Pro and Medici); free tier with 2 accounts, 2 budgets, CSV export | CONFIRMED | "Try Toshl Pro or Medici for the first month without charge". Free plan: 2 financial accounts, 2 budgets, CSV export | https://toshl.com/pricing |
| A19 | Kubera $250/year | CONFIRMED | Essentials $250/year. Black $2500/year (ownership tags, nested portfolios, AI setup, 1:1 calls) | https://kubera.com/ |
| A20 | Kubera: 14-day trial, annual billing only | CONFIRMED | "Try for 14 days". Both plans priced annually; no monthly option | https://kubera.com/ |
| A21 | ZenMoney: official prices "not found" | WRONG (incomplete) | zenmoney.ru/a/ lists 199 RUB per month, 1,490 RUB per year (about 125 RUB/month), and 2,990 RUB lifetime. The paid plan is called "Премиум" (Premium) on the page. Trial length not stated. zenmoney.app shows no numbers and says prices vary by country. The dollar strings in the fetch summary are inconsistent with the ruble figures; do not use them | https://zenmoney.ru/a/ ; https://zenmoney.app/ |
| A22 | Wallet (BudgetBakers): website shows no prices | CONFIRMED | budgetbakers.com shows no prices; budgetbakers.com/pricing returns 404. Help center: Premium is offered monthly, yearly or lifetime, and prices are shown in the app | https://budgetbakers.com/ ; https://support.budgetbakers.com/hc/en-us/articles/7151349344018-Everything-about-Premium |
| A23 | Wallet App Store prices: $5.99, $14.99, $29.99 (lifetime), $49.99 (3-year); no billing period | CONFIRMED (partly) | In-app list: "Premium $5.99", "Premium $14.99", "Lifetime Premium $29.99", "3-Year Premium $49.99", plus a second unlabelled "Premium $29.99". No billing period shown | https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659 |
| A24 | Wallet: free trial offered, length not stated | UNVERIFIABLE | No trial mentioned on the store page as fetched | https://apps.apple.com/us/app/wallet-daily-budget-profit/id1032467659 |
| A25 | Money Manager (Remove Ads) $5.99 (id 564730202) | CONFIRMED | $5.99 (formattedPrice in the App Store lookup) | https://itunes.apple.com/lookup?id=564730202&country=us |

Prices summary: 18 confirmed (2 of them partly), 2 wrong, 5 unverifiable, of 25 claims.

## 2. US App Store ratings (31 October 2026)

| # | App | Notes said (avg / ratings / last update) | Verdict | Correct value (avg / ratings / last update) | Source URL |
|---|---|---|---|---|---|
| B1 | YNAB (id 1010865877) | 4.79 / 62,012 / 2026-10-28 | CONFIRMED | 4.79 / 62,022 / 2026-10-28 | https://itunes.apple.com/lookup?id=1010865877&country=us |
| B2 | Monarch (id 1459319842) | 4.89 / 116,173-116,321 / 2026-10-29 | CONFIRMED | 4.89 / 116,321 / 2026-10-29 | https://itunes.apple.com/lookup?id=1459319842&country=us |
| B3 | Copilot (id 1447330651) | 4.75 / 30,784-30,812 / 2026-10-27 | CONFIRMED | 4.75 / 30,798-30,812 / 2026-10-27 | https://itunes.apple.com/lookup?id=1447330651&country=us |
| B4 | Money Manager, Realbyte (id 560481810) | 4.82 / 19,677-19,693 / 2026-10-26 | CONFIRMED | 4.82 / 19,682-19,693 / 2026-10-26 | https://itunes.apple.com/lookup?id=560481810&country=us |
| B5 | Monefy (id 1212024409) | 4.72 / 6,795-6,803 / 2026-10-30 | CONFIRMED | 4.72 / 6,797-6,799 / 2026-10-30 (Lookup). Search endpoint shows 2026-08-26 for the same id; Lookup used | https://itunes.apple.com/lookup?id=1212024409&country=us |
| B6 | Spendee (id 635861140) | 4.61 / 6,267 / 2026-10-27 | CONFIRMED | 4.61 / 6,266 / 2026-10-27 | https://itunes.apple.com/lookup?id=635861140&country=us |
| B7 | Wallet by BudgetBakers (id 1032467659) | 4.56 / 5,931 / 2026-10-15 | CONFIRMED | 4.56 / 5,931 / 2026-10-15 | https://itunes.apple.com/lookup?id=1032467659&country=us |
| B8 | ZenMoney (id 905934786) | 4.44 / 161 / 2026-10-05 | CONFIRMED | 4.44 / 161 / 2026-10-05 (version 26.8) | https://itunes.apple.com/lookup?id=905934786&country=us |

Ratings summary: 8 of 8 confirmed.

## 3. APIs and exports

| # | Claim (from notes) | Verdict | Correct value | Source URL |
|---|---|---|---|---|
| C1 | YNAB base URL | CONFIRMED | https://api.ynab.com/v1. The older youneedabudget.com host still works | https://api.ynab.com/ |
| C2 | YNAB: personal access token or OAuth | CONFIRMED | Personal access token is for the account owner only; OAuth is for other users. Both are sent as Bearer tokens | https://api.ynab.com/ |
| C3 | YNAB rate limit 200 requests per hour per token | CONFIRMED | 200 requests per hour per access token, rolling window; HTTP 429 when exceeded | https://api.ynab.com/ |
| C4 | YNAB OAuth tokens last 2 hours | CONFIRMED (grant detail) | Implicit Grant tokens last 2 hours with no refresh. Authorization Code Grant supports refresh tokens | https://api.ynab.com/ |
| C5 | YNAB new OAuth apps limited to 25 authorisations until reviewed | CONFIRMED (partly) | Restricted Mode: up to 25 access tokens for non-owner users. The review step that lifts the limit was not read | https://api.ynab.com/ |
| C6 | YNAB API needs a paid plan | UNVERIFIABLE | The page lists errors "subscription lapsed" (403.1) and "trial expired" (403.2) but does not state a plan requirement | https://api.ynab.com/ |
| C7 | YNAB: POST and PATCH on transactions | CONFIRMED (partly) | Page: "some POST, PATCH, and DELETE requests on several resources". Changelog refers to transaction POST and PATCH. Exact endpoints are not on the page | https://api.ynab.com/ |
| C8 | ZenMoney: OAuth2 at api.zenmoney.ru | CONFIRMED | Host api.zenmoney.ru; /oauth2/authorize/ and /oauth2/token/ | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C9 | ZenMoney: access token lifetime 86,400 s | CONFIRMED (sample only) | "expires_in": 86400 appears in a sample response. The page does not state it as a rule | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C10 | ZenMoney: refresh tokens issued, refresh not documented | CONFIRMED | Sample response includes refresh_token. No refresh request is described | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C11 | ZenMoney: client registration by Google Form, manual review | CONFIRMED | Only "real projects" meeting OAuth 2.0 requirements; review is manual; consumer key and secret are emailed | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C12 | ZenMoney: personal token without registration (zerro.app) | CONFIRMED | Token available "without registration" from a ZenMoney-registered service; example zerro.app/token. Scope not stated | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C13 | ZenMoney: diff-based sync | CONFIRMED | Endpoint https://api.zenmoney.ru/v8/diff/ with currentClientTimestamp and serverTimestamp; deletions sent in a deletion array | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C14 | ZenMoney: newer server copy is kept | CONFIRMED (partly) | Page says a newer server object is not overwritten. Outcome when the client copy is newer is not stated | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C15 | ZenMoney: no rate limits, licence or fees stated | CONFIRMED | None stated on the wiki page | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C16 | ZenMoney wiki last edited 4 Aug 2023 | UNVERIFIABLE | Date not in the text read | https://github.com/zenmoney/ZenPlugins/wiki/ZenMoney-API |
| C17 | Toshl base URL | CONFIRMED | https://api.toshl.com (used in examples; no labelled base URL). HTTPS and JSON only | https://developer.toshl.com/docs |
| C18 | Toshl: OAuth2 or long-lived tokens | CONFIRMED | OAuth2 bearer tokens; long-lived tokens generated in account settings | https://developer.toshl.com/docs |
| C19 | Toshl: rate limit headers, example limit 1000 | CONFIRMED | X-RateLimit-Limit and X-RateLimit-Remaining; example values 1000 and 998. /rate-limit returns the same as JSON. Behaviour when exceeded is not stated | https://developer.toshl.com/docs |
| C20 | Toshl: 400 on changing modified, 409 on conflict | CONFIRMED | Changing the read-only modified field returns 400. Conflicts the server cannot resolve return 409 | https://developer.toshl.com/docs |
| C21 | Toshl docs: no beta label; last modified 8 Jan 2024 | CONFIRMED | No beta label; "Page last modified: 08 Jan 2024" | https://developer.toshl.com/docs |
| C22 | Lunch Money v2 base URL and bearer token | CONFIRMED | https://api.lunchmoney.dev/v2. Bearer token from the developers page in the app. Mock server at https://mock.lunchmoney.dev/v2 | https://lunchmoney.dev |
| C23 | Lunch Money v2 supports writing transactions | UNVERIFIABLE | The page does not state write support or list write endpoints | https://lunchmoney.dev |
| C24 | Lunch Money rate limits | UNVERIFIABLE | The page links a Rate Limiting guide (not read) and shows no numbers | https://lunchmoney.dev |
| C25 | monobank endpoints: client info (GET), set webhook (POST), statement (GET) | CONFIRMED | All three present; webhook takes webHookUrl | https://api.monobank.ua/docs/ |
| C26 | monobank auth header not confirmed | CONFIRMED (correction) | Header X-Token, "token for personal access to the API". Notes said unconfirmed | https://api.monobank.ua/docs/ |
| C27 | monobank statement: 31 days + 1 hour | CONFIRMED | "31 доба + 1 година (2682000 секунд)" | https://api.monobank.ua/docs/ |
| C28 | monobank: 1 request per 60 seconds | CONFIRMED | Statement and client info: "не частіше ніж 1 раз у 60 секунд" (no more than once per 60 s) | https://api.monobank.ua/docs/ |
| C29 | monobank statement: max 500 transactions per call | UNVERIFIABLE | Not in the fetched text (text proxy, 6,312 characters; the statement response section may be incomplete). The community doc claims it; search found no confirmation | https://api.monobank.ua/docs/ |
| C30 | monobank: not available to clients under 16 | CONFIRMED (not in notes) | "API недоступне для клієнтів до 16 років". Child accounts are reachable through the parent account | https://api.monobank.ua/docs/ |
| C31 | Not in notes: personal API scope | NEW | The page says that a service serving clients must use the corporate "API для провайдерів послуг" (https://api.monobank.ua/docs/corporate.html). The personal API is for own or family use | https://api.monobank.ua/docs/ |
| C32 | Monobank docs contain text addressed to AI tools | NOT FOUND | No AI-directed text in the fetched docs text (no matches for AI, assistant, LLM, agent, instruction, prompt). Nothing was followed | https://api.monobank.ua/docs/ |

API summary: 25 confirmed (4 partly or sample-only: C5, C7, C9, C14), 0 wrong; 5 unverifiable (C6, C16, C23, C24, C29). C31 is new; C32 not found.

## 4. Erste Group (George) and PrivatBank

| # | Claim (from notes) | Verdict | Correct value | Source URL |
|---|---|---|---|---|
| D1 | Erste developer portal is the access point for PSD2 APIs | UNVERIFIABLE | The portal page as fetched shows only its title, "Erste Developer Portal". No API list was returned | https://developers.erstegroup.com/ |
| D2 | No personal or retail George API outside PSD2 | UNVERIFIABLE | None found. Only George Business (for companies) and an EBICS 3.0 corporate channel on Sparkasse pages. Absence not proven | https://www.sparkasse.at/bregenz/unternehmen/produkte-firmenkunden/digitales-banking/george-business |
| D3 | No personal PrivatBank API; third-party clients use Privat24 for Business | UNVERIFIABLE | No official personal API found. The Python wrapper python-privatbank-client needs the Privat24 for Business Autoclient (a business product). Search snippet only; not fetched | https://pypi.org/project/python-privatbank-client/ |

## 5. EU Software Directive 2009/24/EC

Text read via the r.jina.ai proxy because the direct EUR-Lex fetch returned empty. Wording matches the EUR-Lex text structure. Check on eur-lex.europa.eu before quoting in a legal document.

| # | Claim (from notes) | Verdict | Correct value | Source URL |
|---|---|---|---|---|
| E1 | Art. 1(2): ideas and principles, including those behind interfaces, are not protected | CONFIRMED | "Ideas and principles which underlie any element of a computer program, including those which underlie its interfaces, are not protected by copyright under this Directive." | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024 |
| E2 | Recital 11: same principle, extended to logic and algorithms insofar as they are ideas | CONFIRMED (partly) | Recital 11 states the same principle. The logic and algorithms sentence is cut off in the text read | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024 |
| E3 | Art. 5(3): observe, study or test while doing permitted acts | CONFIRMED | "...entitled, without the authorisation of the rightholder, to observe, study or test the functioning of the program in order to determine the ideas and principles which underlie any element of the program if he does so while performing any of the acts of loading, displaying, running, transmitting or storing the program" | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024 |
| E4 | Art. 6: decompilation only for interoperability | CONFIRMED | 6(1): indispensable for interoperability; information not previously readily available; acts confined to necessary parts. 6(2): information may not be used for other goals, given to others (except for interoperability), or used to develop a substantially similar program. 6(3): must not unreasonably prejudice the rightholder | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024 |
| E5 | Contract override clause (notes: article number not confirmed) | CONFIRMED (article located) | Article 8, second paragraph: "Any contractual provisions contrary to Article 6 or to the exceptions provided for in Article 5(2) and (3) shall be null and void." Recital 16 states the same principle | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024 |
| E6 | Recital 14: observing, studying or testing is allowed if copyright is not infringed | CONFIRMED | "...provided that those acts do not infringe the copyright in the program" | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024 |

Legal summary: 6 of 6 confirmed.

## 6. Overall reliability rating

1. Prices: MEDIUM-HIGH. 18 of 25 confirmed on official or store pages, 2 wrong (Copilot secondary figures; ZenMoney "not found" was incomplete), 5 unverifiable.
2. Ratings and EU law: HIGH. 8 of 8 ratings match the Apple API; 6 of 6 legal points match EUR-Lex text.
3. APIs and banks: MEDIUM. YNAB, ZenMoney and Toshl facts are confirmed. Unverified: monobank 500-per-call cap, Lunch Money write support and rate limits, YNAB plan requirement, and Erste and PrivatBank personal access.
