from __future__ import annotations

import datetime as dt
import logging

import discord
from discord.ext import commands
from zoneinfo import ZoneInfo

from avocado_bot.cogs.report import generate_report_png
from avocado_bot.cogs.war_tracker import DB_PATH, WarTracker

PST = ZoneInfo("America/Los_Angeles")
log = logging.getLogger("war_commands")


class WarCommands(commands.Cog):
    """User-facing commands: !warstats, !warrefresh."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ───── !warstats ──────────────────────────────────────────
    @commands.command(name="warstats")
    async def warstats_cmd(self, ctx: commands.Context):
        await self._send_report(ctx.channel)

    # ───── !warrefresh ───────────────────────────────────────
    @commands.command(name="warrefresh")
    async def warrefresh_cmd(self, ctx: commands.Context):
        tracker: WarTracker = self.bot.get_cog("WarTracker")  # type: ignore
        await tracker.poll_once()
        await ctx.send("🔄  Data refreshed; now run !warstats.")

    # ───── helper ────────────────────────────────────────────
    async def _send_report(self, channel: discord.abc.Messageable):
        placeholder = await channel.send(
            "🛠️  Battling with data to create our war stats image. Won't be long…"
        )
        png = await generate_report_png(DB_PATH, snapshot=True)
        if png is None:
            await placeholder.edit(
                content="⚠️  No war data yet. Wait for the next poll."
            )
            return
        ts = dt.datetime.now(tz=PST).strftime("%b %d %Y %H:%M PST")
        await placeholder.edit(
            content=f"**War stats snapshot** `{ts}`",
            attachments=[discord.File(png, "war_stats.png")],
        )
        log.info("warstats_sent")


async def setup(bot: commands.Bot):
    await bot.add_cog(WarCommands(bot))
