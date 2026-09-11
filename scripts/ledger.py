"""Mimir credit ledger - stdlib only, cross-platform.
Tracks Firecrawl free-tier spend: 1000/month, max ~100/run.
Ledger file is GLOBAL (shared across Hermes profiles) so every profile
counts against the same 1000/month.
Usage:
  python ledger.py status
  python ledger.py guard                  # posture + sweep policy, always exit 0
  python ledger.py precheck --budget 90   # exit 2 = FALLBACK, go free-only
  python ledger.py log --used 12 --note "scrape x10 + search x1"
"""
import argparse
import datetime
import json
import os
import pathlib
import sys

MONTHLY_CAP = 1000
RUN_CAP = 100
SAFE_RUN = 90
FREE_BACKENDS = ("ddgs", "brave-free", "searxng")


def cache_dir():
    home = pathlib.Path.home()
    if os.name == "nt":
        base = pathlib.Path(os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local"))) / "hermes" / "cache"
    else:
        base = home / ".hermes" / "cache"
    hh = os.environ.get("HERMES_HOME")
    if hh:
        p = pathlib.Path(hh)
        parts = p.parts
        if "profiles" in parts:
            # Profile session: share one global ledger.
            idx = parts.index("profiles")
            base = pathlib.Path(*parts[:idx]) / "cache"
        else:
            base = p / "cache"
    return base


def ledger_path():
    override = os.environ.get("MIMIR_LEDGER") or os.environ.get("FENRIR_LEDGER") or os.environ.get("HERMES_MIMIR_LEDGER")
    if override:
        return pathlib.Path(override)
    return cache_dir() / "mimir-ledger.json"


def old_ledger_path():
    return cache_dir() / "fenrir-ledger.json"


def current_month():
    return datetime.datetime.now().strftime("%Y-%m")


def load():
    p = ledger_path()
    if not p.exists() and old_ledger_path().exists():
        try:
            old = json.loads(old_ledger_path().read_text(encoding="utf-8"))
            if old.get("month") == current_month():
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(old, indent=2), encoding="utf-8")
        except Exception:
            pass
    if not p.exists():
        return {"month": current_month(), "used_total": 0, "runs": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"month": current_month(), "used_total": 0, "runs": []}
    if data.get("month") != current_month():
        return {"month": current_month(), "used_total": 0, "runs": []}
    data.setdefault("used_total", 0)
    data.setdefault("runs", [])
    return data


def save(data):
    p = ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return p


def _read_dotenv_key(name):
    try:
        candidates = []
        hh = os.environ.get("HERMES_HOME")
        if hh:
            candidates.append(pathlib.Path(hh) / ".env")
            # Profile .env misses shared keys: also check the global root.
            hp = pathlib.Path(hh)
            if "profiles" in hp.parts:
                idx = hp.parts.index("profiles")
                candidates.append(pathlib.Path(*hp.parts[:idx]) / ".env")
        if os.name == "nt":
            candidates.append(pathlib.Path.home() / "AppData" / "Local" / "hermes" / ".env")
        candidates.append(pathlib.Path.home() / ".hermes" / ".env")
        for p in candidates:
            try:
                if not p.exists():
                    continue
                for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    s = line.strip()
                    if not s or s.startswith("#") or "=" not in s:
                        continue
                    k, v = s.split("=", 1)
                    if k.strip() == name and v.strip().strip("'\"").strip():
                        return v.strip().strip("'\"").strip()
            except Exception:
                continue
    except Exception:
        pass
    return ""


def has_key():
    return bool(os.environ.get("FIRECRAWL_API_KEY", "").strip() or _read_dotenv_key("FIRECRAWL_API_KEY"))


def _pinned_backend():
    # Non-secret config only: which backend serves native search/extract, if pinned.
    try:
        cands = []
        hh = os.environ.get("HERMES_HOME")
        if hh:
            cands.append(pathlib.Path(hh) / "config.yaml")
        if os.name == "nt":
            cands.append(pathlib.Path.home() / "AppData" / "Local" / "hermes" / "config.yaml")
        cands.append(pathlib.Path.home() / ".hermes" / "config.yaml")
        for p in cands:
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="ignore")
                for line in text.splitlines():
                    s = line.strip()
                    # Only explicit search/extract pins count; bare `backend:`
                    # lines belong to other subsystems (terminal, models).
                    if s.startswith(("search_backend:", "extract_backend:")) and ":" in s:
                        val = s.split(":", 1)[1].strip().strip("'\"")
                        if val:
                            return val
                return ""
    except Exception:
        pass
    return ""


def cmd_status(_args):
    d = load()
    left_month = MONTHLY_CAP - int(d.get("used_total", 0))
    print(f"month: {d.get('month')} | used: {d.get('used_total')} | left_month: {left_month}")
    print(f"per-run cap: {RUN_CAP} (aim <={SAFE_RUN} to leave buffer)")
    print(f"runs logged: {len(d.get('runs', []))}")
    print(f"firecrawl key: {'present' if has_key() else 'missing (free-only mode)'}")
    return 0


def cmd_guard(_args):
    d = load()
    left = MONTHLY_CAP - int(d.get("used_total", 0))
    key = has_key()
    pinned = _pinned_backend()
    if not key:
        posture = "FREE-ONLY"
        sweep = "all free tools allowed, Firecrawl skipped"
    elif pinned and any(b in pinned for b in FREE_BACKENDS):
        posture = "PINNED"
        sweep = f"native pinned to {pinned}; free sweep is truly free"
    else:
        posture = "CAREFUL"
        sweep = "native search/extract may spend; sweep with ddgs+arxiv, count native calls"
    print(f"POSTURE: {posture}")
    print(f"key: {'present' if key else 'missing'} | pinned_backend: {pinned or '(none)'} | left_month: {left}")
    print(f"SWEEP: {sweep}")
    return 0


def cmd_precheck(args):
    d = load()
    used = int(d.get("used_total", 0))
    budget = int(args.budget)
    left = MONTHLY_CAP - used
    if budget > RUN_CAP:
        print(f"FALLBACK: budget {budget} exceeds per-run cap {RUN_CAP}. Trim scope or go free-only.")
        return 2
    if used + budget > MONTHLY_CAP:
        print(f"FALLBACK: need {budget}, only {left} left this month. Go free-only.")
        return 2
    if not has_key():
        print(f"FALLBACK: no FIRECRAWL_API_KEY. Go free-only. (Would-be budget {budget}, left {left}.)")
        return 2
    print(f"OK: budget {budget} fits. Used {used}, left_month {left}.")
    if budget > SAFE_RUN:
        print(f"WARN: over safe line {SAFE_RUN}. Keep it tight.")
    return 0


def cmd_log(args):
    d = load()
    used = int(args.used)
    d["used_total"] = int(d.get("used_total", 0)) + used
    d.setdefault("runs", []).append({
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "used": used,
        "note": args.note or "",
    })
    p = save(d)
    left = MONTHLY_CAP - d["used_total"]
    print(f"logged +{used}. total={d['used_total']} left_month={left} file={p}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mimir credit ledger")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("guard")
    pc = sub.add_parser("precheck")
    pc.add_argument("--budget", type=int, required=True, help="estimated credits for this run")
    lg = sub.add_parser("log")
    lg.add_argument("--used", type=int, required=True)
    lg.add_argument("--note", type=str, default="")
    args = ap.parse_args(argv)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "guard":
        return cmd_guard(args)
    if args.cmd == "precheck":
        return cmd_precheck(args)
    if args.cmd == "log":
        return cmd_log(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
