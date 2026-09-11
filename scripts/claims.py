"""Mimir claim ledger - verified facts that survive across runs.
One small JSON file in the global Hermes cache (shared across profiles).
Usage:
  python claims.py add --claim "Paddle base fee is 5% + $0.50" --source https://... --confidence high --topic billing
  python claims.py find "paddle fees"
  python claims.py list --topic billing
Confidence: high (2+ independent sources) | med (1 solid source) | low (single/weak source).
"""
import argparse
import datetime
import json
import os
import pathlib
import sys


def store_path():
    override = os.environ.get("MIMIR_CLAIMS")
    if override:
        return pathlib.Path(override)
    hh = os.environ.get("HERMES_HOME")
    if hh:
        p = pathlib.Path(hh)
        if "profiles" in p.parts:
            idx = p.parts.index("profiles")
            return pathlib.Path(*p.parts[:idx]) / "cache" / "mimir-claims.json"
        return p / "cache" / "mimir-claims.json"
    if os.name == "nt":
        return pathlib.Path.home() / "AppData" / "Local" / "hermes" / "cache" / "mimir-claims.json"
    return pathlib.Path.home() / ".hermes" / "cache" / "mimir-claims.json"


def load():
    p = store_path()
    if not p.exists():
        return {"claims": []}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        d.setdefault("claims", [])
        return d
    except Exception:
        return {"claims": []}


def save(d):
    p = store_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    return p


def cmd_add(args):
    d = load()
    entry = {
        "id": len(d["claims"]) + 1,
        "claim": args.claim,
        "sources": args.source or [],
        "confidence": args.confidence,
        "topic": args.topic or "",
        "added": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    d["claims"].append(entry)
    p = save(d)
    print(f"claim #{entry['id']} stored [{entry['confidence']}] -> {p}")
    return 0


def stem(w):
    w = w.lower()
    return w[:-1] if len(w) > 3 and w.endswith("s") else w


def cmd_find(args):
    d = load()
    words = args.keywords.lower().split()
    hits = []
    for c in d["claims"]:
        hay = (c["claim"] + " " + c.get("topic", "")).lower()
        if all(w in hay or stem(w) in hay for w in words):
            hits.append(c)
    if not hits:
        print("no known claims. research fresh.")
        return 0
    for c in hits:
        print(f"#{c['id']} [{c['confidence']}] {c['claim']}")
        for s in c.get("sources", []):
            print(f"   src: {s}")
    return 0


def cmd_list(args):
    d = load()
    items = [c for c in d["claims"] if not args.topic or c.get("topic") == args.topic]
    print(f"{len(items)} claims" + (f" in topic '{args.topic}'" if args.topic else ""))
    for c in items:
        print(f"#{c['id']} [{c['confidence']}] {c['claim'][:100]}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mimir claim ledger")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--claim", required=True)
    a.add_argument("--source", action="append", default=[])
    a.add_argument("--confidence", choices=["high", "med", "low"], default="med")
    a.add_argument("--topic", default="")
    f = sub.add_parser("find")
    f.add_argument("keywords")
    li = sub.add_parser("list")
    li.add_argument("--topic", default="")
    args = ap.parse_args(argv)
    if args.cmd == "add":
        return cmd_add(args)
    if args.cmd == "find":
        return cmd_find(args)
    return cmd_list(args)


if __name__ == "__main__":
    sys.exit(main())
