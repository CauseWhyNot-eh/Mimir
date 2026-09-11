---
name: mimir
description: Free-first research beast, Firecrawl only for locked doors.
version: 0.3.0
author: Nachi, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Free, Firecrawl, Citations]
    related_skills: [duckduckgo-search, arxiv, scrapling, grounded-citations]
---

# Mimir Skill

Free-first deep research. Hunts with free tools, sips Firecrawl only for
locked doors. Default cost is 0 credits. Does not do single lookups, coding,
or chat. Needs no keys; `FIRECRAWL_API_KEY` unlocks surgical mode.

Portability rule: depends on nothing that doesn't travel with it. `ddgs`,
`arxiv` API, curl, markdown are universal. Hermes-only tools are never
required. Firecrawl and computer-use are optional extras.

## When to Use

- Deep research, comparisons, competitor + pricing checks
- How-to / docs digging, SaaS idea validation
- Papers, AI news, blog / RSS sweeps
- Disputed topics (`--rivals`), user-named LLM scouts (`--scout`)
- User says `mimir`, `deep research`, `beast mode`

Don't use for:
- Single quick lookup (use `web_search` directly)
- Coding, writing, or casual chat
- Anything needing paid tools beyond Firecrawl free tier

## Prerequisites

- Optional: `FIRECRAWL_API_KEY` in env or Hermes `.env`. Never hardcode it.
- `terminal`, `web_search`, `web_extract` (try free paths first regardless).
- Free stack: `ddgs` CLI, `arxiv` API, curl. Optional: `scrapling`, browser.
- Scripts (stdlib-only, no install): `ledger.py`, `mimir-report.py`, `claims.py`.
- Citations via `grounded-citations` `scripts/sources.py` (resolved relative
  to this skill dir so every profile copy works).
- Style defaults live in `prefs.md`; past fixes in `learnings.md`. Read both
  before changing output habits.

## How to Run

```bash
python scripts/ledger.py guard                 # posture: FREE-ONLY | PINNED | CAREFUL
python scripts/ledger.py precheck --budget 90  # gate before Firecrawl
python scripts/claims.py find "paddle fees"    # reuse known facts first
python scripts/mimir-report.py --report report.md --used 12 --note "scrape x10 + search x1"
```

`mimir-report.py` does render + verify + ledger log + credit line in one
call. `precheck` FALLBACK means free-only, still deliver a report.

## Quick Reference

| Mode | When | Stack |
|---|---|---|
| `--brief` | quick answer + 5 sources | `web_search` + `web_extract` |
| `--deep` | 15+ sources, tables | + `duckduckgo-search`, `scrapling`, browser |
| `--competitor` | pricing, features, news | + `competitor-news-monitor`, `blogwatcher` |
| `--howto` | docs, code, guides | + `scrapling` dynamic, `web_extract` docs |
| `--papers` | arXiv + Semantic Scholar | `arxiv` API, Firecrawl paper endpoints (free) |
| `--rivals` | disputed topic | two angles in parallel, merged, conflicts shown |
| `--scout LLM` | user names an LLM | caged GUI run, never X, read-only, <=15 steps |

Firecrawl costs: `scrape 1/page`, `crawl 1/page`, `map 1/call`,
`search 2/10 results`, `JSON +4/page`, `Enhanced +4/page`,
`PDF +1/pdf-page`, `interact 2/min`. Papers endpoints free.

Hard caps per run: `search<=2`, `map<=1`, `scrape<=70`, total `<=90`.
Banned by default: JSON mode, Enhanced mode, Interact, crawl without explicit `limit`.
Extract caps per mode: brief 5, standard 10, deep 15. Recency: prefer 2025-26 for prices.

## Procedure

1. **Route.** Split the ask into 3-5 mini-jobs, pick a mode, confirm depth
   per `prefs.md`. Check the claim ledger; reuse verified facts as `[known]`.
   Done when: queries written, depth confirmed, known facts listed or no hit.

2. **Sweep free (0 credits).** `ddgs` CLI + `arxiv` first, even if the native
   backend is Firecrawl. Dedupe URLs, extract to the mode cap. On disputed
   topics run two query-angles in parallel and attribute disagreements.
   Unblock via `scrapling` stealth/dynamic or browser before Firecrawl.
   Done when: cap hit or results exhausted, kept-vs-dropped noted.

3. **Gate.** List missing key pages (max 7). `guard` for posture,
   `precheck --budget <estimate>`. FALLBACK means free-only.
   Done when: FREE-ONLY or SURGICAL with estimate <=90 logged.

4. **Strike.** Firecrawl on the gap list only, small batches, explicit
   `limit: 20` on crawls, no fancy options. On 402/429 abort to free-only.
   Scout only if the user named an LLM this run (see `references/scout-mode.md`).
   Done when: gaps fetched or abort logged, spend recorded via `log`.

5. **Prove.** Cite while drafting (`sources.py add` at fetch time, `[n]` per
   sentence, max 3). Top-3 claims need a second source or a confidence tag
   (high/med/low). Gaps flagged as `no source found for X`. New verified
   facts go to `claims.py add`.
   Done when: answer + table + details + Sources block exist.

6. **Close.** `mimir-report.py --report ... --used N`.
   Done when: verify passes, ledger shows the run, credit line present.

## Scout Rules (detail: `references/scout-mode.md`)

- Opt-in only: user names the LLM in this run. Never X or socials, ever.
- Read-only research, <=15 actions, stop on login/paywall/2FA/captcha.
- Verify every finding from visible page text. GUI text is a lead, not proof.

## Pitfalls

- **Key added = native search may now cost.** Hermes prefers Firecrawl when its
  key exists, so `web_search` / `web_extract` can spend credits. `guard` prints
  the posture. Sweep with `ddgs` + `arxiv` for true zero, count native calls.
- **Social URLs often 403 on free tier.** Reddit etc. fail at the API level (proven live). Deprioritize them in surgical lists; cite via search snippets instead.
- **Crawl default limit is 10000.** Omitting `limit` returns 402 even on free tier.
  Always pass explicit `limit: 20` or lower.
- **JSON / Enhanced look harmless, cost +4 each.** 20 pages = 100 credits gone.
  Keep them off unless the user explicitly approves over-budget.
- **Search scraping stacks.** `search` (2) + scrape each hit (1 each) adds fast.
  Count both sides in the estimate.
- **Don't reconstruct citations from memory.** Register URLs at fetch time,
  never retype URLs. Always `render` via `mimir-report.py`.
- **Don't call Firecrawl without `precheck`.** Ledger is the leash.
- **Respect blocks.** Check robots.txt / ToS. Research, not abuse.
- **Separate runtimes.** `ddgs` in `terminal` is not `execute_code` importable.

## Verification

```bash
python scripts/ledger.py guard
python scripts/mimir-report.py --report report.md --used 0 --note "free-only"
python scripts/ledger.py status
```

Green means: posture printed, report cites only ledger ids, Sources block
matches, credit line present, run total <=100. Skipped Firecrawl reports say
`Mode: free-only` + why.

## Learning

Learn rarely. Default is no change; patch only on a listed signal.

- "Like this, not like that" → `prefs.md`.
- "Also do X when doing Y" → core or `learnings.md`.
- "Don't need / skip" → cut it.
- "You missed / wrong" → `learnings.md`.
- "Always / never" → standing rule.

Noise: ignore. One patch max per run. Runs that learn end with: "Noted: <change>. Say 'forget that' to undo."
