from __future__ import annotations

import datetime as dt
import logging
import os
import random
from pathlib import Path
from typing import List

import aiosqlite
import discord
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo

from avocado_bot.cogs.report import generate_report_png

log = logging.getLogger("war_tracker")
PST = ZoneInfo("America/Los_Angeles")

DB_PATH = Path("db/war.db")
CLAN_TAG = os.getenv("CLAN_TAG", "#AV0CAD0")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# ─────────────────────────── helpers ────────────────────────────
def now() -> dt.datetime:
    return dt.datetime.now(tz=PST)


def in_war_window(t: dt.datetime) -> bool:
    """02:46 → 02:44 next day (PST)"""
    return dt.time(2, 46) <= t.time() or t.time() <= dt.time(2, 44)


def is_poll_window(t: dt.datetime) -> bool:
    """Skip 02:43 – 03:59 to avoid reset overlap."""
    h, m = t.hour, t.minute
    return not ((h == 2 and m >= 43) or h == 3)


def war_day_key(t: dt.datetime) -> str:
    """Label rows with the *game* day (shift −3 h)."""
    return (t - dt.timedelta(hours=3)).date().isoformat()


# ─────────────────────────── cog ────────────────────────────────
class WarTracker(commands.Cog):
    """60 s poller + auto-snapshot/rollover; NO user commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = bot.get_cog("ClashAPI")  # type: ignore
        self.fetch_task.start()

    # --- DB bootstrap --------------------------------------------------
    async def _ensure_db(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        schema = Path(__file__).parent.parent / "db" / "schema.sql"
        async with aiosqlite.connect(DB_PATH) as db:
            await db.executescript(schema.read_text())
            await db.commit()

    # --- polling loop --------------------------------------------------
    @tasks.loop(seconds=60)
    async def fetch_task(self) -> None:
        await self._ensure_db()
        ts = now()
        if not in_war_window(ts) or not is_poll_window(ts):
            return

        data = await self.api.get_current_river_race(CLAN_TAG)  # type: ignore
        if not data or "clan" not in data:
            return

        async with aiosqlite.connect(DB_PATH) as db:
            for p in data["clan"]["participants"]:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO current_war
                    (war_date, player_tag, name, decks_used, fame, score, donations)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        war_day_key(ts),
                        p["tag"],
                        p["name"],
                        p["decksUsed"],
                        p["fame"],
                        p["scoreEarnedToday"],
                        p.get("donations", 0),
                    ),
                )
            await db.commit()

        # 20:00 snapshot
        if ts.strftime("%H:%M") == "20:00":
            await self._post_report(snapshot=True)

        # 02:42 nightly + Monday rollover
        if ts.strftime("%H:%M") == "02:42":
            await self._post_report(snapshot=False)
            if ts.weekday() == 0:  # Monday
                await self._rollover()

    # --- exposed for manual refresh -----------------------------------
    async def poll_once(self) -> None:
        """Called by !warrefresh; obeys poll-window guards."""
        ts = now()
        if not in_war_window(ts) or not is_poll_window(ts):
            return
        await self.fetch_task()  # runs body once

    # --- helpers -------------------------------------------------------
    async def _post_report(self, snapshot: bool) -> None:
        png = await generate_report_png(DB_PATH, snapshot)
        chan = self.bot.get_channel(CHANNEL_ID)
        if isinstance(chan, discord.abc.Messageable):
            label = "Snapshot" if snapshot else "Final"
            await chan.send(
                file=discord.File(png, "war.png"),
                content=f"**{label}** `{now().ctime()}`",
            )

    async def _rollover(self) -> None:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO war_history SELECT * FROM current_war")
            await db.execute("DELETE FROM current_war")
            await db.commit()
        log.info("db_rollover_done")

    # --- boilerplate ---------------------------------------------------
    @fetch_task.before_loop
    async def before_loop(self) -> None:
        await self.bot.wait_until_ready()

    def cog_unload(self) -> None:
        self.fetch_task.cancel()
