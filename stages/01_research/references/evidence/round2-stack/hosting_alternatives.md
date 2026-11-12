# Hosting and framework options for a personal Telegram bot (seen 2026-10-31)

Scope: webhook bot, SQL database, scheduled jobs, optional Telegram Mini App front end. Telegram Serverless excluded (another researcher). Target: under 100 messages/day, 0-5 EUR/month, built and maintained by Claude Code agents for a non-programmer owner.

Conventions: "seen 2026-10-31" = date fetched. A page's own "last updated" date is quoted when the page shows one. "not found" = no figure in the sources opened this session. Items marked "search summary" come from WebSearch snippets and were not opened.

Option 6 (Val Town) was added by the coordinator mid-task and is included.

## KQ1: Platform options 1-6 (free tiers, paid entry, webhook, cron, backups, Mini App hosting, cold starts, lock-in)

### Takeaway
Option 1 (Cloudflare Workers + D1 + Cron) is the only option in this set whose official free tier documents all four needs: a webhook host, a SQL database, scheduled jobs, and static hosting for a Mini App, with no daily-only cron and no inactivity pause. Its paid entry is $5/month. Vercel Hobby runs cron once per day and is personal-use only. Supabase Free pauses after 1 week of inactivity and has no backups. Deno Deploy Classic shut down on 2026-07-20, and the new Deno Deploy offers KV only, no SQL. Val Town has a 10 MB free SQLite and an official Claude Code plugin, but static hosting, backups and webhook behaviour were not found. The cheapest Hetzner server is EUR 5.99/month excl. VAT on the official page, which is marked unavailable there.

### Cited Findings

#### Summary table
Each cell is sourced in the per-option bullets below. Lock-in and "fit" are inferences (see Inferences).

| Item | 1 Cloudflare Workers + D1 + Cron | 2 Vercel + Neon/Supabase + Vercel Cron | 3 Supabase Edge + pg_cron | 4 Hetzner VPS + aiogram/grammY + SQLite | 5 Deno Deploy + KV | 6 Val Town |
|---|---|---|---|---|---|---|
| Free requests | 100,000/day | 1,000,000 function invocations/month (Hobby) | 500,000 Edge invocations (period not stated) | n/a (always-on server) | 1,000,000 inbound requests/month | 100,000 runs/day (no monthly cap listed) |
| Free CPU/time | 10 ms CPU per request; 10 ms per cron run | 4 Active CPU-hours/month; 300 s max duration | 2 s CPU per request; 150 s wall clock | n/a | 10 active CPU-hours/month | 1-minute max run time |
| Free cron | 5 cron triggers per account; minimum interval not stated | 100 jobs per project, but once per day only (Hobby) | pg_cron on Free not confirmed; "every second" granularity, no cap stated | systemd timer / cron (no plan limit found) | Deno.cron exists; count on Free not stated | every 15 minutes minimum; count not stated |
| Free database | D1: 5M rows read/day, 100k rows written/day, 5 GB total | Neon: 1 GB per project, 20 GB total; Supabase: 500 MB | Postgres 500 MB; paused after 1 week inactivity | SQLite on disk (40 GB NVMe on CX23) | no SQL; KV 1 GiB, 1M reads/month, 500k writes/month | SQLite 10 MB |
| Paid entry | $5/month minimum (Workers Paid) | Vercel Pro $20 per developer seat/month; Neon pay-as-you-go; Supabase Pro from $25/month | Supabase Pro from $25/month | CX23 EUR 5.99/month excl. VAT (official page, marked unavailable) | Pro $20/month | Pro $21/month shown on yearly checkout |
| Webhook | Yes; grammY guides for Workers (Deno and Node.js) | Yes; grammY guide for Vercel | Yes; grammY guide for Supabase Edge | Yes; Telegram ports 443/80/88/8443 | Yes; grammY guide for Deno Deploy | not verified (HTTP vals not checked) |
| Backups/export | D1 Time Travel: 7 days (Free), 30 days (Paid); export to R2 via Workflows | Neon history 6 hours (Free); Supabase daily backups kept 7 days (Pro only) | Free: no automatic backups; Pro: daily, kept 7 days | not researched | KV data not migrated automatically from Classic; export route not verified | not found |
| Mini App static | Workers Static Assets: requests free and unlimited | Static files: 100 MB upload cap on Hobby | not found | nginx on the VPS (inference) | not found | not found |
| Cold starts | Startup limit 1 s; latency not found | not found | not found (no mention) | none, always-on (inference) | idle apps stop after about 20-30 s; latency not found | not found |
| Lock-in (inference) | Medium: D1 and Workers APIs; SQLite data can be exported | Medium: Vercel runtime; Postgres is portable | Medium: Postgres portable; Deno-based Edge runtime | Low | High: proprietary KV; Classic shut down 2026-07-20, the shutdown was already announced in the page dated 2026-03-19 | High: hosted runtime and hosted MCP |

