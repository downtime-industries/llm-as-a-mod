# Discord Code of Conduct Bot

A Discord bot that uses an LLM to automatically evaluate Code of Conduct violations.

## Features

- Responds to ban requests by evaluating messages against the Code of Conduct
- Uses an LLM (via Groq API) to analyze message context
- Keeps the model warm in memory for efficient processing on Raspberry Pi
- Returns decision with action recommendation and reasoning

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file from the template:
   ```
   cp .env.template .env
   ```
4. Edit the `.env` file with your Discord token:
   ```
   DISCORD_TOKEN=your_discord_token_here
   ```

### Getting API Keys

- **Discord Token**: Create a bot application in the [Discord Developer Portal](https://discord.com/developers/applications) and get your token from the Bot tab.

### Adding the Bot to Your Server

1. Go to the Discord Developer Portal
2. Select your application
3. Go to OAuth2 > URL Generator
4. Under "Scopes" select "bot"
5. Under "Bot Permissions" select appropriate permissions (message reading, sending messages, banning members)
6. Use the generated URL to add the bot to your server

## Usage

1. Run the bot:
   ```
   python bot.py
   ```

2. In Discord, use the `!ban` command while replying to a message:
   ```
   !ban @username
   ```

The bot will analyze the message and surrounding context using the Code of Conduct template and return a recommendation.

## Code of Conduct Decisions

The bot will recommend one of three actions:
- **None**: No violation detected
- **Temp-mute**: Minor violation that warrants a temporary mute
- **Temp-ban**: Serious violation that warrants a temporary ban

Each decision includes a reason explaining the judgment.

## Running on Raspberry Pi

This bot is designed to be lightweight and efficient on a Raspberry Pi:
- The model is kept warm in memory to reduce startup time
- The Qwen-3 model can run efficiently on limited hardware
- The bot uses async functionality for responsive performance