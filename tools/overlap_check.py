"""8-word overlap check: compare every repo doc against a source text file
supplied with --source (the source itself is never committed to the repo).

Usage:
    python3 tools/overlap_check.py --source /path/to/source.txt [--docs-dir docs]

Exit code 0 means zero 8-word matches; any match is printed and fails.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_WORD = re.compile(r"[a-z0-9]+")


def shingles(text: str, n: int = 8) -> set:
    words = _WORD.findall(text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--docs-dir", default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    source = shingles(Path(args.source).read_text(encoding="utf-8", errors="ignore"))
    targets = []
    for pattern in ("README.md", "docs/*.md", "knowledge/*.md", "data/*.md"):
        targets.extend(sorted(root.glob(pattern)))
    if args.docs_dir:
        targets.extend(sorted(Path(args.docs_dir).glob("*.md")))
    hits = []
    for target in targets:
        found = shingles(target.read_text(encoding="utf-8", errors="ignore")) & source
        for hit in sorted(found):
            hits.append(f"{target.relative_to(root)}: {hit}")
    if hits:
        print(f"OVERLAP HITS: {len(hits)}")
        for hit in hits:
            print(hit)
        return 1
    print(f"OVERLAP CHECK: 0 hits across {len(targets)} doc files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
