# AvocadoBot

A Discord bot for managing Clash Royale clan wars and riddle games.

## Features

### War Tracking
- Automated war stats collection
- Daily snapshots and final reports
- Historical data tracking
- Manual refresh command
- Color-coded performance reports

### Riddle System
- Daily riddles with point tracking
- Test battle mode
- Weekly leaderboards
- Per-channel state management
- Beautiful stat visualizations

## Setup

1. Clone the repository
2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r avocado_bot/requirements.txt
```

3. Configure environment:
```bash
cp avocado_bot/.env.example avocado_bot/.env
# Edit .env with your tokens and settings
```

4. Run the bot:
```bash
python -m avocado_bot.bot
```

## Docker Support

Build and run with Docker:
```bash
docker build -t avocado_bot .
docker run --env-file avocado_bot/.env avocado_bot
```

## Commands

### War Commands
- `!warstats` - Show current war stats
- `!warrefresh` - Manual data refresh

### Riddle Commands
- `!riddle enable` - Enable riddles in channel
- `!riddle stats` - Show season scores
- `!riddle test` - Start a test battle
- `!riddle teststats` - Show test scores

## Development

- Python 3.12+
- Uses asyncio and discord.py
- SQLite for data storage
- Matplotlib for visualizations

## License

MIT License - See LICENSE file
