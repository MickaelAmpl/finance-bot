# Telegram Mini Apps: capabilities and limits for a single-user finance tracker

Research date: 31 Oct 2026. Tool calls used: 16 (WebFetch and WebSearch; search results used as leads, not as primary facts, unless marked).

Source legend:
- Core = https://core.telegram.org/bots/webapps (official Mini Apps page)
- Changelog = https://core.telegram.org/bots/api-changelog (official)
- Mini Apps ToS = https://telegram.org/tos/mini-apps (official, user-facing)
- Bot Dev ToS = https://telegram.org/tos/bot-developers (official, developer terms)
- Serverless = https://core.telegram.org/bots/serverless (official)
- tma.js docs = https://docs.telegram-mini-apps.com (THIRD-PARTY community SDK docs, not Telegram; used where Telegram's page is silent, flagged below)

## 1. Bot API version and Mini App features (2024-2026)

### Takeaway
Latest Bot API is 10.3 (24 Aug 2026), which has no Mini App changes. Every feature the project needs (CloudStorage, DeviceStorage, SecureStorage, BiometricManager, full-screen, home-screen shortcut, downloadFile, shareMessage, orientation lock) has been available since 2023-2025. Twelve Bot API releases from 7.2 to 10.2 touched Mini Apps, and 10.2 (July 2026) changed the origin rules.

