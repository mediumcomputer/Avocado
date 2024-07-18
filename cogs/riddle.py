import discord
from discord.ext import commands, tasks
import random
import asyncio
import logging
from datetime import datetime, time, timedelta
import pytz
import pandas as pd
import io
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('riddle_cog')

class RiddleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.riddle_channels = {}
        self.current_riddles = {}
        self.riddle_answers = {}
        self.user_scores = {}
        self.riddle_solved = {}
        self.test_riddles = {}
        self.test_user_scores = {}
        self.test_riddle_solved = {}
        self.riddle_task = None
        self.answer_task = None
        self.reset_task = None
        logger.info("RiddleCog initialized")

    @commands.command(name='riddle')
    async def set_riddle_channel(self, ctx):
        channel_id = ctx.channel.id
        self.riddle_channels[channel_id] = ctx.channel
        self.user_scores[channel_id] = {}
        self.test_user_scores[channel_id] = {}

        if not self.riddle_task:
            self.riddle_task = self.bot.loop.create_task(self.post_riddles())
        if not self.answer_task:
            self.answer_task = self.bot.loop.create_task(self.post_answers())
        if not self.reset_task:
            self.reset_task = self.bot.loop.create_task(self.reset_scores())

        await ctx.send("Riddles will now be posted in this channel every night at 6 PM.")
        logger.info(f"Riddles enabled in channel {channel_id}")

    @commands.command(name='riddletest')
    async def riddle_test(self, ctx):
        channel_id = ctx.channel.id
        test_riddle = self.generate_riddle()
        self.test_riddles[channel_id] = test_riddle
        self.test_riddle_solved[channel_id] = False
        if channel_id not in self.test_user_scores:
            self.test_user_scores[channel_id] = {}
        await ctx.send(f"Test Riddle: {test_riddle['question']}")

    @commands.command(name='riddleanswer')
    async def riddle_answer(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.test_riddles:
            await ctx.send(f"The answer to the test riddle is: {self.test_riddles[channel_id]['answer']}")
        elif channel_id in self.current_riddles:
            await ctx.send(f"The answer to the current riddle is: {self.riddle_answers[channel_id]}")
        else:
            await ctx.send("There is no active riddle in this channel.")

    @commands.command(name='riddlereset')
    async def riddle_reset(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.user_scores:
            await self.post_score_table(channel_id, self.user_scores[channel_id], "Regular Riddle", is_test=False)
            self.user_scores[channel_id] = {}
            await ctx.send("Regular riddle scores have been reset.")
        else:
            await ctx.send("There are no riddle scores to reset in this channel.")

    @commands.command(name='riddletestreset')
    async def riddle_test_reset(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.test_user_scores:
            await self.post_score_table(channel_id, self.test_user_scores[channel_id], "Test Riddle", is_test=True)
            self.test_user_scores[channel_id] = {}
            await ctx.send("Test riddle scores have been reset.")
        else:
            self.test_user_scores[channel_id] = {}
            await ctx.send("Test riddle scores have been initialized.")

    @commands.command(name='riddlestats')
    async def riddle_stats(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.user_scores:
            await self.post_score_table(channel_id, self.user_scores[channel_id], "Regular Riddle", is_test=False)
        else:
            await ctx.send("There are no regular riddle scores to display in this channel.")

    @commands.command(name='riddleteststats')
    async def riddle_test_stats(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.test_user_scores:
            await self.post_score_table(channel_id, self.test_user_scores[channel_id], "Test Riddle", is_test=True)
        else:
            await ctx.send("There are no test riddle scores to display in this channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        channel_id = message.channel.id
        content_lower = message.content.lower()

        if content_lower.startswith('riddle '):
            answer_attempt = content_lower[7:].strip()
            if channel_id in self.current_riddles and not self.riddle_solved[channel_id]:
                if answer_attempt == self.riddle_answers[channel_id].lower():
                    self.riddle_solved[channel_id] = True
                    self.user_scores[channel_id][message.author.name] = self.user_scores[channel_id].get(message.author.name, 0) + 100
                    await message.channel.send(f"🎉 Congratulations, {message.author.name}! You've solved the riddle and earned 100 points!")
                else:
                    await message.channel.send("Sorry, that's not the correct answer. Try again!")
            elif channel_id in self.test_riddles and not self.test_riddle_solved[channel_id]:
                if answer_attempt == self.test_riddles[channel_id]['answer'].lower():
                    self.test_riddle_solved[channel_id] = True
                    self.test_user_scores[channel_id][message.author.name] = self.test_user_scores[channel_id].get(message.author.name, 0) + 100
                    await message.channel.send(f"🎉 Correct! {message.author.name}, you've solved the test riddle and earned 100 points!")
                else:
                    await message.channel.send("Sorry, that's not the correct answer. Try again!")
            else:
                await message.channel.send("There is no active riddle in this channel.")

    async def post_score_table(self, channel_id, scores, title_prefix, is_test=False):
        if not scores:
            await self.riddle_channels[channel_id].send(f"No {title_prefix.lower()} scores to display.")
            return

        df = pd.DataFrame(list(scores.items()), columns=['User', 'Points'])
        df = df.sort_values('Points', ascending=False)
        df = df.reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis('off')
        table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 1.5)

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(color='white')
            elif row % 2:
                cell.set_facecolor('#f0f0f0')
            else:
                cell.set_facecolor('white')

        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_string = f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"

        title = f"{'Test ' if is_test else ''}Food Riddle Scores for the week of {week_string}"
        plt.title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)

        await self.riddle_channels[channel_id].send(f"Here are the {title_prefix.lower()} scores:", file=discord.File(fp=buffer, filename='riddle_scores.png'))

    def generate_riddle(self):
        riddles = [
            {"question": "I'm a card that splits in three, a wooden surprise for all to see. What am I?",
             "answer": "Goblin Barrel"},
            {
                "question": "I'm red and round, often mistaken for a fruit. In Clash Royale, I explode to boot. What am I?",
                "answer": "Bomb Tower"},
            {"question": "I split in three, a wooden surprise for all to see. What am I?", "answer": "Goblin Barrel"},
            {"question": "Red and round, I explode in battle without a sound. What am I?", "answer": "Bomb Tower"},
            {"question": "We fly high, breathing fire from the sky. Our bony form is quite a surprise. What are we?",
             "answer": "Skeleton Dragons"},
            {"question": "I shoot and roll, not a tower but on patrol. What am I?", "answer": "Cannon Cart"},
            {"question": "My bolts chain and clear the way, shocking all who come to play. What am I?",
             "answer": "Lightning"},
            {"question": "We're three of a kind, chaos in our mind. What are we?", "answer": "Three Musketeers"},
            {"question": "Troops pop out at quite a rate, from this building they emanate. What am I?",
             "answer": "Goblin Hut"},
            {"question": "I clone with magic so fine, doubling troops in record time. What am I?", "answer": "Mirror"},
            {"question": "Invisible until I fight, my axe swings with ghostly might. What am I?",
             "answer": "Royal Ghost"},
            {"question": "I shrink foes down to size, making giants no bigger than flies. What am I?",
             "answer": "Poison"},
            {"question": "My arrows rain from above, dealing damage with no love. Who am I?", "answer": "Princess"},
            {"question": "Big and slow, with a hammer in tow. Who am I?", "answer": "Giant"},
            {"question": "Small and quick, our daggers are slick. In numbers we thrive. What are we?",
             "answer": "Skeleton Army"},
            {"question": "I make your troops move quick on their feet. What spell am I?", "answer": "Rage"},
            {"question": "Arrows fly from up above, this building's tough and shows no love. What am I?",
             "answer": "X-Bow"},
            {"question": "I heal others in record time, my aura is simply divine. Who am I?",
             "answer": "Battle Healer"},
            {"question": "I slow troops in my icy domain. What spell am I?", "answer": "Freeze"},
            {"question": "My rockets always find their mark, destroying towers after dark. What am I?",
             "answer": "Rocket"},
            {"question": "My hammer glows with electric might, shocking all in sight. Who am I?",
             "answer": "Electro Giant"},
            {"question": "I drill and spit goblins on the scene. What building am I?", "answer": "Goblin Drill"},
            {"question": "I push troops back super fast, a spell that's sure to last. What am I?", "answer": "The Log"},
            {"question": "My barrel roll is sure to impress, leaving defenses in a mess. What troop am I?",
             "answer": "Barbarian Barrel"},
            {"question": "Bats fly out when I join the fight, spreading terror in the night. Who am I?",
             "answer": "Night Witch"},
            {"question": "I generate elixir for your team, a building of which players dream. What am I?",
             "answer": "Elixir Collector"},
            {"question": "My fireworks light up the sky, making opponents want to cry. Who am I?",
             "answer": "Firecracker"},
            {"question": "I duplicate troops in a flash, causing havoc in a clash. What spell am I?",
             "answer": "Clone"},
            {"question": "My punch sends troops flying far, a legendary card that's up to par. Who am I?",
             "answer": "Mega Knight"},
            {"question": "With my bow, I shoot through all, my arrows never fall. Who am I?", "answer": "Magic Archer"},
            {"question": "I lob shells over walls with ease, a building that's sure to please. What am I?",
             "answer": "Mortar"},
            {"question": "I surround troops with rings of light, a spell that's quite a sight. What am I?",
             "answer": "Zap"},
            {"question": "My electric attacks make foes sizzle, opponents I'll surely frizzle. Who am I?",
             "answer": "Electro Wizard"},
            {"question": "I melt on scene, a frosty dream. What card am I?", "answer": "Ice Golem"},
            {"question": "Fire spirits I spawn with glee, a hot building, don't you see? What am I?",
             "answer": "Furnace"},
            {"question": "In golden armor, I shine bright, a champion in every fight. Who am I?",
             "answer": "Royal Champion"},
            {"question": "We rain down like rain, a spell causing pain. What are we?", "answer": "Arrows"},
            {"question": "A flying beast with quite some might, I soar above the frenzied fight. Who am I?",
             "answer": "Mega Minion"},
            {"question": "My sword glows in the night, striking fear with all my might. Who am I?", "answer": "Pekka"},
            {"question": "Hidden until I strike, my coils are electric-like. What building am I?", "answer": "Tesla"},
            {"question": "I swirl and twirl, troops I unfurl. What spell am I?", "answer": "Tornado"},
            {"question": "Quick as a flash, with a daring dash. Who am I?", "answer": "Bandit"},
            {"question": "I split when destroyed, my foes annoyed. What card am I?", "answer": "Elixir Golem"},
            {"question": "My beam grows stronger by the second, defenses fall when I'm reckoned. What building am I?",
             "answer": "Inferno Tower"},
            {"question": "With my hook, I make troops dance, giving your push a second chance. Who am I?",
             "answer": "Fisherman"},
            {"question": "I burn oh so bright, setting the arena alight. What spell am I?", "answer": "Fireball"},
            {"question": "I fly and split, my pups commit. What legendary am I?", "answer": "Lava Hound"},
            {"question": "My shot is true, piercing through. Who am I?", "answer": "Musketeer"},
            {"question": "Explosions are my middle name, destroying swarms is my game. What building am I?",
             "answer": "Bomb Tower"},
            {"question": "I spawn skeletons in a row, a haunting spell, don't you know. What am I?",
             "answer": "Graveyard"},
            {"question": "Small but mighty, my sword glows brightly. Who am I?", "answer": "Mini Pekka"},
            {"question": "I ride and bind, leaving foes behind. Who am I?", "answer": "Ram Rider"},
            {"question": "Skeletons pop out when I fall, a spawner building, that's my call. What am I?",
             "answer": "Tombstone"},
            {"question": "My axe flies true, cutting foes in two. Who am I?", "answer": "Executioner"},
            {"question": "I damage over time, a toxic spell in its prime. What am I?", "answer": "Poison"},
            {"question": "My cannon's range is quite immense, a giant threat to any defense. Who am I?",
             "answer": "Royal Giant"},
            {"question": "Quick and nimble, my blowgun's simple. Who am I?", "answer": "Dart Goblin"},
            {"question": "I pump out elixir, making your push quicker. What building am I?",
             "answer": "Elixir Collector"},
            {"question": "I shake buildings to the ground, a rumbling spell I've been found. What am I?",
             "answer": "Earthquake"},
            {"question": "My axe spins with might, clearing swarms left and right. Who am I?", "answer": "Valkyrie"},
            {"question": "I soar in the sky, my propellers whir by. What card am I?", "answer": "Flying Machine"},
            {"question": "Cannonballs I shoot with pride, a classic defense for your side. What building am I?",
             "answer": "Cannon"},
            {"question": "How many battle days are there in a Clash Royale clan war?", "answer": "4"},
            {"question": "In what year was Clash Royale first released?", "answer": "2016"},
            {"question": "How many cards are in a standard Clash Royale deck?", "answer": "8"},
            {"question": "What's the maximum level a card can reach in Clash Royale?", "answer": "14"},
            {"question": "How many elixir bars does a player have at the start of a match?", "answer": "10"},
            {"question": "What's the name of the floating arena in Clash Royale?", "answer": "Legendary Arena"},
            {"question": "How many trophies do you need to reach Legendary Arena?", "answer": "5000"},
            {"question": "What's the maximum number of cards you can request from your clan?", "answer": "40"},
            {"question": "How many members can a Clash Royale clan have at maximum?", "answer": "50"},
            {"question": "What's the name of the currency used to upgrade cards?", "answer": "Gold"},
            {"question": "How many elixir does it cost to deploy a Goblin Barrel?", "answer": "3"},
            {"question": "What color is the King's crown in Clash Royale?", "answer": "Blue"},
            {"question": "How many Princess Towers are there on each side of the arena?", "answer": "2"},
            {"question": "What vegetable is the most fun to be around?", "answer": "Fungi"},
            {"question": "What is the wealthiest nut?", "answer": "Cashew"},
            {"question": "You cut me, chop me, dice me, and cry over me. What am I?", "answer": "Onion"},
            {"question": "What do golfers like to drink?", "answer": "Tee"},
            {"question": "What kind of food do mummies prefer?", "answer": "Wraps"},
            {"question": "What do you call a fake noodle?", "answer": "Impasta"},
            {"question": "What do you call cheese that isn't yours?", "answer": "Nacho cheese"},
            {"question": "What kind of egg did the evil chicken lay?", "answer": "Deviled eggs"},
            {"question": "What do you call a sad fruit?", "answer": "Blueberry"},
            {"question": "Why did the tomato blush?", "answer": "It saw the salad dressing"},
            {"question": "What do you call a cheese that's not yours?", "answer": "Nacho cheese"},
            {"question": "Why don't eggs tell jokes?", "answer": "They'd crack each other up"},
            {"question": "What do you call a fake pasta?", "answer": "An impasta"},
            {"question": "Why did the cookie go to the doctor?", "answer": "It was feeling crumbly"},
            {"question": "What do you call a sleeping bull?", "answer": "A bulldozer"},
            {"question": "Why don't oysters donate to charity?", "answer": "Because they're shellfish"},
            {"question": "What do you call a French cheese?", "answer": "Brieyoncé"},
            {"question": "Why did the banana go to the doctor?", "answer": "It wasn't peeling well"},
            {"question": "What do you call a fake stone in Ireland?", "answer": "A sham rock"},
            {"question": "Why don't eggs tell jokes?", "answer": "They'd crack each other up"},
            {"question": "What do you call a parade of rabbits hopping backwards?", "answer": "A receding hare-line"},
            {"question": "Why did the pizza maker go bankrupt?", "answer": "He ran out of dough"},
            {"question": "What do you get when you cross a snowman with a vampire?", "answer": "Frostbite"},
            {"question": "Why don't scientists trust atoms?", "answer": "Because they make up everything"},
            {"question": "What do you call a bear with no teeth?", "answer": "A gummy bear"},
            {"question": "Why don't skeletons fight each other?", "answer": "They don't have the guts"},
            {"question": "What do you call a boomerang that doesn't come back?", "answer": "A stick"},
            {"question": "Why don't scientists trust atoms?", "answer": "Because they make up everything"},
            {"question": "What's orange and sounds like a parrot?", "answer": "A carrot"},
            {"question": "Why did the scarecrow win an award?", "answer": "He was outstanding in his field"},
            {"question": "What do you call a fake noodle?", "answer": "An impasta"},
            {"question": "Why don't eggs tell jokes?", "answer": "They'd crack each other up"}
        ]
        return random.choice(riddles)

    async def post_riddles(self):
        while True:
            now = datetime.now(pytz.utc)
            target_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if now > target_time:
                target_time += timedelta(days=1)
            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            for channel_id, channel in self.riddle_channels.items():
                riddle = self.generate_riddle()
                self.current_riddles[channel_id] = riddle['question']
                self.riddle_answers[channel_id] = riddle['answer']
                self.riddle_solved[channel_id] = False
                await channel.send(f"🧩 Tonight's riddle: {riddle['question']}")
                logger.info(f"Posted riddle in channel {channel_id}")

    async def post_answers(self):
        while True:
            now = datetime.now(pytz.utc)
            target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if now > target_time:
                target_time += timedelta(days=1)
            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            for channel_id, channel in self.riddle_channels.items():
                if channel_id in self.riddle_answers:
                    answer = self.riddle_answers[channel_id]
                    if self.riddle_solved[channel_id]:
                        solver = next((user for user, score in self.user_scores.get(channel_id, {}).items() if score > 0), None)
                        await channel.send(f"The answer to last night's riddle was: {answer}. Congratulations to {solver} for solving it!")
                    else:
                        await channel.send(f"The answer to last night's riddle was: {answer}. Nobody solved it this time!")
                    logger.info(f"Posted answer in channel {channel_id}")

    async def reset_scores(self):
        while True:
            now = datetime.now(pytz.utc)
            target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
            if now.weekday() != 0:
                target_time += timedelta(days=(7 - now.weekday()))
            if now > target_time:
                target_time += timedelta(weeks=1)
            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            for channel_id in self.riddle_channels:
                if channel_id in self.user_scores:
                    await self.post_score_table(channel_id, self.user_scores[channel_id], "Regular Riddle", is_test=False)
                    self.user_scores[channel_id] = {}
                if channel_id in self.test_user_scores:
                    await self.post_score_table(channel_id, self.test_user_scores[channel_id], "Test Riddle", is_test=True)
                    self.test_user_scores[channel_id] = {}
            logger.info("Reset all user scores")

async def setup(bot):
    logger.info("Setting up RiddleCog")
    await bot.add_cog(RiddleCog(bot))
    logger.info("RiddleCog setup complete")