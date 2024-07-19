API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjY5ZGJmZjE3LTYzYTEtNDc2ZS04NzIwLTI0ZTc3Y2MzYTZmMSIsImlhdCI6MTcyMDg0NTQwOSwic3ViIjoiZGV2ZWxvcGVyLzA3MTk0ODRkLTJjNzYtMDE3NC1lZWMwLTU5OWZkOWQyNDVhNSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI1NC4yMTUuNjAuMTkxIiwiNjcuMTg4LjExMy4yMDciLCIyMy45My40OS4xMDEiXSwidHlwZSI6ImNsaWVudCJ9XX0.u2bpwpwJ0chDsoTJ3mPPjq7CNiue1G-QTHF4YdxB1E0na8w7ZPZ8rqKjofwWqoRma9AYb0ZzqQN2LhNK-vAqYg'
CLAN_TAG = '%2389YU9VP'

thursday rules. promote everyone who has done all their war day battles and demote everyone who didnt use them by the end of the night.
import discord
from discord.ext import commands, tasks
import io
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import logging
from datetime import datetime, time, timedelta
import pytz

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('war_stats')

API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjY5ZGJmZjE3LTYzYTEtNDc2ZS04NzIwLTI0ZTc3Y2MzYTZmMSIsImlhdCI6MTcyMDg0NTQwOSwic3ViIjoiZGV2ZWxvcGVyLzA3MTk0ODRkLTJjNzYtMDE3NC1lZWMwLTU5OWZkOWQyNDVhNSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI1NC4yMTUuNjAuMTkxIiwiNjcuMTg4LjExMy4yMDciLCIyMy45My40OS4xMDEiXSwidHlwZSI6ImNsaWVudCJ9XX0.u2bpwpwJ0chDsoTJ3mPPjq7CNiue1G-QTHF4YdxB1E0na8w7ZPZ8rqKjofwWqoRma9AYb0ZzqQN2LhNK-vAqYg'
CLAN_TAG = '%2389YU9VP'

class WarStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.war_data = self.load_war_data()
        self.pacific_tz = pytz.timezone('US/Pacific')
        self.update_war_data.start()
        self.reset_war_data.start()
        logger.info("WarStats cog initialized")

    def cog_unload(self):
        self.update_war_data.cancel()
        self.reset_war_data.cancel()

    @tasks.loop(minutes=30)
    async def update_war_data(self):
        current_day = datetime.now(self.pacific_tz).weekday()
        if 3 <= current_day <= 6:  # Thursday to Sunday
            war_day = ['Thurs', 'Fri', 'Sat', 'Sun'][current_day - 3]
            await self.fetch_and_save_war_data(war_day)
            logger.info(f"War data updated for {war_day}")

    @tasks.loop(time=time(hour=0, minute=0, tzinfo=pytz.timezone('US/Pacific')))
    async def reset_war_data(self):
        if datetime.now(self.pacific_tz).weekday() == 1:  # Tuesday
            self.war_data = {}
            self.save_war_data()
            logger.info("War data reset on Tuesday")

    @update_war_data.before_loop
    @reset_war_data.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

    def load_war_data(self):
        try:
            with open('war_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_war_data(self):
        with open('war_data.json', 'w') as f:
            json.dump(self.war_data, f)

    async def fetch_and_save_war_data(self, war_day):
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Accept': 'application/json'
        }

        clan_url = f'https://api.clashroyale.com/v1/clans/{CLAN_TAG}'
        war_url = f'https://api.clashroyale.com/v1/clans/{CLAN_TAG}/currentriverrace'

        async with self.bot.session.get(clan_url, headers=headers) as clan_response:
            clan_data = await clan_response.json()

        async with self.bot.session.get(war_url, headers=headers) as war_response:
            war_data = await war_response.json()

        for member in clan_data['memberList']:
            player_tag = member['tag']
            war_info = next((p for p in war_data['clan']['participants'] if p['tag'] == player_tag), {})
            decks_used = war_info.get('decksUsedToday', 0)

            if player_tag not in self.war_data:
                self.war_data[player_tag] = {'Thurs': 'Not used', 'Fri': 'Not used', 'Sat': 'Not used', 'Sun': 'Not used'}

            # Update only the current day's data
            self.war_data[player_tag][war_day] = str(4 - decks_used) if decks_used > 0 else 'Not used'

        self.save_war_data()

    @commands.command(name='warstats')
    async def generate_war_stats(self, ctx):
        logger.info(f"Warstats command invoked by {ctx.author}")
        await ctx.send("Generating war statistics image. Please wait...")
        image_buffer = await self.generate_war_stats_image()
        await ctx.send(file=discord.File(fp=image_buffer, filename='war_stats.png'))
        logger.info("Warstats command completed")

    async def generate_war_stats_image(self):
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Accept': 'application/json'
        }

        clan_url = f'https://api.clashroyale.com/v1/clans/{CLAN_TAG}'
        war_url = f'https://api.clashroyale.com/v1/clans/{CLAN_TAG}/currentriverrace'

        async with self.bot.session.get(clan_url, headers=headers) as clan_response:
            clan_data = await clan_response.json()

        async with self.bot.session.get(war_url, headers=headers) as war_response:
            war_data = await war_response.json()

        player_data = []

        for member in clan_data['memberList']:
            player_tag = member['tag']
            player_name = member['name']
            donations = member['donations']
            role = member['role'].capitalize()

            war_info = next((p for p in war_data['clan']['participants'] if p['tag'] == player_tag), {})
            war_score = war_info.get('fame', 0)

            player_data.append({
                'Name': player_name,
                'Role': role,
                'Donations': donations,
                'Thurs': self.war_data.get(player_tag, {}).get('Thurs', 'Not used'),
                'Fri': self.war_data.get(player_tag, {}).get('Fri', 'Not used'),
                'Sat': self.war_data.get(player_tag, {}).get('Sat', 'Not used'),
                'Sun': self.war_data.get(player_tag, {}).get('Sun', 'Not used'),
                'Score': war_score
            })

        df = pd.DataFrame(player_data)
        df = df.sort_values('Score', ascending=False)
        df = df.reset_index(drop=True)

        max_donations_row = df['Donations'].idxmax()
        max_donations_leader_co = df[df['Role'].isin(['Leader', 'Co-leader'])]['Donations'].idxmax()

        fig, ax = plt.subplots(figsize=(8, 10))  # Increased figure size
        ax.axis('off')
        table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)  # Slightly increased font size
        bold_font = FontProperties(weight='bold')
        table.scale(1, 1.2)  # Increased row height
        table.auto_set_column_width(col=list(range(len(df.columns))))

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(fontproperties=bold_font)
                cell.set_facecolor('#4CAF50')
                cell.set_text_props(color='white')
            elif row - 1 == max_donations_row:
                cell.set_facecolor('#ADD8E6')  # Light blue for highest overall donations
            elif row - 1 == max_donations_leader_co:
                cell.set_facecolor('#72bcd4')  # Dark blue for highest leader/co-leader donations
            elif row % 2:
                cell.set_facecolor('#f0f0f0')
            else:
                cell.set_facecolor('white')

            if 3 <= col <= 6 and row > 0:  # War day columns
                cell_value = cell.get_text().get_text()
                if cell_value == 'Not used':
                    cell.set_facecolor('#FFCCCC')  # Light red
                elif cell_value in ['1', '2', '3']:
                    cell.set_facecolor('#FFCC99')  # Light orange

        plt.tight_layout(pad=0.4)  # Reduced padding
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)  # Adjusted margins

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
        buffer.seek(0)
        plt.close(fig)

        return buffer

async def setup(bot):
    async with bot.session.get("https://example.com") as response:
        if response.status == 200:
            logger.info("Internet connection verified")
    logger.info("Setting up WarStats cog")
    await bot.add_cog(WarStats(bot))
    logger.info("WarStats cog setup complete")
