# Telegram Mini App vs alternatives for a single-user personal finance tracker (as of 31 Oct 2026)

Source tags used below:
- [F] = page fetched and read with WebFetch (a summary of the page text, so short quotes are the fetch model's wording of the page).
- [P] = page read through the r.jina.ai reader proxy after a direct fetch failed (403 or timeout). Text read directly.
- [S] = only the search-result summary was seen, the page itself was not opened. Treat as lower confidence.
- Tool use: 16 WebSearch calls, 15 WebFetch calls, 5 reader-proxy curl calls. Over the usual 15-call guideline because the question set is wide.

## 1. Option comparison (Mini App, bot only, PWA, native, Sheets + bot, no-code, ready-made app)

### Takeaway
No option wins on every criterion in the sources. A bot you already have, writing to a store the user owns, is the lowest-friction daily input in the cases I found. A Mini App is well documented, but Telegram's own storage limits are too small to hold a transaction ledger. PWA and native are judged here from platform docs only. No source measures taps or seconds per transaction for any option.

### Cited Findings

Telegram Mini App, platform facts (official docs):
- Storage limits: DeviceStorage up to 5 MB per user, device-only; CloudStorage up to 1,024 items per user, values up to 4,096 characters; SecureStorage up to 10 items per user. [F](https://core.telegram.org/bots/webapps)
- Encryption: the page says SecureStorage values are "encrypted at rest" and names the iOS Keychain or Android Keystore. It does not say whether DeviceStorage or CloudStorage data is encrypted. [F](https://core.telegram.org/bots/webapps)
- Release dates: DeviceStorage and SecureStorage were added in Bot API 9.0 on 11 Apr 2025. [F](https://core.telegram.org/bots/api-changelog)
- Home-screen shortcuts: Mini Apps "can now be accessed via direct shortcuts" in Bot API 8.0 (17 Nov 2024 entry on the webapps page). Also `addToHomeScreen()` and `checkHomeScreenStatus()` exist. [F](https://core.telegram.org/bots/webapps)
- Biometric unlock: BiometricManager documented for Bot API 7.2+, token saved in device secure storage. [F](https://core.telegram.org/bots/webapps)
- Haptics documented for Bot API 6.1+; the page warns the Telegram app "may play" haptics, so playback is not guaranteed. [F](https://core.telegram.org/bots/webapps)
- Offline use, service workers, caching: the page does not mention any of them in the part I read (about 100k of 113k characters). [F](https://core.telegram.org/bots/webapps)
- Push: the only mention is one intro sentence saying Mini Apps support "tailored push notifications"; no setup steps or limits. [F](https://core.telegram.org/bots/webapps)
- Bot write access (the route for reminders): `requestWriteAccess` (Bot API 6.9+) shows a popup asking to let the bot message the user. [F](https://core.telegram.org/bots/webapps)
- Launch points: menu button (set via @BotFather or setChatMenuButton), inline `web_app` button, attachment menu (listing restricted to "major advertisers" per the page), plus several others. [F](https://core.telegram.org/bots/webapps)

PWA (installable web app):
- Web Push for Home Screen web apps arrived with iOS and iPadOS 16.4, announced 16 Feb 2023 alongside the 16.4 beta 1. The web app must be added to the Home Screen first, and the permission request must follow a direct user action such as a subscribe button. No paid Apple Developer membership needed. [F](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)
- Shipping-version behaviour was not checked against Apple's iOS 16.4 release notes. [gap]
- A freelancer listing offers a Telegram Mini App and a PWA version on one Python and React stack, launched from a bot button, with data kept in sync (paraphrased from a search summary). [S](https://www.fl.ru/uslugi-freelancera/21423/razrabotka-pwa-telegram-mini-app-pod-klyuch.html)

Native app:
- Only vendor price claims found. A Russian agency (Vibes, 1 Apr 2025) says a native app starts "from 600,000 rubles" and takes 1.5–2 months, against a Mini App "under 300,000 rubles" in 7 working days. Self-reported, promotional. [F](https://www.sostav.ru/blogs/280723/58933)
- The same agency's other price articles (search summaries; which article holds which figure was not verified): Mini App from about 500,000 rubles and native from about 2 million rubles (March 2025); Mini App from about 150,000 rubles, native from 600,000 (another piece). Figures conflict; do not average them. [S](https://www.sostav.ru/blogs/280723/57630) and [S](https://www.sostav.ru/blogs/281129/65963)
- Offline and notification behaviour for native apps: not researched in this pass.

Bot only (chat input, text and photo reports):
- Budgy (WhatsApp, published 1 Apr 2026): text "lunch 280 swiggy" is logged and categorised; receipt photos and bank-SMS screenshots are parsed with Claude Vision; PDF statements are imported after confirmation; nudges run on a cron job; data goes to a Google Sheet the user owns; WhatsApp delivery via Twilio. One user at time of writing. [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)
- Telegram-chat trackers seen in search results: Tabby (chat-based, per search summary) [S](https://www.producthunt.com/posts/tabby-10); Spendly, a chat-based budget assistant [S](https://www.producthunt.com/p/spendly-6/spendly-7). No usage or retention data for either.

Spreadsheet + bot:
- Budgy's data store is Google Sheets, with the user owning the sheet. [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)
- No source on Excel-specific bot integration. [gap]

No-code:
- Glide pricing as shown on the page (no date or currency statement on the page): Basic $25/month (2 team members, 2 published apps, 10 projects); Plus $50 (3 members, 5 apps, 20 projects); Pro $125 (5+ members, unlimited apps); Enterprise custom. Row limits, offline support, custom domain and data export are not shown for any paid plan. Annual plans "coming soon". [F](https://www.glideapps.com/pricing)
- Airtable: Free plan "formulated for individual users, very small teams, or those with lightweight needs"; Team $20/user/month billed annually; Business $45/user/month billed annually; charged per seat with edit rights. [P](https://airtable.com/pricing)
- Softr: the pricing page opened, but no plan prices were extracted. Not found. [P](https://www.softr.io/pricing)
- Notion: not researched in this pass.

Ready-made apps:
- Not researched beyond the Mint shutdown example in Section 3 (a lock-in case, not a comparison).

Daily input speed:
- No measured taps or seconds for any option in the sources. The only timing claim is from the Budgy author: manual logging "forces a pause" and "for four seconds you're choosing to notice what you just did". Opinion, one author. [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)

### Inferences
- In the sources I read, the cheapest daily input is a text or photo message to a bot the user already has. It needs no screen change; Budgy is one example, for one user. Confidence: medium.
- Telegram cloud storage cannot be the ledger. A 1,024-item cap and 4,096-character values are hard limits from the official page. One key per transaction would hit the item cap at 1,024 entries. Confidence: high. The ledger must sit in a sheet or a database the user controls.
- Offline use is undocumented for Mini Apps in the official docs. A PWA or native app has more established offline paths. That last point is general knowledge, not sourced here. Confidence on Mini App offline being undocumented: high.
- On iPhone, a PWA can only send push after a Home Screen install and a user tap (WebKit). A Mini App reminder is a bot message, which needs the user's write-access grant. Both add a setup step.

### Gaps
- No measured taps or seconds per transaction for any option.
- No offline test evidence for a Mini App or a PWA.
- No independent native-app price source.
- Notion, Softr prices, YNAB, Monefy, Spendee and other ready-made finance apps: not researched or not extracted.
- Dashboards and charts: no source comparing chart options across the seven choices.
- Telegram's own offline message queueing in the client: not checked.

## 2. First-hand developer experiences, Telegram Mini Apps (2024–2026)

### Takeaway
There are few detailed postmortems with numbers. Reported build times are short (two days for a first MVP; 7 working days for a vendor build), but both are self-reports. Repeated Telegram-specific gotchas: a WebKit black-screen bug on iOS, `initData` and `sendData()` rules, and server-side checks. One 2026 author advises putting Telegram constraints into the AI agent's CLAUDE.md before building.

### Cited Findings
- HackerNoon, Vibe Seeker, 13 Aug 2026, Part 1 of a three-part series. GoosleeBot is a Mini App and bot that creates video-meeting links. Author-reported: first MVP in "two days", polish in "four weeks"; cost and team size not stated. [F](https://hackernoon.com/building-a-business-app-on-telegram-4-lessons-we-learned-the-hard-way)
  - Advice: put Telegram's constraints in the agent's instructions; the author says to "copy this section directly into your agent's CLAUDE.md or system prompt as is." [F, fetch-summary wording]
  - Advice: set up a tunnel from day one; "Without a tunnel, every iteration requires a full deployment." [F, fetch-summary wording]
  - Advice: detect platform and mode on every page; use WebSockets, with polling as backup. [F]
- Kopilo, a Telegram Mini App finance tracker by a solo developer (Java backend, React frontend on Vercel, VPS backend). Post dated 27 Jun 2026. "The WebKit black screen bug on iOS ate two days." Telegram Stars payments needed a workaround in a Java library that refused an empty provider token. Nine build phases from a blank repo; 7-day free trial, "no card needed". Account creation avoided: "Just Telegram". [P](https://www.indiehackers.com/post/building-a-liquid-glass-finance-tracker-for-telegram-solo-dev-xBgVJgRvdITLGUgOrepV) and [P](https://www.indiehackers.com/product/kopilo) (product page lists the post)
- Habr article by MarkovM, 10 Aug 2025 (also on the Amvera blog). `initDataUnsafe` has data only when the app opens inside Telegram; sendData() works only from a reply-keyboard `web_app` button, not an inline button; initData should be verified on the server, yet the author's own example skips that check (paraphrased). [F](https://habr.com/en/articles/935718)
- Vibes agency case, 1 Apr 2025: a Mini App for an online school (participant catalogue, guided onboarding, event sign-up with bot reminders, sync to Google Sheets and CRM). Claimed 7 working days, under 300,000 rubles. Self-reported: participation +38%, material views +47%, 11 fewer support hours per week; no baseline or method. The author lists no setbacks. [F](https://www.sostav.ru/blogs/280723/58933)
- AdsGram blog (vendor): swipe gestures that dismiss the app harm drag-based screens; Bot API 10.2 blocks Mini App method calls from other origins. The second claim matches the official changelog (see Section 5). [S](https://adsgram.ai/blog/adsgram/telegram-mini-app-tma-development-mistakes-and-how-to-avoid-them)
- Conflict on one URL: the search-index summary of https://hackernoon.com/building-a-business-app-on-telegram-4-lessons-we-learned-the-hard-way described redirect-flow, directory-rule and manual-testing lessons for a business app. The live fetch (13 Aug 2026) described the GoosleeBot video-link app instead. Only the fetched content is used above; the search-summary lessons are unverified. [S]
- Russian agency listing of ten failure causes (unclear first-run flow, traffic expectations, no post-launch work). Vendor opinion. [S](https://www.sostav.ru/blogs/280723/62987)
- Habr, custom URI schemes: an author found cross-platform onboarding UX, not the backend, was the hardest part; asks about iOS handoff. Date not seen. [S](https://habr.com/ru/articles/1038392/)

### Inferences
- The recurring gotchas (environment detection, `initData` validation, webview-specific behaviour, payments) are real but Telegram-specific. They teach Telegram skills, not general web or product skills. Confidence: medium.
- Self-reported build times ("two days", "7 days") describe simple bot-plus-app projects. None of the sources describes a finance ledger with reconciliation, two currencies or bank import. Confidence: medium.
- The Kopilo author is a developer; the question is about a non-programmer working with an AI coding agent. No source reports that situation. [gap]

### Gaps
- No Reddit or Hacker News threads found on Mini App finance builds. The Reddit search returned product pages only.
- No finance-specific postmortem with measured time, cost or retention beyond Kopilo's narrative.
- No Doubletapp or dev.family article read in full.
- Telegram-webview layout quirks (avoid `100vh`, use Telegram popups, redirects break): reported in search summaries of several dev blogs, but I could not tie them to a page. Not usable as a cited finding.

## 3. Why people abandon expense tracking, and what keeps them using it

### Takeaway
No peer-reviewed or primary dataset on abandonment was found. Vendor blogs disagree on timing (2 weeks, 2–3 weeks, 6 weeks) and cite no primary data. The best available figure is a cross-industry Day-30 retention benchmark (about 7%) with no finance split. The manual-entry versus auto-import question is argued in both directions with one anecdote and opinion each.

### Cited Findings
- Adjust, cross-industry retention: "At the end of the 30 days, the rate settles at 7%." Day 1 26%, Day 7 13%, Day 14 10%. iOS Day 30 8%, Android 6%; Europe 6%, North America 5%. Page date and dataset period not shown in the part I read. [P](https://www.adjust.com/blog/what-makes-a-good-retention-rate/)
- Getpanto compilation: finance app Day-30 retention 4.2%. Not verified; page not opened. [S](https://www.getpanto.ai/blog/mobile-app-retention-statistics)
- Vendor blogs in the search results say most people abandon expense tracking within 14 days, or within 2–3 weeks, and blame friction. They cite no primary data, and the sources conflict. Examples (not opened individually): [S](https://freenance.io/budgeting/expense-tracking-methods/) and [S](https://mybanktracker.com/blog/find-my-answers/expense-tracking-ends-failure-116520)
- Search-result blogs cite a "2023 Carnegie Mellon study", a "2022 University of Toronto" model and a "2019 Journal of Marketing Research" 15–20% spending-cut finding. None located, and the blogs gave no links. Not usable.
- Budgy author (one user): "I'd set it up, use it for four days, and abandon it." Auto-tracking apps were "Technically impressive. Completely useless for changing how I spent." [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)
- Budgy author, on their own design: "I genuinely don't know if it's a market." [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)
- Kopilo author: finance apps "asked me to create an account before I could see anything." Onboarding friction as a stated reason to build inside Telegram. [P](https://www.indiehackers.com/post/building-a-liquid-glass-finance-tracker-for-telegram-solo-dev-xBgVJgRvdITLGUgOrepV)
- Counter-view: a blog in the search results says a "Zhang study" links manual recording to higher financial self-awareness. The study was not located. Probable blog: [S](https://lifetips.alibaba.com/tech-efficiency/how-not-automating-your-budget-can-help-you-spend-less) (attribution not confirmed). [gap]
- Corporate, not personal: Forrester Consulting found T&E expenses entered after the event in 80% of surveyed companies. Weak relevance. [S](https://www.phocuswire.com/Forrester-analysis-shows-expenses-continued-to-be-entered-manually-despite-automation)
- Automatic bank import under EU rules: strong customer authentication applies to each online access to a payment account, including through an AISP. For account information, the RTS lets the bank skip SCA on repeat access but requires a re-check at least every 90 days. EBA proposed moving this to 180 days; outcome not confirmed. [S](https://paytechlaw.com/en/regulatory-technical-standards-rts-sca-csc/) and [S](https://www.eba.europa.eu/calendar/consultation-amending-rts-sca-and-csc-under-psd2)
- Erste Bank (Austria): third-party directories list an Account Information Service and a developer portal, developers.erstegroup.com. Directories also list a separate Croatian entity, Erste & Steiermärkische. Not confirmed on Erste's own site. [S](https://www.openbankingtracker.com/provider/erste-bank-and-sparkassen)
- Mint (Intuit) shutdown, lock-in example: CSV export reportedly ended 23 Mar 2024, covering about three years of data. Net-worth history and categorised spending from before the window reportedly could not be recovered. The 23 Mar date comes from a competitor comparison page in the search results (probably https://beancount.io/compare/beancount-vs-mint, not opened). Secondary sources only; Intuit's own page and the Nasdaq article were not retrieved. [S](https://plisio.net/tradfi/mint-vs-credit-karma) and [S](https://ttlc.intuit.com/community/other-financial-discussions-21/mint-shutting-down-in-less-than-two-months-994471)
- Budgy: example nudge text, "You're 31% above pace with 18 days to go", tied to a pay cycle rather than the calendar month. Author's design choice; no retention effect measured. [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)

### Inferences
- Whether manual entry helps or hurts is an open question in the sources. Budgy's view is anecdote, and the blog view is unsourced. Testing it on the user's own logs is the only real evidence available. Confidence: high that no solid data exists.
- Even a well-built bank feed needs re-authentication every 90 days under PSD2 rules as described. Automatic import is therefore not "set and forget", and some manual or semi-manual input (photo, PDF, SMS) stays in any design. Confidence: medium-high, from search-summary level sources.
- The Mint case supports keeping a copy of the data under the user's control (a sheet or database), not only inside an app's export tool. Confidence: medium, secondary sources.

### Gaps
- No peer-reviewed or industry study on expense-tracker abandonment found. The Zhang and Journal of Marketing Research claims could not be located.
- No finance-specific Day-30 benchmark verified at source level. The Getpanto 4.2% figure is unverified.
- No data on whether reminders or nudges change retention for trackers.
- Erste's API access for a personal app is not verified on Erste's site.
- PrivatBank personal data access (Ukraine): not researched.
- Excel as the current tool: no source on migration rates from spreadsheets to apps.

## 4. Experiment and career value

### Takeaway
Telegram Mini App and bot work has visible freelance supply and published budget ranges, but all of them are vendor-published, and no independent demand volume was found. The business uses cited are vendor case studies (catalogues, onboarding, event sign-up, CRM sync). No source links this skill to selling AI-agent automation to small businesses in Ukraine, CIS or EU markets.

### Cited Findings
- CyberPanel (vendor blog, 2025): freelance budgets of $2,000–$15,000. Methodology not stated. [S](https://cyberpanel.net/blog/how-to-hire-telegram-mini-app-developers-in-2025)
- Ronasit (vendor blog, opinion): a typical build may need a team of four to six engineers; recruiting momentum argued from category growth. [S](https://ronasit.com/blog/hire-telegram-mini-app-developers/)
- Habr vacancies (dates not seen): one frontend Mini App role up to 150,000 rubles; one full-stack posting "starting salary of $2,000". Which listing shows which wage was not verified. [S](https://career.habr.com/vacancies/1000146882) and [S](https://career.habr.com/vacancies/1000157435)
- Upwork: a posting seeks a Telegram bot development expert (not Mini App-specific). [S](https://www.upwork.com/jobs/~022067657975833497255)
- Fiverr: many Mini App gigs; supply is high, prices not extracted. [S](https://fiverr.com/denisefimenko/develop-a-high-quality-telegram-mini-app-or-webapp)
- fl.ru has a Mini Apps freelancer category. No volume figures on the page. [S](https://www.fl.ru/freelancers/telegram-mini-apps/)
- Telegram user scale: a stats blog says Telegram crossed 1 billion monthly users in March 2025 (secondary). [S](https://voxbooster.com/blog/telegram-statistics-2026) The official Telegram statement it cites was not opened.
- Mini App reach: one Telegram channel post says 360 million of 900 million monthly users interact with Mini Apps each month; date and exact post not confirmed. [S](https://tx.me/s/tginfoen?after=1942) Other third-party reach estimates range widely (1.44 billion in Sep 2024 down to 150–190 million by mid-2025); no primary URL captured, not usable.
- Bot API cadence in 2026 (official changelog): 10.0 on 8 May 2026, 10.1 on 11 Jun 2026, 10.2 on 14 Jul 2026, 10.3 on 24 Aug 2026. Mini App-related changes per release are the maintenance signal. [F](https://core.telegram.org/bots/api-changelog)
- Not usable: a vendor guide in the search results says crypto-focused apps, including tap games, are the most common category. Its URL was not confirmed.

### Inferences
- Demand evidence is thin and vendor-sourced. The supportable read: Telegram Mini App work is a visible freelance category at low to mid price points. Nothing in the sources shows it as a premium niche.
- For selling automation to small businesses, the transferable part is the agent-built pipeline (input, parsing, storage, reminders, dashboard), not the Mini App UI. No source shows SMB demand for either in Ukraine, CIS or EU markets. Confidence: low.
- Learning value: a Mini App teaches Telegram-specific skills (`initData` checks, origin rules, API churn). A bot-plus-sheet-plus-LLM pipeline teaches general automation skills closer to the stated goal. Confidence: medium, based on the content of the sources in Sections 2 and 5.

### Gaps
- No Upwork, Kwork or Freelancehunt volume statistics found. The Kwork search returned nothing usable.
- No independent SMB adoption data for Mini Apps in Ukraine, CIS or EU.
- No data on Telegram penetration among business customers in Austria, the EU or Ukraine.
- 2026 project prices are not sourced; the price sources are 2025 vendor blogs.
- No independent case study with metrics for a business Mini App. Only vendor cases.

## 5. Platform risks and regulation (Telegram dependency, bans, outages, Austria/EU, Ukraine)

### Takeaway
Telegram-platform risk is concrete: Bot API changes ship about monthly in 2026, and the July 2026 change turned on origin restrictions automatically. Ukraine restricted Telegram for officials, military and critical infrastructure from 20 Sep 2024. A 2026 bill is pending, and the latest official line found says there is no plan to ban private users. Account bans and outages were not researched. GDPR's household exemption (Art. 2(2)(c)) covers purely personal processing; whether it reaches a third-party host is an inference, not a sourced legal reading.

### Cited Findings
- Ukraine, 20 Sep 2024: the National Security and Defence Council decided to "restrict the use of Telegram in government agencies"; bodies covered: government agencies, military formations, critical infrastructure. Kyiv Post does not say whether personal devices are covered, or name exemptions. [F](https://www.kyivpost.com/post/39311)
- The same decision is reported with conflicts. One report: personal devices not restricted. Another: personal devices covered if used for work. A third: staff whose duties need Telegram are exempt. [S](https://www.channelstv.com/2024/09/20/ukraine-bans-telegram-for-officials-over-security-threats) and [S](https://nikvesti.com/en/news/public/295684-restricted-use-telegram-kherson-rma) and [S](https://thehackernews.com/2024/09/ukraine-bans-telegram-use-for.html)
- Bill No. 11115 (registered 25 Mar 2024) would require disclosure of platform ownership and funding and set penalties for non-compliance with removal demands. Not described as a ban. Placed on the agenda on 10 Feb 2026; "Pending" as of the article. Article dated 18 Mar 2026. [F](https://dev.ua/en/news/rada-mozhe-naiblyzhchym-chasom-rozhlianuty-zakonoproiekt-pro-obmezhennia-telegram-v-ukraini-1773847639). Status after March 2026 not found.
- Official line, March 2026, per a search summary of mezha.net (page returned 403): no direct ban planned for private users; state bodies may stop using the platform if it fails transparency and law-enforcement cooperation conditions. [S](https://mezha.net/eng/bukvy/ukraine_will_not/)
- Interior Ministry view (search summary): full blocking is unrealistic; wants control instead. [S](https://news.liga.net/en/politics/news/the-ministry-of-internal-affairs-has-admitted-that-it-is-impossible-to-block-telegram-completely-chief-wants-control-due-to-terrorist-attacks)
- Official Telegram Bot API 10.2, 14 Jul 2026: disallows Mini App method calls from origins other than the app's own domain. Automatic on 20 Jul 2026 for all Mini Apps; opt-out via @BotFather settings. [F](https://core.telegram.org/bots/api-changelog)
- Official Mini App docs: SecureStorage encrypted at rest; CloudStorage and DeviceStorage encryption not stated. [F](https://core.telegram.org/bots/webapps)
- GDPR Article 2(2)(c), the household exemption: "by a natural person in the course of a purely personal or household activity;" [F](https://gdpr-info.eu/art-2-gdpr/). The page gives no regulation date.
- Mint shutdown (see Section 3): export window closed in March 2024 per secondary sources. [S](https://plisio.net/tradfi/mint-vs-credit-karma)

### Inferences
- Ukraine risk for a personal-use tool is low on current official statements. The bigger exposure is work devices: if the user or clients work with state bodies, Telegram use may be restricted on those devices. Confidence: medium.
- Telegram-held data (CloudStorage, DeviceStorage) adds lock-in and a size ceiling. Data in a user-owned sheet or database limits both. Confidence: high on the limits, medium on the lock-in judgement.
- The GDPR household exemption covers the user's own processing. It does not, by itself, cover a third-party host that stores the data. This is general reasoning, not a sourced legal opinion. Confidence: medium. Advise a legal check before storing other people's data.

### Gaps
- Account bans and terms enforcement against Mini Apps: not researched.
- Telegram outages and uptime history: not researched.
- Telegram's EU status (DSA, data disclosure) and Austrian FMA rules for personal finance tools: not researched.
- Russia's restrictions on Telegram: not researched.
- Whether Telegram's cloud chats or cloud storage are end-to-end encrypted: not checked on telegram.org (general knowledge says default cloud chats are not, but that is unverified here).
- Bill 11115 after March 2026: not found.
- The 2024 scope conflicts (personal devices, exemptions) are not resolved. Kyiv Post is the only fetched primary account.

## 6. Hybrid patterns (bot for input + Mini App for dashboards; one codebase as PWA and Mini App)

### Takeaway
Bot-for-input plus Mini App-for-dashboard is supported by the platform: a bot can open a Mini App from its menu button or an inline button. I found no finance product that combines both in the sources read. One codebase as a PWA and a Mini App is technically plausible (a Mini App is a web page). A freelancer listing offers it. How common it is: not found.

### Cited Findings
- Entry points for a Mini App attached to a bot: menu button, inline `web_app` button, attachment menu, and others. [F](https://core.telegram.org/bots/webapps)
- A Mini App runs as a web page in Telegram's sandbox, using the Telegram web app JavaScript object. [S](https://dev.family/blog/article/how-to-build-a-web-app-part-ii-deploying-telegram-mini-app.md) (search summary only; probable source, not confirmed)
- Freelancer listing: Mini App plus PWA on one stack, launched from a bot button, installable in a browser, data kept in sync. [S](https://www.fl.ru/uslugi-freelancera/21423/razrabotka-pwa-telegram-mini-app-pod-klyuch.html)
- Environment differences: `initDataUnsafe` is empty outside Telegram (Habr, MarkovM, 10 Aug 2025). This is the first shared-code gotcha. [F](https://habr.com/en/articles/935718)
- Kopilo is a Mini App-only tracker; Budgy is bot-only. Neither is a hybrid. [P](https://www.indiehackers.com/product/kopilo) and [P](https://www.indiehackers.com/post/i-built-an-expense-tracker-in-whatsapp-because-i-couldnt-stop-abandoning-apps-here-s-what-i-learned-about-intentional-friction-01776a7f3c)
- Vendor view: PWAs suit "marketing, content-based apps" best; Mini Apps need no app-store install. Opinion from a comparison article, not fetched. [S](https://www.purrweb.com/ru/blog/chto-takoye-telegram-mini-app/)

### Inferences
- A shared codebase is plausible: a Mini App is a web page; a PWA adds a manifest and a service worker, and iOS push needs a Home Screen install. The main work is detecting the runtime and handling Telegram-specific navigation. Confidence: medium.
- Bot-as-input and Mini-App-as-dashboard reuse one backend. This is the cheapest hybrid: the bot needs no UI, and the dashboard reads the same API. Confidence: medium, from the platform's documented entry points.
- Bot API 10.2's origin rule matters only when the Mini App calls Mini App methods across domains. A single domain for the app avoids it. Inference from the changelog wording. Confidence: medium.

### Gaps
- No count of products that ship as both PWA and Mini App.
- No finance example that combines a bot and a Mini App, in the reads done here.
- No source on whether a Mini App can work offline. The official page is silent.
- Telegram-webview layout details (for example `100vh`) are reported in search summaries only, and no page could be tied to them.

## 7. Evidence balance for the verdict ("Mini App or not")

### Takeaway
The evidence argues against a Mini App-only tracker as the main daily tool. It supports a bot-first input layer, with a store the user controls, and an optional dashboard. A Mini App is a good choice for the dashboard, not for the input. A PWA is the main alternative if Telegram lock-in or offline use matters more. As a learning project, a Mini App teaches Telegram-specific skills with thin demand data; a bot-plus-agent pipeline teaches more general automation skills.

### Cited Findings (the inputs behind the verdict)
- Official storage limits: 1,024 items, 4,096 characters per value (CloudStorage); 5 MB per user (DeviceStorage). [F](https://core.telegram.org/bots/webapps)
- Official release cadence in 2026: four Bot API releases between 8 May and 24 Aug 2026. [F](https://core.telegram.org/bots/api-changelog)
- Shipped finance examples: Budgy (bot-only, Google Sheets store, one user) [P]; Kopilo (Mini App-only, 7-day trial, solo developer, WebKit bug cost two days) [P].
- Retention baseline: Day 30 about 7% cross-industry [P](https://www.adjust.com/blog/what-makes-a-good-retention-rate/); no finance split.
- Build-time self-reports: two days for a first MVP (non-finance bot+app) [F]; seven working days for a vendor build [F].
- PSD2 repeat-access re-check at least every 90 days (search summary) [S](https://paytechlaw.com/en/regulatory-technical-standards-rts-sca-csc/).
- Ukraine: 2024 restriction on officials (Kyiv Post) [F]; 2026 bill pending (dev.ua) [F].

### Inferences (with confidence)
1. High: Telegram Cloud and Device storage cannot hold the ledger alone. The ledger belongs in a sheet or a database the user owns.
2. High: Telegram Bot API changes about monthly in 2026, so a Mini App carries ongoing maintenance tied to Telegram's release schedule.
3. Medium: Bot-first input is the fastest daily input in the sources, based on one user's report.
4. Medium: A Mini App is the right tool for an editable dashboard, and it reuses the same backend as the bot.
5. Medium: A PWA is the strongest alternative if Telegram independence matters. On iPhone it needs a Home Screen install before push works.
6. Low: The Mini App as a route to paid freelance work. Budgets are visible, but the volume is not sourced.
7. Low: The offline behaviour of a Mini App. Not documented.

### Verdict candidates (for the report writer to weigh, not decided here)
- Candidate A, bot-first with user-owned store plus optional Mini App dashboard. Best fit to the sources on daily input, data ownership and maintenance. Uses an existing Telegram bot.
- Candidate B, PWA as the single web codebase, bot optional. Best fit if Telegram lock-in and offline use outweigh the Telegram-native entry point.
- Candidate C, Mini App-only. Supported by the docs and one shipped product (Kopilo), but the sources show weaker daily input, no documented offline use, and a storage ceiling that forces an external store anyway.
- Native and ready-made apps: not evidenced enough here to rank.

### Gaps
- Daily input speed, measured: none.
- Offline behaviour of Mini Apps: undocumented.
- Ready-made finance apps and Notion: not researched.
- Account bans, outages and Telegram EU status: not researched.
- Fit with the user's Erste and PrivatBank accounts: Erste's AIS listed by directories only; PrivatBank not researched.
- Sources that failed to load: mezha.net (403), Intuit community thread (read only as a search snippet), Nasdaq Mint article (timeout), Kopilo product page direct (403, read via proxy), Adjust (timeout direct, read via proxy), Softr pricing (no prices extracted), Erste developer portal (not opened).
