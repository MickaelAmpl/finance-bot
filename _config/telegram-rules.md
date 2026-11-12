# Telegram rules

Facts verified 31.10.2026 against core.telegram.org (evidence: `stages/01_research/references/evidence/round2-stack/verification_telegram_skills.md`).

- `callback_data` is 1-64 bytes. Keep callback payloads short (action + numeric ids).
- Always answer a callback query (`callback.answer()`), even on error, or the button spins.
- Rate limits: about 1 message per second per chat, 20 messages per minute in a group. A 429 response carries `retry_after`; wait and retry once.
- A bot cannot start a private chat: it can message a user only after that user pressed /start.
- Groups (phase 2): privacy mode is on by default; the bot receives commands, replies to its messages and service messages only. No API lists group members; members register with `/join`. `getChatMember` is guaranteed for other users only when the bot is an admin.
- `deleteMessage` works only within 48 hours.
- Message text limit is 4096 characters; split longer reports.
- Server trap (seen on job-digest, 07.10.2026): IPv6 from the VPS server to api.telegram.org stalls. The bot session must connect over IPv4 only.
- Two bots: a dev bot for local runs and Misha's acceptance, a prod bot on the server. Never point the dev code at the prod token.