### Cited Findings
- Latest Bot API version: 10.3, August 24, 2026, "no Mini App changes" - [Changelog](https://core.telegram.org/bots/api-changelog)
- 6.1 (Jun 20, 2022): attachment menu in groups/channels, BackButton, haptics, header/background colors, openInvoice - [Core](https://core.telegram.org/bots/webapps) (version index)
- 6.2 (Aug 12, 2022): closing confirmation, popups - [Core](https://core.telegram.org/bots/webapps)
- 6.4 (Dec 30, 2022): QR scanner, clipboard reading - [Core](https://core.telegram.org/bots/webapps)
- 6.7 (Apr 21, 2023): launch from inline results and direct links - [Core](https://core.telegram.org/bots/webapps)
- 6.9 (Sep 22, 2023): CloudStorage, write-access and contact requests - [Core](https://core.telegram.org/bots/webapps) (the changelog extract did not include 2022-2023 text, so this date is from the Core version index only)
- 7.0 (Dec 29, 2023): SettingsButton - [Core](https://core.telegram.org/bots/webapps)
- 7.2 (Mar 31, 2024): BiometricManager - [Changelog](https://core.telegram.org/bots/api-changelog); [Core](https://core.telegram.org/bots/webapps)
- 7.6 (Jul 1, 2024): direct links open at full height by default; section_separator_color - [Changelog](https://core.telegram.org/bots/api-changelog)
- 7.7 (Jul 7, 2024): vertical swipe control (enableVerticalSwipes / disableVerticalSwipes) - [Changelog](https://core.telegram.org/bots/api-changelog)
- 7.8 (Jul 31, 2024): Main Mini App (set in BotFather, reachable from bot profile or link), shareToStory - [Changelog](https://core.telegram.org/bots/api-changelog)
- 7.10 (Sep 6, 2024): SecondaryButton, setBottomBarColor; MainButton renamed BottomButton - [Changelog](https://core.telegram.org/bots/api-changelog)
- 8.0 (Nov 17, 2024): full-screen (requestFullscreen / exitFullscreen), safe-area insets, home-screen shortcut (addToHomeScreen / checkHomeScreenStatus), emoji status, shareMessage, downloadFile, LocationManager, motion sensors, lockOrientation / unlockOrientation, third-party initData validation (Ed25519), iOS debugging support - [Changelog](https://core.telegram.org/bots/api-changelog); method-level version tags also on [Core](https://core.telegram.org/bots/webapps)
- 9.0 (Apr 11, 2025): DeviceStorage and SecureStorage - [Changelog](https://core.telegram.org/bots/api-changelog)
- 9.1 (Jul 3, 2025): hideKeyboard - [Changelog](https://core.telegram.org/bots/api-changelog)
- 9.5 (Mar 1, 2026): iconCustomEmojiId on BottomButton - [Changelog](https://core.telegram.org/bots/api-changelog)
- 9.6 (Apr 3, 2026): requestChat (PreparedKeyboardButton) - [Changelog](https://core.telegram.org/bots/api-changelog)
- 10.1 (Jun 11, 2026): InputRichMessageContent in Web App query results; sendChatJoinRequestWebApp - [Changelog](https://core.telegram.org/bots/api-changelog)
- 10.2 (Jul 14, 2026): security hardening. Mini App methods are blocked when called from origins other than the Mini App's original domain. Applies automatically to all Mini Apps from July 20, 2026. Opting out through BotFather makes the bot responsible for keeping the Mini App free of links to untrusted sites - [Changelog](https://core.telegram.org/bots/api-changelog)
- 10.3 (Aug 24, 2026): no Mini App changes - [Changelog](https://core.telegram.org/bots/api-changelog)
- Serverless (Telegram-hosted backend): the page's most recent change is dated October 6, 2026. It does not appear in the changelog entries read (which end at 10.3) - [Serverless](https://core.telegram.org/bots/serverless)
- Attachment menu: the page says it is "limited to major Telegram Ad Platform advertisers, but all bots can use it on the test server" - [Core](https://core.telegram.org/bots/webapps)
- Telegram Mini Apps ToS: Telegram may alter, suspend or discontinue Mini App features at any time and accepts no liability - [Mini Apps ToS](https://telegram.org/tos/mini-apps)

### Inferences
- The feature set is complete for a finance tracker UI and storage. The risk is not missing features but frequent changes to the platform rules (origin enforcement added in 10.2 within the last three months).
- Origin enforcement (10.2) matters if the front end is served from a domain different from the one declared for the Mini App, or embedded from another domain. A single-domain deployment should be unaffected. To verify on the real setup.

### Gaps
- Release date for Bot API 6.0 (menu button launch): not found in the fetched text.
- Full text of 2022-2023 changelog entries was not read; only the Core version index was used for those dates.
- Whether Serverless is GA or beta, and which Bot API version introduced it: not stated (Serverless page), not in changelog entries read.

## 2. Storage options, limits and persistence

### Takeaway
Three storage types, each with a hard cap: CloudStorage 1024 items x 4096 characters per user per bot; DeviceStorage 5 MB per user per bot, device-local; SecureStorage 10 items, backed by iOS Keychain / Android Keystore. Only SecureStorage states encryption at rest. None of the three documents what happens on reinstall, new device or logout. Keeping all finance data in Telegram storage with no backend is not realistic.

### Cited Findings
- CloudStorage (Bot API 6.9+): "Each bot can store up to 1024 items per user in the cloud storage." Keys 1-128 characters from A-Z, a-z, 0-9, _ and -. Values 0-4096 characters. Methods: setItem, getItem, getItems, removeItem, removeItems, getKeys - [Core](https://core.telegram.org/bots/webapps)
- CloudStorage encryption, server location, retention, cross-device availability: not stated on Core - [Core](https://core.telegram.org/bots/webapps)
- DeviceStorage (Bot API 9.0+): "All data is stored locally and is available only to the bot that created it." "Each bot can store up to 5 MB per user using this storage." Methods: setItem, getItem, removeItem, clear. Encryption, reinstall and new-device behaviour: not stated - [Core](https://core.telegram.org/bots/webapps)
- SecureStorage (Bot API 9.0+): "On iOS, it uses the system Keychain; on Android, it uses the Keystore." "This ensures that all stored values are encrypted at rest and inaccessible to unauthorized applications." Up to 10 items per user per bot - [Core](https://core.telegram.org/bots/webapps)
- SecureStorage restore: getItem returns { value, canRestore }. canRestore is true only if the value is missing and can be restored; the tma.js page says this is "can be restored from the iCloud backup" and "Available on iOS only". restoreItem requires user confirmation - [tma.js SecureStorage](https://docs.telegram-mini-apps.com/packages/tma-js-sdk/features/secure-storage) (third-party docs)
- SecureStorage value size, key count beyond 10, and reinstall behaviour on Android: not stated in the fetched text - [tma.js SecureStorage](https://docs.telegram-mini-apps.com/packages/tma-js-sdk/features/secure-storage)
- Method-name discrepancy: Core lists SecureStorage delete as removeItem; tma.js documents deleteItem. Check against the live SDK before coding - [Core](https://core.telegram.org/bots/webapps); [tma.js SecureStorage](https://docs.telegram-mini-apps.com/packages/tma-js-sdk/features/secure-storage)
- Telegram Serverless storage: one SQLite-backed database per bot, persisting between invocations. Database size limits, backups and retention: not stated - [Serverless](https://core.telegram.org/bots/serverless)
- Telegram's Bot Dev ToS: "user data is always encrypted at rest and stored separately from its encryption key" is a developer obligation (section 4.4(a)) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Unverified secondary claim (search summary only, not fetched): a third-party blog says DeviceStorage and SecureStorage do not sync between devices - [adsgram blog](https://adsgram.ai/blog/adsgram/telegram-mini-app-tma-development-mistakes-and-how-to-avoid-them)

### Inferences
- Derived ceiling for CloudStorage: 1024 x 4096 = 4,194,304 characters per user per bot. The limit is in characters, not bytes, so the byte size is larger for non-ASCII text (e.g. Cyrillic). Not measured.
- DeviceStorage (5 MB) and CloudStorage are not documented as backups. Without a documented reinstall or new-device guarantee, they cannot be the only copy of financial data.
- Because of the ToS encryption duty, values in CloudStorage or DeviceStorage would have to be encrypted by the app before writing. A possible design is to keep the key in SecureStorage and the encrypted data in CloudStorage (separate storage, as the ToS requires). This is the author's inference, not a documented pattern.
- Verdict: client-side storage alone is not a safe system of record. Storage caps, undocumented persistence and the encryption burden argue for a backend (own server or Telegram Serverless) plus regular exports.

### Gaps
- CloudStorage encryption at rest, data location, retention and whether it survives reinstall or a new device: not found in official sources.
- DeviceStorage encryption and reinstall behaviour: not found.
- SecureStorage value size limit: not found.

## 3. Authentication (initData)

### Takeaway
Telegram documents two server-side checks: HMAC-SHA256 with the bot token, and Ed25519 third-party validation without the token. Telegram gives no exact expiry window; the docs say to check auth_date against your own maximum age. Restricting the app to one Telegram user ID is not documented; it is a check you write yourself.

### Cited Findings
- initData is the raw query string; initDataUnsafe should not be trusted: "Data from this field should not be trusted." - [Core](https://core.telegram.org/bots/webapps)
- HMAC check: secret = HMAC-SHA256 with key "WebAppData" applied to the bot token; data-check-string = all key=value pairs except hash, sorted alphabetically, joined by line feeds (0x0A); compare HMAC-SHA256 (hex) with hash - [Core](https://core.telegram.org/bots/webapps); [tma.js init-data](https://docs.telegram-mini-apps.com/platform/init-data) (third-party docs)
- auth_date is a Unix timestamp; "Check it to reject stale data." No window given - [Core](https://core.telegram.org/bots/webapps); [tma.js init-data](https://docs.telegram-mini-apps.com/platform/init-data) (page: "gives no exact window")
- Ed25519 third-party validation (Bot API 8.0, Nov 17, 2024): no bot token needed. Check string = bot_id, colon, "WebAppData", line feed, sorted pairs excluding hash and signature. Verify the base64 signature field. Public keys: production e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d; test 40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec - [Core](https://core.telegram.org/bots/webapps); [Changelog](https://core.telegram.org/bots/api-changelog)
- initData fields include auth_date, hash, query_id, start_param, user (id, first_name, last_name, username, language_code, is_premium, is_bot, photo_url, etc.) - [tma.js init-data](https://docs.telegram-mini-apps.com/platform/init-data)
- initData is empty when the app is launched from a keyboard button or inline mode - [Core](https://core.telegram.org/bots/webapps)
- Serverless: the platform checks initData before endpoint code runs; missing or invalid initData is rejected with HTTP 401; ctx.initData is "already verified by the platform". The algorithm, secret and freshness check are not stated - [Serverless](https://core.telegram.org/bots/serverless)

### Inferences
- Restrict to one user: after HMAC or Ed25519 validation, compare user.id with the one allowed ID and reject all others. This is a developer-side check, not a documented Telegram feature.
- Validate on every backend request, not only at login. initData is sent with each call (per Serverless docs) and has an auth_date.
- Choose the max age for auth_date yourself; no number is documented by Telegram.
- Store the bot token only on the server that validates (HMAC path). The Ed25519 path avoids storing the token.

### Gaps
- Exact recommended auth_date expiry window: not found.
- Telegram's own recommendation for single-user restriction: not found.
- Whether initData is still valid for long-running sessions: not stated.

## 4. Hosting requirements, backend, offline

### Takeaway
Telegram needs only an application URL, and the app is "just a set of static files". No hosting provider is named. HTTPS is not stated for production (only the test environment allows plain HTTP). Telegram now offers its own hosting and backend (Serverless). Offline behaviour is not documented; treat it as unsupported until tested on real devices.

### Cited Findings
- "Internally, Mini Apps are typical web applications, which are displayed in WebView." "they are just a set of static files." "The only thing Telegram needs from the developer is the application URL." - [About the Platform](https://docs.telegram-mini-apps.com/platform/about) (third-party docs)
- "creating a Mini App without creating a Telegram Bot is not possible." "Mini Apps are not self-served services." - [About the Platform](https://docs.telegram-mini-apps.com/platform/about) (third-party docs)
- Test environment: "you may use HTTP links without TLS" to test a Mini App. Production HTTPS requirement not stated - [Core](https://core.telegram.org/bots/webapps)
- Hosting or server requirements: not stated - [About the Platform](https://docs.telegram-mini-apps.com/platform/about)
- Bot Dev ToS: "TPA are hosted on their developers' own servers", provided they comply with the terms; Operate the TPA in "a reasonably secure environment" (section 4.4(c)) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Serverless (Telegram-hosted): Mini App build served at https://app<app_id>.tgcloud.ai/ with SPA fallback, caching and header options. Endpoints at POST /api/<name> on the same host. Enabled in BotFather per bot - [Serverless](https://core.telegram.org/bots/serverless)
- Serverless runtime: plain JavaScript; "no npm packages, no filesystem, and no network except through the SDK's fetch"; outbound response capped at 30 MB; uploads 50 MB (10 MB photos); getFile downloads 20 MB - [Serverless](https://core.telegram.org/bots/serverless)
- Serverless: pricing, execution time limits, rate limits, memory, hosting regions, cold start: not stated - [Serverless](https://core.telegram.org/bots/serverless)
- Telegram Web opens Mini Apps in an iframe - [Serverless](https://core.telegram.org/bots/serverless)
- Offline: not stated by Telegram in the fetched text - [About the Platform](https://docs.telegram-mini-apps.com/platform/about); [Core](https://core.telegram.org/bots/webapps)
- Generic WebView facts (not Telegram-specific, search summary only): Android WebView supports service workers for SSL requests; WKWebView service-worker support on iOS arrived in iOS 14 and only with App-Bound domains; HTML5 Cache Manifest is deprecated on iOS - [Median service workers](https://docs.median.co/docs/service-workers) (search summary, not fetched)

### Inferences
- Free static hosting (Vercel, Cloudflare Pages, GitHub Pages) fits the documented model: a URL serving static files. Telegram does not name these providers, and their free-tier limits were not researched.
- The existing Telegram bot can host the Mini App (set in BotFather). Telegram says a bot is required; attaching a Mini App to an existing bot is the author's inference, not a documented step.
- Offline: Telegram's embedded WebView cache and service-worker support are not documented. The Median notes describe generic wrappers, not the Telegram client. Do not design for offline use until tested on iOS and Android.
- Keep the Mini App and any API calls on the one declared domain, given the 10.2 origin rule.

### Gaps
- Production HTTPS requirement: not stated in fetched text.
- Telegram-specific offline and service-worker behaviour: not found.
- Free-tier limits of Vercel, Cloudflare Pages, GitHub Pages: not researched (out of scope).

## 5. Client differences, pain points, debugging, test environment

### Takeaway
Six client targets: Android, iOS, macOS, Telegram Desktop, Telegram Web A and Web K. Telegram itself says implementations differ. Known pain points cluster on mobile: swipe-to-close, keyboard and viewport. Debugging exists on each platform, but it is hidden behind secret menu taps and beta builds. No official performance data was found.

### Cited Findings
- Supported clients: Android, iOS, macOS, Telegram Desktop, Telegram Web A, Telegram Web K. "As long as all applications are being developed separately, there may be variations in how they implement the platform." - [About the Platform](https://docs.telegram-mini-apps.com/platform/about) (third-party docs quoting Telegram)
- Viewport: viewportHeight updates in real time but "not fast enough to pin UI"; use viewportStableHeight for bottom-pinned elements (CSS variables --tg-viewport-height and --tg-viewport-stable-height) - [Core](https://core.telegram.org/bots/webapps)
- Swipe: from 7.7 developers can disable vertical swipes; users can still minimize or close by swiping the header - [Core](https://core.telegram.org/bots/webapps)
- Swipe conflicts (search summary of tma.js docs, not fetched): the lock applies on mobile; desktop and web return early in the sample code - [tma.js swipe-behavior](https://docs.telegram-mini-apps.com/platform/swipe-behavior)
- Telegram bug tracker (2024 reports, listing only): users close apps by accident through swipe-to-close; scrolling up in a scroll container on Android closed the web app, marked fixed - [bugs.telegram.org](https://bugs.telegram.org/c/36664/3)
- Developer write-up (anecdotal): one commenter says the swipe fix still fails on iOS but works on Android - [DEV Community](https://dev.to/nimaxin/how-to-fix-the-telegram-mini-app-scrolling-collapse-issue-a-handy-trick-1abe)
- Telegram-iOS GitHub issues (listing only, not opened, status unknown): #1410 (opened Jun 3, 2024) keyboard overlaps content in a Mini App; #1377 asks for env(safe-area-inset-bottom) support; #1385 no Done button on the keyboard in Web Apps - [Telegram-iOS issues](https://github.com/telegrammessenger/Telegram-iOS/issues)
- iOS debugging: tap the Settings icon 10 times, turn on "Allow Web View Inspection", connect by USB, open Safari > Develop > [device] - [Core](https://core.telegram.org/bots/webapps)
- Android debugging: enable USB debugging; in Telegram Settings press and hold the version number twice; enable "Enable WebView Debug" in Debug Settings; open chrome://inspect/#devices in Chrome - [Core](https://core.telegram.org/bots/webapps)
- Telegram Desktop (Windows, Linux): download the Beta; Settings > Advanced > Experimental settings > enable webview inspection; right-click in the WebView > Inspect. Beta "isn't yet supported on macOS" (this section) - [Core](https://core.telegram.org/bots/webapps)
- Telegram macOS: download the Beta; click the Settings icon 5 times for the debug menu; enable "Debug Mini Apps"; right-click > Inspect Element - [Core](https://core.telegram.org/bots/webapps)
- Test environment: a fully separate server with its own accounts and bots created through @BotFather. Access: iOS - tap Settings 10 times, Accounts, Login to another account, Test; Desktop - Settings, Shift+Alt, right-click "Add Account"; macOS - Settings icon 10 times for the Debug Menu, then Cmd+click "Add Account". Bot API test path: https://api.telegram.org/bot<token>/test/METHOD_NAME - [Core](https://core.telegram.org/bots/webapps)
- iOS debugging support was extended in Bot API 8.0 (Nov 17, 2024) - [Changelog](https://core.telegram.org/bots/api-changelog)
- Performance (rendering, memory, startup on low-end phones): not found in official sources

### Inferences
- Pain points are mobile-specific (swipe, keyboard, viewport). Forms with bottom-pinned inputs and fixed bottom bars need testing on real phones, not only in the desktop client.
- iOS debugging requires a Mac with Safari and a USB cable; Android debugging requires desktop Chrome. Desktop Telegram debugging is in Beta.
- The test environment is a separate account universe; test data does not carry over to the live bot.

### Gaps
- Mini App performance numbers: not found.
- Current status of Telegram-iOS issues #1377, #1385, #1410: not verified (listing only).
- Whether Telegram Desktop macOS Beta now supports the debugging described: not verified.

## 6. Launch methods

### Takeaway
Eight launch methods. For a single-user app the stable entry points are the menu button or the Main Mini App (profile "Launch app"). Direct links with startapp are useful for deep links. The attachment menu is documented as limited to ad-platform advertisers.

### Cited Findings
- Main Mini App: set in BotFather; profile "Launch app" button; link https://t.me/botusername?startapp; mode=compact opens half height; Bot API 7.8 - [Core](https://core.telegram.org/bots/webapps); [Changelog](https://core.telegram.org/bots/api-changelog)
- Menu button: set in BotFather (/setmenubutton) or per user via setChatMenuButton; Bot API 6.0 - [Core](https://core.telegram.org/bots/webapps)
- Keyboard button: web_app KeyboardButton; sendData up to 4096 bytes, closes the app - [Core](https://core.telegram.org/bots/webapps)
- Inline button: web_app InlineKeyboardButton; the bot replies via answerWebAppQuery - [Core](https://core.telegram.org/bots/webapps)
- Inline mode: InlineQueryResultsButton in answerInlineQuery; no chat access; Bot API 6.7 - [Core](https://core.telegram.org/bots/webapps)
- Direct link: https://t.me/botusername/appname, optional ?startapp= and &mode=compact; Bot API 6.7; full height default since 7.6 - [Core](https://core.telegram.org/bots/webapps)
- Attachment menu: set via /setattach or Bot Settings; startattach link; limited to major Telegram Ad Platform advertisers, but all bots can use it on the test server; groups and channels from 6.1; main button hidden until user interaction - [Core](https://core.telegram.org/bots/webapps)
- Chat join requests (guard bots): sendChatJoinRequestWebApp; chat_join_request_query_id added in 10.1 - [Core](https://core.telegram.org/bots/webapps); [Changelog](https://core.telegram.org/bots/api-changelog)

### Inferences
- The menu button (per user) or Main Mini App gives a persistent entry point for one user.
- Do not put any sensitive data in startapp or other link parameters. Links are visible and shareable (this follows the project's general rule; not a Telegram rule).
- The attachment menu is not a practical entry point for a private app, given the advertiser restriction on the page.

### Gaps
- Whether the attachment menu is available to a non-advertiser bot in production: the page says limited; no further detail found.
- Exact date of the menu button launch (Bot API 6.0): not found.

## 7. Policies: developer terms, privacy, data handling

### Takeaway
Two official documents apply: the Mini Apps ToS (user-facing) and the Bot Platform Developer Terms (developer obligations, covering bots and Mini Apps as "TPA"). The developer must publish a privacy policy, encrypt stored user data at rest, keep the key separate, collect only what is essential, and delete data on request or when it is no longer needed. Telegram states it has no access to data exchanged between users and developers via the Mini App. Neither page shows a last-updated date.

### Cited Findings
- Developer must have a privacy policy: "all TPA must be bound by a privacy policy that is easily accessible to their users" detailing data stored, collection method and purpose - [Bot Dev ToS](https://telegram.org/tos/bot-developers) (section 4)
- Telegram's standard policy applies by default only if the TPA has none of its own. "TPAs must set up a Privacy Policy in @BotFather" - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Encryption: "Make sure user data is always encrypted at rest and stored separately from its encryption key" (4.4(a)) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Collection: "You agree not to use your TPA to collect, store, aggregate or process data beyond what is essential" (4.3). Voluntarily submitted data is an exception with explicit, revocable consent - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Prohibited: data collection for large datasets, machine learning models and AI products (4.3) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Deletion: delete user data on request, when retention is no longer needed to operate the TPA, and all data on cessation; exception for data users expressly agreed to retain (4.2) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- These duties survive termination (10.2 lists 4.2 and 4.4) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Termination: may lead to immediate termination of account, TPA or both (4.2); TPA may be removed from Bot Platform; "You will not be compensated for any direct or indirect losses resulting from your termination" (10) - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Telegram data access: Mini Apps automatically receive the user's IP address; Telegram may share user ID, public name, username, profile photo, language, Premium status and theme parameters; chat info if opened in a group. "Telegram does not have any access to or control over data shared between users and SP via MAF." Data shared with Telegram itself is governed by the Telegram Privacy Policy - [Mini Apps ToS](https://telegram.org/tos/mini-apps)
- Mini Apps ToS on developer responsibility: the service provider "is responsible for handling and storing any data provided to it" - [Mini Apps ToS](https://telegram.org/tos/mini-apps)
- Payments: Telegram does not process payments for physical goods; digital goods must use Telegram Stars only; Telegram withholds a non-refundable 15% fee (6.1-6.2.6). Stars are the only payment route for digital goods - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Financial-data-specific rules: none found beyond the payments section and the general data rules - [Bot Dev ToS](https://telegram.org/tos/bot-developers); [Mini Apps ToS](https://telegram.org/tos/mini-apps)
- No last-updated date on either page; the Bot Dev ToS changes take effect "when we post the revised Bot Developer Terms" (14) - [Bot Dev ToS](https://telegram.org/tos/bot-developers); [Mini Apps ToS](https://telegram.org/tos/mini-apps)

### Inferences
- The "no access" statement in the Mini Apps ToS covers the traffic between the Mini App and the developer's own server. Telegram still sees IP addresses and the initData fields. If data is stored in Telegram Serverless, the data sits on Telegram's infrastructure, and the "no access" statement is not obviously applicable. Read the Serverless terms before relying on it (not found in this research).
- The developer terms say "TPA" covers bots and Mini Apps. Whether they apply to a private, single-user app is not stated. The safe assumption is that they apply and a privacy policy is needed.
- Telegram can discontinue features and terminate accounts without compensation. For a finance tracker that is a continuity risk. Regular export of the data to a location the author controls follows from this.
- Austrian and EU data-protection law (GDPR) was not researched.

### Gaps
- Whether the developer terms apply to a private single-user Mini App: not stated.
- Telegram's own retention of Mini App logs and IP addresses: not stated.
- Any financial-services or financial-data rule beyond payments: not found.
- Serverless terms regarding who can access data stored there: not found.

## 8. Telegram Stars (one line)
Digital goods in Mini Apps must be sold via Telegram Stars; Telegram withholds a 15% non-refundable fee (Bot Dev ToS 6.2, 6.2.6) - [Bot Dev ToS](https://telegram.org/tos/bot-developers). Not needed for this project.

## 9. Telegram Serverless (hosted backend, new since 2026)

### Takeaway
Telegram now offers a hosted backend for Mini Apps: JavaScript endpoints, one SQLite database per bot, static hosting for the front end, and platform-verified initData. This makes "no own backend" technically possible. Data residency, encryption, retention, pricing and beta status are not stated.

### Cited Findings
- Telegram Serverless "lets you run backend code for your bot and Mini App directly on Telegram's infrastructure." Intended uses include Mini App backends - [Serverless](https://core.telegram.org/bots/serverless)
- Modules: plain JavaScript, deployed with `npx tgcloud push`; each invocation runs in a V8 isolate - [Serverless](https://core.telegram.org/bots/serverless)
- Storage: SQLite-backed store, one database per bot, schema in schema.js, queried through sdk/db (Drizzle-style); foreign keys unsupported; schema changes applied with `npx tgcloud migrate` - [Serverless](https://core.telegram.org/bots/serverless)
- Limits stated: uploads 50 MB per file (10 MB photos); getFile downloads 20 MB; outbound fetch total response 30 MB; batch inserts limited by SQLite variable count - [Serverless](https://core.telegram.org/bots/serverless)
- Not stated: execution time, endpoint request/response size, rate limits, memory, module count, invocation quotas, DB size, backups, retention, pricing, hosting regions, cold start - [Serverless](https://core.telegram.org/bots/serverless)
- Calling: Telegram.WebApp.Serverless.call(name, input, callback); input must be a plain object; SDK sends initData automatically; errors: ENDPOINT_ERROR (EndpointError) and UNAUTHORIZED - [Serverless](https://core.telegram.org/bots/serverless); [Core](https://core.telegram.org/bots/webapps) (Serverless section)
- Platform check: "The platform checks that the call comes from a Telegram user inside your Mini App before your code runs." Missing or invalid initData gives HTTP 401 - [Serverless](https://core.telegram.org/bots/serverless)
- Encryption at rest, data location, retention and backups: not stated - [Serverless](https://core.telegram.org/bots/serverless)
- CLI credential stored in .tgcloud/credentials (git-ignored) or TGCLOUD_TOKEN env var; separate from the bot token - [Serverless](https://core.telegram.org/bots/serverless)
- Abuse reports for Mini App subdomains go to abuse@telegram.org - [Serverless](https://core.telegram.org/bots/serverless)
- Enablement: BotFather > bot > Serverless > on; also available in BotFather on mobile - [Serverless](https://core.telegram.org/bots/serverless)
- Bot API version and GA/beta status: not stated - [Serverless](https://core.telegram.org/bots/serverless)

### Inferences
- Serverless plus the SQLite store removes the need for a separate server for a single-user app. This is technically sufficient for storing and reading records.
- Outbound calls are only via the SDK fetch and no npm packages are allowed. Any bank or open-banking integration would have to be plain HTTP calls. Not in scope here.
- Because Telegram hosts the data, the ToS encryption duty (4.4(a)) applies to the developer, but whether the platform encrypts at rest is unknown. Ask or check the Serverless terms before storing real financial data there.
- Serverless is new (page changed 6 Oct 2026, 25 days before this research). Expect changes; no SLA was found.

### Gaps
- Beta or GA status, pricing, SLA, data residency, encryption at rest, backups, retention: not found.
- Serverless does not appear in the changelog entries read (latest 10.3, 24 Aug 2026): the Bot API version is unknown.

## 10. Fit for a single-user finance tracker (synthesis)

### Takeaway
Technically sound as a Mini App front end for one user: Telegram gives an authenticated user ID on every request, a documented launch path, and enough storage for entry screens and small datasets. Not sound as the sole store for finance data: the storage caps, undocumented persistence across reinstall or new device, the developer-side encryption duty, and the termination and discontinuation clauses all argue for a backend (own server or Telegram Serverless) plus regular exports.

### Cited Findings
- Hard limits: CloudStorage 1024 items x 4096 characters per user per bot; DeviceStorage 5 MB; SecureStorage 10 items - [Core](https://core.telegram.org/bots/webapps)
- Developer must encrypt stored user data at rest, separate from the key - [Bot Dev ToS](https://telegram.org/tos/bot-developers) (4.4(a))
- Privacy policy must be set in @BotFather - [Bot Dev ToS](https://telegram.org/tos/bot-developers)
- Termination without compensation; features may be discontinued - [Bot Dev ToS](https://telegram.org/tos/bot-developers) (10); [Mini Apps ToS](https://telegram.org/tos/mini-apps)
- Mini App requires a bot; "not self-served services" - [About the Platform](https://docs.telegram-mini-apps.com/platform/about) (third-party docs)
- Offline behaviour not documented - [Core](https://core.telegram.org/bots/webapps); [About the Platform](https://docs.telegram-mini-apps.com/platform/about)

### Inferences
- Fit for the front end: good. Entry forms, dashboards, charts and the Telegram login (initData) suit the platform.
- Fit for storage: poor as the only copy. Use an own backend or Telegram Serverless SQLite as the record store, with client-side or server-side encryption and a key kept apart from the data. Export to a location the author controls.
- Authentication is solid: validate initData on the server (HMAC with bot token, or Ed25519 without it), check auth_date, and allow only the author's user ID.
- Reliability: plan for no offline mode and for mobile quirks (swipe, keyboard, viewport). Test on real iOS and Android devices early.
- Compliance: the Bot Dev ToS applies to the Mini App (privacy policy in BotFather, minimal data collection, deletion rules). Whether it applies to a private app is not stated; treat it as applicable.
- Platform risk: Telegram may change rules (10.2 origin enforcement from 20 Jul 2026) or discontinue features; no compensation. Keep an export.

### Gaps
- Everything listed in sections 2-9 under "Gaps". The most consequential: CloudStorage and DeviceStorage persistence on reinstall or new device; Serverless encryption, residency and status; production HTTPS requirement; Telegram-specific offline behaviour.
- Not researched: GDPR and Austrian law; free-tier limits of Vercel or Cloudflare; actual performance on low-end phones.
