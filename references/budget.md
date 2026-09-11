# Mimir budget cheat-sheet

Free tier: 1000 credits / month. Goal: 10 runs = ~100 per run. Aim <=90 to leave buffer.

| Call | Cost | Notes |
|---|---|---|
| scrape 1 page | 1 | base, clean markdown |
| crawl 1 page | 1 | MUST pass explicit `limit`, default 10000 = instant 402 |
| map 1 site | 1 | discover URLs only |
| search 10 results | 2 | 11 results = 4, count it |
| search + scrape hits | 2 + 1 per hit | stacks fast, estimate both |
| PDF page | +1 | per PDF page on top |
| JSON extract | +4/page | BANNED by default, 20 pages = 100 gone |
| Enhanced mode | +4/page | BANNED by default |
| interact | 2/min | BANNED by default |
| papers endpoints | free | `search_papers`, `related_papers`, `inspect_paper`, `read_paper` |
| agent | 5 daily free then dynamic | avoid, unpredictable cost |

## Safe example (total ~77)

- search x2 (20 results) = 4
- map x1 = 1
- scrape x70 = 70
- buffer = 15
- total = ~90 max

## Unsafe examples

- crawl without limit -> 402 error, run fails
- scrape 20 pages with JSON mode -> 20 * (1+4) = 100, whole run gone
- scrape 20 pages with Enhanced + JSON -> 20 * 9 = 180, blows two runs

## Rules

1. Always `precheck --budget <estimate>` before touching Firecrawl.
2. FALLBACK means free-only, still deliver a report.
3. Log real spend with `log --used N` after.
4. Never invent credit numbers in the report, read them from the ledger.
