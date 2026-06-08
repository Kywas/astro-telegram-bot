from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Optional

import aiosqlite


@dataclass
class UserProfile:
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    birth_date: Optional[date]
    birth_time: Optional[time]
    city: Optional[str]
    sign: Optional[str]
    language: str
    gender: Optional[str]
    relationship_status: Optional[str]
    goal: Optional[str]
    mood_score: Optional[int]
    mood_updated_at: Optional[str]
    daily_enabled: bool
    daily_time: str
    timezone: str
    premium_until: Optional[str]
    natal_mode: str


class Database:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    birth_date TEXT,
                    birth_time TEXT,
                    city TEXT,
                    sign TEXT,
                    language TEXT DEFAULT 'en',
                    gender TEXT,
                    relationship_status TEXT,
                    goal TEXT,
                    mood_score INTEGER,
                    mood_updated_at TEXT,
                    daily_enabled INTEGER DEFAULT 0,
                    daily_time TEXT DEFAULT '09:00',
                    timezone TEXT DEFAULT 'UTC',
                    premium_until TEXT,
                    natal_mode TEXT DEFAULT 'full'
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_delivery_log (
                    user_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    date_key TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, period, date_key)
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    context TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            async with db.execute("PRAGMA table_info(users)") as cursor:
                columns = await cursor.fetchall()
                column_names = {row[1] for row in columns}
            required_columns: dict[str, str] = {
                "language": "TEXT DEFAULT 'en'",
                "gender": "TEXT",
                "relationship_status": "TEXT",
                "goal": "TEXT",
                "mood_score": "INTEGER",
                "mood_updated_at": "TEXT",
                "daily_enabled": "INTEGER DEFAULT 0",
                "daily_time": "TEXT DEFAULT '09:00'",
                "timezone": "TEXT DEFAULT 'UTC'",
                "premium_until": "TEXT",
                "natal_mode": "TEXT DEFAULT 'full'",
            }
            for col_name, col_def in required_columns.items():
                if col_name not in column_names:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            await db.commit()

    async def upsert_user_identity(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        language: str,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, first_name, language)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    language = COALESCE(users.language, excluded.language)
                """,
                (user_id, username, first_name, language),
            )
            await db.commit()

    async def update_profile(
        self, user_id: int, birth_date: date, birth_time: Optional[time], city: str, sign: str
    ) -> None:
        birth_time_str = birth_time.isoformat(timespec="minutes") if birth_time else None
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET birth_date = ?, birth_time = ?, city = ?, sign = ?
                WHERE user_id = ?
                """,
                (birth_date.isoformat(), birth_time_str, city, sign, user_id),
            )
            await db.commit()

    async def get_user(self, user_id: int) -> Optional[UserProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None

                birth_date = date.fromisoformat(row["birth_date"]) if row["birth_date"] else None
                birth_time = time.fromisoformat(row["birth_time"]) if row["birth_time"] else None
                return UserProfile(
                    user_id=row["user_id"],
                    username=row["username"],
                    first_name=row["first_name"],
                    birth_date=birth_date,
                    birth_time=birth_time,
                    city=row["city"],
                    sign=row["sign"],
                    language=row["language"] or "en",
                    gender=row["gender"],
                    relationship_status=row["relationship_status"],
                    goal=row["goal"],
                    mood_score=row["mood_score"],
                    mood_updated_at=row["mood_updated_at"],
                    daily_enabled=bool(row["daily_enabled"]),
                    daily_time=row["daily_time"] or "09:00",
                    timezone=row["timezone"] or "UTC",
                    premium_until=row["premium_until"],
                    natal_mode=row["natal_mode"] or "full",
                )

    async def set_user_language(self, user_id: int, language: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET language = ? WHERE user_id = ?",
                (language, user_id),
            )
            await db.commit()

    async def update_preferences(
        self,
        user_id: int,
        *,
        gender: Optional[str] = None,
        relationship_status: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET gender = COALESCE(?, gender),
                    relationship_status = COALESCE(?, relationship_status),
                    goal = COALESCE(?, goal)
                WHERE user_id = ?
                """,
                (gender, relationship_status, goal, user_id),
            )
            await db.commit()

    async def update_mood(self, user_id: int, mood_score: int) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET mood_score = ?, mood_updated_at = ?
                WHERE user_id = ?
                """,
                (mood_score, now_iso, user_id),
            )
            await db.commit()

    async def set_daily_subscription(
        self,
        user_id: int,
        *,
        enabled: bool,
        daily_time: Optional[str] = None,
        timezone_name: Optional[str] = None,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET daily_enabled = ?,
                    daily_time = COALESCE(?, daily_time),
                    timezone = COALESCE(?, timezone)
                WHERE user_id = ?
                """,
                (1 if enabled else 0, daily_time, timezone_name, user_id),
            )
            await db.commit()

    async def set_premium_until(self, user_id: int, premium_until: Optional[str]) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET premium_until = ? WHERE user_id = ?",
                (premium_until, user_id),
            )
            await db.commit()

    async def set_natal_mode(self, user_id: int, mode: str) -> None:
        normalized = "short" if mode == "short" else "full"
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET natal_mode = ? WHERE user_id = ?",
                (normalized, user_id),
            )
            await db.commit()

    async def get_daily_recipients(self, hhmm: str) -> list[UserProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM users
                WHERE daily_enabled = 1
                  AND sign IS NOT NULL
                  AND daily_time = ?
                """,
                (hhmm,),
            ) as cursor:
                rows = await cursor.fetchall()

        result: list[UserProfile] = []
        for row in rows:
            birth_date = date.fromisoformat(row["birth_date"]) if row["birth_date"] else None
            birth_time = time.fromisoformat(row["birth_time"]) if row["birth_time"] else None
            result.append(
                UserProfile(
                    user_id=row["user_id"],
                    username=row["username"],
                    first_name=row["first_name"],
                    birth_date=birth_date,
                    birth_time=birth_time,
                    city=row["city"],
                    sign=row["sign"],
                    language=row["language"] or "en",
                    gender=row["gender"],
                    relationship_status=row["relationship_status"],
                    goal=row["goal"],
                    mood_score=row["mood_score"],
                    mood_updated_at=row["mood_updated_at"],
                    daily_enabled=bool(row["daily_enabled"]),
                    daily_time=row["daily_time"] or "09:00",
                    timezone=row["timezone"] or "UTC",
                    premium_until=row["premium_until"],
                    natal_mode=row["natal_mode"] or "full",
                )
            )
        return result

    async def log_event(self, user_id: int, event_name: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO events (user_id, event_name, created_at) VALUES (?, ?, ?)",
                (user_id, event_name, now_iso),
            )
            await db.commit()

    async def was_daily_sent(self, user_id: int, period: str, date_key: str) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT 1 FROM daily_delivery_log
                WHERE user_id = ? AND period = ? AND date_key = ?
                """,
                (user_id, period, date_key),
            ) as c:
                row = await c.fetchone()
        return row is not None

    async def mark_daily_sent(self, user_id: int, period: str, date_key: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO daily_delivery_log (user_id, period, date_key, sent_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, period, date_key, now_iso),
            )
            await db.commit()

    async def get_stats(self) -> dict[str, int]:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                total_users = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM users WHERE daily_enabled = 1") as c:
                daily_subscribers = (await c.fetchone())[0]
            now_iso = datetime.now(timezone.utc).isoformat()
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE premium_until IS NOT NULL AND premium_until > ?",
                (now_iso,),
            ) as c:
                premium_users = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM events") as c:
                total_events = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM error_log") as c:
                total_errors = (await c.fetchone())[0]
        return {
            "total_users": total_users,
            "daily_subscribers": daily_subscribers,
            "premium_users": premium_users,
            "total_events": total_events,
            "total_errors": total_errors,
        }

    async def get_all_user_ids(self) -> list[int]:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT user_id FROM users") as c:
                rows = await c.fetchall()
        return [int(row[0]) for row in rows]

    async def log_error(
        self,
        *,
        source: str,
        error_type: str,
        message: str,
        context: str | None = None,
    ) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO error_log (source, error_type, message, context, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source, error_type, message[:2000], context, now_iso),
            )
            await db.commit()
