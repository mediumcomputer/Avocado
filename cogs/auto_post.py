import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import asyncio
from cogs.clan_stats import ClanStats
import logging
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('auto_post')

class AutoPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channels = {}
        self.pacific_tz = ZoneInfo("America/Los_Angeles")
        self.stats_time = time(hour=2, minute=42, tzinfo=self.pacific_tz)
        self.reminder_time = time(hour=22, minute=0, tzinfo=self.pacific_tz)
        self.stats_task = self.schedule_stats.start()
        self.reminder_task = self.schedule_reminder.start()
        logger.info("AutoPost cog initialized")

    def cog_unload(self):
        self.stats_task.cancel()
        self.reminder_task.cancel()

    @tasks.loop(time=time(hour=2, minute=42, tzinfo=ZoneInfo("America/Los_Angeles")))
    async def schedule_stats(self):
        await self.post_clan_stats()

    @tasks.loop(time=time(hour=22, minute=0, tzinfo=ZoneInfo("America/Los_Angeles")))
    async def schedule_reminder(self):
        await self.post_reminder()

    async def post_clan_stats(self):
        now = datetime.now(self.pacific_tz)
        yesterday = now - timedelta(days=1)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        report_day = day_names[yesterday.weekday()]

        if report_day not in ["Thursday", "Friday", "Saturday", "Sunday"]:
            logger.info(f"Skipping clan stats post for {report_day}")
            return

        logger.info(f"Posting clan stats for {report_day} at {now}")
        clan_stats_cog = self.bot.get_cog('ClanStats')
        if clan_stats_cog:
            image_buffer = clan_stats_cog.generate_clan_stats_image()
            for server_id, channel_id in self.target_channels.items():
                channel = self.bot.get_channel(channel_id)
                if channel:
                    message = f"{report_day} Night Clan Stats Update:"
                    await channel.send(message,
                                       file=discord.File(fp=image_buffer, filename='clan_stats.png'))
                    logger.info(f"Clan stats posted successfully in server {server_id}, channel {channel_id}")
                else:
                    logger.error(f"Channel {channel_id} not found in server {server_id}")
        else:
            logger.error("ClanStats cog not found")
            for channel_id in self.target_channels.values():
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send("Error: ClanStats cog not found.")

    async def post_reminder(self):
        now = datetime.now(self.pacific_tz)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day = day_names[now.weekday()]

        if current_day not in ["Monday", "Tuesday", "Wednesday"]:
            return  # No reminder on other days

        logger.info(f"Posting reminder for {current_day} at {now}")
        for server_id, channel_id in self.target_channels.items():
            channel = self.bot.get_channel(channel_id)
            if channel:
                message = (f"Skipping clan stats post for {current_day} because it's a training day. "
                           f"Don't forget to try and improve your decks at least once before the next war!")
                await channel.send(message)
                logger.info(f"Reminder posted successfully in server {server_id}, channel {channel_id}")
            else:
                logger.error(f"Channel {channel_id} not found in server {server_id}")

    @commands.command(name='set_autopost_channel')
    @commands.has_permissions(administrator=True)
    async def set_autopost_channel(self, ctx, channel: discord.TextChannel):
        self.target_channels[ctx.guild.id] = channel.id
        await ctx.send(f"Auto-post channel set to {channel.mention}\n\n"
                       f"Clan stats will be posted automatically at {self.stats_time.strftime('%I:%M %p')} Pacific Time "
                       f"on Thursday, Friday, Saturday, and Sunday nights.\n"
                       f"Reminders to work on War Decks will be posted at {self.reminder_time.strftime('%I:%M %p')} Pacific Time "
                       f"on Monday, Tuesday, and Wednesday nights.")
        logger.info(f"Auto-post channel set for server {ctx.guild.id}")

    @set_autopost_channel.error
    async def set_autopost_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need administrator permissions to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify a channel: !set_autopost_channel #channel-name")
        else:
            await ctx.send("An error occurred while setting the auto-post channel.")
            logger.error(f"Error in set_autopost_channel: {error}")

    @commands.command(name='remove_autopost_channel')
    @commands.has_permissions(administrator=True)
    async def remove_autopost_channel(self, ctx):
        if ctx.guild.id in self.target_channels:
            del self.target_channels[ctx.guild.id]
            await ctx.send("Auto-post channel removed for this server.")
            logger.info(f"Auto-post channel removed for server {ctx.guild.id}")
        else:
            await ctx.send("No auto-post channel was set for this server.")

async def setup(bot):
    logger.info("Setting up AutoPost cog")
    await bot.add_cog(AutoPost(bot))
    logger.info("AutoPost cog setup complete")