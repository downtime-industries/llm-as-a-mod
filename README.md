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

2. **Install Ollama (local)**
   Follow the instructions at https://ollama.com/ to install Ollama for your platform.

3. **(Optional) Pull a model locally**
   If you're running Ollama locally you can pull a model you plan to use:
   ```bash
   ollama pull gemma3:12b-it-qat
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the repository root. At minimum set your Discord token and, optionally, an Ollama base URL and log level:

   ```ini
   DISCORD_TOKEN=your_discord_bot_token_here
   # Optional: point to a remote or local Ollama server (default: http://localhost:11434)
   OLLAMA_BASE_URL=http://localhost:11434
   # Optional: DEBUG, INFO, WARNING, ERROR
   LOG_LEVEL=INFO
   ```

   - To use a remote Ollama instance, set `OLLAMA_BASE_URL` to the remote host (e.g. `http://someserver:11434`). Ensure that host is reachable and the required model is available on that server.

5. **Run the Bot**

   Recommended: run from the `llm-as-a-mod` directory:

   ```bash
   cd llm-as-a-mod
   python bot.py
   ```

   Or run from repository root:
   ```bash
   python llm-as-a-mod/bot.py
   ```

## Logging and debugging

- The bot reads `LOG_LEVEL` from `.env` (defaults to `INFO`). Set `LOG_LEVEL=DEBUG` for verbose logs.
- Logs are written to `bot.log` in the working directory and also to stdout.
- The bot will report the configured `OLLAMA_BASE_URL` on startup and test the connection. If you point to a remote server, ensure that server has the expected model installed and is reachable.

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