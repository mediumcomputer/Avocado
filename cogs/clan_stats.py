import discord
from discord.ext import commands
import asyncio
import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('clan_stats')

API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjY5ZGJmZjE3LTYzYTEtNDc2ZS04NzIwLTI0ZTc3Y2MzYTZmMSIsImlhdCI6MTcyMDg0NTQwOSwic3ViIjoiZGV2ZWxvcGVyLzA3MTk0ODRkLTJjNzYtMDE3NC1lZWMwLTU5OWZkOWQyNDVhNSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI1NC4yMTUuNjAuMTkxIiwiNjcuMTg4LjExMy4yMDciLCIyMy45My40OS4xMDEiXSwidHlwZSI6ImNsaWVudCJ9XX0.u2bpwpwJ0chDsoTJ3mPPjq7CNiue1G-QTHF4YdxB1E0na8w7ZPZ8rqKjofwWqoRma9AYb0ZzqQN2LhNK-vAqYg'
CLAN_TAG = '%2389YU9VP'

class ClanStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ClanStats cog initialized")

    @commands.command(name='clanstats')
    async def generate_clan_stats(self, ctx):
        logger.info(f"Clanstats command invoked by {ctx.author}")
        await ctx.send("Generating clan statistics image. Please wait...")
        image_buffer = self.generate_clan_stats_image()
        await ctx.send(file=discord.File(fp=image_buffer, filename='clan_stats.png'))
        logger.info("Clanstats command completed")

    def generate_clan_stats_image(self):
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Accept': 'application/json'
        }

        clan_url = f'https://api.clashroyale.com/v1/clans/{CLAN_TAG}'
        clan_response = requests.get(clan_url, headers=headers)
        clan_data = clan_response.json()

        war_url = f'https://api.clashroyale.com/v1/clans/{CLAN_TAG}/currentriverrace'
        war_response = requests.get(war_url, headers=headers)
        war_data = war_response.json()

        war_info = {}
        for participant in war_data['clan']['participants']:
            player_tag = participant['tag']
            decks_used = participant.get('decksUsedToday', 0)
            war_info[player_tag] = {
                'decksRemaining': 4 - decks_used if decks_used > 0 else "Not used",
                'score': participant.get('fame', 0)
            }

        player_data = []

        for member in clan_data['memberList']:
            player_tag = member['tag']
            player_name = member['name']
            donations = member['donations']
            role = member['role'].capitalize()

            war_decks_remaining = war_info.get(player_tag, {}).get('decksRemaining', "Not used")
            war_score = war_info.get(player_tag, {}).get('score', 0)

            player_data.append({
                'Name': player_name,
                'Role': role,
                'Donations': donations,
                'Battles Left': war_decks_remaining,
                'Score': war_score
            })

        df = pd.DataFrame(player_data)
        df = df.sort_values('Score', ascending=False)
        df = df.reset_index(drop=True)

        max_donations_row = df['Donations'].idxmax()
        max_donations_member = df[~df['Role'].isin(['Leader', 'Co-leader'])]['Donations'].idxmax()

        fig, ax = plt.subplots(figsize=(4, 4.5))
        ax.axis('off')
        table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        bold_font = FontProperties(weight='bold')
        table.scale(1, 1.1)
        table.auto_set_column_width(col=list(range(len(df.columns))))

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(fontproperties=bold_font)
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(color='white')
            elif row - 1 == max_donations_row:
                cell.set_facecolor('#FFFF00')  # Yellow highlight for overall highest donations
            elif row - 1 == max_donations_member:
                cell.set_facecolor('#FFA500')  # Orange highlight for highest donations among non-leaders/co-leaders
            elif row % 2:
                cell.set_facecolor('#f0f0f0')
            else:
                cell.set_facecolor('white')

        plt.tight_layout()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', pad_inches=0.05)
        buffer.seek(0)
        plt.close(fig)

        return buffer

async def setup(bot):
    logger.info("Setting up ClanStats cog")
    await bot.add_cog(ClanStats(bot))
    logger.info("ClanStats cog setup complete")