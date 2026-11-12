# Agent skills and tooling for a Telegram bot, Mini App and data layer (state as of 2026-10-31)

Method: gh API reads (repo metadata, file contents, code and repo search), WebFetch, 4 WebSearch calls (aggregator results only used as leads). Nothing was installed, cloned or run. WebFetch answers are produced by a fetch model, so quoted wording may differ slightly from the page; check the page before quoting externally. Stars, license and "pushed" dates are GitHub API values read on 2026-10-31. Trust scale is defined under Key Question 3.

## Key Question 1: Does Telegram or the framework vendors publish agent guidance (AGENTS.md, CLAUDE.md, llms.txt)?

### Takeaway
Telegram publishes agent guidance only for its new Serverless platform: every new tgcloud project is scaffolded with an AGENTS.md. For the Bot API, grammY, aiogram and the Mini App SDK (tma.js) there is no end-user agent file: aiogram and tma.js ship AGENTS.md/CLAUDE.md for their own contributors, and grammY and the Mini App docs ship none. No official Telegram Mini App skill or agent file was found.

### Cited Findings
- Telegram Serverless, section "Building with AI": new projects are scaffolded with an `AGENTS.md` and a `docs/tgcloud-sdk.md` reference that agentic coding tools read automatically; the suggested flow is `npm create @tgcloud/bot my-bot`, then `npx tgcloud run` (local test), `npx tgcloud push` and `npx tgcloud migrate` (go live) - [core.telegram.org/bots/serverless#building-with-ai](https://core.telegram.org/bots/serverless#building-with-ai) (markdown source: [core.telegram.org/bots/serverless.md](https://core.telegram.org/bots/serverless.md)). The page names Claude Code and Cursor and "any agent that reads AGENTS.md"; it does not mention CLAUDE.md, llms.txt or skills.
- Serverless built-in database is SQLite. Foreign keys are not supported: the runtime runs with `PRAGMA foreign_keys` off, and declaring `.references()` or a table-level foreign key makes the schema fail to deploy - [core.telegram.org/bots/serverless.md](https://core.telegram.org/bots/serverless.md) (sections "the database", "no foreign keys"). `push` deploys the schema without touching data; `migrate` applies changes after confirmation - same page, "migrations".
- Serverless runtime: no npm packages at runtime; one library `sdk` with submodules `sdk/db`, `sdk/api`, `sdk/fetch` - same page, "the module system" and "the SDK". CLI package is `@tgcloud/cli` (MIT, version 0.2.0, published 2026-10-06, 5 dependencies, Node.js 18+) - [registry.npmjs.org/@tgcloud/cli](https://registry.npmjs.org/@tgcloud/cli); Node requirement from [serverless.md](https://core.telegram.org/bots/serverless.md), "command-line interface".
- Serverless limits stated on the official page: a bot can upload up to 50 MB per file (10 MB for photos), `getFile` downloads up to 20 MB, outbound `fetch` response capped at 30 MB - [serverless.md](https://core.telegram.org/bots/serverless.md), "files" and "http".
- Serverless "Recent changes" (dated 2026-10-06): Mini App front-end is deployed together with the bot; Mini App calls endpoints via `Telegram.WebApp.Serverless.call`; `tgcloud.jsonc` project config added; relative imports with `.js` allowed - [serverless.md](https://core.telegram.org/bots/serverless.md), "recent changes".
- Serverless availability: the official page does not state beta, early access or pricing. It says to turn on Serverless for the bot in @BotFather. Unofficial secondary articles (not verified) describe it as early with access requested via @BotFather - [drweb.de](https://www.drweb.de/telegram-serverless-bot-backend-plattform/), [zeli.app](https://zeli.app/de/story/48918534).
- Official grammY package for Serverless: `@grammyjs/tgcloud` (MIT, 9 stars, created 2026-10-11, pushed 2026-10-18) provides typings for the `sdk`, a build step from `src/**/*.ts` into `tgcloud/`, and grammY on the platform. `npm create @grammyjs/tgcloud my_bot` adds "a TypeScript section in AGENTS.md" - [github.com/grammyjs/tgcloud](https://github.com/grammyjs/tgcloud) (README).
- Telegram doc index: [core.telegram.org/llms.txt](https://core.telegram.org/llms.txt) exists. It is a Markdown index of the Bot API, bot guides, the MTProto API and optional pages (30 links, advises fetching the `.md` pages). It contains no agent instructions.
- Telegram test environment (Bot API): a separate account and bot; requests go to `https://api.telegram.org/bot<token>/test/METHOD_NAME`; flood limits are not raised; plain HTTP is allowed for Mini Apps and Web Login in the test environment - [core.telegram.org/bots/features.md#testing-your-bot](https://core.telegram.org/bots/features.md#testing-your-bot).
- Telegram Mini Apps page: [core.telegram.org/bots/webapps](https://core.telegram.org/bots/webapps) has no AI, agent, AGENTS.md or llms.txt content in the first 100,000 characters. Its test-environment sections (`#using-bots-in-the-test-environment`, `#debug-mode-for-mini-apps`) are linked but fall beyond the part I read.
- Mini App docs site: [docs.telegram-mini-apps.com/llms.txt](https://docs.telegram-mini-apps.com/llms.txt) returns HTTP 404 (checked 2026-10-31); [docs.telegram-mini-apps.com/llms-full.txt](https://docs.telegram-mini-apps.com/llms-full.txt) also returns 404.
- grammY: [grammy.dev/llms.txt](https://grammy.dev/llms.txt) returns the VitePress HTML home page, so no llms file is served. The repo root [github.com/grammyjs/grammY](https://github.com/grammyjs/grammY) has no AGENTS.md, CLAUDE.md, llms.txt or llms-full.txt. grammY org repos include `awesome-grammY` (283 stars, pushed 2026-10-29) - [github.com/grammyjs/awesome-grammY](https://github.com/grammyjs/awesome-grammY).
- aiogram: root has [AGENTS.md](https://github.com/aiogram/aiogram/blob/dev-3.x/AGENTS.md) and CLAUDE.md. AGENTS.md is written for contributors to the library ("how coding agents should contribute to aiogram on dev-3.x", base branch dev-3.x, use Serena MCP for code navigation, run `make lint`). The repo also has `.claude/skills` with 13 maintainer skills (for example `bot-api-bump`, `aiogram-release`, `test-bot-api-codegen`) - [github.com/aiogram/aiogram/tree/dev-3.x/.claude/skills](https://github.com/aiogram/aiogram/tree/dev-3.x/.claude/skills). aiogram repo: 5,913 stars, MIT, pushed 2026-10-31. [docs.aiogram.dev/llms.txt](https://docs.aiogram.dev/llms.txt) returns 404.
- tma.js (Mini App SDK monorepo, [github.com/Telegram-Mini-Apps/tma.js](https://github.com/Telegram-Mini-Apps/tma.js): MIT, 1,209 stars, pushed 2026-10-28) has AGENTS.md (a Turborepo-managed block) and [CLAUDE.md](https://github.com/Telegram-Mini-Apps/tma.js/blob/master/CLAUDE.md). CLAUDE.md is contributor guidance: it names https://core.telegram.org/bots/webapps as the source of truth for platform behaviour, and it forbids AI attribution in contributions to that repo. Not guidance for building an app.
- The official reactjs Mini App template ([github.com/Telegram-Mini-Apps/reactjs-template](https://github.com/Telegram-Mini-Apps/reactjs-template), 430 stars, tma.js-based) has no AGENTS.md, CLAUDE.md or llms.txt.
- TelegramMessenger GitHub org: 22 repos returned by `gh repo list` (names include `TGMiniAppsJsSDK`, `telegram-macos`, `Telegram-iOS`, `cocoon`); none is an MCP server, skill or agent-guidance repo - [github.com/TelegramMessenger](https://github.com/TelegramMessenger).

### Inferences
- Agent guidance from Telegram is currently Serverless-specific. If the team builds on Serverless, AGENTS.md from the scaffold is the first file an agent should read. For a classic bot or a Mini App hosted elsewhere, the team has to supply its own guidance (or use the community skills in Key Question 3).
- For grammY and aiogram, the agent needs current API documentation from another source. A docs MCP (Context7, Key Question 2) or a vetted skill fills that gap.

### Gaps
- Not found: official Telegram agent files for Mini Apps (AGENTS.md, CLAUDE.md, llms.txt, skills).
- Not found: a public URL for the scaffolded `docs/tgcloud-sdk.md`; only its name is documented on the official page.
- Not verified: Serverless availability (beta, early access, pricing); the official page is silent on these.
- Not read: [core.telegram.org/bots/webapps](https://core.telegram.org/bots/webapps) beyond its first 100,000 characters (page is 114,125 characters).

## Key Question 2: Anthropic official skills and plugin marketplaces

### Takeaway
Anthropic's official repos give generic skills that fit this stack: `webapp-testing` (Playwright tests for web apps, which covers Mini App UIs in a browser), `mcp-builder` (to build an MCP server around the bot's database), `frontend-design`, and `skill-creator`. The official plugin directory has a Telegram channel plugin and a Microsoft Playwright plugin. There is no Anthropic-owned Telegram, grammY, aiogram or tma.js skill.

### Cited Findings
- [anthropics/skills](https://github.com/anthropics/skills): 185,667 stars, pushed 2026-10-28, no top-level license (GitHub reports none). README: skills are "provided for demonstration and educational purposes only"; many skills are Apache 2.0, and each folder has its own LICENSE.txt. Skill folders include `webapp-testing`, `mcp-builder`, `frontend-design`, `skill-creator`, `claude-api`, `web-artifacts-builder`, plus document skills (docx, pdf, pptx, xlsx) that the README calls source-available.
- `webapp-testing`: "Toolkit for interacting with and testing local web applications using Playwright." Instructs the agent to write native Python Playwright scripts; `scripts/with_server.py` manages server lifecycle - [skills/webapp-testing](https://github.com/anthropics/skills/tree/HEAD/skills/webapp-testing) (SKILL.md frontmatter, license per LICENSE.txt).
- `mcp-builder`: guide for MCP servers in Python (FastMCP) or TypeScript (MCP SDK) - [skills/mcp-builder](https://github.com/anthropics/skills/tree/HEAD/skills/mcp-builder).
- `frontend-design`: "Guidance for distinctive, intentional visual design when building new UI" - [skills/frontend-design](https://github.com/anthropics/skills/tree/HEAD/skills/frontend-design).
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official): 45,494 stars, Apache-2.0, pushed 2026-10-31. `/external_plugins` holds "Third-party plugins from partners and the community"; external plugins "must meet quality and security standards for approval" - [README](https://github.com/anthropics/claude-plugins-official/blob/HEAD/README.md).
- Official plugins relevant to the stack (plugin.json descriptions read): [security-guidance](https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins/security-guidance) ("Security review for Claude-generated code", pattern warnings, LLM review of diffs, checks for injection, XSS, SSRF, hardcoded secrets); [claude-md-management](https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins/claude-md-management) (audit and keep CLAUDE.md files current); [mcp-server-dev](https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins/mcp-server-dev) (skills for designing and building MCP servers); also present: skill-creator, frontend-design, feature-dev, code-review.
- External plugin `telegram`: [external_plugins/telegram](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/telegram), version 0.0.7, Apache-2.0 LICENSE. It is a Telegram bot exposed as an MCP channel into a Claude Code session: tools `reply`, `react`, `edit_message`. Runs on Bun; package `claude-channel-telegram` depends on `grammy` ^1.21.0 and `@modelcontextprotocol/sdk`; the only URL found in `server.ts` is `api.telegram.org/file/bot` (grep of the file). Default DM policy is `pairing` (6-character code, approved with `/telegram:access pair <code>`); alternatives are `allowlist` and `disabled`; users are identified by numeric ID; token is stored in `~/.claude/channels/telegram/.env`. Author is not stated in plugin.json - [ACCESS.md](https://github.com/anthropics/claude-plugins-official/blob/HEAD/external_plugins/telegram/ACCESS.md) and README in the same folder.
- External plugin `playwright`: "Browser automation and end-to-end testing MCP server by Microsoft" (author Microsoft in plugin.json) - [external_plugins/playwright](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/playwright).
- External plugin `context7`: connects Claude Code to Context7's hosted remote MCP server `https://mcp.context7.com/mcp`, which fetches current docs and code examples from source repositories - [external_plugins/context7](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/context7). Upstream repo [upstash/context7](https://github.com/upstash/context7): MIT, 64,004 stars, pushed 2026-10-30.

### Inferences
- For grammY and aiogram, the most useful Anthropic-side pieces are generic: Playwright tests (webapp-testing or the Microsoft Playwright plugin) for Mini App UI, mcp-builder for a database or finance tool server, security-guidance for secret and injection review. Context7 covers the missing current API docs for grammY and aiogram.
- The official Telegram channel plugin is a messaging bridge (chat -> Claude session). It is not a builder aid. If the product needs "message the bot to run the agent", it is a candidate; otherwise it adds an injection surface.
- Context7 sends the agent's documentation queries to a third-party hosted server. Keep it out of any project that must not leak code context.

### Gaps
- No Anthropic-owned skill covers Telegram, grammY, aiogram or tma.js.
- Only plugin.json descriptions were read for security-guidance, claude-md-management and mcp-server-dev; their internals were not reviewed.
- The author of external_plugins/telegram is not stated.

## Key Question 3: Community skills (vetted, with trust levels)

### Trust scale used in this file
- A: official vendor, Anthropic or Microsoft owned, checked at source.
- B: established open source (about 100+ stars, or a large org), license file present, pushed in 2026. Headline content reviewed only.
- C: small or new (under about 50 stars, or created in 2026), license missing or unclear, or only part of the content read. Read the full file before use.
- D: do not use for this stack: off-stack, or no license plus a risky capability, or a high-risk capability (see Key Question 4).

### Search coverage
- `gh search repos` for: "telegram bot skill claude", "grammy skill", "aiogram skill", "telegram mini app skill", "claude code telegram", "telegram bot agent skill", "telegram mcp server", "telegram mcp", "telegram bot api mcp", "sqlite mcp server", "postgres mcp server". "awesome claude skills telegram" returned nothing. Query "telegram bot skill claude" returned nothing; the variant with "claude code" returned mostly remote-control bots (see below).
- `gh search code` for `name: telegram`, `name: grammy`, `name: aiogram`, `name: telegram-mini-app` in SKILL.md files. The `name: telegram-mini-app` search returned nothing; the `name: telegram` search found the repos below.

### Cited Findings (community)

1. ballisarium/aiogram-skills - Trust C (best-supported aiogram option)
   - Repo: [github.com/ballisarium/aiogram-skills](https://github.com/ballisarium/aiogram-skills). MIT (LICENSE file present). 2 stars, created 2026-07-11, pushed 2026-10-27.
   - 16 skills in `skills/<name>/SKILL.md`, for example [aiogram-testing](https://github.com/ballisarium/aiogram-skills/tree/HEAD/skills/aiogram-testing), aiogram-fsm, aiogram-routing, aiogram-callback-data (64-byte limit), aiogram-rate-limits, aiogram-webhooks, aiogram-streaming (Bot API 10.x drafts).
   - The README says the skills were verified against aiogram 3.31.0 and Bot API 10.3 on 2026-09-07. I checked one claim: the aiogram repo package folder has no `test_utils` directory, and the test mock sits in `tests/mocked_bot.py` - consistent with the skill's statement.
   - Red flags: none in the README (install is symlinks, no scripts). The README also describes eight "lookup tools" that inspect the installed aiogram package, which ship in the Codex plugin form; I did not read that tool code.

2. Nitish-bot/grammy-skill - Trust C (testing reference)
   - Repo: [github.com/Nitish-bot/grammy-skill](https://github.com/Nitish-bot/grammy-skill). Frontmatter says MIT, but the repo root has no LICENSE file and GitHub reports no license. Created 2026-06-14, pushed the same day, 0 stars.
   - Files: SKILL.md, `references/testing.md`, `references/deployment.md`, `references/plugins.md`, `assets/bot-template/`. Covers grammY structure, sessions, conversations, keyboards, inline queries, testing and deployment.
   - Red flags: none in SKILL.md (no curl, npx or eval lines).

3. DeltaUniverse/grammy-skills - Trust C, installer caveat
   - Repo: [github.com/DeltaUniverse/grammy-skills](https://github.com/DeltaUniverse/grammy-skills). Badge says MIT; no LICENSE file in the repo listing and GitHub reports no license. Created 2026-08-26, pushed 2026-09-21, 0 stars.
   - Claims grammY v1.46.0 and v2.0 beta, Bot API 10.0-10.3, runtimes Node, Deno, Bun and Cloudflare. Skill at `grammy/SKILL.md` plus `grammy/references`.
   - Red flags: ships `install.sh`, `install.mjs`, `update.sh` and `update.mjs`, which write skills into several agents' global folders (for example `~/.claude/skills/grammy`) and `update.mjs` queries `registry.npmjs.org/grammy/latest` and `jsr.io` for version checks. My grep found no `curl | sh` lines, but the scripts self-update and write outside the project. Copy SKILL.md by hand instead of running the installer.

4. PBnicad/telegram-bot-grammy-skill - Trust C (Cloudflare-only)
   - Repo: [github.com/PBnicad/telegram-bot-grammy-skill](https://github.com/PBnicad/telegram-bot-grammy-skill). No license file. 3 stars, created 2026-01-27, pushed 2026-02-11.
   - Stack: grammY on Cloudflare Workers with D1 (SQLite), Drizzle ORM, Vitest, Biome, GitHub Actions. Use only if the target is Cloudflare Workers.
   - Red flags: setWebhook `curl` examples use `<DEV_TOKEN>` and `<PROD_TOKEN>` placeholders; no real values.

5. timequity/vibe-coder, skills/telegram-bot - Trust C (secrets hygiene)
   - Path: [skills/telegram-bot](https://github.com/timequity/vibe-coder/tree/HEAD/skills/telegram-bot). Repo MIT (GitHub API). 0 stars, created 2025-12-10, pushed 2026-01-03. A duplicate sits at timequity/plugins `vibe-coder/skills/telegram-bot`.
   - Covers aiogram, grammY, teloxide and telegraf. Its first step is mandatory secret protection: `.gitignore` for `.env`, `bot_token.txt` and keys, plus pre-commit hooks `detect-private-key` and `gitleaks`. Good baseline for the agent team; framework sections not reviewed in depth.

6. davila7/claude-code-templates - container Trust B, skills Trust C
   - Repo: [github.com/davila7/claude-code-templates](https://github.com/davila7/claude-code-templates): MIT, 33,013 stars, pushed 2026-10-31.
   - [telegram-bot-builder/SKILL.md](https://github.com/davila7/claude-code-templates/tree/HEAD/cli-tool/components/skills/enterprise-communication/telegram-bot-builder): generic bot architecture, monetization and scaling; names grammY, aiogram, Telegraf and python-telegram-bot as options. Not framework-specific.
   - [telegram-mini-app/SKILL.md](https://github.com/davila7/claude-code-templates/tree/HEAD/cli-tool/components/skills/enterprise-communication/telegram-mini-app): TON Connect and React examples, loads `telegram-web-app.js`. Not tma.js-specific.
   - Both files say `source: vibeship-spawner-skills (Apache 2.0)`. The source repo [vibeforge1111/vibeship-spawner-skills](https://github.com/vibeforge1111/vibeship-spawner-skills) (884 stars, pushed 2026-01-02) has no LICENSE file in its root listing and GitHub reports no license, so the Apache claim is not confirmed.
   - Red flags: none in grep; only placeholder URLs (`your-app.com`).

7. Rithprohos/telegram-mini-app-skills - Trust C (Mini App, framework-agnostic)
   - Repo: [github.com/Rithprohos/telegram-mini-app-skills](https://github.com/Rithprohos/telegram-mini-app-skills). 14 stars, created 2026-02-20, pushed 2026-02-21. Files: README.md, SKILL.md only.
   - SKILL.md is about 1,100+ lines in 18 sections per the README, including section 10 (HMAC-SHA256 initData validation and Ed25519 signatures) and section 17 "Testing & Debugging" (line 1025 of SKILL.md). Loads the official `https://telegram.org/js/telegram-web-app.js`.
   - The README shows an MIT badge, but there is no LICENSE file in the repo.
   - Red flags: none in grep. Check its values against core.telegram.org/bots/webapps before trusting them.

8. boozybatsMain/DevinationBot, `.claude/skills/telegram-bot/SKILL.md` - Trust C, not reviewed
   - [Repo](https://github.com/boozybatsMain/DevinationBot): 0 stars, no license, pushed 2026-02-05. Skill titled "Telegram Bot with grammY", aimed at serverless platforms. Only the first lines were read.

9. Mini App skills seen only as aggregator listings - Trust unverified
   - `telegram-mini-apps-react` (claims tma.js sdk-react, mock environment) on skills.cat, repo cited as `nailorsh/agents-utils`; `gh api` returned 404 for `nailorsh/agents-utils`.
   - `telegram-mini-apps-sdk` on Smithery, repo cited as `Kaiukov/telegram-mini-apps-sdk`; `gh api` returned 404.
   - An aggregator claims about 28.1k stars for davila7's telegram-mini-app skill; not verified (GitHub shows 33,013 stars for the whole templates repo, not per skill).
   - Sources of the listings: [skills.cat listing](https://skills.cat/skills/nailorsh/agents-utils/telegram-mini-apps-react), [Smithery listing](https://smithery.ai/skills/Kaiukov/telegram-mini-apps-sdk).

10. Off-target or unsuitable - Trust D
   - AndVl1/claude-plugin, `skills/ktgbotapi-patterns`: Kotlin library (ktgbotapi), not grammY or aiogram. Not reviewed further.
   - 10110I/hermes-operator-miniapp-skill: operator status dashboard for a Hermes agent, not a Mini App builder skill.
   - overwirehq/claude-code-telegram - see Key Question 4 and the Trust D note there. 2,817 stars, pushed 2026-10-01, no license. A Telegram bot that gives remote access to Claude Code sessions: a bridge, not a builder skill. Many similar repos exist (for example a5c-ai/claude-code-telegram-bot, 16 stars); none was reviewed.

11. Reference architecture, not a skill - nerdimite/personal-finance-tracker - Trust C (ideas only; do not copy code)
   - Repo: [github.com/nerdimite/personal-finance-tracker](https://github.com/nerdimite/personal-finance-tracker). "Chat-first personal finance tracker: Telegram bot + Claude Code agent + double-entry Postgres ledger + local dashboard." No license (GitHub reports none). 0 stars, created 2026-10-12, pushed 2026-10-12. No AGENTS.md or CLAUDE.md at the repo root; `workspace/CLAUDE.md` exists (not read).
   - Stack from the README: python-telegram-bot, Postgres in Docker Compose, headless `claude -p` agent, a finance MCP server with `sql` and `propose_migration` tools, read-only Next.js dashboard.
   - Guardrails from the README (worth copying as design ideas): the agent has no shell; it may edit only MEMORY.md and CATEGORIES.md; the DB role changes rows but not schema; schema changes go through a separate migrator role after approval; the dashboard uses a read-only role; text inside uploaded files is data, not instructions.
   - Ledger rule: postings must sum to zero and "the database enforces that" (README).

12. Official grammY and aiogram community lists
   - [grammyjs/awesome-grammY](https://github.com/grammyjs/awesome-grammY): 283 stars, pushed 2026-10-29. Lists `PavelPolyakov/grammy-with-tests` as a tested example (see Key Question 5). Trust B.

### Shortlist for the agent team (all categories)

| Item | Use it for | Source | Trust | Caveat |
|---|---|---|---|---|
| Serverless AGENTS.md scaffold (`npm create @tgcloud/bot`) | Starting point for an agent on Telegram Serverless | [core.telegram.org/bots/serverless#building-with-ai](https://core.telegram.org/bots/serverless#building-with-ai) | A | Availability and pricing not stated officially |
| `@grammyjs/tgcloud` (`npm create @grammyjs/tgcloud`) | grammY on Serverless with typed `sdk` | [github.com/grammyjs/tgcloud](https://github.com/grammyjs/tgcloud) | A | 9 stars, created 2026-10-11 |
| grammY transformers and deployment testing | Mocking Bot API calls in tests | [grammy.dev/advanced/transformers.html](https://grammy.dev/advanced/transformers.html), [grammy.dev/advanced/deployment.html#testing](https://grammy.dev/advanced/deployment.html#testing) | A | Docs only; no test framework |
| Telegram test environment | End-to-end tests against the test DC | [core.telegram.org/bots/features.md#testing-your-bot](https://core.telegram.org/bots/features.md#testing-your-bot) | A | Needs a manually created test account |
| tma.js `mockTelegramEnv` | Running a Mini App outside Telegram | [packages/bridge/src/mockTelegramEnv.ts](https://github.com/Telegram-Mini-Apps/tma.js/blob/master/packages/bridge/src/mockTelegramEnv.ts) | A | File located; body not read |
| aiogram `tests/mocked_bot.py` | Reference mock for aiogram tests | [github.com/aiogram/aiogram](https://github.com/aiogram/aiogram/blob/dev-3.x/tests/mocked_bot.py) | A | In the repo's tests folder, not shipped in the package |
| aiogram AGENTS.md and CLAUDE.md | Only for people contributing to aiogram | [AGENTS.md](https://github.com/aiogram/aiogram/blob/dev-3.x/AGENTS.md) | A | Not guidance for building a bot |
| ballisarium/aiogram-skills | aiogram skills, incl. aiogram-testing | [repo](https://github.com/ballisarium/aiogram-skills) | C | Best-supported aiogram option; 2 stars |
| Nitish-bot/grammy-skill | grammY skill with testing reference | [repo](https://github.com/Nitish-bot/grammy-skill) | C | License not in repo |
| timequity telegram-bot skill | Secret hygiene plus aiogram/grammY basics | [path](https://github.com/timequity/vibe-coder/tree/HEAD/skills/telegram-bot) | C | Framework sections not reviewed in depth |
| Rithprohos telegram-mini-app-skills | Framework-agnostic Mini App guide, initData validation | [repo](https://github.com/Rithprohos/telegram-mini-app-skills) | C | No LICENSE file; verify values against official docs |
| davila7 telegram-bot-builder and telegram-mini-app | Generic bot and Mini App skills | [path](https://github.com/davila7/claude-code-templates/tree/HEAD/cli-tool/components/skills/enterprise-communication) | C | Source license claim unconfirmed; TON-heavy |
| PBnicad telegram-bot-grammy-skill | grammY on Cloudflare Workers with D1 | [repo](https://github.com/PBnicad/telegram-bot-grammy-skill) | C | Cloudflare-only; no license |
| DeltaUniverse/grammy-skills | grammY skill (v2 beta aware) | [repo](https://github.com/DeltaUniverse/grammy-skills) | C | Installer and self-updating scripts; read before running |
| nerdimite/personal-finance-tracker | Finance-bot architecture ideas | [repo](https://github.com/nerdimite/personal-finance-tracker) | C | No license; Python; reference only |
| Microsoft Playwright plugin and playwright-mcp | Browser tests for Mini App UI | [external_plugins/playwright](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/playwright), [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | A | Browser-side only; Mini App needs a mocked env |
| anthropics/skills webapp-testing | Playwright scripts for local web apps | [path](https://github.com/anthropics/skills/tree/HEAD/skills/webapp-testing) | A | Demo-grade per repo README |
| anthropics/skills mcp-builder | Building the team's own MCP server | [path](https://github.com/anthropics/skills/tree/HEAD/skills/mcp-builder) | A | Generic guide |
| security-guidance plugin | Secret and injection review of agent-written code | [path](https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins/security-guidance) | A | Plugin internals not reviewed |
| Context7 plugin | Current grammY, aiogram and tma.js docs | [external_plugins/context7](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/context7), [upstash/context7](https://github.com/upstash/context7) | B | Queries go to a third-party hosted server |
| Telegram channel plugin | Chat-to-Claude bridge | [external_plugins/telegram](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/telegram) | B | Prompt-injection surface; author not stated |
| overwirehq/claude-code-telegram | Remote control of Claude Code via Telegram | [repo](https://github.com/overwirehq/claude-code-telegram) | D | No license; agent with tools reachable from chat |
| ktgbotapi skill (AndVl1) | Kotlin library patterns | [repo](https://github.com/AndVl1/claude-plugin) | D | Off-stack |

### Inferences
- The strongest single pick for aiogram is ballisarium/aiogram-skills. For grammY, the official docs plus Context7 are the strongest option: the grammY community skills I reviewed have at most 3 stars (PBnicad).
- For the Mini App, no vetted skill is tied to tma.js; the team should pair official tma.js docs and mockTelegramEnv with a generic skill and Playwright tests.

### Gaps
- No community skill was installed or run; behaviour is judged from SKILL.md text and repo metadata only.
- Only a sample of GitHub search results was read (about 30 repos). Coverage is not exhaustive.
- Not found: a community grammY skill with real activity (more than 3 stars).

## Key Question 4: MCP servers for development and testing

### Takeaway
No official Telegram MCP server exists. Bot API MCPs (bot token) and user-account MTProto MCPs (full access to a person's account) are plentiful; the user-account ones are a high-risk choice. Official SQLite and Postgres MCP reference servers are archived, so community servers are the options. For Mini App browser tests, Microsoft's Playwright MCP is the most trusted choice.

### Cited Findings
- Official Telegram MCP: not found. The TelegramMessenger org has 22 repos (per `gh repo list`) and none is an MCP server ([github.com/TelegramMessenger](https://github.com/TelegramMessenger)).
- Bot API MCPs (act as the bot; hold the bot token):
  - [timoncool/telegram-api-mcp](https://github.com/timoncool/telegram-api-mcp): MIT, 34 stars, pushed 2026-10-31. README claims 185 Bot API methods, "Bot API 10.2", token masking, rate limiting. Trust C. Its version claim (10.2) is older than the 10.3 cited by ballisarium and DeltaUniverse; check before relying on it.
  - [FantomaSkaRus1/telegram-bot-mcp](https://github.com/FantomaSkaRus1/telegram-bot-mcp): MIT, 7 stars, pushed 2026-03-07, "174 tools" per description. Trust C (no update since March).
  - [shekelstrong/telegram-bot-api-mcp](https://github.com/shekelstrong/telegram-bot-api-mcp): no license, 0 stars, pushed 2026-06-16, 18 tools per description. Trust D.
- User-account MTProto MCPs (log in as a person; read chats, send messages, manage contacts). Risk: full access to that account. Do not connect Misha's personal account. Use only with a dedicated test account.
  - [chigwell/telegram-mcp](https://github.com/chigwell/telegram-mcp): Apache-2.0, 1,940 stars, pushed 2026-10-31, Telethon-based.
  - [mcp-telegram/mcp-telegram](https://github.com/mcp-telegram/mcp-telegram): MIT, 64 stars, pushed 2026-10-26, "182 tools over MTProto". README also offers a hosted version; how it stores the Telegram session was not checked, so do not use it with a personal account.
  - [chaindead/telegram-mcp](https://github.com/chaindead/telegram-mcp): MIT, 350 stars, pushed 2026-05-28.
  - Trust C for the code, D for a personal account.
- Telegram-to-Claude bridges: the official [telegram plugin](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/telegram) (Trust B) and overwirehq/claude-code-telegram (Trust D; see Key Question 3, item 10).
- Serverless needs no MCP for local iteration: the official page describes `npx tgcloud run` as the way to test a change, and `tgcloud` CLI commands cover `push`, `migrate`, `status`, `diff`, `fetch`, `pull` ([serverless.md](https://core.telegram.org/bots/serverless.md), "command-line interface").
- SQLite:
  - Official SQLite reference server is archived: listed under "Archived" in [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) with link [servers-archived/src/sqlite](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite).
  - [StacklokLabs/sqlite-mcp](https://github.com/StacklokLabs/sqlite-mcp): Apache-2.0, 16 stars, pushed 2026-10-30, Go-based (README cites testify and golangci-lint). Tools `execute_query`, `execute_statement` (read-write mode only), `list_tables`, `describe_table`; optional read-only mode. Trust C.
- Postgres:
  - Official PostgreSQL reference server is archived: "Read-only database access with schema inspection", same archive list in [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers).
  - [crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp) ("Postgres MCP Pro"): MIT, 3,446 stars, pushed 2026-08-17. "Configurable read/write access and performance analysis." Trust B. Keep agents on read-only access to live data.
  - [devopam/MCPg](https://github.com/devopam/MCPg): MIT, 14 stars, pushed 2026-10-28. Not reviewed. Trust C.
- Mini App browser tests: [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp): Apache-2.0, 38,886 stars, pushed 2026-10-31. Marketplace wrapper [external_plugins/playwright](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/playwright) names Microsoft as author. Trust A.
- Building your own MCP server (for example over the bot's database): [anthropics/skills mcp-builder](https://github.com/anthropics/skills/tree/HEAD/skills/mcp-builder) and [claude-plugins-official mcp-server-dev](https://github.com/anthropics/claude-plugins-official/tree/HEAD/plugins/mcp-server-dev). Trust A.

### Inferences
- For any agent that touches live data, start with read-only DB access. Both viable community SQLite and Postgres servers offer a read-only mode or role.
- On Serverless the database is built into the platform and reached through the CLI and `schema.js`; a database MCP is only needed for classic hosting.

### Gaps
- None of the MCP servers were installed or run; permissions, outbound calls and tool behaviour are unverified beyond READMEs and descriptions.
- Star counts and dates are from GitHub API on 2026-10-31.

### Finance-bot note (data layer)
- If the bot needs database-enforced integrity (foreign keys, zero-sum ledger rules), check that first against Telegram Serverless: its SQLite runs with foreign keys off, and the official page does not mention CHECK constraints or triggers (inference from the page text).
- A double-entry ledger like nerdimite's keeps the zero-sum rule in Postgres. On Serverless the same rule would have to live in application code plus tests (inference).

## Key Question 5: Testing approaches an agent can run automatically

### Takeaway
Mock the outgoing Bot API calls: grammY transformers and aiogram's dispatcher (feed an Update in, record calls out) run offline and automatically. The Telegram test environment is real but needs a human to create a test account, so it cannot be fully automated. For Mini Apps, tma.js `mockTelegramEnv` runs the app outside Telegram, and Playwright covers browser-level tests.

### Cited Findings
- Telegram test environment: separate from the main environment; Test Bot API URL `https://api.telegram.org/bot<token>/test/METHOD_NAME`; a separate test account is needed, enabled through hidden client settings (iOS: tap Settings 10 times; Telegram Desktop: hold Shift and Alt while right-clicking "Add Account"; macOS: tap Settings 10 times, then hold Cmd while clicking "Add Account") - [core.telegram.org/bots/features.md#testing-your-bot](https://core.telegram.org/bots/features.md#testing-your-bot).
- grammY API transformers: `bot.api.config.use((prev, method, payload, signal) => ...)` intercepts every outgoing Bot API call; the docs list "mock API requests during testing" as a use case, with a minimal example that returns `{ ok: true }` - [grammy.dev/advanced/transformers.html](https://grammy.dev/advanced/transformers.html).
- grammY deployment checklist, Testing section: "Write tests for your bot." "Mock outgoing API requests using transformer functions." Feed sample updates through `bot.handleUpdate`; the section notes that dedicated bot testing frameworks are rare and links an example - [grammy.dev/advanced/deployment.html#testing](https://grammy.dev/advanced/deployment.html#testing).
- grammY's own test suite: `test/` folder with `bot.test.ts`, `composer.test.ts`, `context.test.ts`, `filter.test.ts` and type tests - [github.com/grammyjs/grammY/tree/HEAD/test](https://github.com/grammyjs/grammY/tree/HEAD/test). Library tests, not an app test kit.
- Community grammY testing pattern: [Nitish-bot/grammy-skill references/testing.md](https://github.com/Nitish-bot/grammy-skill/blob/HEAD/references/testing.md) says grammY has no official test framework; it recommends constructing `new Bot("TEST_TOKEN", { botInfo })` to skip the `getMe` call, or mocking `getMe` in a transformer before `init()`; examples use Vitest. Trust C.
- Example bot with tests: [PavelPolyakov/grammy-with-tests](https://github.com/PavelPolyakov/grammy-with-tests): 29 stars, no license, pushed 2025-05-16. Files: `__tests__/bot.test.ts`, `bot.ts`, `start.ts`. A third-party summary (DeepWiki, via WebSearch) says it intercepts outgoing calls with a transformer; I did not verify this in the code.
- aiogram: test at the dispatcher boundary. The repo has [tests/mocked_bot.py](https://github.com/aiogram/aiogram/blob/dev-3.x/tests/mocked_bot.py) (2,999 bytes) - maintainer-side mock. The package folder has no `test_utils` - [aiogram/ package folder](https://github.com/aiogram/aiogram/tree/dev-3.x/aiogram).
- aiogram-testing skill ([ballisarium/aiogram-skills](https://github.com/ballisarium/aiogram-skills/tree/HEAD/skills/aiogram-testing)): uses `feed_update` and a fake `BaseSession` with three abstract methods (`make_request`, `stream_content`, `close`); states that `aiogram.test_utils` is not in the released wheel. Trust C; snippets not run.
- aiogram-test-framework on PyPI: latest 1.0.4, uploaded 2026-07-18, MIT, "A testing framework for Aiogram 3.x Telegram bots", requires Python 3.10+. Provides `MockBot`, `RequestCapture`, `TestClient`, `AsyncBotTestMixin` for pytest. Author field empty; source repo [sgavka/aiogram-test-framework](https://github.com/sgavka/aiogram-test-framework) - [PyPI JSON](https://pypi.org/pypi/aiogram-test-framework/json). Trust C; code not reviewed.
- Serverless: `npx tgcloud run` gives a fast local loop per the official page; the page describes no separate test framework - [serverless.md](https://core.telegram.org/bots/serverless.md).
- Mini Apps outside Telegram: tma.js [mockTelegramEnv.ts](https://github.com/Telegram-Mini-Apps/tma.js/blob/master/packages/bridge/src/mockTelegramEnv.ts) in the bridge package (file located, body not read). Browser-level tests: [Playwright plugin](https://github.com/anthropics/claude-plugins-official/tree/HEAD/external_plugins/playwright) and [anthropics/skills webapp-testing](https://github.com/anthropics/skills/tree/HEAD/skills/webapp-testing).
- Mini App test environment: HTTP without TLS is allowed for Mini Apps and Web Login in the Telegram test environment - [features.md#testing-your-bot](https://core.telegram.org/bots/features.md#testing-your-bot).

### Inferences
- Fully automatic tests: grammY transformer or aiogram feed-update tests, with recorded outgoing calls asserted in CI. No Telegram account needed.
- End-to-end checks against Telegram: a human sets up the test account once; after that, tokens from the test environment can run scripted checks against the `/test/` endpoint. Whether an agent may do the manual account step is a decision for Misha, not something to automate.
- Serverless adds its own loop (`run`); whether it has an offline test mode is not documented on the official page.

### Gaps
- Not verified: whether the Telegram test environment can be fully scripted after setup (for example, token creation and rate limits).
- Not found: a published grammY test-utilities package from the grammyjs org (its repo list has no test-utils repo).
- Not reviewed: aiogram-test-framework code and the internals of the grammY test helpers in community repos.

