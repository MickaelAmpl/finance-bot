# Telegram Serverless: practical research (as of 31 Oct 2026)

Scope: can a personal finance Telegram bot run on Telegram Serverless (tgcloud) today. Checked 31 Oct 2026.
Method: saved official snapshot of https://core.telegram.org/bots/serverless read in full; live official pages checked with WebFetch (serverless, Mini Apps reference, Bot API, Bot API features, bots page with BotFather section); npm registry metadata for `@tgcloud/cli` and `@tgcloud/create-bot`; 12 WebSearch calls; fetches of secondary articles and one Hacker News thread. No BotFather login, no bot creation, no npm install, no code run.
Quote conventions: quotes without a tag are verbatim from the saved official snapshot. Quotes tagged (extracted) come from a WebFetch summary of the page, so check the wording against the page before reusing them. The only dated change on the official page is 6 Oct 2026.

## 1. Availability, enablement, pricing, quotas

### Takeaway
Officially, a bot owner turns Serverless on per bot in @BotFather. The official pages do not say who may use it, what it costs, or what the quotas are. Secondary sources from July to October 2026 describe a closed or request-based early-access beta, and one October 2026 tester saw no charge. The only quotas stated officially are file and HTTP size caps. The row-read cap below comes from one early-access account and is not published.

