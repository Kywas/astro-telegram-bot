from pathlib import Path
import sys


def main() -> None:
    env_path = Path("/opt/astro-telegram-bot/.env")
    if not env_path.is_file():
        print("Missing /opt/astro-telegram-bot/.env", file=sys.stderr)
        raise SystemExit(1)

    token = ""
    admin_ids: list[str] = []
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("BOT_TOKEN="):
            token = stripped.split("=", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("ADMIN_IDS="):
            raw = stripped.split("=", 1)[1].strip().strip('"').strip("'")
            admin_ids = [part.strip() for part in raw.split(",") if part.strip()]

    if not token:
        print("BOT_TOKEN is missing or empty in .env", file=sys.stderr)
        raise SystemExit(1)

    print("OK: .env contains BOT_TOKEN")
    if not admin_ids:
        print("WARN: ADMIN_IDS is empty — admin alerts and /stats access will not work", file=sys.stderr)
    else:
        print(f"OK: ADMIN_IDS has {len(admin_ids)} id(s)")


if __name__ == "__main__":
    main()
