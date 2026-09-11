"""Install Mimir into a skills directory. Stdlib only.
Usage:
  python install.py                        # Hermes default location
  python install.py --target <skills-dir>  # custom location (skill lands in <skills-dir>/mimir)
"""
import argparse
import pathlib
import shutil
import sys

SRC = pathlib.Path(__file__).resolve().parent
FILES = ["SKILL.md"]
DIRS = ["scripts", "references"]


def default_target():
    home = pathlib.Path.home()
    if sys.platform == "win32":
        import os
        base = pathlib.Path(os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local")))
        return base / "hermes" / "skills" / "research"
    return home / ".hermes" / "skills" / "research"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Install the Mimir skill")
    ap.add_argument("--target", default=str(default_target()),
                    help="research skills dir (skill lands in <target>/mimir)")
    args = ap.parse_args(argv)
    dest = pathlib.Path(args.target) / "mimir"
    if dest.exists():
        print(f"exists, refreshing: {dest}")
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        shutil.copy2(SRC / f, dest / f)
    for d in DIRS:
        shutil.copytree(SRC / d, dest / d)
    for pyc in dest.rglob("__pycache__"):
        shutil.rmtree(pyc)
    print(f"installed mimir {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
