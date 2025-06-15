from __future__ import annotations
import asyncio, logging, time as _t
from datetime import datetime as dt, timedelta
from typing import Dict

import discord
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo

from avocado_bot.cogs.riddle_utils import (
    State, PST, next_seconds, random_riddle, score_png
)

log = logging.getLogger("riddle")

# ─────────────────────────── cog
class RiddleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot=bot
        self.states: Dict[int, State] = {}  # chan_id -> State
        self.daily_riddle.start(); self.daily_answer.start(); self.weekly_reset.start(); self.cleanup_tests.start()

    # ---------- command group
    @commands.group(invoke_without_command=True, name="riddle")
    async def riddle(self, ctx: commands.Context): await ctx.send_help(ctx.command)

    @riddle.command(name="enable")
    async def enable(self, ctx): self.states.setdefault(ctx.channel.id, State(ctx.channel.id)); await ctx.send("🧩 Daily riddles enabled (6 PM PST).")

    @riddle.command(name="stats")
    async def stats(self, ctx):
        st=self.states.get(ctx.channel.id); buf=score_png(list(st.points.items()) if st else [])
        await ctx.send(file=discord.File(buf,"riddle_stats.png"))

    @riddle.command(name="reset")  # manual season reset
    async def reset(self, ctx):
        st=self.states.get(ctx.channel.id); st.points.clear() if st else None; await ctx.send("Scores reset.")

    # ---- TEST sub-commands
    @riddle.command(name="test")
    async def test(self, ctx):
        st=self.states.setdefault(ctx.channel.id, State(ctx.channel.id))
        q,a=random_riddle(); st.question,st.answer,st.solved=q,a,False
        await ctx.send(f"⚔️ Test Riddle:\n> {q}\n*(expires in 3 h, no season points)*")
        # store expiry ts
        st.test_pts.clear(); st.test_pts["__expiry__"]=(int(_t.time())+10800,0)

    @riddle.command(name="teststats")
    async def teststats(self, ctx):
        st=self.states.get(ctx.channel.id); rows=[(k,v[1]) for k,v in st.test_pts.items() if k!="__expiry__"] if st else []
        buf=score_png(rows); await ctx.send(file=discord.File(buf,"test_stats.png"))

    @riddle.command(name="testreset")
    async def testreset(self, ctx):
        st=self.states.get(ctx.channel.id); st.test_pts.clear() if st else None; await ctx.send("Test scores cleared.")

    # ---------- listener for guesses
    @commands.Cog.listener()
    async def on_message(self, m: discord.Message):
        if m.author.bot or not m.content.lower().startswith("riddle "): return
        st=self.states.get(m.channel.id); guess=m.content[7:].strip().lower()
        # normal
        if st and not st.solved and st.answer and guess==st.answer.lower():
            st.solved=True; st.points[m.author.display_name]=st.points.get(m.author.display_name,0)+100
            await m.channel.send(f"🎉 **{m.author.display_name}** cracked it! +100 pts"); return
        # test
        if st and "__expiry__" in st.test_pts and _t.time()<st.test_pts["__expiry__"][0]:
            if guess==st.answer.lower():
                pts=st.test_pts.get(m.author.display_name,(0,0))[1]+100
                st.test_pts[m.author.display_name]=(0,pts); await m.channel.send(f"🏅 Test solve by **{m.author.display_name}** (+100)"); st.solved=True

    # ---------- scheduled tasks
    @tasks.loop(hours=24)
    async def daily_riddle(self):
        for st in self.states.values():
            q,a=random_riddle(); st.question,st.answer,st.solved=q,a,False
            chan=self.bot.get_channel(st.chan_id)
            if chan: await chan.send(f"🧩 Tonight's riddle:\n> {q}")

    @daily_riddle.before_loop
    async def _wait_riddle(self): await self.bot.wait_until_ready(); await asyncio.sleep(next_seconds(18,0))

    @tasks.loop(hours=24)
    async def daily_answer(self):
        for st in self.states.values():
            if not st.answer: continue
            msg="✅ Solved!" if st.solved else "❌ Nobody solved it."
            chan=self.bot.get_channel(st.chan_id)
            if chan: await chan.send(f"🔎 Answer: **{st.answer}** — {msg}")
            st.answer=""

    @daily_answer.before_loop
    async def _wait_ans(self): await self.bot.wait_until_ready(); await asyncio.sleep(next_seconds(6,0))

    @tasks.loop(hours=24)
    async def weekly_reset(self):
        if dt.now(tz=PST).weekday()!=0: return
        for st in self.states.values():
            if not st.points: continue
            buf=score_png(list(st.points.items())); chan=self.bot.get_channel(st.chan_id)
            if chan: await chan.send("🏆 Weekly leaderboard:", file=discord.File(buf,"weekly_scores.png"))
            st.points.clear()

    @tasks.loop(minutes=30)
    async def cleanup_tests(self):
        now=int(_t.time())
        for st in self.states.values():
            if "__expiry__" in st.test_pts and now>st.test_pts["__expiry__"][0]:
                st.test_pts.clear(); log.info("test_pts_expired",extra={"chan":st.chan_id})

async def setup(bot): await bot.add_cog(RiddleCog(bot))
