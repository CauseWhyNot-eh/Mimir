# Mimir dev workflow (standing rule)

Two homes, one direction of travel.

1. **Test in Hermes.** All experiments and edits happen in the live Hermes
   skill first (`skills/research/mimir`).
2. **Mirror on approval only.** When Nachi tests a change and likes it, copy
   the changed files into this repo. Nothing lands here unapproved.
   Repo-only deltas (live here, never mirrored back to Hermes): Firecrawl
   framed as a tagged optional module (`references/firecrawl-surgical.md`).
3. **Re-sync profiles.** The Hermes install keeps one copy per profile. After
   mirroring, refresh every profile copy from the default skill so all
   sessions run the same version:
   ```bash
   SRC="$LOCALAPPDATA/hermes/skills/research/mimir"
   for d in "$LOCALAPPDATA/hermes/profiles/"*/; do
     dest="${d}skills/research/mimir"
     rm -rf "$dest"; mkdir -p "$dest"; cp -r "$SRC/." "$dest/"
   done
   ```
4. **Bump the version** in `SKILL.md` frontmatter on any behavior change.

Ledger and claim files (`mimir-ledger.json`, `mimir-claims.json`) are
runtime state, never committed — see `.gitignore`.
