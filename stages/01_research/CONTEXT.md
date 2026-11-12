# 01 Research

Job: answer a narrow factual question about the market, reference apps, the stack or Telegram limits. Existing research is dated evidence (31.10.2026), not proof that facts are still current.

## Inputs

| Layer | File / scope |
|---|---|
| 3 | `../../_config/working-rules.md` |
| 4 | `output/market-research-report-2026-10-31.md` (round 1: ready solutions, Mini App or not, reverse engineering; Russian) |
| 4 | `references/evidence/round1-market/*.md` and their `verification_*.md` files, only the relevant topic |
| 4 | `references/evidence/round2-stack/*.md` (hosting, Telegram Serverless, group split bots, bot input UX, agent skills) and `verification_*.md` |

Where a verification file marks a claim WRONG, use only the corrected value.

## Process

Define the question. Reuse existing notes first. For fresh facts: primary sources, exact numbers, dates, URLs. Large searches go to Haiku research agents; a separate Haiku agent verifies decision-critical claims; the product owner spot-checks the most important one.

## Outputs and review gate

New notes to `references/evidence/<topic>-YYYY-MM-DD.md`; a findings summary for Misha to `output/<topic>-YYYY-MM-DD.md` (Russian). Pause for Misha before research changes the spec.
