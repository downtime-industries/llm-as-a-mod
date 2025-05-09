# Discord Code of Conduct Moderation Bot

A Discord bot that uses LLMs to automatically evaluate Code of Conduct violations with minimal intervention.

## Features

- Responds to message reports with AI-powered moderation decisions
- Focuses only on extreme violations, avoiding false positives
- Evaluates messages in context for better decisions
- Uses Ollama to run models locally with minimal setup
- Returns decision with action recommendation and reasoning

## Setup

1. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Install Ollama**
   
   Follow the instructions at [Ollama.com](https://ollama.com/) to install Ollama for your platform.

3. **Pull the Gemma Model**
   ```
   ollama pull gemma:3-4b-it-qat
   ```

4. **Set Up Environment Variables**
   
   Create a `.env` file with your Discord token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

5. **Run the Bot**
   ```
   python bot.py
   ```

## Usage

1. **Start the Bot**
   ```
   python bot.py
   ```

2. **Reporting Messages**
   - Reply to the message you want to check
   - Use the command: `!remove @username`

The bot will analyze the message and surrounding context using the configured Code of Conduct prompt and return a recommendation.

## Code of Conduct Decisions

The bot is configured to be minimal-intervention, focusing only on extreme violations:

- **None**: No violation detected (default for most cases)
- **Temp-mute**: For clear spam or commercial promotion
- **Temp-ban**: For explicit threats, harassment, or discriminatory attacks

## Customization

The Code of Conduct prompt can be modified in `prompts/code_of_conduct.txt` to adjust the moderation policy.

## Requirements

- Python 3.8+
- Discord.py
- Ollama (running locally)
- Internet connection for Discord API

## Advanced Configuration

You can modify parameters like temperature and context window in the `bot.py` file to adjust the model behavior.