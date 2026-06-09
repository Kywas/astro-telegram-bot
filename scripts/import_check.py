"""Fail fast if any app module cannot be imported (Python 3.12-safe)."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULES = (
    "app.bot",
    "app.bot_context",
    "app.handlers.admin",
    "app.handlers.user",
    "app.keyboards",
    "app.profile_public",
    "app.services.admin_users",
    "app.services.compat",
    "app.services.daily_panels",
    "app.services.dates",
    "app.services.home",
    "app.services.locale_users",
    "app.services.menu",
    "app.services.onboarding",
    "app.services.premium_panel",
    "app.services.referral",
)


def main() -> None:
    for name in MODULES:
        importlib.import_module(name)
    print(f"OK: imported {len(MODULES)} modules")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
