#!/usr/bin/env python
import asyncio, logging, os, sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import configure_logging
from avocado_bot.cogs.war_commands import WarCommands  # new

load_dotenv(); configure_logging()
TOKEN = os.getenv("DISCORD_TOKEN")
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

@bot.event
async def on_ready():
    logging.getLogger(__name__).info("Logged in as %s", bot.user)

async def main():
    async with bot:
        from cogs.clash_api import ClashAPI
        from cogs.war_tracker import WarTracker
        from cogs.auto_post import AutoPost
        await bot.add_cog(ClashAPI(bot))
        await bot.add_cog(WarTracker(bot))
        await bot.add_cog(AutoPost(bot))
        await bot.add_cog(WarCommands(bot))  # new
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)