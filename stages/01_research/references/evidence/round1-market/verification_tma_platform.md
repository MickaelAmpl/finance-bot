# Verification: tma_platform_capabilities.md (Telegram Mini Apps)

Checked: 31 Oct 2026. Notes file checked (not modified): `tma_platform_capabilities.md` in the same folder.
Method: raw HTML of official pages fetched with curl, text extracted, quotes copied verbatim from that text (apostrophes normalised). Third-party tma.js pages fetched only to check quotes the notes attribute to them. WebSearch used once, to locate Serverless pages. No logins, forms, bots, downloads or code execution.

## Claims table

| Claim | Verdict | Correct value (if wrong) | Exact quote | Source URL |
|---|---|---|---|---|
| **P1.** Latest Bot API is 10.3, dated 24 Aug 2026 | CONFIRMED | n/a. Top entry on the changelog as fetched 31 Oct 2026 | "August 24, 2026 / Bot API 10.3" (changelog heading) | https://core.telegram.org/bots/api-changelog |
| **P1.** Bot API 10.2 dated 14 Jul 2026; Mini App methods blocked from origins other than the original domain | CONFIRMED | n/a | "disallowing the usage of Mini App methods from origins different from the original Mini App domain" | https://core.telegram.org/bots/api-changelog |
| **P1.** Origin rule enforced from 20 Jul 2026 | CONFIRMED | n/a | "The protection will be automatically enabled for all Mini Apps on July 20, 2026." | https://core.telegram.org/bots/api-changelog |
| **P1.** 10.3 has "no Mini App changes" | CONFIRMED in substance; quoted phrase WRONG | The phrase is not on the changelog. The 10.3 entry lists only Rich Messages, Ephemeral messages, Reply markup and General items, none about Mini Apps. Cite it as "no Mini App items listed" | None found (section headings: "Rich Messages", "Ephemeral messages", "Reply markup", "General") | https://core.telegram.org/bots/api-changelog |
| **P1.** "Twelve Bot API releases from 7.2 to 10.2 touched Mini Apps" | CONFIRMED by my count | Count is 12 (7.2, 7.6, 7.7, 7.8, 7.10, 8.0, 9.0, 9.1, 9.5, 9.6, 10.1, 10.2). 9.4 (BotFather setting only) excluded | "Bot API 8.0 introduces 10 powerful new features for Mini Apps" | https://core.telegram.org/bots/api-changelog |
| **P2.** Official Serverless page exists on a Telegram domain | CONFIRMED | n/a. Page is linked from the Mini Apps page as well | "Telegram Serverless lets you run backend code for your bot and Mini App directly on Telegram's infrastructure" | https://core.telegram.org/bots/serverless |
| **P2.** JavaScript endpoints | CONFIRMED | n/a | "You write plain JavaScript modules, deploy them with a single command" | https://core.telegram.org/bots/serverless |
| **P2.** One SQLite database per bot | CONFIRMED | n/a | "Every bot gets its own database — an SQLite-backed store that persists between invocations" | https://core.telegram.org/bots/serverless |
| **P2.** Mini App hosted at app<id>.tgcloud.ai | CONFIRMED | n/a. Also: tgcloud.ai root answers HTTP 302 to core.telegram.org/bots/serverless (observed 31 Oct 2026). Ownership and terms of tgcloud.ai not verified | "served at https://app<app_id>.tgcloud.ai/" | https://core.telegram.org/bots/serverless |
| **P2.** Platform-verified initData | CONFIRMED | n/a | "already verified by the platform" | https://core.telegram.org/bots/serverless |
| **P2.** Page changed 6 Oct 2026 | CONFIRMED | n/a | "October 6, 2026" (Recent changes: "Added Mini App hosting.") | https://core.telegram.org/bots/serverless |
| **P2.** Serverless is beta or GA | UNVERIFIABLE | Not stated. No beta, preview or early-access wording on the page | None | https://core.telegram.org/bots/serverless |
| **P2.** Serverless pricing | UNVERIFIABLE | Not stated anywhere on the page | None | https://core.telegram.org/bots/serverless |
| **P2.** Data residency, encryption at rest, retention, backups | UNVERIFIABLE | Not stated on the page (absence confirmed by keyword search) | None | https://core.telegram.org/bots/serverless |
| **P2.** Missing or invalid initData gives HTTP 401 | WRONG | Page gives an error type, not an HTTP status: 'UNAUTHORIZED' when the init data is missing or invalid. No "401" on the page | "'UNAUTHORIZED' when the init data is missing or invalid" | https://core.telegram.org/bots/serverless |
| **P2.** Outbound response capped at 30 MB; uploads 50 MB (10 MB photos); getFile downloads 20 MB | CONFIRMED | n/a | "The total response is capped at 30 MB." | https://core.telegram.org/bots/serverless |
| **P2.** Client call via Telegram.WebApp.Serverless.call(name, input, callback) | CONFIRMED | n/a | "Telegram.WebApp.Serverless.call('getProfile', {lang: 'en'}, function(error, profile) {" | https://core.telegram.org/bots/webapps |
| **P3.** BiometricManager, Bot API 7.2, 31 Mar 2024 | CONFIRMED | n/a (date confirmed) | "Added the field BiometricManager to the class WebApp." | https://core.telegram.org/bots/api-changelog |
| **P3.** disableVerticalSwipes, Bot API 7.7 | CONFIRMED | n/a. 7.7 dated July 7, 2024 | "Added the field isVerticalSwipesEnabled and the methods enableVerticalSwipes, disableVerticalSwipes to the class WebApp." | https://core.telegram.org/bots/api-changelog |
| **P3.** Main Mini App, Bot API 7.8 | CONFIRMED | n/a. Dated July 31, 2024 | "Added the option for bots to set a Main Mini App" | https://core.telegram.org/bots/api-changelog |
| **P3.** Bot API 8.0 (17 Nov 2024): full-screen, home-screen, downloadFile, shareMessage, LocationManager, Ed25519 validation | CONFIRMED | n/a (date confirmed: November 17, 2024). Ed25519 part: third parties validate without the bot token | "Added the method downloadFile to the class WebApp"; "are now able to validate it without knowing the App's bot token" | https://core.telegram.org/bots/api-changelog |
| **P3.** DeviceStorage and SecureStorage, Bot API 9.0 (11 Apr 2025) | CONFIRMED | n/a (date confirmed: April 11, 2025) | "Added the field DeviceStorage, allowing Mini Apps to use persistent local storage on the user's device." | https://core.telegram.org/bots/api-changelog |
| **P3.** CloudStorage, Bot API 6.9 | CONFIRMED | n/a (date confirmed: September 22, 2023) | "Added the field CloudStorage to the class WebApp." | https://core.telegram.org/bots/api-changelog |
| **P4.** CloudStorage: 1024 items per user | CONFIRMED | n/a | "Each bot can store up to 1024 items per user in the cloud storage." | https://core.telegram.org/bots/webapps |
| **P4.** CloudStorage key up to 128 characters | CONFIRMED | n/a | "The key should contain 1-128 characters, only A-Z, a-z, 0-9, _ and - are allowed." | https://core.telegram.org/bots/webapps |
| **P4.** CloudStorage value up to 4096 characters | CONFIRMED | n/a. Page counts characters, not bytes | "The value should contain 0-4096 characters." | https://core.telegram.org/bots/webapps |
| **P4.** DeviceStorage 5 MB | CONFIRMED | n/a | "Each bot can store up to 5 MB per user using this storage." | https://core.telegram.org/bots/webapps |
| **P4.** SecureStorage 10 items; iOS Keychain, Android Keystore | CONFIRMED | n/a | "Each bot can store up to 10 items per user."; "On iOS, it uses the system Keychain; on Android, it uses the Keystore." | https://core.telegram.org/bots/webapps |
| **P5.** Bot Dev ToS 4.4(a): encrypt user data at rest, key stored separately | CONFIRMED | n/a | "Make sure user data is always encrypted at rest and stored separately from its encryption key;" | https://telegram.org/tos/bot-developers |
| **P5.** Data minimisation (4.3) | CONFIRMED | n/a | "You agree not to use your TPA to collect, store, aggregate or process data beyond what is essential for the operation of your services." | https://telegram.org/tos/bot-developers |
| **P5.** Deletion on request (4.2a) | CONFIRMED | n/a | "Delete user data upon their (or our, as the case may be) request that you do so;" | https://telegram.org/tos/bot-developers |
| **P5.** Section 10: no compensation on termination | CONFIRMED | n/a. Section 10 is titled "Termination" | "You will not be compensated for any direct or indirect losses resulting from your termination." | https://telegram.org/tos/bot-developers |
| **P5.** Duties survive termination (10.2 lists 4.2 and 4.4) | CONFIRMED | n/a | "will continue to apply and survive the termination of Bot Platform" (list includes 4.2. and 4.4.) | https://telegram.org/tos/bot-developers |
| **P6.** Mini Apps ToS: Telegram has "no access to or control over data shared between users and SP via MAF" | CONFIRMED with qualifier | Full sentence starts "After transmitting it,". Scope is data shared between users and the service provider. Same ToS: the Mini App automatically acquires the user's IP address | "Telegram does not have any access to or control over data shared between users and SP via MAF." | https://telegram.org/tos/mini-apps |
| **P6.** Service provider "is responsible for handling and storing any data" | CONFIRMED | n/a | "which is responsible for handling and storing any data provided to it." | https://telegram.org/tos/mini-apps |
| **P7.** Digital goods only via Telegram Stars | CONFIRMED | n/a | "all transactions pertaining to digital goods and services must be executed exclusively through the exchange of Telegram Stars" (6.2). Stars page: "all transactions must be carried out in Telegram Stars, with currency tag XTR." | https://telegram.org/tos/bot-developers ; https://core.telegram.org/bots/payments-stars |
| **P7.** Telegram withholds a non-refundable 15% fee (cites 6.1-6.2.6) | WRONG as stated (conditional; wrong section range) | 15% applies only to Stars purchases in a Mini App where the developer has enabled topics in private chats via @BotFather, and only while that setting is on. Section 6.1 covers physical goods, not a fee. No general 15% fee appears in these terms. The Stars developer page text does not state 15% (its fee table is not in the extracted text) | "all subsequent Telegram Stars purchases carried out within that TPA shall be subject to a non-refundable fee of 15%"; "This fee shall apply only for the duration that topics in private chats remain enabled for the TPA." | https://telegram.org/tos/bot-developers (6.2.6) |
| **P8.** SecureStorage delete method name | CONFIRMED that the names differ | Official Telegram name is removeItem. tma.js uses deleteItem as its own wrapper name (I did not check which underlying call tma.js makes). Use removeItem | Core: "removeItem(key[, callback])" listed under SecureStorage. tma.js: "To delete a key, use the deleteItem method." | https://core.telegram.org/bots/webapps ; https://docs.telegram-mini-apps.com/packages/tma-js-sdk/features/secure-storage (third-party) |
| SecureStorage restore: getItem returns canRestore; restoreItem asks the user | CONFIRMED | n/a. canRestore is from tma.js (third-party); restoreItem is from Core | Core: "When called, the user will be asked for permission to restore the value." tma.js: "canRestore: boolean: true if the value is missing, but can be restored from the iCloud backup. Available on iOS only." | https://core.telegram.org/bots/webapps ; https://docs.telegram-mini-apps.com/packages/tma-js-sdk/features/secure-storage |
| initData: "Data from this field should not be trusted." | CONFIRMED | n/a (page prefix: "WARNING:") | "Data from this field should not be trusted." | https://core.telegram.org/bots/webapps |
| auth_date: notes quote "Check it to reject stale data." | QUOTE WRONG (substance OK) | Real wording: to prevent use of outdated data, check auth_date. No freshness window is given | "To prevent the use of outdated data, you can additionally check the auth_date field" | https://core.telegram.org/bots/webapps |
| auth_date: tma.js "gives no exact window" | NOT FOUND on the fetched tma.js init-data page | Telegram also gives no window (consistent with notes) | None | https://docs.telegram-mini-apps.com/platform/init-data |
| HMAC-SHA256 check (WebAppData key); Ed25519 check string; both Ed25519 public keys | CONFIRMED | n/a. Both public keys match the notes | "secret key, which is the HMAC-SHA-256 signature of the bot's token with the constant string WebAppData used as a key." | https://core.telegram.org/bots/webapps |
| initData empty when launched from keyboard button or inline mode | CONFIRMED | n/a | "It is empty if the Mini App was launched from a keyboard button or from inline mode." | https://core.telegram.org/bots/webapps |
| Attachment menu: notes quote "limited to major Telegram Ad Platform advertisers, but all bots can use it on the test server" | QUOTE PARAPHRASED (substance OK) | Exact: "Attachment menu integration is currently only available for major advertisers on the Telegram Ad Platform. However, all bots can use it in the test server environment." | As above | https://core.telegram.org/bots/webapps |
| Viewport: notes quote "not fast enough to pin UI" | QUOTE PARAPHRASED (substance OK) | Exact: "It should not be used to pin interface elements to the bottom of the visible area." Use viewportStableHeight for that | "It should not be used to pin interface elements to the bottom of the visible area." | https://core.telegram.org/bots/webapps |
| Telegram Desktop Beta "isn't yet supported on macOS" | QUOTE PARAPHRASED (substance OK) | Exact: "(not supported on Telegram Desktop for macOS yet)" | "(not supported on Telegram Desktop for macOS yet)" | https://core.telegram.org/bots/webapps |
| Test environment allows HTTP links without TLS | CONFIRMED | n/a | "you may use HTTP links without TLS to test your Mini App." | https://core.telegram.org/bots/webapps |
| Production HTTPS requirement | UNVERIFIABLE | Not stated on the page (absence confirmed) | None | https://core.telegram.org/bots/webapps |
| iOS debugging: tap Settings icon 10 times; enable "Allow Web View Inspection" | CONFIRMED | n/a | "In Telegram tap 10 times on the Settings icon and toggle on Allow Web View Inspection." | https://core.telegram.org/bots/webapps |
| Direct links open full height by default since 7.6; mode=compact opens half height | CONFIRMED | n/a | "Starting from Bot API 7.6, by default, Mini Apps of this type open to full-screen height" | https://core.telegram.org/bots/webapps |
| Bot API 6.0 release date "not found" (gap in notes) | CORRECTION: date found | April 16, 2022 | "Added support for Web Apps" (6.0 entry, dated April 16, 2022) | https://core.telegram.org/bots/api-changelog |
| Other version dates: 6.1, 6.2, 6.4, 6.7, 6.9, 7.0, 7.6, 7.10, 9.1, 9.5, 9.6, 10.1 | Dates CONFIRMED; feature lists for 6.1 and 6.2 NOT verified | 6.1 June 20, 2022; 6.2 Aug 12, 2022; 6.4 Dec 30, 2022; 6.7 Apr 21, 2023; 6.9 Sep 22, 2023; 7.0 Dec 29, 2023; 7.6 Jul 1, 2024; 7.10 Sep 6, 2024; 9.1 Jul 3, 2025; 9.5 Mar 1, 2026; 9.6 Apr 3, 2026; 10.1 Jun 11, 2026. Changelog says only "Web App Improvements" for 6.1 and 6.2 | "Added the method requestChat to the class WebApp." (9.6) | https://core.telegram.org/bots/api-changelog |
| 7.10: MainButton renamed BottomButton; SecondaryButton; setBottomBarColor | CONFIRMED (rename version not checked) | n/a | "Renamed the class MainButton to the class BottomButton." | https://core.telegram.org/bots/webapps ; https://core.telegram.org/bots/api-changelog |
| Serverless: SPA fallback, caching and header options | CONFIRMED | n/a | "serve index.html for paths that don't exist and have no file extension" | https://core.telegram.org/bots/serverless |
| Serverless: no npm packages, no filesystem, no network except SDK fetch | CONFIRMED | n/a | "There are no npm packages, no filesystem, and no network except through the SDK's fetch." | https://core.telegram.org/bots/serverless |
| Serverless: Telegram Web opens Mini Apps in an iframe | CONFIRMED | n/a | "Telegram Web opens Mini Apps in an iframe" | https://core.telegram.org/bots/serverless |
| Serverless: foreign keys unsupported; Drizzle-style sdk/db | CONFIRMED | n/a | "The absence of foreign keys is a deliberate constraint, not an oversight."; "The schema DSL and query builder follow Drizzle" | https://core.telegram.org/bots/serverless |
| Serverless: CLI credential in .tgcloud/ (git-ignored) | CONFIRMED | n/a | "written by npx tgcloud login" (.tgcloud/credentials) | https://core.telegram.org/bots/serverless |
| Serverless: enable via BotFather > bot > Serverless | CONFIRMED | n/a | "In @BotFather, open your bot → Serverless and turn it on." | https://core.telegram.org/bots/serverless |
| Serverless: abuse reports to abuse@telegram.org | CONFIRMED | n/a | "email abuse@telegram.org" | https://core.telegram.org/bots/serverless |
| Serverless: Bot API version and GA/beta status not stated | CONFIRMED (absence) | n/a | None | https://core.telegram.org/bots/serverless |
| Bot Dev ToS: TPA "hosted on their developers' own servers" | CONFIRMED wording; now out of date for Serverless | Terms do not mention Telegram-hosted backends such as Serverless | "TPA are hosted on their developers' own servers" | https://telegram.org/tos/bot-developers |
| Bot Dev ToS: Standard Privacy Policy default; TPA must set a privacy policy in @BotFather | CONFIRMED | n/a | "TPAs must set up a Privacy Policy in @BotFather" | https://telegram.org/tos/bot-developers |
| Bot Dev ToS 4.3: ML/AI datasets prohibited | CONFIRMED | n/a | "data collection aimed at creating large datasets, machine learning models and AI products" | https://telegram.org/tos/bot-developers |
| Bot Dev ToS 4.4(c): reasonably secure environment | CONFIRMED | n/a | "Operate your TPA in a reasonably secure environment" | https://telegram.org/tos/bot-developers |
| Bot Dev ToS 6.1: Telegram does not process payments for physical goods | CONFIRMED | n/a | "Telegram does not process payments for physical goods and services." | https://telegram.org/tos/bot-developers |
| Bot Dev ToS 14: changes effective when revised terms are posted | CONFIRMED | n/a | "will become effective when we post the revised Bot Developer Terms of Service on this page" | https://telegram.org/tos/bot-developers |
| Bot Dev ToS 10.1: Telegram may discontinue TPA or Bot Platform | CONFIRMED | n/a | "Telegram can decide to fully or partially discontinue TPA or Bot Platform at any time" | https://telegram.org/tos/bot-developers |
| Mini Apps ToS: features may be altered or suspended; no liability | CONFIRMED | n/a | "at our sole and absolute discretion and without liability, at any time and without notice, modify MAF" | https://telegram.org/tos/mini-apps |
| Mini Apps ToS: data shared with the app (user ID, name, username, photo, language, Premium status, theme); IP address | CONFIRMED | n/a | "When you interact with a MA, it will automatically acquire your IP address." | https://telegram.org/tos/mini-apps |
| Neither ToS page shows a last-updated date | CONFIRMED (absence) | n/a | None | https://telegram.org/tos/bot-developers ; https://telegram.org/tos/mini-apps |
| Notes: "Financial-data-specific rules: none found" | WRONG (incomplete) | Section 6.3 has a financial-assets clause; section 9.1 names GDPR. See new findings below | See new findings | https://telegram.org/tos/bot-developers |
| Notes: "GDPR and Austrian law not researched" | PARTLY SUPERSEDED | Bot Dev ToS 9.1 names GDPR and leaves applicability to the developer. Austrian law still not checked | "such as the European Union's General Data Protection Regulation (GDPR)" | https://telegram.org/tos/bot-developers |
| adsgram blog: DeviceStorage and SecureStorage do not sync between devices | UNVERIFIABLE (search snippet only, not fetched) | Official pages are silent on sync. Do not rely on it | None | https://adsgram.ai/blog/adsgram/telegram-mini-app-tma-development-mistakes-and-how-to-avoid-them |
| Median service-worker facts (iOS 14, App-Bound domains, Cache Manifest) | UNVERIFIABLE for Telegram (generic, search snippet only) | Not Telegram-specific. Do not use for the Telegram client | None | https://docs.median.co/docs/service-workers |
| tma.js swipe-behavior: lock applies on mobile only | UNVERIFIABLE (search summary; page not fetched) | n/a | None | https://docs.telegram-mini-apps.com/platform/swipe-behavior |
| bugs.telegram.org 2024 swipe and close reports | UNVERIFIABLE (listing only, not opened) | n/a | None | https://bugs.telegram.org/c/36664/3 |
| DEV Community: swipe fix fails on iOS (one commenter) | UNVERIFIABLE (single anecdote) | Anecdote, not evidence | None | https://dev.to/nimaxin/how-to-fix-the-telegram-mini-app-scrolling-collapse-issue-a-handy-trick-1abe |
| Telegram-iOS issues #1377, #1385, #1410 | UNVERIFIABLE (listing only, not opened; status unknown) | n/a | None | https://github.com/telegrammessenger/Telegram-iOS/issues |
| Serverless early access, no public price, data location not disclosed (WebSearch snippets) | UNVERIFIABLE (secondary sources, not fetched) | Official page is silent (verified by absence). Snippets from drweb.de and zeli.app say early access, no price, location not disclosed; treat as leads only | None | https://www.drweb.de/telegram-serverless-bot-backend-plattform/ ; https://zeli.app/de/story/48918534 |

