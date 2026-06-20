"""Assign and build unique *-base.png for every channel post."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.channel_base_pool import assign_all_posts, verify_unique_bases  # noqa: E402


def main() -> None:
    rows = assign_all_posts(force="--force" in sys.argv)
    ok, dupes = verify_unique_bases()
    for slug, source, variant in rows:
        if variant < 0:
            print(f"OK {slug} (locked original)")
        else:
            print(f"OK {slug} <- {source} variant={variant}")
    if ok:
        print(f"\nAll {len(rows)} posts have unique base images.")
    else:
        print("\nWARN duplicates remain:")
        for line in dupes:
            print(f"  • {line}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