### Cited Findings
- Enablement: "In [@BotFather](https://t.me/BotFather), open your bot → **Serverless** and turn it on. That turns the feature on for this bot and unlocks its CLI access token, handlers, library, and database." - [Official page](https://core.telegram.org/bots/serverless)
- CLI token is separate from the bot token: "a separate token from your bot's API token". Path: BotFather → your bot → Serverless → CLI Access → Access token. - [Official page](https://core.telegram.org/bots/serverless)
- Eligibility, waitlist, beta, GA date: not stated on the [official page](https://core.telegram.org/bots/serverless), on the [bots BotFather section](https://core.telegram.org/bots#botfather) (extracted: no "Serverless" mention), or on the [Mini Apps reference](https://core.telegram.org/bots/webapps) (extracted: no availability statement).
- Price and free tier: not stated on any official page checked.
- Early access, secondary sources:
  - Telegram invited some contest winners to closed testing; the article says access "is currently limited to a narrow circle of testers" (translated from Russian). - [kod.ru, 14 Jul 2026](https://kod.ru/telegram-serverless-bot-api-test/amp) (news report, no hands-on test; cites a Telegram Info post, which was not located)
  - Access request via a "Get access to Serverless" button in BotFather; "not a general public release yet". - [Trashbox, 7 Sep 2026](https://trashbox.ru/link/2026-09-07-telegram-boty), based on [Habr news](https://habr.com/ru/news/1078906/) (extracted: page shows "5 сен", year not visible in capture)
  - Author of the Oct 2026 test says the "Get access to Serverless" button appears when access has not been granted; the route by which the author got access is not stated. - [Hackernoon, 21 Oct 2026](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted)
- Conflict: the official text describes a switch in BotFather, while secondary sources describe a request flow. Not resolved, because BotFather was not opened (login not permitted). A July 2026 Hacker News commenter wrote that the BotFather setting "isn't even there" ([HN thread](https://news.ycombinator.com/item?id=48918534), extracted summary).
- Pricing statements:
  - Dr Web, 15 Jul 2026: Telegram "has so far named neither a price nor a server location" (translated from German). The article adds that production planning needs terms and a data processing agreement. - [Dr Web](https://www.drweb.de/telegram-serverless-bot-backend-plattform/) (extracted)
  - Hackernoon, 21 Oct 2026: "The bot, database and Mini App incurred no hosting charge in this experiment." and "I found no public pricing in the documentation I checked." Author's early-access experience, not a published price. - [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted)
  - Hacker News, July 2026: a commenter says there is no pricing because the program is a restricted beta, citing a Telegram developer-channel post (not located). - [HN thread](https://news.ycombinator.com/item?id=48918534) (extracted summary)
- Official size and quota statements:
  - Uploads: "a bot can currently upload up to **50 MB** per file (and **10 MB** for a photo)." - [Official page](https://core.telegram.org/bots/serverless), Files section
  - getFile downloads: "Telegram's Bot API caps `getFile` downloads at **20 MB**, so that's the ceiling for both helpers." - same
  - Outbound fetch: "The **total response is capped at 30 MB**. That cap covers the whole response". Streaming does not raise the cap. - same, HTTP section
  - fetch response body is read as text ("`await res.json()` / `await res.text()`") or streamed chunk by chunk. - same
  - Batch inserts: "capped by SQLite's variable limit (`rows × columns`)", no number given. - same, Querying section
  - Not stated on the official page: CPU time per invocation, timeout, memory, database size, row count, request rate, outbound request count, number of modules, size limits for endpoint requests and responses.
- Observed limits, secondary, one early-access account, tests on 10 and 17 Oct 2026 - [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted):
  - Summing 50,000 rows succeeded; 50,001 failed with `rows_read limit exceeded`.
  - A single 10,000-row insert succeeded; a 10,001-row insert was rejected, with no partial insert left behind.
  - A full-history recalculation at 10,000 records took about 36 ms on Serverless (about 2.1 ms on the VPS). At 100,000 records the query failed with `rows_read limit exceeded`.
  - The author: "These were observed query limits on this early-access account, not published platform-wide guarantees."
- Discrepancy on the outbound cap: July 2026 sources give 32 MB. [Dr Web](https://www.drweb.de/telegram-serverless-bot-backend-plattform/) says "32 MB Antwortgröße" (translated: 32 MB response size), and an HN commenter quotes the HTTP docs as "capped at 32 MB". The current official page says 30 MB. The 6 Oct 2026 changelog does not mention a change. The cause is not stated.

### Inferences
- Blockers for a finance bot, in the order they would stop a build: (1) access, since no eligibility is documented; (2) ownership and export of the data, since no export is documented (section 5); (3) data location, encryption and terms (section 8); (4) scheduled reminders (section 4); (5) price and quotas.
- The documented caps (50 MB upload, 30 MB fetch response) are unlikely to bind for a personal ledger. The observed row-read cap (about 50,000 rows per query on one account) can bind for full-history queries, so keep running totals or per-period tables. This is an inference from one test.
- Official quotas cannot size cost or capacity. A decision needs written answers from Telegram.

### Gaps
- Eligibility, GA date, SLA, price, free tier, and CPU, timeout, memory, database-size, row and request limits: not found in official sources.
- The actual BotFather Serverless screen: not verified (no login).
- The Telegram developer-channel post cited on HN: not located.

## 2. Runtime and SDK

### Takeaway
Handlers and endpoints are plain JavaScript ES modules that run in a V8 isolate. Only the platform SDK and your own `tgcloud/` modules can be imported. There are no npm packages, no filesystem, and no network except the SDK's `fetch`. TypeScript, timeouts and CPU budget are not stated officially.

### Cited Findings
- "You write plain JavaScript modules, deploy them with a single command, and Telegram runs them in a fast, isolated V8 sandbox" - [Official page](https://core.telegram.org/bots/serverless), intro
- "At runtime, a module can see exactly two things: **the platform SDK** and **the other modules in your project**. There are no npm packages, no filesystem, and no network except through the SDK's `fetch`." - same, Module system section
- Imports must be relative with a `.js` extension and cannot leave `tgcloud/`; an npm import such as `zod` is listed as not resolvable. - same
- SDK surface: `db`, `api`, `fetch`, `InputFile`, `EndpointError`, `BotApiError`, plus submodules `sdk/db`, `sdk/api`, `sdk/fetch`. The official page calls this "the whole platform surface". - same, SDK section
- `api`: "Call any method as `api.<method>(params)`." "Every current — and future — Bot API method works with **no SDK update** required." Results are unwrapped; failures throw `BotApiError` with `.code`, `.description`, `.method`, `.parameters`. - same
- Files: `new InputFile(bytes, 'report.pdf', { type })`; `api.getFileContent(file_id)` returns a `Uint8Array`; `api.getFileStream` streams the body. Uploads are streamed as multipart. - same, Files section
- Runtime has no Node `Buffer`; `Uint8Array` is the byte type. - same, column types
- fetch streaming is documented for AI APIs: "which is how you consume server‑sent events or token‑by‑token output from **AI APIs**." Request bodies can be `Uint8Array`, `InputFile` or `FormData`. - same, HTTP section
- Console: "The standard global `console` is available". Output is captured and shown by `npx tgcloud run`. - same, Logging section
- Secrets: endpoints are described as the place for "talking to outside services with your secrets". No secrets store is documented. - same, Endpoints section
- Outbound fetch test: one Telegram JavaScript file, 30 requests from each environment, median 16 ms on Serverless versus 54 ms and 23 ms on two VPS. The author says one URL "is not an internet speed ranking." - [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted)
- Author: "Ordinary npm imports and Node's filesystem APIs are unavailable there." - same (extracted)
- Third-party skill, not Telegram-authored: runtime described as "V8 JavaScript (ES Module) isolates" with a "built-in SQLite database"; unsupported: "raw TCP sockets, background cron daemons, native Node.js C++ addons, or filesystem persistence outside SQLite." - [skills.sh, rijans/agent-skills/use-telegram-serverless](https://www.skills.sh/rijans/agent-skills/use-telegram-serverless) (extracted; first seen 11 Oct 2026)
- HN commenter (July 2026) lists missing "TypeScript support", "secrets management" and "dependency management". Commenter claim, not official. - [HN thread](https://news.ycombinator.com/item?id=48918534) (extracted summary)

### Inferences
- Anything beyond `fetch` must be hand-written in `lib/`: parsers, CSV import, currency or date helpers, crypto helpers, API clients for banks.
- Streaming an LLM response (for example, receipt parsing) is possible through `res.body`, but the 30 MB response cap still applies.
- CPU cost cannot be measured from inside the runtime. The Hackernoon author reports that "Telegram's internal clock returned zero for nontrivial CPU work."

### Gaps
- TypeScript: not stated on the official page.
- Whether `Date`, `Intl`, `crypto`, `URL`, `TextEncoder` and similar globals exist: not stated.
- Timeouts, memory, concurrency inside one invocation: not stated.
- Where third-party API keys are stored: not stated.

## 3. Handlers, update types, group chats

### Takeaway
Each Telegram update type maps to one file in `handlers/`. A missing or empty file means that update type is ignored. The official page names `message`, `inline_query`, `callback_query` and "any other Bot API update type". The Serverless pages say nothing about groups, so the Bot API rules (privacy mode, admin rights, `allowed_updates`) apply.

### Cited Findings
- Handler table: `handlers/message.js` handles "New incoming messages"; `handlers/inline_query.js` handles "New incoming inline queries"; `handlers/callback_query.js` handles "New incoming callback queries"; "… _any other Bot API update type_". - [Official page](https://core.telegram.org/bots/serverless), Projects and modules
- "An update type is handled **only if its handler file exists and is non‑empty**." - same
- "For `handlers/`, the name must be a Telegram update type. The platform advertises the valid set, so an invalid name is rejected up front." - same, `add` section
- CLI error example for `npx tgcloud add handlers`: "Available handlers/ types: callback_query, inline_query, chat_member, …" - same
- The handler gets the unwrapped payload (for `handlers/message.js`, the Message object); the second argument `ctx` carries the raw update as `ctx.update`. - same, Handlers section
- Webhook: "Telegram delivers updates to your bot through a webhook, which the platform manages for you — you never point it anywhere by hand." - same, webhook section
- `npx tgcloud webhook sync` "rebuilds `allowed_updates` from your deployed handlers." - same
- Bot API update types (extracted from [Bot API](https://core.telegram.org/bots/api)): the Update object lists `message`, `edited_message`, `channel_post`, `business_message`, `inline_query`, `callback_query`, `my_chat_member`, `chat_member`, `chat_join_request`, `message_reaction`, `poll`, `poll_answer`, `chat_boost`, `managed_bot` and others. The page's newest entry is Bot API 10.3 dated 24 Aug 2026.
- `my_chat_member`: reports changes to the bot's own status in a chat; in private chats it fires only when a user blocks or unblocks the bot (extracted, Bot API).
- `chat_member`: requires the bot to be an admin in the chat and "chat_member" in `allowed_updates` (extracted, Bot API). An empty `allowed_updates` excludes `chat_member`, `message_reaction` and `message_reaction_count` (extracted).
- `chat_join_request` needs the `can_invite_users` admin right; bots receive `poll_answer` only for polls they sent (extracted, Bot API).
- Privacy mode (extracted from [Bot API features](https://core.telegram.org/bots/features)): "Privacy mode is enabled by default for all bots, except bots that were added to a group as admins." With it on, bots receive commands meant for them, replies to their messages, service messages, private chats and channel messages. Bot admins receive all messages. To change it: `/setprivacy` in BotFather, then re-add the bot to the group, which is required for the change to take effect.
- The Serverless pages contain no group-specific statement. - [Official page](https://core.telegram.org/bots/serverless)

### Inferences
- A group-facing finance bot should expect only commands and replies as message updates, unless it is a group admin or privacy mode is off. This follows from the Bot API rules and was not tested on Serverless.
- Deploying handler files for `my_chat_member` and `chat_member` should add those types to the webhook's `allowed_updates`, since the sync rebuilds the list from deployed handlers. Verify with `npx tgcloud webhook` in a test group.
- Bot API 10.3 is the current Bot API version per the page; Serverless's supported version is not stated.

### Gaps
- Full list of handler names the platform accepts: printed only by the CLI, not checked.
- Whether `edited_message`, business and other update types work on Serverless beyond the generic "any other Bot API update type": not verified.
- Whether `inline_query` needs an inline-mode setting in BotFather: not checked.
- Whether handlers process updates concurrently or in order: not stated.
- Retry behavior when a handler throws: not stated.

## 4. Scheduled work (cron, delayed jobs, monthly reminders)

### Takeaway
No cron, scheduled trigger, timer or delayed job is documented. Code runs when an update arrives or when a Mini App calls an endpoint. No workaround is documented by Telegram. Monthly reminders need an external scheduler, or a design that sends the reminder on the user's next interaction.

### Cited Findings
- Trigger model: "When an update arrives — a message, a button press, an inline query — Telegram routes it to the matching handler … and calls its default export." - [Official page](https://core.telegram.org/bots/serverless), intro to Projects and modules
- "Endpoints can only be called this way — from your bot's Mini App, by a Telegram user — so there is no public API to protect and no login to build." - same, Endpoints section
- The snapshot contains no match for "cron" or "schedul" (schedule, scheduled). - local grep of the snapshot
- Hackernoon: "Telegram runs it when an update or a Mini App call arrives." - [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted, author's wording)
- HN commenter (July 2026): cron is "missing" and "not offered". - [HN thread](https://news.ycombinator.com/item?id=48918534) (extracted summary)
- Third-party skill: "background cron daemons" are unsupported (see section 2).
- Vendor blog, marketing, not verified: Telegram offers no built-in scheduler for bot messages; the suggested pattern is an external cron calling a backend. - [Crontap](https://crontap.com/use-cases/cron-jobs-for-telegram-bots) (search snippet only, not fetched)
- Example of an external pattern, not Telegram: a Cloudflare Workers cron bot template. - [github.com/brachkow/telegram-scheduled-message-bot](https://github.com/brachkow/telegram-scheduled-message-bot) (search snippet only, not fetched)

### Inferences
- An external cron cannot call an endpoint, because endpoints need valid Telegram initData from a Mini App. An external scheduler would have to call the Bot API directly with the bot token. That path does not reach the Serverless database, so the schedule and the ledger would have to live in another store, or the scheduler would need a separate service.
- Lazy reminders: store due dates in the database and, on any update from the user, send the overdue reminder. This works only when the user writes to the bot. It cannot push a reminder on the 1st of the month to a silent user.
- A monthly item can also be shown when the Mini App opens, with no push. This is a design option, not a documented feature.

### Gaps
- Scheduler, queue, delayed-job or timer API: not found.
- Retry on handler failure and delivery guarantees: not stated.
- Any roadmap item for scheduling: not found.

## 5. Database

### Takeaway
Each bot gets one SQLite database that persists between invocations. Tables are declared in `schema.js` with a Drizzle-style DSL and changed in two steps: `push` deploys the schema without touching data, and `migrate` applies changes after confirmation. Foreign keys are impossible (declaring one throws). Transactions, backups, owner export and data deletion are not documented.

### Cited Findings
- "Every bot gets its own database — an SQLite‑backed store that persists between invocations and is available to every module through `db`." - [Official page](https://core.telegram.org/bots/serverless), The database section
- "The schema DSL and query builder follow Drizzle" - same
- Tables are named exports of `schema.js`; `table()` builds a description at load time and does not touch the database; the platform discovers exported tables on deploy. - same
- Column factories: `text`, `integer`, `real` (alias `float`), `numeric`, `blob`, `boolean`, `json`. Modes: `timestamp` (Date from unix seconds), `timestamp_ms`, `bytes`, `boolean`, `json`. - same
- Modifiers: `primaryKey({ autoIncrement: true })`, `notNull()`, `unique()`, `default()`, `generatedAlwaysAs()`, `deprecated()`. Indexes: `index`, `uniqueIndex`, `unique`, `check`, expression and partial indexes. Table modifiers: `.strict()`, `.withoutRowid()`, `.deprecated()`. - same
- No foreign keys: "A declared foreign key would be silently inert"; `.references()` and table-level `foreignKey()` "throw when declared". The runtime runs with `PRAGMA foreign_keys` off. - same, No foreign keys section
- Query builder: `select().from().where().orderBy().limit().offset().groupBy().having().distinct()`; terminals `.all()`, `.get()`, `.values()`; `db.$count(table, where?)`; `insert().values().onConflictDoUpdate().returning().run()`; `update`; `delete`. "Every query is asynchronous." - same
- Raw SQL: `db.run`, `db.all`, `db.get`, `db.values` with the `sql` tag. Raw rows come back without mode conversion. - same
- "Deploying never touches your database." `migrate` statuses: safe (applied together on one confirmation), warning (each confirmed one at a time), manual (shown with guidance, applied by hand), undocumented (shown, not applied). "there is no 'apply all' for destructive changes." - same, Migrations section
- `migrate` flags: `--dry-run`, `--safe`, `--yes`, `--local`. Without a flag it "errors in a non‑interactive environment rather than guessing." - same, migrate section
- Dropping: deleting a table or column from `schema.js` does not drop it; mark it `.deprecated()` and confirm the drop in `migrate`. Type changes are manual raw SQL. - same
- `push` after a schema change "prints a summary of the pending changes and suggests `npx tgcloud migrate`. It never applies them itself." - same, push section
- Hackernoon author: "I couldn't inspect its synchronization settings" for Telegram's SQLite. - [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted)
- HN thread (July 2026): questions on database size cap and replication are asked; the thread gives no official answer. One commenter says Telegram runs "a few logical data centers", a claim that is unverified. - [HN thread](https://news.ycombinator.com/item?id=48918534) (extracted summary)
- Contradiction, unverified: a Russian-language Telegram channel (search snippet only, not fetched) says Telegram creates tables on its own. The official text requires `migrate` with confirmation. Treat the channel claim as wrong until proven. - [tgstat, Маркетинговая лаборатория](https://tgstat.ru/channel/@tg_mlab)
- Local grep of the snapshot: no match for "transaction" or "backup". "export" appears only in code samples (`export const`, `export default`), not as a data-export feature.

### Inferences
- Ledger integrity is the app's job: there are no foreign keys and no documented transactions. A transfer between two accounts needs two writes that succeed or fail together. Atomicity is unverified. Test it on a throwaway bot by forcing a failure in the second write.
- Bank CSV imports need chunked inserts. The exact ceiling depends on rows times columns, so measure it.
- Running totals in a separate table avoid full-history scans. The Hackernoon author suggests this for the garden benchmark but did not implement it in the live bot.
- There is no documented way for an owner to download the whole database. Any export must be code you write, for example an endpoint or a handler that sends a file through `InputFile`. Whether that can capture the full database is unknown.

### Gaps
- Transactions API: not found.
- Backups, point-in-time restore, owner download of the database: not found.
- Deleting all data, or the database when the bot is unlinked: not found.
- Database size cap and row cap: not stated. Only the observed row-read cap is known.
- Durability, replication, locking and concurrency semantics: not stated.
- Migration rollback: not documented. The only paths are deprecation or manual SQL.

## 6. Mini App front-end hosting and endpoints

### Takeaway
Mini App build output is deployed with `push` and served at `https://app<app_id>.tgcloud.ai/`. Endpoints are served under `/api/` and called with `Telegram.WebApp.Serverless.call`. The platform validates initData and rejects missing or invalid data with 401 before your code runs, so `ctx.initData.user` can be trusted. The CLI does not run your frontend build.

### Cited Findings
- "One `push` deploys the code and the static files together, and the app is served at `https://app<app_id>.tgcloud.ai/`" - [Official page](https://core.telegram.org/bots/serverless), Mini App front-end section
- "`push` uploads the folder exactly as it is on disk … and never runs your build" - same
- `tgcloud.jsonc` keys under `static`: `source` (required), `spa`, `immutable`, `headers`, `redirects`. `"static": false` removes the deployed site on the next push. - same
- "The site is served from the root of its own host"; "The same host answers your endpoints under `/api/`" - same
- "`endpoints/getProfile.js` answers `POST /api/getProfile`." - same, Projects section
- Endpoint signature: `export default async function (input, ctx)`. `ctx.initData` is "already **verified by the platform**". "A call without valid init data is rejected with `401` before your code runs" - same, Endpoints section
- "The platform checks that the call comes from a Telegram user inside your Mini App before your code runs, and hands you that user." - same
- Errors: `throw new EndpointError(description, parameters?)` reaches the client as is. "Any other exception is reported as a generic internal error, and the real message goes only to your logs" - same
- Client call: `Telegram.WebApp.Serverless.call('getProfile', { lang: 'en' }, function (err, profile) { … })`; the input "must be a plain object". - same
- Mini Apps reference (extracted from [Mini Apps reference](https://core.telegram.org/bots/webapps)): signature `call(name[, input][, callback])`; error object fields `message`, `type` (`'ENDPOINT_ERROR'` or `'UNAUTHORIZED'`), `parameters`, `status` (HTTP status, or 0 if the request could not be completed).
- Telegram Web opens Mini Apps in an iframe, so the official page says not to add `X-Frame-Options`. - [Official page](https://core.telegram.org/bots/serverless)
- Abuse reporting: "Mini Apps on tgcloud.ai are published by independent developers." - same
- Third-party SDK (search snippet only, not fetched): tma.js documents a serverless component; its legacy docs show an `abortSignal` option, so the SDK version matters. - [docs.telegram-mini-apps.com](https://docs.telegram-mini-apps.com/packages/tma-js-sdk/features/serverless)

### Inferences
- A finance Mini App can take user identity from `ctx.initData.user.id` without a login flow, because the official page says endpoints can only be called from the Mini App by Telegram users.
- Mini App data access goes only through endpoints you write. There is no client-side database.
- Browser testing without Telegram is possible only with `npx tgcloud run` and hand-written `--ctx` init data, which the CLI does not verify.

### Gaps
- Endpoint request and response size caps, timeouts, rate limits, caching of endpoints, CORS for other domains, custom domains, Mini App bundle size limit, static hosting quotas: not stated.
- The init-data validation algorithm for your own server code: not checked in this session (the Mini Apps reference has a separate validation section, not fetched).

## 7. Developer workflow, testing, logs, rollback, AI guidance

### Takeaway
The CLI behaves like a git-style deploy tool: offline `status` and `diff`, atomic `push`, and a revision check against other deployers. `run` executes a handler on the platform with your local files, so it is not a local emulator. Logs are the console output shown by `run` and in the BotFather console. No production log access, rollback or version history is documented. The official AI section scaffolds `AGENTS.md` and `docs/tgcloud-sdk.md`. Telegram's official page does not mention a CLAUDE.md or a skill file.

### Cited Findings
- CLI commands: `init`, `add`, `login`, `status`, `diff`, `push`, `migrate`, `run`, `fetch`, `pull`, `reset`, `webhook`, `completion`, `upgrade`. It "needs Node.js 18 or newer." - [Official page](https://core.telegram.org/bots/serverless), CLI section
- "`npx tgcloud run` executes a handler on the platform using your **local** files, without publishing them." "This is the tightest loop for iterating on logic — no deploy, no waiting for a real message." - same
- "The platform runs the module against the module space assembled from your **local** project" - same
- Logs: "Its output is captured and shown by `npx tgcloud run`, which makes it your primary debugging tool during development." Running a handler "even shows its **Console** output right in the chat" in BotFather. - same
- Revision: "Every project has a monotonically increasing **revision** in the cloud, bumped on each deploy." A stale push is "**rejected** instead of silently overwriting their work". `push --force` overwrites the cloud state, marked "(dangerous)". - same, Staying in sync section
- Atomic push: "`push` uploads every changed module in one atomic batch". Deletions mirror: "Anything present in the cloud but absent from your project is removed". - same
- `reset` "Discards your local changes and restores the modules from the last known cloud state." - same
- CI: "Commands exit non‑zero on failure"; `TGCLOUD_TOKEN` is the CI token variable. - same
- CLI versions (npm registry, read via Python JSON parse; the `jq` tool is not installed here): `@tgcloud/cli` 0.1.0 published 12 Jul 2026, 0.1.1 on 12 Jul, 0.1.2 on 13 Jul, 0.2.0 on 6 Oct 2026 (latest). Maintainer "asmico", MIT license. The package metadata has no repository, homepage or bugs URL. - [npm: @tgcloud/cli](https://registry.npmjs.org/@tgcloud/cli)
- Official changelog 6 Oct 2026: "All modules now live in the `tgcloud/` folder. Run `npx tgcloud upgrade` once in a project created with an earlier version of the CLI." - [Official page](https://core.telegram.org/bots/serverless), Recent changes
- Scaffolder: `npm create @tgcloud/bot` resolves to `@tgcloud/create-bot`, versions 0.1.0 (12 Jul 2026) and 0.1.1 (12 Jul 2026, latest). The name `@tgcloud/bot` returns "Not found" on the npm registry. - [npm: @tgcloud/create-bot](https://registry.npmjs.org/@tgcloud/create-bot), [npm: @tgcloud/bot](https://registry.npmjs.org/@tgcloud/bot)
- AI section, verbatim: "every new one is scaffolded with an `AGENTS.md` and a `docs/tgcloud-sdk.md` reference that agentic coding tools read automatically." - [Official page](https://core.telegram.org/bots/serverless), Building with AI
- Official example: "opencode            # or Claude Code, Cursor, … — any agent that reads AGENTS.md" - same
- "`AGENTS.md` is part of your project — edit it as the bot grows so the guidance stays accurate." - same
- CLAUDE.md, skill files, MCP for coding agents: not mentioned on the official page. Local grep: "CLAUDE" appears only in the opencode example, and "skill" does not appear.
- Third-party skills, not Telegram-authored: `use-telegram-serverless` (rijans/agent-skills; first seen 11 Oct 2026) says "Powered by Telegram Serverless" and does not say Telegram wrote or endorsed it; its listed audits include Snyk "Warn" (extracted). [skills.sh](https://www.skills.sh/rijans/agent-skills/use-telegram-serverless). A second skill, `telegram-serverless` by stark-ai-de, appeared in search results. Not installed or reviewed in depth.
- Author friction note: "uploading code and creating tables are separate steps" (opinion). - [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted)

### Inferences
- Rollback in practice is probably a git revert of `tgcloud/` files followed by `push`, plus manual handling of any schema change. Database rollback is manual. This is inference, not documented.
- `run` against a finance ledger is a risk. Unless the docs say `run` uses a separate data copy, a test call could write to real rows. Test on a separate bot first.
- The only documented separation is one project per bot. A second test bot is therefore the practical staging option (inference from "Every project is tied to one bot").
- Team use: the revision check gives conflict detection. No branches or environments are documented.

### Gaps
- Local emulator: not documented; `run` requires the platform.
- Whether `run` reads and writes the live database or a sandbox copy: not stated.
- Production log retention, search and alerts: not stated.
- Version history, named releases, rollback command: not found.
- Dev, staging and production environments: not found.
- Content of the scaffolded `AGENTS.md` and `docs/tgcloud-sdk.md`: not inspected. The package was not downloaded or unpacked.

## 8. Data location, privacy and terms

### Takeaway
The official page does not state where data is stored, how it is encrypted, how long it is kept, or how it is deleted. The Bot Developer Terms (fetched text, no effective date visible, no mention of Serverless) make the developer responsible for encryption at rest and for protecting data. They also let Telegram delete chats, messages and files sent to a bot at any time. For a personal finance ledger this is the largest open item.

### Cited Findings
- "Telegram Serverless lets you run backend code for your bot and Mini App **directly on Telegram's infrastructure**" - [Official page](https://core.telegram.org/bots/serverless), intro
- "Each invocation runs in a lightweight V8 isolate, close to Telegram's own systems" - same, Why serverless. "close to" is not a location statement.
- Region, data residency, encryption, retention, backup: not stated on the official page (local grep: no match for "region", "encrypt", "backup").
- Dr Web, 15 Jul 2026: Telegram has named neither a price nor a server location; "every production plan remains built on sand until terms and a data processing agreement are available" (translated from German). - [Dr Web](https://www.drweb.de/telegram-serverless-bot-backend-plattform/) (extracted)
- Local-only data: "Only `.js` files inside `tgcloud/` … are **deployed**. Everything else … stays on your machine." - [Official page](https://core.telegram.org/bots/serverless), Anatomy of a project
- CLI token: "The CLI keeps it in `.tgcloud/`, which is git‑ignored, and never prints the secret part." - same, login section
- Bot Developer Terms (extracted from [telegram.org/tos/bot-developers](https://telegram.org/tos/bot-developers); the fetch returned no effective date):
  - Section 4.4(a): "Make sure user data is always encrypted at rest and stored separately from its encryption key"
  - Section 4.4: "it is your responsibility to employ all reasonable efforts to protect any data you receive"
  - Section 4.2(c): "Delete all user data obtained through or in connection with Bot Platform upon the cessation of your TPA's operations"
  - Section 6.3: "Telegram may delete or make inaccessible whole chats, messages, media and files sent to and from your TPA at any time."
  - Section 12.3: "Telegram makes no commitment, either express or implied, about Bot Platform's … dependability, uptime"
  - Section 2: "TPA are hosted on their developers' own servers". The text does not name Serverless.
  - Section 6.3 also names "key-value pairs in the Telegram Cloud Storage for Bots and Mini Apps".
- Bots page, general text not updated for Serverless (extracted): "Bots are connected to their owner's server, which processes inputs and requests from users." - [core.telegram.org/bots](https://core.telegram.org/bots#botfather)
- HN commenter (July 2026): "no encryption for the bot backend". Commenter claim, unverified. - [HN thread](https://news.ycombinator.com/item?id=48918534) (extracted summary)

### Inferences
- A ledger held on Serverless would sit in a Telegram-run store under those terms. The developer must encrypt at rest (section 4.4(a)), but Serverless's own storage encryption is undocumented. The developer may not be able to show compliance. This needs Telegram's answer in writing.
- Telegram may delete data at any time (section 6.3) and gives no uptime promise (section 12.3). A personal finance record needs a second copy kept outside the platform.
- If the owner or the users are in the EU, a data processing agreement and a statement on location are needed, per the Dr Web point. Not checked against law.

### Gaps
- Data location; encryption at rest and in transit on the platform; backups; retention periods; access logs; staff access; sub-processors: not found.
- A data processing agreement or processing terms specific to Serverless: not found.
- Deletion on bot unlink or account deletion: not found.
- Whether Serverless falls under the Bot Developer Terms as written: not stated, since the fetched terms do not name it.

## 9. Community experience since launch (dated)

### Takeaway
Little first-hand reporting exists. The most detailed account is one Hackernoon author, published 21 Oct 2026, with measurements on an early-access account. A July 2026 Hacker News thread asked the same questions about limits, cron, pricing and access, and got no official answers. No GitHub issues, Reddit threads, or Serverless-specific outage reports were found. A Telegram-wide disruption on 13 Aug 2026, reported by a third-party provider, is not linked to Serverless.

### Cited Findings (chronological)
- 12 Jul 2026: `@tgcloud/cli` 0.1.0 and `@tgcloud/create-bot` 0.1.0 first published on npm. - [npm: @tgcloud/cli](https://registry.npmjs.org/@tgcloud/cli), [npm: @tgcloud/create-bot](https://registry.npmjs.org/@tgcloud/create-bot)
- 13 Jul 2026: `@tgcloud/cli` 0.1.2. - same
- 14 Jul 2026: news report that Telegram began inviting some contest winners to closed testing, invitations sent from @ContestBot (per the article). - [kod.ru](https://kod.ru/telegram-serverless-bot-api-test/amp)
- 15 Jul 2026: Dr Web article, no hands-on test, no price or location named by Telegram. - [Dr Web](https://www.drweb.de/telegram-serverless-bot-backend-plattform/). The same day, a summary of the HN thread: [zeli.app](https://zeli.app/story/48918534).
- About July 2026 (relative "3 months ago" as seen on 31 Oct): HN thread "Telegram Serverless", 212 points, 105 comments. Questions with no answer in the thread: execution time and storage quotas, database size cap, replication, cron, pricing. One commenter says pricing is absent because it is a restricted beta, citing an unlocated Telegram developer-channel post. The only first-hand comment reads "I have updated my app just now" with no details. A commenter reports that the BotFather setting "isn't even there". - [HN thread](https://news.ycombinator.com/item?id=48918534) (extracted summary)
- 5 Sep 2026 (Habr news page; year inferred from the Trashbox citation): early-access request through @BotFather, based on community reports and screenshots, not an official statement. - [Habr news](https://habr.com/ru/news/1078906/) (extracted)
- 7 Sep 2026: Trashbox repeats the early-access report. "exact limits, supported technologies, deployment features, data storage and cost are unknown" (translated). - [Trashbox](https://trashbox.ru/link/2026-09-07-telegram-boty)
- 6 Oct 2026: official Mini App hosting and endpoints added; CLI 0.2.0 published the same day. - [Official page](https://core.telegram.org/bots/serverless), Recent changes; [npm](https://registry.npmjs.org/@tgcloud/cli)
- 11 Oct 2026: third-party skill `use-telegram-serverless` first seen on skills.sh. - [skills.sh](https://www.skills.sh/rijans/agent-skills/use-telegram-serverless)
- 21 Oct 2026: Hackernoon, Jabrail Khalilov. Functional checks on 10 Oct and benchmarks on 17 Oct 2026. Key points, all from the author:
  - No hosting charge during the experiment; no public pricing found in the docs.
  - Query row limit and insert limit as in section 1.
  - Writes were slower on Serverless: 32 separate inserts took 533 ms versus 18.16 ms and 95.48 ms on the two VPS; accepting a watering took 22 ms versus 0.74–0.87 ms. The JSON test was faster: 11.1 ms versus 29.8 ms and 34.2 ms.
  - Timer caveat: the internal clock returned zero for CPU-heavy work, so the author used execution time from the run API, which includes overhead.
  - Scope: "SQL and compute timings exclude message delivery to the Telegram client and cold starts." The full Mini App HTTP path was not benchmarked.
  - Opinion: the Serverless version "would need a different design" for full-history recalculation.
  - Source: [Hackernoon](https://hackernoon.com/telegram-can-host-your-bot-should-you-give-up-your-vps) (extracted)
- 13 Aug 2026: a third-party provider (GREEN-API) reports a Telegram messenger disruption of 3 h 15 min, with failed requests and delayed messages. Not related to Serverless. - [GREEN-API](https://green-api.com/articles/en/all-news/08-13-2026-technical-issues-resolved/) (search snippet only, not fetched)

### Inferences
- Every number above comes from one or two early-access accounts. They may change with the platform and do not establish a service level.
- The public signal is consistent across sources: access is gated, pricing is not announced, and the runtime's hard limits are not documented.

### Gaps
- No GitHub issues found for tgcloud; the npm metadata has no repository link.
- No Reddit threads found in search. X and most Telegram channels were not searched; WebSearch was limited to 12 calls and there is no X search tool here.
- No Serverless outage reports found.
- No production finance or budgeting bot on Serverless found.
- The "Маркетинговая лаборатория" Telegram channel says Telegram creates tables automatically. Search snippet only, not fetched. This conflicts with the official migrate flow, so treat it as unreliable.