## New findings (not in the notes)

- Bot Dev ToS 6.3 (https://telegram.org/tos/bot-developers): "Telegram makes no guarantee that any data it stores in connection with your TPA" covers "key-value pairs in the Telegram Cloud Storage for Bots and Mini Apps", and developers "are expected to design your application and its persistence paradigms" to survive data loss. This backs the notes' verdict that CloudStorage cannot be the only copy, and is stronger than the notes say.
- Bot Dev ToS 6.3, financial assets: "it is your responsibility to ensure that any assets, credentials or other information is stored securely." It also says that if the owning Telegram account is lost, "all TPA it created may be terminated at any time". Relevant for a finance tracker that depends on one Telegram account.
- Bot Dev ToS 9.1 names GDPR. Applicability is left to the developer.
- Bot Dev ToS section 4 says TPA are "hosted on their developers' own servers". This predates Telegram-hosted Serverless (6 Oct 2026). The terms do not say how Serverless-stored data is treated. Ask before storing real financial data there.

## Corrections to make in the notes (not edited by me)

1. Replace the 15% Stars fee sentence with the conditional version (ToS 6.2.6, topics in private chats only). Remove "6.1" from that reference.
2. Remove "HTTP 401". Use: error type 'UNAUTHORIZED'.
3. Replace "no Mini App changes" in quotation marks with "no Mini App items listed".
4. Replace paraphrases in quotation marks with the exact wording: attachment menu, auth_date, viewport, Desktop Beta (see table).
5. Change "Financial-data-specific rules: none found" to list ToS 6.3 and 9.1.
6. Add ToS 6.3 "no guarantee" for Cloud Storage to the storage section.
7. Mark the Bot API 6.0 date as found: April 16, 2022.
8. Use removeItem as the SecureStorage delete method, with deleteItem noted as tma.js naming.

## Gaps not closed

- Serverless beta or GA status, pricing, SLA, data residency, encryption at rest, backups, retention and database size limits: not on any official page read. Check the BotFather Serverless settings or ask via @BotNews.
- tgcloud.ai ownership and terms: only the 302 redirect observed.
- Telegram Stars fee table on core.telegram.org/bots/payments-stars: not in the extracted text.
- Not fetched: bugs.telegram.org, Telegram-iOS issues, adsgram, Median, tma.js swipe page, drweb.de and zeli.app articles.
- Not checked: Telegram Desktop and Android debug menu steps (beyond iOS), Main Mini App "section_separator_color", and the 6.1 and 6.2 feature lists.

## Overall reliability rating

Overall: MEDIUM.
Why not low: the core facts hold. Every priority date, version, storage limit and the quoted ToS clauses match the official text, except the 15% fee and the HTTP 401 status.
Why not high: one wrong status (HTTP 401), one conditional fee stated as general (15%), a missed financial clause (ToS 6.3), five quoted phrases that are not verbatim (including "no Mini App changes"), and Serverless beta, pricing and data-residency facts that remain open.
