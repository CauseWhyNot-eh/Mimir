"""Mimir one-command report closer: render Sources + verify + log spend + credit line.
Replaces the old 4-call tmp-file chain.
Usage:
  python mimir-report.py --report report.md --used 12 --note "scrape x10 + search x1"
  python mimir-report.py --report report.md --used 0 --note "free-only" --no-strict
Exit codes: 0 = done, 1 = render/verify failed (ledger NOT logged, fix first).
"""
import argparse
import json
import pathlib
import subprocess
import sys

CREDIT_OPEN = "<!-- mimir-credits -->"
CREDIT_CLOSE = "<!-- /mimir-credits -->"


def here():
    return pathlib.Path(__file__).resolve().parent


def skill_home():
    return here().parent


def homes():
    # <home>/skills/research/mimir -> <home> is skill_home().parent.parent
    return skill_home().parent.parent


def sources_py():
    return homes() / "research" / "grounded-citations" / "scripts" / "sources.py"


def ledger_py():
    return here() / "ledger.py"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def ledger_data():
    sys.path.insert(0, str(here()))
    import ledger as L
    return L.load()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mimir report closer")
    ap.add_argument("--report", required=True)
    ap.add_argument("--used", type=int, required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("--no-strict", action="store_true")
    args = ap.parse_args(argv)
    report = pathlib.Path(args.report)
    if not report.exists():
        print(f"FAIL: report not found: {report}")
        return 1
    py = sys.executable or "python"
    code, out = run([py, str(sources_py()), "render", "--replace-in", str(report)])
    print(out.strip()[-500:] if out.strip() else "(render silent)")
    if code != 0:
        print("FAIL: sources render failed. ledger untouched.")
        return 1
    vargs = [py, str(sources_py()), "verify", str(report)]
    if not args.no_strict:
        vargs.append("--strict")
    code, out = run(vargs)
    print(out.strip()[-800:] if out.strip() else "(verify silent)")
    if code != 0 and not args.no_strict:
        print("FAIL: verify failed. Fix citations, then re-run. ledger untouched.")
        return 1
    code, out = run([py, str(ledger_py()), "log", "--used", str(args.used), "--note", args.note])
    print(out.strip())
    if code != 0:
        print("FAIL: ledger log failed.")
        return 1
    d = ledger_data()
    total = int(d.get("used_total", 0))
    left = 1000 - total
    mode = "surgical" if args.used > 0 else "free-only"
    block = (f"{CREDIT_OPEN}\n"
             f"Mimir used: {args.used} | Month used: {total} | Left: {left} | Mode: {mode}\n"
             f"{CREDIT_CLOSE}\n")
    text = report.read_text(encoding="utf-8")
    if CREDIT_OPEN in text:
        pre, rest = text.split(CREDIT_OPEN, 1)
        _, post = rest.split(CREDIT_CLOSE, 1)
        text = pre + block + post
    else:
        text = text.rstrip() + "\n\n" + block
    report.write_text(text, encoding="utf-8")
    print(f"CLOSED: mode={mode} used={args.used} left_month={left}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
