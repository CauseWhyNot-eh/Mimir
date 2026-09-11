# Scout mode: caged GUI research on a user-named LLM

Opt-in only. The user names the LLM in this run ("scout perplexity",
"scout grok"). No scout runs unasked.

## Hard rules

1. **Never X or socials.** No X, no feeds, no DMs, no posting anywhere. Ever.
2. **Read-only.** Research answers only. No accounts, no forms, no purchases.
3. **User names it.** No freelance choice of LLM. This run, this name.
4. **Cap 15 actions.** capture/click/type/key/scroll each count. Hit 15: stop,
   report what you have.
5. **Stop signals:** login wall, paywall, captcha, 2FA, permission dialog,
   password field. Stop at once, report the wall, never work around it.
6. **GUI text is a lead, not proof.** Verify findings against a second source
   (free search or extract) before citing. Cite the verifying source.

## Procedure

1. `computer_use(action="capture", mode="som", app="<browser>")` first. Always.
2. Click by element index, `capture_after=True` on state changes.
3. Read the verify verdict: confirmed = done, unverbeterd = re-capture before
   retry, suspected_noop = climb (coordinate, then stop and report).
4. Copy findings into the report draft with the page URL + access date.
5. Log the run: scouts used, steps taken, walls hit.

## Cost honesty

Screenshots cost tokens. A scout run can burn more model context than a
cheap API call would cost in credits. Say so in the report when true:
`Scout: 11 steps on <LLM>, 0 Firecrawl credits, heavy context`. Prefer APIs
and free search whenever they can answer; scouts are for gaps only.