#### Option 1: Cloudflare Workers + D1 + Cron Triggers (grammY)
- Workers Free: 100,000 requests/day; 10 ms CPU per HTTP request; 10 ms CPU per Cron Trigger; 50 subrequests per request; 5 Cron Triggers per account; 64 MiB worker size; 1 second startup time. Page "Last updated Oct 29, 2026" - [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/) (seen 2026-10-31).
- Workers Paid: $5 USD minimum per account per month; 10 million requests included, then $0.30 per additional million; 30 million CPU-ms included, then $0.02 per additional million; "Requests to static assets are free and unlimited." Page "Oct 2, 2026" - [Cloudflare Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/) (seen 2026-10-31).
- Workers Paid: 250 Cron Triggers per account; CPU per cron run 30 s (interval under 1 hour) or 15 min (interval of 1 hour or more) - [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/) (seen 2026-10-31).
- Cron Triggers page: no minimum interval stated; example `* * * * *` ("At every minute"); the free-plan figure is in the limits page, which lists a 10 ms CPU per cron run on Free, which implies cron runs on Free - [Cloudflare Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/) ("Last updated Oct 17, 2026", seen 2026-10-31).
- D1 Free: 5 million rows read per day; 100,000 rows written per day; 5 GB storage total; 10 databases. Page "Last updated Oct 30, 2026" - [Cloudflare D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/) (seen 2026-10-31).
- D1 Paid: 25 billion rows read/month included, then $0.001 per million; 50 million rows written/month included, then $1.00 per million; 5 GB storage included, then $0.75 per GB-month; 100,000 databases included, then $0.10 per extra database/month. Same page.
- D1 Time Travel (point-in-time restore): up to 30 days on Workers Paid, 7 days on Workers Free; always on, no extra cost; restore overwrites the database in place; a D1 database can be exported automatically to R2 via the REST API and Cloudflare Workflows; Time Travel applies only to databases on the "production" backend (check with `wrangler d1 info`). Page "Apr 21, 2026" - [Cloudflare D1 Time Travel](https://developers.cloudflare.com/d1/reference/time-travel/) (seen 2026-10-31).
- grammY: official hosting guides "Cloudflare Workers (Deno)" and "Cloudflare Workers (Node.js)" listed on grammY's hosting page - [grammY hosting](https://grammy.dev/hosting/) (seen 2026-10-31).
- Drizzle: supports D1 (see KQ2).

#### Option 2: Vercel Functions + Neon or Supabase Postgres + Vercel Cron (grammY)
- Vercel Hobby included usage: 1,000,000 function invocations; 4 Active CPU-hours; 360 GB-hours provisioned memory; 100 GB Fast Data Transfer. Page "last_updated 2026-09-14" - [Vercel Hobby plan](https://vercel.com/docs/plans/hobby) (seen 2026-10-31).
- Hobby is for "non-commercial, personal use only" (the page cites Vercel's fair use guidelines). Same page.
- Vercel Pro upgrade: developer seats cost $20 per user/month; viewer seats free. Same page (the Pro base price was not fetched).
- Vercel limits, Hobby: 100 deployments created per day; max function duration 300 s (default and max); memory 2 GB / 1 vCPU; static file uploads 100 MB (Pro 1 GB); runtime logs kept 1 hour (Pro 1 day); Cron Jobs per project 100. Page "last_updated 2026-09-16" - [Vercel limits](https://vercel.com/docs/limits) (seen 2026-10-31).
- Vercel Cron, Hobby: once per day minimum; scheduling precision within the hour (about +/-59 min); expressions that run more often fail at deploy. Pro: once per minute, per-minute precision. Page "last_updated 2026-07-15" - [Vercel Cron usage and pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing) (seen 2026-10-31).
- Neon Free: 1 GB Postgres storage per project; 20 GB across all projects; 100 CU-hours per project per month; idle compute suspends after 5 minutes (cannot be turned off on Free); history/restore window 6 hours, capped at 1 GB; up to 100 projects. No date on page - [Neon pricing](https://neon.com/pricing) (seen 2026-10-31).
- Neon Launch: pay-as-you-go at $0.106 per CU-hour and $0.35 per GB-month; the page lists no fixed monthly fee. Same page.
- Supabase Free: 500 MB database; 50,000 monthly active users; 500,000 Edge Function invocations (period not stated); 5 GB egress plus 5 GB cached egress; "Free projects are paused after 1 week of inactivity"; no automatic backups on Free. Pro: from $25/month; daily backups kept 7 days. No date on page - [Supabase pricing](https://supabase.com/pricing) (seen 2026-10-31).
- grammY: official guide for Vercel listed on grammY's hosting page - [grammY hosting](https://grammy.dev/hosting/).

#### Option 3: Supabase Edge Functions + Supabase Postgres + pg_cron (grammY)
- Edge Functions limits: wall clock 150 s (Free), 400 s (paid); 2 s CPU time per request; 256 MB memory; no cold-start statement. No date on page - [Supabase Edge Functions limits](https://supabase.com/docs/guides/functions/limits) (seen 2026-10-31).
- Free database and pause rule: see Option 2 bullet for Supabase pricing (500 MB, pause after 1 week of inactivity, no backups on Free). The page does not define "inactivity".
- pg_cron (Supabase Cron): jobs "can run anywhere from every second to once a year"; recommendation of no more than 8 jobs concurrently, each under 10 minutes; no cap on number of jobs stated; no statement on availability on Free - [Supabase Cron](https://supabase.com/docs/guides/cron) (no date; seen 2026-10-31).
- grammY: official guide for Supabase Edge Functions listed on grammY's hosting page - [grammY hosting](https://grammy.dev/hosting/).

#### Option 4: Hetzner VPS + aiogram 3 or grammY + SQLite + systemd/cron
- Price: see KQ3. CX23 is the cheapest plan on the official page; it is listed as currently unavailable.
- Always-on server: no platform cold start (inference).
- Webhook ports: see KQ4 (443, 80, 88, 8443).
- Backups, snapshots and their prices: not researched.
- Local development, maintenance effort, and AI-agent handling: not researched.

#### Option 5: Deno Deploy + Deno KV (grammY)
- Deno Deploy Classic: "Deno Deploy Classic will be shut down on July 20, 2026." No new Classic accounts; existing projects had to move to console.deno.com before the shutdown date. Page "Last updated March 19, 2026" - [Deno Deploy Classic](https://docs.deno.com/deploy/classic) (seen 2026-10-31).
- Migration guide: Classic and the subhosting v1 API shut down on July 20, 2026; "your existing KV data is not automatically migrated" (contact support@deno.com); "The Deno.cron() API works the same way on the new Deploy"; new Deploy has 2 regions (US and EU) vs 6 on Classic; the page announces no end-of-life date for the new Deploy. "Last updated on June 18, 2026" - [Deno Deploy migration guide](https://docs.deno.com/deploy/migration_guide/) (seen 2026-10-31).
- New Deno Deploy free plan: 1M inbound HTTP requests/month; 10 active CPU-hours; 150 GiB-hours memory; idle apps shut down after about 20-30 s; KV 1 GiB storage, 1,000,000 read units/month, 500,000 write units/month; no separate database offering listed; 10 active apps per organization; 20 GiB egress; 5 custom domains; 1 day of log retention. Cron count on Free not stated. Pro: $20/month. No update date on page (footer 2026) - [Deno pricing](https://deno.com/pricing) (seen 2026-10-31).
- Unverified: a WebSearch summary of a Japanese tech article (https://www.issoh.co.jp/tech/details/18318/, not opened) says the new Deno Deploy itself will end around April 2027, after an announcement dated 2026-10-09. No official Deno source in this session confirms it. Treat as unconfirmed.
- grammY: official guide for Deno Deploy listed on grammY's hosting page - [grammY hosting](https://grammy.dev/hosting/).

#### Option 6: Val Town (added by coordinator)
- Pricing, Free: up to 100,000 runs per day (no monthly cap listed); minimum cron/interval frequency every 15 minutes; 1-minute max run time; 3 days of log retention. Pro: $21/month, shown with the yearly checkout (monthly price not confirmed); Pro minimum cron interval 1 minute; 1,000,000 runs per day. Static file hosting not mentioned. Number of cron/interval vals and SQLite size are not on this page. No date on page - [Val Town pricing](https://www.val.town/pricing) (seen 2026-10-31).
- SQLite storage limits: "You can store 10mb on the free plan"; "up to 1gb on the paid plan"; contact for more. No row, query, or database-count limits stated. "Last updated September 10, 2026" - [Val Town SQLite docs](https://docs.val.town/reference/std/sqlite) (seen 2026-10-31).
- SQLite model (search summary, page not opened): each val has its own private SQLite database; account-level global databases are described as legacy - [Val Town SQLite docs](https://docs.val.town/reference/std/sqlite) (search summary).
- Official Claude Code plugin: repository val-town/plugins, MIT license, about "Val Town for AI coding agents"; install with `claude plugin install valtown@claude-plugins-official`; installing registers the hosted Val Town MCP server at https://api.val.town/v3/mcp; first MCP use starts a browser OAuth login; ships Skills for web endpoints, scheduled jobs, SQLite, email, OAuth. No release date shown; about 100 commits; no GitHub releases - [val-town/plugins](https://github.com/val-town/plugins) (seen 2026-10-31).
- Not found in this session: HTTP-val webhook behaviour; backups or export; static hosting for a Mini App; cron/interval count; cold starts.

### Inferences
- For under 100 messages per day, the request and row volumes are not the binding constraint on options 1, 2, 3, 5 or 6. 100 messages/day is 0.1% of Cloudflare's 100,000 requests/day limit.
- The binding constraints are: Vercel Hobby cron once per day; Supabase Free pause after 1 week of inactivity and no backups; Deno Deploy Classic shutdown and KV-only storage; Val Town 10 MB SQLite on Free.
- Option 1 is the only option where the sourced free tier covers webhook, SQL, cron and static hosting. Paid entry ($5/month) is needed only if D1 limits or the 5-cron-trigger limit are exceeded.
- Vercel Hobby is personal use only. A bill-splitting bot for friends is personal use; any commercial use or team use is not. Per-minute or hourly reminders on Vercel need Pro ($20 per developer seat/month per the Hobby page).
- Supabase Pro ($25/month) is above the 0-5 EUR budget and is the only tier with backups. Supabase Free does not define "inactivity", so whether a daily-used bot keeps the project awake is not confirmed.
- Hetzner: the official cheapest plan is above 5 EUR before VAT, so option 4 fits the budget only if a lower official price is confirmed.
- Lock-in ranking (inference from the features above): Hetzner VPS lowest; Postgres options medium-low because Postgres is portable; Cloudflare and Vercel medium; Deno KV and Val Town highest (proprietary storage and runtime).
- Agent-friendliness, observed only: Val Town ships an official Claude Code plugin; grammY has about 3.9M weekly npm downloads (KQ2). Official docs quality, local dev stories, and agent performance on each platform were not researched.

### Gaps
- Cold-start latency: not found for any option. Cloudflare gives only a 1 s startup limit; Deno gives only the idle shutdown window.
- Supabase: definition of inactivity; pg_cron on Free; static hosting for a Mini App.
- Vercel: Pro base monthly price (only the per-seat $20 was seen); cold-start figures.
- Val Town: webhook suitability of HTTP vals; backups or export; static hosting; cron count; monthly Pro price (only the yearly-checkout $21 was seen).
- Deno: cron count on Free; export route for KV; the April 2027 end-of-life claim is unconfirmed.
- Hetzner: a confirmed current price and availability on an official page (see KQ3); backup and snapshot prices; the Hetzner pricing page at https://www.hetzner.com/pricing/ returned 404.
- Local development stories for each option: not researched.

## KQ2: Framework and ORM/adapter facts (grammY, aiogram, Drizzle, Kysely)

### Takeaway
grammY is actively maintained: npm latest 1.46.0, last registry modification 2026-08-26, about 3.9M weekly downloads. aiogram latest is 3.31.0, uploaded 2026-08-26. Drizzle documents D1 support (on RC packages at the time of the page). Kysely has no official D1 dialect; community packages only.

### Cited Findings
- grammY npm: dist-tags.latest = 1.46.0; time.modified = 2026-08-26T20:32:23.143Z - [npm registry: grammy](https://registry.npmjs.org/grammy) (seen 2026-10-31).
- grammY weekly downloads: 3,924,629 for 2026-10-23 to 2026-10-29 - [npm downloads API: grammy](https://api.npmjs.org/downloads/point/last-week/grammy) (seen 2026-10-31).
- grammY hosting guides in the site sidebar: Deno Deploy; Supabase Edge Functions; Cloudflare Workers (Deno); Cloudflare Workers (Node.js); Fly; Firebase Functions; Vercel; Zeabur (Deno). Also lists "Long Polling vs. Webhooks" guide (content not opened) - [grammY hosting](https://grammy.dev/hosting/) (seen 2026-10-31 through a text reader, so the sidebar grouping label is as the reader output showed it).
- aiogram PyPI: info.version = 3.31.0; latest release upload_time = 2026-08-26T00:00:41 - [PyPI: aiogram JSON](https://pypi.org/pypi/aiogram/json) (seen 2026-10-31).
- Drizzle D1: "Drizzle ORM fully supports the Cloudflare D1 database and Cloudflare Workers environment." Import from `drizzle-orm/d1` and pass the D1 binding to `drizzle()`. Install uses `drizzle-orm@rc` and `drizzle-kit@rc`. Page has no date; its two wrangler examples use different compatibility settings, and the query example is a fragment - [Drizzle: connect Cloudflare D1](https://orm.drizzle.team/docs/connect-cloudflare-d1) (seen 2026-10-31).
- Kysely with D1 (search summary only, packages not opened): no official D1 dialect; community options are @gawdn/kysely-cloudflare-d1 (search summary: no transactions, since D1's public API has none), kysely-d1 by samlaycock, and kysely-d1-external (v1.1.0; connects through Cloudflare's API instead of a Worker binding) - [npm: @gawdn/kysely-cloudflare-d1](https://www.npmjs.com/package/%40gawdn%2Fkysely-cloudflare-d1), [GitHub: samlaycock/kysely-d1](https://github.com/samlaycock/kysely-d1) (search results, seen 2026-10-31).

### Inferences
- Drizzle is the lower-risk ORM for option 1, because its D1 setup is documented by the maintainer. Kysely would rely on third-party dialects.

### Gaps
- Maintenance status, license and last release of the Kysely D1 dialects: not verified.
- aiogram weekly downloads: not fetched (no pypistats call).
- Drizzle docs for Postgres and SQLite on Neon/Supabase: not fetched.

## KQ3: Hetzner cheapest cloud server price in EUR (2026)

### Takeaway
The official Hetzner page lists the cheapest plan, Cost-Optimized CX23, at EUR 5.99/month excl. VAT, but marks it "currently unavailable". Third-party sources report lower prices and 2026 price changes that could not be confirmed on an official page.

### Cited Findings
- CX23 (Cost-Optimized): 2 vCPU, 4 GB RAM, 40 GB NVMe, 20 TB traffic (EU); EUR 5.99/month excl. VAT; EUR 0.0096/hour excl. VAT; "This product is currently unavailable. Please check back later." No page date - [Hetzner Cost-Optimized](https://www.hetzner.com/cloud/cost-optimized/) (seen 2026-10-31).
- Hetzner cloud page: Cost-Optimized from EUR 5.99/month excl. VAT; Regular Performance from EUR 6.49/month excl. VAT; one card labelled "Currently not available." No page date - [Hetzner Cloud](https://www.hetzner.com/cloud) (seen 2026-10-31).
- https://www.hetzner.com/pricing/ returned HTTP 404 and was not used.
- Conflicting, not official (search summary only): one guide says CX23 was EUR 3.99/month after an April 1, 2026 increase of about 30-37% on most plans, and a second adjustment effective June 15, 2026 applies to new orders - [privatedevops: Hetzner June 2026 price increase](https://privatedevops.com/news/hetzner-june-2026-cloud-price-increase-what-to-do). A VPSBenchmarks trial lists EUR 4.49/month for German locations and EUR 5.99/month on 28 Aug 2026 - [VPSBenchmarks CX23 trial, 28 Aug 2026](https://www.vpsbenchmarks.com/trials/hetzner_performance_trial_28Aug2026). An August 2026 comparison lists EUR 5.49 - [Cloud pricing comparison 2026-08](https://kimmo.suominen.com/stuff/cpc-2026-08.txt).
- Single source (search summary): a Spanish-language Bitdoze article says the order button for cost-optimized plans, including CX23, was disabled on several dates in September-October 2026 - [Bitdoze: Hetzner precios 2026](https://www.bitdoze.com/es/hetzner-cloud-precios-2026/).
- All official prices are excl. VAT. The VAT rate for the billing country was not checked.

### Inferences
- On the official page, the cheapest plan costs more than 5 EUR/month before VAT, and it is marked unavailable. Option 4 fits the 0-5 EUR budget only if a lower official price and availability are confirmed on hetzner.com.

### Gaps
- An official Hetzner pricing page with a date and the effective date of 2026 price changes: not found (pricing page 404).
- Snapshot and backup prices: not researched.

## KQ4: Telegram webhook constraints (apply to all options)

### Takeaway
Telegram webhooks need an HTTPS URL and accept only ports 443, 80, 88 and 8443. Every option must expose an HTTPS endpoint on one of those ports.

### Cited Findings
- setWebhook: the url parameter is an "HTTPS URL to send updates to"; "Ports currently supported for webhooks: 443, 80, 88, 8443"; max_connections is 1-100 (default 40); Telegram repeats the request after a non-2XX response and "give up after a reasonable amount of attempts" (count not stated) - [Telegram Bot API](https://core.telegram.org/bots/api#setwebhook) (no date; seen 2026-10-31).
- Getting updates section: updates "will not be kept longer than 24 hours" - [Telegram Bot API](https://core.telegram.org/bots/api) (no date; seen 2026-10-31).
- The setWebhook section does not mention Telegram Mini Apps.

### Inferences
- A platform outage longer than 24 hours would lose undelivered updates. Inference from the 24-hour statement; the page does not link the two rules.

### Gaps
- Number of retry attempts and the length of the retry window: not found.
