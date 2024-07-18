import discord
from discord.ext import commands
import aiohttp
import os
import random
import logging
import urllib.parse
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('negstats')


class NegStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('CLASH_ROYALE_API_KEY')
        self.base_url = 'https://api.clashroyale.com/v1'
        if not self.api_key:
            logger.error("CLASH_ROYALE_API_KEY environment variable is not set!")
        else:
            logger.info("CLASH_ROYALE_API_KEY is set")
            logger.debug(f"API Key: {self.api_key[:5]}...{self.api_key[-5:]}")
        logger.info('NegStats cog initialized')

    def get_leadership_comment(self, role):
        leader_comments = [
            "Ah, a {0}. I'm sure your clan members tremble with... excitement?",
            "Oh, you're the {0}? That explains the state of your clan.",
            "A {0}, huh? I bet your speeches are as inspiring as your win rate.",
            "Being a {0} must be tough. Almost as tough as winning matches, right?",
            "The {0}! Your clan's very own Captain Mediocre, at your service.",
            "A {0} with those stats? Your clan must have very... unique standards.",
            "Wow, a {0}! I bet your strategy meetings are as thrilling as watching paint dry.",
            "The {0} has arrived! Time to lower everyone's expectations.",
            "A {0} who plays like you? Your clan must be a comedy club.",
            "Behold, the {0}! Master of losing with style.",
        ]
        return random.choice(leader_comments).format(role.lower())

    @commands.command()
    async def negstats(self, ctx, player_tag: str = None):
        logger.info(f'Negstats command invoked by {ctx.author} with player tag: {player_tag}')
        if player_tag is None:
            await ctx.send(
                "Oops! You forgot to include a player ID. The correct syntax is `!negstats <playerID>`. For example: `!negstats PPUQL8YC`. Don't worry, I'm sure forgetting things is a common occurrence for you.")
            logger.info('Negstats command called without player tag')
            return

        try:
            if not player_tag.startswith('#'):
                player_tag = f'#{player_tag}'

            encoded_tag = urllib.parse.quote(player_tag)
            url = f'{self.base_url}/players/{encoded_tag}'

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            }
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Headers: {headers}")

            async with aiohttp.ClientSession() as session:
                logger.debug("ClientSession created")
                async with session.get(url, headers=headers) as response:
                    logger.info(f'Received response with status code: {response.status}')
                    response_text = await response.text()
                    logger.debug(f'Response content: {response_text}')

                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f'Received data for player {player_tag}: {data}')

                        message = self.generate_neg_stats_message(data)
                        await ctx.send(message)
                    elif response.status == 404:
                        await ctx.send(f"Player with tag {player_tag} not found. Are you sure you didn't make that up?")
                    elif response.status == 403:
                        await ctx.send("Oops! It seems the API key is invalid. Blame the developer, not me.")
                    else:
                        await ctx.send(
                            f"Failed to fetch stats. The API responded with: {response.status}. Maybe it just doesn't like you?")

        except aiohttp.ClientError as e:
            logger.exception(f"Network error occurred: {str(e)}")
            await ctx.send("Looks like the internet is as unreliable as your gameplay. Try again later.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {str(e)}")
            await ctx.send("Something went wrong. Probably karma for all those battles you've lost.")
            logger.error(f"Full traceback: {traceback.format_exc()}")

    def generate_neg_stats_message(self, data):
        name = data.get('name', 'Unknown Player')
        trophies = data.get('trophies', 0)
        wins = data.get('wins', 0)
        losses = data.get('losses', 0)
        total_games = wins + losses
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        exp_level = data.get('expLevel', 0)
        max_trophies = data.get('bestTrophies', 0)
        cards_found = len(data.get('cards', []))
        total_donations = data.get('totalDonations', 0)
        war_day_wins = data.get('warDayWins', 0)

        messages = [
            f"Oh look, it's {name}'s stats. Brace yourself for mediocrity:\n",
            f"Trophies: {trophies}. I've seen training dummies with higher scores.",
            f"Win rate: {win_rate:.2f}%. Winning {wins} out of {total_games} games? My grandma could do better, and she doesn't even play.",
            f"Experience level: {exp_level}. All that experience and still playing like a beginner? Impressive.",
            f"Highest trophies: {max_trophies}. Let me guess, you reached that by accident?",
            f"Cards found: {cards_found}. Collecting cards is the only thing you're good at, huh?",
            f"Total donations: {total_donations}. Ah, so you're better at giving away cards than using them.",
            f"War day wins: {war_day_wins}. I'm sure your clan is thrilled with your... contributions.",
        ]

        # Add more specific insults based on stats
        if trophies < 2000:
            messages.append("With those trophies, you must be aiming for the 'Participation Award'.")
        elif trophies > 6000:
            messages.append("Impressive trophies! Did you buy that account, or just get really lucky?")

        if win_rate < 40:
            messages.append("Your win rate is so low, I'm starting to think you're trying to lose on purpose.")
        elif win_rate > 60:
            messages.append("Nice win rate! Must be all those battles against your little sister.")

        if exp_level < 10:
            messages.append("Your experience level suggests you're new. Your gameplay confirms it.")
        elif exp_level > 13:
            messages.append("High experience level, low skill level. Perfectly balanced.")

        if total_donations < 1000:
            messages.append("Your donation count is lower than your IQ. Impressive!")
        elif total_donations > 100000:
            messages.append("Wow, you donate a lot! Trying to compensate for something?")

        if war_day_wins < 10:
            messages.append("Your war day wins are so low, I bet your clan uses you as a scout... for the enemy.")
        elif war_day_wins > 100:
            messages.append("Lots of war day wins! I guess even a broken clock is right twice a day.")

        # Add clan-specific comment if available
        if 'clan' in data and data['clan']:
            clan_role = data['clan'].get('role', 'Member')
            messages.append(self.get_leadership_comment(clan_role))
        else:
            messages.append("No clan? I guess no one wanted to recruit you. Can't blame them, really.")

        # Randomly select 5-7 messages to include
        selected_messages = random.sample(messages, min(len(messages), random.randint(5, 7)))
        return "\n".join(selected_messages)


async def setup(bot):
    await bot.add_cog(NegStats(bot))
    logger.info('NegStats cog setup complete')