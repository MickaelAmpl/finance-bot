# SDD ledger, phase 1.4 (AI input), 12.11.2026

Product-owner record of every review and ruling. Rulings are part of the requirements for QA; they are not new findings.

Base: plan commit `308d3db`; decisions `e9ab6a8` (credits and limit). Code commits `bd846bf..01cb65c` (see build log).

## Process notes

- Wave 1 (Tasks 1-4) and wave 2 (5, 6) and wave 3 (7, 9) ran in parallel in one checkout with pathspec commits; wave 4 (8) alone. Machine load reached 40 with many agents; full test runs took up to 3.5 min.
- Four early commits carry `Co-Authored-By: Claude Haiku 5.5` instead of the plan's Opus trailer (086a551 is correct; 7ac74e0, 086f44a, 8b364c8 are not). Not rewritten: other developers were committing in parallel. Later commits use the plan's trailer.
- One full run (by the Task 8 developer) failed `test_ai_bot.py::test_draft_send_flood_control_is_retried` once while the Task 7 developer was editing `ai_handlers.py` in the same checkout. Not reproduced: 5 consecutive runs of `test_ai_bot.py` (41 passed each) and the full gate (1063 passed). Re-checked in QA.
- Credits and limit confirmed by Misha 12.11 15:45-15:46 (decision row): real model calls allowed; the [Q6] live run still needs his yes.

## Rulings

| Task | Ruling |
|---|---|
| 4 | `25 майка` routes to the parser. The plan line said AI; the rule as written (exact words мая/май/мае, stems only for RU/UK month names) is right and the plan line was a product-owner error. |
| 4 | `Memory.add` also drops items older than 2 h before appending (prevents mixing an expired history into a new pair). Accepted. |
| 4 | Taught-words SQL stays in `ai_prompt.py` (categories.py not in the task's files). |
| 3 | `SCHEMA_KEYWORDS` lives in production code (plan); `(text, is_error)` tuple and the `if name ==` chain kept; "no category" wording kept. |
| 2 | A photo draft is refused unless exactly one entry and it is an expense. A non-string note or category counts as absent. `MAX_DRAFT_ENTRIES` comes from `parser.MAX_ENTRIES`. |
| 5 | Date format, pluralisation helpers and copy-pinning tests accepted; only the help-text anchor lookup was fixed. |
| 6 | A failed or timed-out model call still counts toward the daily cap (it may have been billed). Non-API exceptions go to the caller (Task 7's catch-all). |
| 7 | The 5 MB filter applies to image documents only; Telegram photos are not size-checked (they are small). Larger image documents get no reply, like other files (spec A1.6). Callback chat id falls back to `from_user.id`. |
| 7 | Telegram failures after a database change never undo it: memory is marked first, edits ignore "not modified", a failed saved reply is logged (class name) and the rest still go out; a draft whose message cannot be sent is cancelled. |
| 9 | Keywords for the synthetic data are taught with `remember_keyword`; expectations are recomputed from the database; a too-early `today` exits 2. The live run does not store drafts, so the correction text works through memory only. |

## Review history

| Task | Standards review | Spec review | Fix round |
|---|---|---|---|
| 1 | longest-first masking leak (reproduced), stack_info, getaddrinfo not blocked | clean; whitespace secret, stack_info minor | 1254b0a |
| 2 | ISO week date accepted (reproduced); create_draft lookup outside the lock; duplicated 10 | ISO week date | d64c8e2 |
| 3 | missing-key KeyError, month parsed three times, `_day` name | missing-key raises | 91833ec |
| 4 | copied word lists, tautological test, anthropic import before the pin | symbol class not from SYMBOLS, prompt test partial | 95b55c6 |
| 5 | help anchor lookup fragile | clean | 97005c9 |
| 6 | no-leak log tests hollow, cap message duplicated the constant | missing tests (new day, text next to a tool call) | 91ce561 |
| 7 | edits not ignoring "not modified"; unguarded sends; draft send 429; catch-all send; silent download failure | missing tests (sqlite error, memory marks, 429), album order (plan gap) | aa33344 |
| 9 | live-DB guard only by file existence; hollow key test | failures entered memory; Groceries range not exercised | f31970f |
| 8 | stale deploy.sh header comment (to the closing fix) | clean | - |

## Closing whole-branch review

Opus, `308d3db..01cb65c`, 1063 passed; probes in the session scratchpad (`rv/probe*.py`). No blockers.

| Finding | Ruling |
|---|---|
| M1 unknown `/commands` went to the model (breaks A1.2) | fix: slash text never routed to the AI |
| M2 Save on the old draft while a correction is processed: both saved (reproduced) | fix: when a correction replaces nothing, the new draft says `The earlier draft is closed already. Save adds this as a new entry.` |
| M3 a correction replaced the newest open text draft, not necessarily the one corrected; a corrected receipt stayed open beside the new draft (reproduced) | fix: replace only when it is the only live draft (open, under 48 h, any source); otherwise nothing is replaced and the draft says `Another draft is still open above. Cancel the one you do not want.` New copy, product-owner ruling inside A4.6's intent; reported to Misha |
| M4 image files 3.8-5 MB may exceed the API image limit after base64 | not a defect: official vision docs (fetched 12.11): "10 MB (base64-encoded) on the Claude API"; 5 MB raw is about 6.7 MB base64. Images over 8000x8000 px would get the generic AI-unavailable reply (rare, accepted) |
| m1 `ANTHROPIC_LOG` makes the SDK call basicConfig first, so `AI input: on` is not logged | fix: `basicConfig(force=True)` |
| m2 multi-entry draft: each budget line shows the month total after all entries | accepted (more correct; typed input shows running totals) |
| stale `deploy.sh` header comment (Task 8 review) | fix in the same commit |

## QA fix set (Misha 12.11: "Да, правь")

| Finding | Commits | Ruling |
|---|---|---|
| Q-1 routing gap | eeb3b1f, 2aa9174 | Warning words widened: currency stems (грн, гривн, гривен, гривень, бакс, доллар, долар, евро, євро, рубл, фунт, злот, hryvn, zlot), weekday stems, relative days (назад, тому, ago, last, завтра, tomorrow), apostrophes removed before splitting. Short stems that caught everyday words (руб, сред, серед, четвер, euro, pound, dollar, buck, franc, франк) became exact words after a review probe (`25 рубашка`, `40 средство для посуды`, `15 euroshop` stay on the parser). Accepted: `15 рубленое мясо` goes to the AI (stem рубл); cost is one draft. |
| Q-5 live-run script | 2d2fb05 | prints each line as produced, `failed turns: N of 15`, exit 1 when any turn failed |
| Q-2, Q-3 Save/Cancel error paths | d4990e7 | every press answered once; after the commit Telegram and database errors are logged (class name) and the remaining replies and the draft edit still go out; new copy `Could not cancel. Nothing changed. Press Cancel again.` |

Reviewed (two-axis, Sonnet) and re-checked by QA (all four closed, section "Re-check after the fix set" of the QA report). Gate at 2aa9174: ruff clean, 60 files formatted, pyright 0, pytest 1120 passed. Later (Misha decides): Q-4, Q-6..Q-11.
