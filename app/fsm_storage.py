"""Persistent FSM storage in SQLite (survives bot restarts)."""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping

import aiosqlite
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

logger = logging.getLogger(__name__)


def _state_str(state: StateType) -> str | None:
    if state is None:
        return None
    if isinstance(state, State):
        return state.state
    return str(state)


class SQLiteFsmStorage(BaseStorage):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._ready = False

    async def _ensure_ready(self) -> None:
        if self._ready:
            return
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA busy_timeout = 5000")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS fsm_storage (
                    bot_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    destiny TEXT NOT NULL DEFAULT 'default',
                    state TEXT,
                    data TEXT NOT NULL DEFAULT '{}',
                    PRIMARY KEY (bot_id, chat_id, user_id, destiny)
                )
                """
            )
            await db.commit()
        self._ready = True

    @staticmethod
    def _row_key(key: StorageKey) -> tuple[int, int, int, str]:
        return key.bot_id, key.chat_id, key.user_id, key.destiny

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        await self._ensure_ready()
        bot_id, chat_id, user_id, destiny = self._row_key(key)
        state_value = _state_str(state)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA busy_timeout = 5000")
            await db.execute(
                """
                INSERT INTO fsm_storage (bot_id, chat_id, user_id, destiny, state, data)
                VALUES (?, ?, ?, ?, ?, '{}')
                ON CONFLICT(bot_id, chat_id, user_id, destiny) DO UPDATE SET
                    state = excluded.state
                """,
                (bot_id, chat_id, user_id, destiny, state_value),
            )
            await db.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        await self._ensure_ready()
        bot_id, chat_id, user_id, destiny = self._row_key(key)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA busy_timeout = 5000")
            async with db.execute(
                """
                SELECT state FROM fsm_storage
                WHERE bot_id = ? AND chat_id = ? AND user_id = ? AND destiny = ?
                """,
                (bot_id, chat_id, user_id, destiny),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        await self._ensure_ready()
        bot_id, chat_id, user_id, destiny = self._row_key(key)
        payload = json.dumps(dict(data), ensure_ascii=False)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA busy_timeout = 5000")
            await db.execute(
                """
                INSERT INTO fsm_storage (bot_id, chat_id, user_id, destiny, state, data)
                VALUES (?, ?, ?, ?, NULL, ?)
                ON CONFLICT(bot_id, chat_id, user_id, destiny) DO UPDATE SET
                    data = excluded.data
                """,
                (bot_id, chat_id, user_id, destiny, payload),
            )
            await db.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        await self._ensure_ready()
        bot_id, chat_id, user_id, destiny = self._row_key(key)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("PRAGMA busy_timeout = 5000")
            async with db.execute(
                """
                SELECT data FROM fsm_storage
                WHERE bot_id = ? AND chat_id = ? AND user_id = ? AND destiny = ?
                """,
                (bot_id, chat_id, user_id, destiny),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None or not row[0]:
            return {}
        try:
            parsed = json.loads(row[0])
        except json.JSONDecodeError:
            logger.warning("invalid fsm json user_id=%s", user_id)
            return {}
        return parsed if isinstance(parsed, dict) else {}

    async def close(self) -> None:
        self._ready = False
