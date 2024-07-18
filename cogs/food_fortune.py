import discord
from discord.ext import commands, tasks
import random
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('food_fortune')

class FoodFortune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fortune_channels = {}
        self.fortune_task = None
        logger.info("FoodFortune cog initialized")

    def cog_unload(self):
        if self.fortune_task:
            self.fortune_task.cancel()
        logger.info("FoodFortune cog unloaded")

    @commands.command(name='foodfortune')
    async def set_food_fortune(self, ctx):
        if isinstance(ctx.channel, discord.GroupChannel) or isinstance(ctx.channel, discord.TextChannel):
            channel_id = ctx.channel.id
            self.fortune_channels[channel_id] = ctx.channel

            if not self.fortune_task or not self.fortune_task.is_running():
                self.fortune_task = self.bot.loop.create_task(self.post_fortunes())

            await ctx.send("Food fortunes will now be posted in this channel every 12 hours.")
            logger.info(f"Food fortunes enabled in channel {channel_id}")
        else:
            await ctx.send("This command can only be used in a group DM or server channel.")

    @commands.command(name='stopfortune')
    async def stop_food_fortune(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.fortune_channels:
            del self.fortune_channels[channel_id]
            await ctx.send("Food fortunes have been stopped for this channel.")
            logger.info(f"Food fortunes disabled in channel {channel_id}")
        else:
            await ctx.send("Food fortunes were not active in this channel.")

        if not self.fortune_channels and self.fortune_task:
            self.fortune_task.cancel()
            self.fortune_task = None
            logger.info("Fortune task cancelled as no active channels remain")

    async def post_fortunes(self):
        logger.info("Starting fortune posting task")
        while True:
            for channel in self.fortune_channels.values():
                fortune = self.generate_fortune()
                await channel.send(f"🥠 {fortune}")
                logger.info(f"Posted fortune in channel {channel.id}")
            await asyncio.sleep(43200)  # Wait for 12 hours

    def generate_fortune(self):
        fortunes = [
            "Your next battle will be as sour as unripe avocados. Prepare for a crushing defeat!",
            "Beware the upcoming clan war - your teammates will crumble like stale cookies.",
            "Your favorite card will be nerfed harder than overcooked pasta. Adapt or perish!",
            "A trophy-dropping spree is your future. Your rank will plummet like a fallen soufflé.",
            "Your next chest will contain nothing but common cards - as disappointing as a bland meal.",
            "Your elixir management will be as messy as a food fight in the coming matches.",
            "Expect your towers to fall faster than a house of cards made of crackers.",
            "Your strategy will be as half-baked as undercooked bread in the next tournament.",
            "Your clan's performance will be roasted harder than burned coffee beans.",
            "Your next legendary card will be as rare as a perfectly ripe avocado - nonexistent.",
            "Your win streak will end faster than ice cream melting on a hot day.",
            "Your deck will be as unbalanced as a wobbly table at a cheap restaurant.",
            "Your opponent's push will steamroll you like a rolling pin flattening dough.",
            "Your emote game will be as stale as week-old bread.",
            "Your card levels will be as low as the nutritional value of junk food.",
            "Your clan chat will be saltier than overseasoned French fries.",
            "Your next battle will leave a worse taste in your mouth than spoiled milk.",
            "Your trophy road rewards will be as disappointing as finding a hair in your soup.",
            "Your clan war performance will be roasted harder than coffee beans in an industrial oven.",
            "Your next losing streak will be longer than spaghetti in a pasta factory.",
            "Your next match will be as one-sided as a slice of bread.",
            "Your strategy will fall apart faster than a poorly made sandwich.",
            "Your card rotation will be as mixed up as a blindfolded chef's ingredients.",
            "Your next battle will be as messy as eating ribs without napkins.",
            "Your clan's reputation will sink like a rock in tomato soup.",
            "Your next update will bring changes as unwelcome as pineapple on pizza to some.",
            "Your next chest opening will be as anticlimactic as a failed soufflé.",
            "Your next battle will be harder to swallow than overcooked steak.",
            "Your next win will be as rare as a four-leaf clover in a field of cabbages.",
            "Your clan war deck will be as useful as a chocolate teapot.",
            "Your elixir leaks will be more frequent than a sieve trying to hold water.",
            "Your next meta deck will age like milk left out in the sun.",
            "Your card collection will grow slower than a bonsai tree.",
            "Your next challenge run will be as successful as a restaurant with one-star reviews.",
            "Your clan leader's strategy will be as clear as pea soup fog.",
            "Your tower's health will melt away faster than ice cream on a hot sidewalk.",
            "Your win condition will be as effective as a fork in a soup eating contest.",
            "Your next opponent will slice through your defenses like a hot knife through butter.",
            "Your clan's war day will be as coordinated as a food fight in a pitch-black room.",
            "Your next battle will be more one-sided than a pancake.",
            "Your emote choices will be as tasteless as unseasoned tofu.",
            "Your next chest will be as empty as a vegetarian's BBQ grill.",
            "Your card upgrade progress will move slower than molasses uphill in January.",
            "Your next match will be as balanced as a diet consisting only of candy.",
            "Your clan's trophy count will drop faster than a hot potato.",
            "Your next battle will be more painful than biting into a ghost pepper.",
            "Your strategies will be as effective as bringing a spoon to a knife fight.",
            "Your clan war preparations will be as organized as a food truck in a tornado.",
            "Your next losing streak will be longer than the line at a popular food truck.",
            "Your card levels will be lower than the chances of finding a golden ticket in a Wonka bar.",
            "Your next battle will be as chaotic as a kitchen with 10 novice chefs.",
            "Your clan's performance will leave a taste worse than burnt popcorn.",
            "Your emote spam will be as annoying as a mosquito at a picnic.",
            "Your next match will be as predictable as instant noodles.",
            "Your win rate will plummet faster than a soufflé in an earthquake.",
            "Your deck synergy will be as harmonious as oil and water.",
            "Your next chest will be as rewarding as an empty fortune cookie.",
            "Your clan war attacks will be as coordinated as a blindfolded relay race.",
            "Your trophy gain will be smaller than the tips at a bad restaurant.",
            "Your next battle will be as tense as overcooked spaghetti.",
            "Your card collection will grow slower than organic vegetables.",
            "Your clan chat will be more toxic than week-old sushi.",
            "Your next match will be as satisfying as sugar-free candy.",
            "Your elixir management will be leakier than a colander.",
            "Your strategy will backfire worse than microwaving fish in the office.",
            "Your next tournament run will be as successful as an ice cream truck in a blizzard.",
            "Your emote usage will be as excessive as sprinkles on a birthday cake.",
            "Your win condition will be as clear as murky soup.",
            "Your clan's leadership will be as stable as a Jenga tower on a rollercoaster.",
            "Your next battle will be more frustrating than trying to eat soup with a fork.",
            "Your card levels will be more imbalanced than a see-saw with an elephant and a mouse.",
            "Your clan war participation will be as low as the nutritional value of cotton candy.",
            "Your trophy count will yo-yo more than a crash dieter's weight."
            "Your next chest will be as golden as perfectly toasted bread!",
            "Your clan war performance will be as smooth as melted chocolate.",
            "Your next legendary card pull will be as satisfying as finding the last piece of pizza.",
            "Your elixir management will flow as smoothly as honey from the comb.",
            "Your strategy will be as well-balanced as a gourmet five-course meal.",
            "Your next battle will be a piece of cake - victory is assured!",
            "Your clan's teamwork will be as harmonious as a perfectly layered lasagna.",
            "Your emote game will be as zesty as a freshly squeezed lemon.",
            "Your next opponent will crumble like a cookie against your mighty deck.",
            "Your trophy count will rise like a perfectly baked soufflé.",
            "Your card collection will grow as abundantly as a well-tended vegetable garden.",
            "Your next win streak will be as long as a string of spaghetti.",
            "Your clan chat will be as sweet and supportive as a jar of homemade jam.",
            "Your next update will bring changes as welcome as ice cream on a hot day.",
            "Your defensive plays will be as impenetrable as the crust on a well-baked pie.",
            "Your next challenge run will be as successful as a Michelin-starred restaurant.",
            "Your card levels will skyrocket like popcorn in a hot pan.",
            "Your clan war deck will be as perfectly assembled as a gourmet sandwich.",
            "Your next battle will be more one-sided than a knife - in your favor!",
            "Your strategies will be as effective as using the right spice in a gourmet dish.",
            "Your next tournament run will be as hot as freshly baked cinnamon rolls.",
            "Your win condition will be as clear as crystal-clear spring water.",
            "Your clan's reputation will rise like bread dough on a warm day.",
            "Your next match will be as satisfying as a perfectly grilled steak.",
            "Your gameplay will be as smooth and creamy as the finest custard."

        ]
        return random.choice(fortunes)

async def setup(bot):
    logger.info("Setting up FoodFortune cog")
    await bot.add_cog(FoodFortune(bot))
    logger.info("FoodFortune cog setup complete")