# Mimir

Free-first deep-research skill for AI coding agents. Does the expensive-looking work with free tools and only spends Firecrawl credits on pages that genuinely need rendering — blocked docs, JS-heavy comparison tables, that kind of thing. Zero keys required: with no credentials it runs fully free-only and still hands you a cited report instead of an error.

Named after Mímir, the Norse keeper of the Well of Wisdom — Odin gave an eye for a single drink from it.

## Architecture

Six-step pipeline, each step with a checkable exit condition:

1. **Route** — decompose the ask into 3–5 sub-queries, pick a mode, confirm output depth. Check the claim ledger first so repeat questions don't pay twice.
2. **Sweep free** — `ddgs` CLI + arXiv API first, regardless of what backend the host wires up. Dedupe, extract to a per-mode cap (brief 5, standard 10, deep 15).
3. **Gate** — list the gap pages (max 7), print the spend posture, run the budget precheck. Anything over budget degrades to free-only, never fails.
4. **Strike** — Firecrawl on the gap list only. Hard caps per run: ≤2 searches, ≤1 map, ≤70 scrapes, ≤90 credits total. JSON/extract and Enhanced modes are banned by default (+4/page each — 20 pages wipes a month). Crawls always carry an explicit `limit` (Firecrawl defaults to 10,000 and 402s you if your balance can't cover it).
5. **Prove** — cite-while-drafting against a URL→id ledger. Top-3 claims need a second source or an explicit confidence tag. Unknowns are flagged, not smoothed over.
6. **Close** — one command renders Sources, verifies citations, logs spend, stamps the credit line.

Two ledgers, both plain JSON in the host cache dir:

- `mimir-ledger.json` — monthly spend vs the 1,000-credit free tier. Global across profiles so parallel sessions can't double-spend the quota. `precheck` exits 2 on FALLBACK, which callers treat as free-only.
- `mimir-claims.json` — verified facts with sources and confidence (`high` = 2+ independent sources). `find` does stemmed keyword match.

## Install

Python 3, stdlib only. Nothing to pip install.

```bash
python install.py                        # Hermes default location
python install.py --target <skills-dir>  # any harness: lands in <dir>/mimir
```

## Configuration (all optional)

```bash
cp .env.example .env
```

| Variable | Effect |
|---|---|
| `FIRECRAWL_API_KEY` | Unlocks surgical mode. Absent = free-only, permanently. Never hardcoded; read from env or host `.env` at runtime. Keyless installs can ignore `references/firecrawl-surgical.md` and every `[Firecrawl module]` line — that combination is the entire paid surface. |
| `MIMIR_LEDGER` / `MIMIR_CLAIMS` | Override ledger paths (tests, multi-tenant setups). |

First thing every run does is print its posture, machine-readable on line one:

```
POSTURE: FREE-ONLY | PINNED | CAREFUL
```

- `FREE-ONLY` — no key. Nothing billable will run.
- `PINNED` — native search pinned to a free backend. The free sweep is truly free.
- `CAREFUL` — key present, native backend unpinned. The sweep uses `ddgs`+arXiv and counts any native calls against the budget.

## Modes

`--brief` quick answer · `--deep` full report · `--competitor` pricing/features ·
`--howto` docs · `--papers` arXiv + Semantic Scholar (Firecrawl paper endpoints are free) ·
`--rivals` two query-angles in parallel, merged with conflicts attributed ·
`--scout <LLM>` caged GUI run on a user-named model: read-only, ≤15 actions, never social media, stops at login/paywall/captcha.

## Portability

Depends on nothing that doesn't travel with the repo: `ddgs`, arXiv, curl, markdown. No host-specific tools required, no network calls at import, Windows/macOS/Linux paths handled. Guard scripts exit 0/2, never throw on missing config.

## Layout

- `SKILL.md` — the procedure (frozen core)
- `prefs.md` — output taste, 10-line cap
- `learnings.md` — dated fixes, pruned
- `scripts/ledger.py` — posture gate + spend ledger
- `scripts/mimir-report.py` — render + verify + log + credit stamp, one call
- `scripts/claims.py` — cross-run fact ledger
- `references/budget.md` — credit cheat-sheet
- `references/scout-mode.md` — caged-scout protocol

## License

MIT — see `LICENSE`.
