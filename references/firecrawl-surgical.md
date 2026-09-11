# Firecrawl module (optional add-on)

Everything Firecrawl lives here and in the lines tagged `[Firecrawl module]`
in `SKILL.md`. Keyless users: ignore all of it. The skill loses nothing —
sweeps, rivals, scouts, claims, and cited reports all run at 0 credits.

## Costs (free tier: 1,000/month)

`scrape 1/page`, `crawl 1/page`, `map 1/call`, `search 2/10 results`,
`JSON +4/page`, `Enhanced +4/page`, `PDF +1/pdf-page`, `interact 2/min`.
Papers endpoints (`search_papers`, `related_papers`, `inspect_paper`,
`read_paper`) are free. Agent runs are dynamic — avoid them.

## Hard caps per run

`search<=2`, `map<=1`, `scrape<=70`, total `<=90`. Extract caps per mode:
brief 5, standard 10, deep 15.

## Bans (default)

JSON mode, Enhanced mode, Interact, crawl without explicit `limit`.
JSON/Enhanced cost +4/page each — 20 pages wipes a month. Firecrawl's crawl
default `limit` is 10,000 and returns 402 if your balance can't cover it, so
always pass explicit `limit: 20` or lower.

## Postures (`ledger.py guard`, line one is machine-readable)

- `FREE-ONLY` — no key. Nothing billable will run.
- `PINNED` — native search pinned to a free backend. The free sweep is truly free.
- `CAREFUL` — key present, native backend unpinned. Sweep with `ddgs`+`arxiv`
  and count native calls against the budget.

`precheck --budget N` exits 2 on FALLBACK: over per-run cap, over monthly
remainder, or no key. FALLBACK means deliver a free-only report, never an error.

## Known live findings

- Social URLs (Reddit etc.) fail at the API level with 403 on free tier.
  Deprioritize them in surgical lists; cite via search snippets instead.
- Search-plus-scrape stacks: `search` (2) plus 1 per scraped hit. Estimate both.
- Key present flips some hosts' native search to Firecrawl backends. When in
  doubt, sweep with `ddgs`+`arxiv` and count native calls.
