"""
Discord bot for LLM-powered moderation.

This bot evaluates messages for Code of Conduct violations using a
language model through Ollama.
"""

import logging
import sys

import discord
from discord.ext import commands

from config import bot_config
from llm_handler import llm_handler
from commands import ModerationCommands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger("bot")


class ModerationBot:
    """
    Discord bot for moderating messages using LLMs.
    
    This class handles the initialization and management of the Discord bot,
    including event handlers and command registration.
    """
    
    def __init__(self):
        """Initialize the bot with proper configuration."""
        # Validate configuration
        try:
            bot_config.validate()
        except ValueError as e:
            logger.critical(f"Configuration error: {e}")
            sys.exit(1)
            
        # Configure Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        # Create bot instance
        self.bot = commands.Bot(command_prefix=bot_config.command_prefix, intents=intents)
        
        # Register event handlers
        self._register_events()
        
    def _register_events(self):
        """Register event handlers for the bot."""
        
        @self.bot.event
        async def on_ready():
            """Called when the bot is ready."""
            logger.info(f"Bot connected to Discord as {self.bot.user}")
            
            # Test LLM connection
            if not llm_handler.test_connection():
                logger.error("Failed to connect to Ollama LLM service")
                logger.error("Make sure Ollama is running and the model is available")
                logger.error("You can pull the model with: ollama pull gemma:3-4b-it-qat")
            else:
                logger.info("LLM service connection successful, bot is ready for use")
                
        @self.bot.event
        async def on_command_error(ctx: commands.Context, error: Exception):
            """Handle command errors."""
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("You don't have permission to use this command!")
            elif isinstance(error, commands.CommandNotFound):
                await ctx.send(f"Command not found. Available commands: `!remove`")
            elif isinstance(error, commands.MissingRequiredArgument):
                if ctx.command and ctx.command.name == "remove":
                    await ctx.send("Usage: !remove (while replying to a message)")
            elif isinstance(error, commands.BadArgument):
                await ctx.send(f"Invalid arguments. For !remove, please reply to a message.")
            else:
                error_details = str(error)
                await ctx.send(f"An error occurred: {error_details}")
                logger.error(f"Command error: {type(error).__name__}: {error}", exc_info=True)
        
    def run(self):
        """Run the bot."""
        logger.info("Starting bot...")
        
        # Add command cogs
        self.bot.add_cog(ModerationCommands(self.bot))
        
        # Connect to Discord
        self.bot.run(bot_config.token)


if __name__ == "__main__":
    bot = ModerationBot()
    bot.run()