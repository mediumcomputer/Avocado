import discord
from discord.ext import commands
import asyncio
import logging
import os
import aiohttp

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('main')

TOKEN = 'MTI1NzE0MTcyNzc0Mzk3MTM5OQ.GOL6iy.yy7v0AbpyvopEdjSY1giz8O1Ha-80VEWKGL8fI'

intents = discord.Intents.all()  # Enable all intents

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

bot = MyBot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    await load_cogs()

async def load_cogs():
    cogs = ['cogs.clan_stats', 'cogs.claude_integration', 'cogs.Hello', 'cogs.auto_post', 'cogs.food_fortune', 'cogs.negstats', 'cogs.riddle', 'cogs.war_stats']
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f'Loaded {cog} successfully')
        except Exception as e:
            logger.error(f'Failed to load {cog}. Error: {str(e)}')
            logger.exception(e)  # This will print the full traceback

async def main():
    # Set the Clash Royale API key as an environment variable
    os.environ['CLASH_ROYALE_API_KEY'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjY5ZGJmZjE3LTYzYTEtNDc2ZS04NzIwLTI0ZTc3Y2MzYTZmMSIsImlhdCI6MTcyMDg0NTQwOSwic3ViIjoiZGV2ZWxvcGVyLzA3MTk0ODRkLTJjNzYtMDE3NC1lZWMwLTU5OWZkOWQyNDVhNSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI1NC4yMTUuNjAuMTkxIiwiNjcuMTg4LjExMy4yMDciLCIyMy45My40OS4xMDEiXSwidHlwZSI6ImNsaWVudCJ9XX0.u2bpwpwJ0chDsoTJ3mPPjq7CNiue1G-QTHF4YdxB1E0na8w7ZPZ8rqKjofwWqoRma9AYb0ZzqQN2LhNK-vAqYg'

    try:
        async with bot:
            await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"Error starting the bot: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    asyncio.run(main())