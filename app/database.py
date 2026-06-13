from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

import aiosqlite

from app.premium import extend_premium_until


@dataclass
class UserProfile:
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    birth_date: Optional[date]
    birth_time: Optional[time]
    city: Optional[str]
    birth_lat: Optional[float]
    birth_lon: Optional[float]
    birth_timezone: Optional[str]
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
    evening_enabled: bool
    evening_time: str
    mood_streak: int
    last_mood_date: Optional[str]
    lunar_notify_enabled: bool
    moon_focus: str
    moon_style: str
    premium_until: Optional[str]
    trial_used: bool
    natal_mode: str
    natal_style: str
    natal_qa_free_used: bool
    ref_code: Optional[str]
    referrer_id: Optional[int]
    ref_bonus_count: int


@dataclass
class UserListRow:
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    sign: Optional[str]
    language: str
    premium_until: Optional[str]
    start_source: Optional[str]
    created_at: Optional[str]


@dataclass
class PartnerProfile:
    id: int
    user_id: int
    name: str
    birth_date: date
    birth_time: Optional[time]
    city: Optional[str]
    timezone: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    sign: str
    created_at: str


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
                    natal_mode TEXT DEFAULT 'full',
                    ref_code TEXT UNIQUE,
                    referrer_id INTEGER,
                    ref_bonus_count INTEGER DEFAULT 0
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS referrals (
                    invited_id INTEGER PRIMARY KEY,
                    inviter_id INTEGER NOT NULL,
                    bonus_days INTEGER NOT NULL,
                    created_at TEXT NOT NULL
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
                "evening_enabled": "INTEGER DEFAULT 1",
                "evening_time": "TEXT DEFAULT '20:00'",
                "mood_streak": "INTEGER DEFAULT 0",
                "last_mood_date": "TEXT",
                "lunar_notify_enabled": "INTEGER DEFAULT 1",
                "moon_focus": "TEXT DEFAULT 'practices'",
                "moon_style": "TEXT",
                "premium_until": "TEXT",
                "trial_used": "INTEGER DEFAULT 0",
                "natal_mode": "TEXT DEFAULT 'full'",
                "natal_style": "TEXT DEFAULT 'terms'",
                "natal_qa_free_used": "INTEGER DEFAULT 0",
                "ref_code": "TEXT",
                "referrer_id": "INTEGER",
                "ref_bonus_count": "INTEGER DEFAULT 0",
                "start_source": "TEXT",
                "created_at": "TEXT",
            }
            for col_name, col_def in required_columns.items():
                if col_name not in column_names:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            await db.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)"
            )
            async with db.execute(
                "SELECT 1 FROM schema_migrations WHERE name = ?",
                ("evening_default_20",),
            ) as cursor:
                if await cursor.fetchone() is None:
                    await db.execute(
                        """
                        UPDATE users
                        SET evening_enabled = 1, evening_time = '20:00'
                        WHERE evening_enabled = 0
                          AND (evening_time IS NULL OR evening_time = '21:00')
                        """
                    )
                    await db.execute(
                        "INSERT INTO schema_migrations (name) VALUES (?)",
                        ("evening_default_20",),
                    )
            await db.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_ref_code ON users(ref_code)"
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS partner_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    birth_time TEXT,
                    city TEXT,
                    timezone TEXT,
                    sign TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_partner_profiles_user ON partner_profiles(user_id)"
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS city_geocache (
                    query_key TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    timezone TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            async with db.execute("PRAGMA table_info(users)") as cursor:
                columns = await cursor.fetchall()
                column_names = {row[1] for row in columns}
            user_geo_columns: dict[str, str] = {
                "birth_lat": "REAL",
                "birth_lon": "REAL",
                "birth_timezone": "TEXT",
            }
            for col_name, col_def in user_geo_columns.items():
                if col_name not in column_names:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            async with db.execute("PRAGMA table_info(partner_profiles)") as cursor:
                partner_columns = {row[1] for row in await cursor.fetchall()}
            for col_name, col_def in {"lat": "REAL", "lon": "REAL"}.items():
                if col_name not in partner_columns:
                    await db.execute(f"ALTER TABLE partner_profiles ADD COLUMN {col_name} {col_def}")
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA busy_timeout=5000")
            await db.commit()

    async def upsert_user_identity(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        language: str,
    ) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO users (
                    user_id, username, first_name, language,
                    evening_enabled, evening_time, created_at
                )
                VALUES (?, ?, ?, ?, 1, '20:00', ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    language = COALESCE(users.language, excluded.language)
                """,
                (user_id, username, first_name, language, now_iso),
            )
            await db.commit()

    async def update_profile(
        self,
        user_id: int,
        birth_date: date,
        birth_time: Optional[time],
        city: str,
        sign: str,
        *,
        birth_lat: Optional[float] = None,
        birth_lon: Optional[float] = None,
        birth_timezone: Optional[str] = None,
    ) -> None:
        birth_time_str = birth_time.isoformat(timespec="minutes") if birth_time else None
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET birth_date = ?, birth_time = ?, city = ?, sign = ?,
                    birth_lat = ?, birth_lon = ?, birth_timezone = ?
                WHERE user_id = ?
                """,
                (
                    birth_date.isoformat(),
                    birth_time_str,
                    city,
                    sign,
                    birth_lat,
                    birth_lon,
                    birth_timezone,
                    user_id,
                ),
            )
            await db.commit()

    async def update_user_sign(self, user_id: int, sign: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET sign = ? WHERE user_id = ?",
                (sign, user_id),
            )
            await db.commit()

    async def update_partner_sign(self, partner_id: int, sign: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE partner_profiles SET sign = ? WHERE id = ?",
                (sign, partner_id),
            )
            await db.commit()

    @staticmethod
    def _resolved_user_sun_sign(profile: UserProfile) -> str | None:
        if profile.birth_date is None:
            return None
        from app.zodiac import resolve_sun_sign

        return resolve_sun_sign(
            profile.birth_date,
            profile.birth_time,
            city=profile.city,
            timezone_name=profile.birth_timezone or profile.timezone or "UTC",
            lat=profile.birth_lat,
            lon=profile.birth_lon,
            birth_timezone=profile.birth_timezone,
        )

    @staticmethod
    def _resolved_partner_sun_sign(partner: PartnerProfile) -> str:
        from app.zodiac import resolve_sun_sign

        return resolve_sun_sign(
            partner.birth_date,
            partner.birth_time,
            city=partner.city,
            timezone_name=partner.timezone or "UTC",
            lat=partner.lat,
            lon=partner.lon,
            birth_timezone=partner.timezone,
        )

    async def _sync_user_sign(self, profile: UserProfile) -> UserProfile:
        resolved = self._resolved_user_sun_sign(profile)
        if resolved and resolved != profile.sign:
            await self.update_user_sign(profile.user_id, resolved)
            profile.sign = resolved
        return profile

    async def _sync_partner_sign(self, partner: PartnerProfile) -> PartnerProfile:
        resolved = self._resolved_partner_sun_sign(partner)
        if resolved != partner.sign:
            await self.update_partner_sign(partner.id, resolved)
            partner.sign = resolved
        return partner

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
                profile = UserProfile(
                    user_id=row["user_id"],
                    username=row["username"],
                    first_name=row["first_name"],
                    birth_date=birth_date,
                    birth_time=birth_time,
                    city=row["city"],
                    birth_lat=row["birth_lat"],
                    birth_lon=row["birth_lon"],
                    birth_timezone=row["birth_timezone"],
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
                    evening_enabled=bool(
                        row["evening_enabled"] if row["evening_enabled"] is not None else 1
                    ),
                    evening_time=row["evening_time"] or "20:00",
                    mood_streak=row["mood_streak"] or 0,
                    last_mood_date=row["last_mood_date"],
                    lunar_notify_enabled=bool(row["lunar_notify_enabled"] if row["lunar_notify_enabled"] is not None else 1),
                    moon_focus=row["moon_focus"] if row["moon_focus"] else "practices",
                    moon_style=row["moon_style"] if row["moon_style"] else (row["natal_style"] if row["natal_style"] else "terms"),
                    premium_until=row["premium_until"],
                    trial_used=bool(row["trial_used"] if row["trial_used"] is not None else 0),
                    natal_mode=row["natal_mode"] or "full",
                    natal_style=row["natal_style"] if row["natal_style"] else "terms",
                    natal_qa_free_used=bool(
                        row["natal_qa_free_used"] if row["natal_qa_free_used"] is not None else 0
                    ),
                    ref_code=row["ref_code"],
                    referrer_id=row["referrer_id"],
                    ref_bonus_count=row["ref_bonus_count"] or 0,
                )
                return await self._sync_user_sign(profile)

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

    async def update_mood(self, user_id: int, mood_score: int, *, local_date_key: str | None = None) -> int:
        profile = await self.get_user(user_id)
        now_iso = datetime.now(timezone.utc).isoformat()
        streak = profile.mood_streak if profile else 0
        last_date = profile.last_mood_date if profile else None

        if local_date_key:
            if last_date == local_date_key:
                streak = streak or 1
            else:
                try:
                    current = date.fromisoformat(local_date_key)
                    yesterday = (current - timedelta(days=1)).isoformat()
                except ValueError:
                    yesterday = ""
                if last_date == yesterday and streak > 0:
                    streak += 1
                else:
                    streak = 1
                last_date = local_date_key

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET mood_score = ?,
                    mood_updated_at = ?,
                    mood_streak = ?,
                    last_mood_date = COALESCE(?, last_mood_date)
                WHERE user_id = ?
                """,
                (mood_score, now_iso, streak, last_date, user_id),
            )
            await db.commit()
        return streak

    async def set_evening_checkin(
        self,
        user_id: int,
        *,
        enabled: bool,
        evening_time: Optional[str] = None,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET evening_enabled = ?,
                    evening_time = COALESCE(?, evening_time)
                WHERE user_id = ?
                """,
                (1 if enabled else 0, evening_time, user_id),
            )
            await db.commit()

    async def set_lunar_notify(self, user_id: int, enabled: bool) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET lunar_notify_enabled = ? WHERE user_id = ?",
                (1 if enabled else 0, user_id),
            )
            await db.commit()

    async def get_evening_subscribers(self) -> list[UserProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM users
                WHERE evening_enabled = 1
                  AND sign IS NOT NULL
                """
            ) as cursor:
                rows = await cursor.fetchall()
        return await self._profiles_from_rows(rows)

    async def get_lunar_notify_subscribers(self) -> list[UserProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM users
                WHERE sign IS NOT NULL
                  AND lunar_notify_enabled = 1
                """
            ) as cursor:
                rows = await cursor.fetchall()
        return await self._profiles_from_rows(rows)

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

    async def set_daily_timezone(self, user_id: int, timezone_name: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET timezone = ? WHERE user_id = ?",
                (timezone_name, user_id),
            )
            await db.commit()

    async def get_daily_subscribers(self) -> list[UserProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM users
                WHERE daily_enabled = 1
                  AND sign IS NOT NULL
                """
            ) as cursor:
                rows = await cursor.fetchall()

        return await self._profiles_from_rows(rows)

    def _rows_to_profiles(self, rows: list) -> list[UserProfile]:
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
                    birth_lat=row["birth_lat"],
                    birth_lon=row["birth_lon"],
                    birth_timezone=row["birth_timezone"],
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
                    evening_enabled=bool(
                        row["evening_enabled"] if row["evening_enabled"] is not None else 1
                    ),
                    evening_time=row["evening_time"] or "20:00",
                    mood_streak=row["mood_streak"] or 0,
                    last_mood_date=row["last_mood_date"],
                    lunar_notify_enabled=bool(row["lunar_notify_enabled"] if row["lunar_notify_enabled"] is not None else 1),
                    moon_focus=row["moon_focus"] if row["moon_focus"] else "practices",
                    moon_style=row["moon_style"] if row["moon_style"] else (row["natal_style"] if row["natal_style"] else "terms"),
                    premium_until=row["premium_until"],
                    trial_used=bool(row["trial_used"] if row["trial_used"] is not None else 0),
                    natal_mode=row["natal_mode"] or "full",
                    natal_style=row["natal_style"] if row["natal_style"] else "terms",
                    natal_qa_free_used=bool(
                        row["natal_qa_free_used"] if row["natal_qa_free_used"] is not None else 0
                    ),
                    ref_code=row["ref_code"],
                    referrer_id=row["referrer_id"],
                    ref_bonus_count=row["ref_bonus_count"] or 0,
                )
            )
        return result

    async def _profiles_from_rows(self, rows: list) -> list[UserProfile]:
        synced: list[UserProfile] = []
        for profile in self._rows_to_profiles(rows):
            synced.append(await self._sync_user_sign(profile))
        return synced

    async def set_premium_until(self, user_id: int, premium_until: Optional[str]) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET premium_until = ? WHERE user_id = ?",
                (premium_until, user_id),
            )
            await db.commit()

    async def extend_premium(self, user_id: int, days: int) -> str | None:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT premium_until FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                current_until = row[0]
        until = extend_premium_until(current_until, days)
        until_iso = until.isoformat()
        await self.set_premium_until(user_id, until_iso)
        return until_iso

    async def grant_trial_if_eligible(self, user_id: int, days: int) -> str | None:
        from app.premium import is_premium_active

        if days <= 0:
            return None
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT trial_used, premium_until FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                if bool(row[0]):
                    return None
                if is_premium_active(row[1]):
                    return None
        until_iso = await self.extend_premium(user_id, days)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET trial_used = 1 WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()
        return until_iso

    async def get_users_with_premium(self) -> list[UserProfile]:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM users
                WHERE premium_until IS NOT NULL
                  AND premium_until > ?
                """,
                (now_iso,),
            ) as cursor:
                rows = await cursor.fetchall()
        return await self._profiles_from_rows(rows)

    async def set_natal_mode(self, user_id: int, mode: str) -> None:
        normalized = "short" if mode == "short" else "full"
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET natal_mode = ? WHERE user_id = ?",
                (normalized, user_id),
            )
            await db.commit()

    async def set_natal_style(self, user_id: int, style: str) -> None:
        normalized = "plain" if style == "plain" else "terms"
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET natal_style = ? WHERE user_id = ?",
                (normalized, user_id),
            )
            await db.commit()

    async def set_moon_focus(self, user_id: int, focus: str) -> None:
        normalized = focus if focus in {"practices", "health", "creativity"} else "practices"
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET moon_focus = ? WHERE user_id = ?",
                (normalized, user_id),
            )
            await db.commit()

    async def set_moon_style(self, user_id: int, style: str) -> None:
        normalized = "plain" if style == "plain" else "terms"
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET moon_style = ? WHERE user_id = ?",
                (normalized, user_id),
            )
            await db.commit()

    async def consume_natal_qa_free_answer(self, user_id: int) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                """
                UPDATE users
                SET natal_qa_free_used = 1
                WHERE user_id = ? AND COALESCE(natal_qa_free_used, 0) = 0
                """,
                (user_id,),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def ensure_ref_code(self, user_id: int) -> str:
        code = f"u{user_id}"
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE users SET ref_code = COALESCE(ref_code, ?) WHERE user_id = ?",
                (code, user_id),
            )
            await db.commit()
            async with db.execute(
                "SELECT ref_code FROM users WHERE user_id = ?",
                (user_id,),
            ) as c:
                row = await c.fetchone()
                return row[0] if row and row[0] else code

    async def get_user_id_by_ref_code(self, ref_code: str) -> Optional[int]:
        ref_code = ref_code.strip()
        if ref_code.startswith("u") and ref_code[1:].isdigit():
            return int(ref_code[1:])
        if ref_code.isdigit():
            return int(ref_code)
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT user_id FROM users WHERE ref_code = ?",
                (ref_code,),
            ) as c:
                row = await c.fetchone()
                return int(row[0]) if row else None

    async def set_referrer_if_empty(self, invited_user_id: int, referrer_user_id: int) -> bool:
        if invited_user_id == referrer_user_id:
            return False
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT referrer_id FROM users WHERE user_id = ?",
                (invited_user_id,),
            ) as c:
                row = await c.fetchone()
                if row is None:
                    return False
                if row[0] is not None:
                    return False
            await db.execute(
                "UPDATE users SET referrer_id = ? WHERE user_id = ?",
                (referrer_user_id, invited_user_id),
            )
            await db.commit()
            return True

    async def get_referral_count(self, inviter_user_id: int) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM referrals WHERE inviter_id = ?",
                (inviter_user_id,),
            ) as c:
                row = await c.fetchone()
                return int(row[0] if row else 0)

    async def reward_referral(
        self,
        invited_user_id: int,
        bonus_days: int = 7,
    ) -> Optional[int]:
        profile = await self.get_user(invited_user_id)
        if (
            profile is None
            or profile.birth_date is None
            or not profile.sign
            or not profile.goal
            or not profile.relationship_status
        ):
            return None

        now = datetime.now(timezone.utc)
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT referrer_id FROM users WHERE user_id = ?",
                (invited_user_id,),
            ) as c:
                row = await c.fetchone()
                if row is None or row[0] is None:
                    return None
                inviter_id = int(row[0])
                if inviter_id == invited_user_id:
                    return None

            async with db.execute(
                "SELECT inviter_id FROM referrals WHERE invited_id = ?",
                (invited_user_id,),
            ) as c:
                exists = await c.fetchone()
                if exists is not None:
                    return None

            async with db.execute(
                "SELECT premium_until FROM users WHERE user_id = ?",
                (inviter_id,),
            ) as c:
                inviter_row = await c.fetchone()
                current_until = inviter_row[0] if inviter_row else None

            base = now
            if current_until:
                try:
                    parsed = datetime.fromisoformat(current_until)
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    if parsed > now:
                        base = parsed
                except Exception:
                    base = now

            new_until = (base + timedelta(days=max(1, bonus_days))).isoformat()
            await db.execute(
                "UPDATE users SET premium_until = ?, ref_bonus_count = COALESCE(ref_bonus_count, 0) + 1 WHERE user_id = ?",
                (new_until, inviter_id),
            )
            await db.execute(
                "INSERT INTO referrals (invited_id, inviter_id, bonus_days, created_at) VALUES (?, ?, ?, ?)",
                (invited_user_id, inviter_id, max(1, bonus_days), now.isoformat()),
            )
            await db.commit()
            return inviter_id

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
        return await self._profiles_from_rows(rows)

    async def log_event(self, user_id: int, event_name: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO events (user_id, event_name, created_at) VALUES (?, ?, ?)",
                (user_id, event_name, now_iso),
            )
            await db.commit()

    async def has_event(self, user_id: int, event_name: str) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT 1 FROM events WHERE user_id = ? AND event_name = ? LIMIT 1",
                (user_id, event_name),
            ) as cursor:
                return await cursor.fetchone() is not None

    async def has_payment_charge(self, charge_id: str) -> bool:
        if not charge_id:
            return False
        event_name = f"premium_charge:{charge_id}"
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT 1 FROM events WHERE event_name = ? LIMIT 1",
                (event_name,),
            ) as cursor:
                return await cursor.fetchone() is not None

    async def record_payment_charge(self, charge_id: str, user_id: int) -> None:
        if charge_id:
            await self.log_event(user_id, f"premium_charge:{charge_id}")

    async def count_events_for_day(self, user_id: int, event_name: str, date_key: str) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE user_id = ?
                  AND event_name = ?
                  AND substr(created_at, 1, 10) = ?
                """,
                (user_id, event_name, date_key),
            ) as c:
                row = await c.fetchone()
                return int(row[0] if row else 0)

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

    async def set_start_source_if_empty(self, user_id: int, source: str) -> bool:
        normalized = source.strip().lower()[:32]
        if not normalized:
            return False
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                """
                UPDATE users
                SET start_source = ?
                WHERE user_id = ?
                  AND (start_source IS NULL OR start_source = '')
                """,
                (normalized, user_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_start_source_stats(self) -> list[tuple[str, int]]:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                """
                SELECT COALESCE(NULLIF(start_source, ''), 'direct') AS src, COUNT(*) AS cnt
                FROM users
                GROUP BY src
                ORDER BY cnt DESC, src ASC
                LIMIT 20
                """
            ) as cursor:
                rows = await cursor.fetchall()
        return [(str(row[0]), int(row[1])) for row in rows]

    async def count_errors_since(self, since_iso: str) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM error_log WHERE created_at >= ?",
                (since_iso,),
            ) as cursor:
                row = await cursor.fetchone()
        return int(row[0] if row else 0)

    async def get_recent_error_summaries(
        self,
        since_iso: str | None = None,
        *,
        limit: int = 5,
    ) -> list[dict[str, str]]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            if since_iso is None:
                query = """
                    SELECT source, error_type, message, created_at
                    FROM error_log
                    ORDER BY id DESC
                    LIMIT ?
                """
                params: tuple[object, ...] = (limit,)
            else:
                query = """
                    SELECT source, error_type, message, created_at
                    FROM error_log
                    WHERE created_at >= ?
                    ORDER BY id DESC
                    LIMIT ?
                """
                params = (since_iso, limit)
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
        return [
            {
                "source": str(row["source"]),
                "error_type": str(row["error_type"]),
                "message": str(row["message"]),
                "created_at": str(row["created_at"]),
            }
            for row in rows
        ]

    async def get_stats(self) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        since_24h = (now - timedelta(hours=24)).isoformat()
        since_7d = (now - timedelta(days=7)).isoformat()
        since_30d = (now - timedelta(days=30)).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                total_users = (await c.fetchone())[0]
            async with db.execute(
                """
                SELECT COUNT(*) FROM users
                WHERE created_at IS NOT NULL AND created_at >= ?
                """,
                (since_7d,),
            ) as c:
                new_users_7d = (await c.fetchone())[0]
            async with db.execute(
                """
                SELECT COUNT(*) FROM users
                WHERE created_at IS NOT NULL AND created_at >= ?
                """,
                (since_30d,),
            ) as c:
                new_users_30d = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM users WHERE daily_enabled = 1") as c:
                daily_subscribers = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE premium_until IS NOT NULL AND premium_until > ?",
                (now_iso,),
            ) as c:
                premium_users = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM referrals WHERE created_at >= ?",
                (since_7d,),
            ) as c:
                referrals_7d = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM referrals WHERE created_at >= ?",
                (since_30d,),
            ) as c:
                referrals_30d = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM events") as c:
                total_events = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM error_log WHERE created_at >= ?",
                (since_24h,),
            ) as c:
                errors_24h = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM error_log") as c:
                total_errors = (await c.fetchone())[0]
        return {
            "total_users": total_users,
            "new_users_7d": new_users_7d,
            "new_users_30d": new_users_30d,
            "daily_subscribers": daily_subscribers,
            "premium_users": premium_users,
            "referrals_7d": referrals_7d,
            "referrals_30d": referrals_30d,
            "total_events": total_events,
            "errors_24h": errors_24h,
            "total_errors": total_errors,
        }

    async def get_all_user_ids(self) -> list[int]:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT user_id FROM users") as c:
                rows = await c.fetchall()
        return [int(row[0]) for row in rows]

    async def count_users(self) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                row = await c.fetchone()
        return int(row[0]) if row else 0

    async def list_users_page(self, *, offset: int, limit: int) -> list[UserListRow]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT user_id, username, first_name, sign, language,
                       premium_until, start_source, created_at
                FROM users
                ORDER BY created_at DESC, user_id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ) as cursor:
                rows = await cursor.fetchall()
        return [
            UserListRow(
                user_id=int(row["user_id"]),
                username=row["username"],
                first_name=row["first_name"],
                sign=row["sign"],
                language=row["language"] or "en",
                premium_until=row["premium_until"],
                start_source=row["start_source"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def _row_to_partner(self, row: aiosqlite.Row) -> PartnerProfile:
        birth_date = date.fromisoformat(row["birth_date"])
        birth_time = time.fromisoformat(row["birth_time"]) if row["birth_time"] else None
        return PartnerProfile(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            name=row["name"],
            birth_date=birth_date,
            birth_time=birth_time,
            city=row["city"],
            timezone=row["timezone"],
            lat=row["lat"],
            lon=row["lon"],
            sign=row["sign"],
            created_at=row["created_at"],
        )

    async def list_partners(self, user_id: int) -> list[PartnerProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM partner_profiles
                WHERE user_id = ?
                ORDER BY name COLLATE NOCASE ASC, id ASC
                """,
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
        partners = [self._row_to_partner(row) for row in rows]
        synced: list[PartnerProfile] = []
        for partner in partners:
            synced.append(await self._sync_partner_sign(partner))
        return synced

    async def get_partner(self, user_id: int, partner_id: int) -> Optional[PartnerProfile]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM partner_profiles WHERE user_id = ? AND id = ?",
                (user_id, partner_id),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            return None
        return await self._sync_partner_sign(self._row_to_partner(row))

    async def count_partners(self, user_id: int) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM partner_profiles WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
        return int(row[0] if row else 0)

    async def add_partner(
        self,
        user_id: int,
        *,
        name: str,
        birth_date: date,
        birth_time: Optional[time],
        city: Optional[str],
        tz_name: Optional[str],
        sign: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        birth_time_str = birth_time.isoformat(timespec="minutes") if birth_time else None
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO partner_profiles (
                    user_id, name, birth_date, birth_time, city, timezone, lat, lon, sign, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    name,
                    birth_date.isoformat(),
                    birth_time_str,
                    city,
                    tz_name,
                    lat,
                    lon,
                    sign,
                    now_iso,
                ),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def delete_partner(self, user_id: int, partner_id: int) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "DELETE FROM partner_profiles WHERE user_id = ? AND id = ?",
                (user_id, partner_id),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def get_city_geocache(self, query_key: str):
        from app.geo import GeocodedLocation

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM city_geocache WHERE query_key = ?",
                (query_key,),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            return None
        return GeocodedLocation(
            display_name=row["display_name"],
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            timezone=row["timezone"],
            source="cache",
        )

    async def save_city_geocache(self, query_key: str, location) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO city_geocache (query_key, display_name, lat, lon, timezone, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(query_key) DO UPDATE SET
                    display_name = excluded.display_name,
                    lat = excluded.lat,
                    lon = excluded.lon,
                    timezone = excluded.timezone,
                    updated_at = excluded.updated_at
                """,
                (
                    query_key,
                    location.display_name,
                    location.lat,
                    location.lon,
                    location.timezone,
                    now_iso,
                ),
            )
            await db.commit()

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
