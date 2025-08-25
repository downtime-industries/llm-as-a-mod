"""
Discord bot for LLM-powered moderation.

This bot evaluates messages for Code of Conduct violations using a
language model through Ollama.
"""

import logging
import sys

import discord
from discord.ext import commands

from config import bot_config, model_config
from llm_handler import llm_handler
from commands import ModerationCommands

# Configure logging
_level_name = (getattr(bot_config, 'log_level', 'INFO') if 'bot_config' in globals() else 'INFO')
_level = getattr(logging, _level_name.upper(), logging.INFO)
logging.basicConfig(
    level=_level,
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
                logger.error(f"Failed to connect to Ollama LLM service at {model_config.base_url}")
                logger.error("Make sure Ollama is running and accessible")
                if "localhost" in model_config.base_url:
                    logger.error("You can pull the model with: ollama pull gemma:3-4b-it-qat")
                else:
                    logger.error(f"Check that the external server {model_config.base_url} is accessible")
                    logger.error("and has the required model available")
            else:
                logger.info(f"LLM service connection successful at {model_config.base_url}, bot is ready for use")

                # Log registered commands at startup for debugging
                try:
                    registered = [c.name for c in self.bot.commands]
                    logger.debug(f"Registered commands at startup: {registered}")
                except Exception:
                    logger.exception("Failed to list registered commands at startup")

                # Ensure the moderation cog is present (add asynchronously)
                if "ModerationCommands" not in self.bot.cogs:
                    try:
                        import inspect
                        logger.debug(f"ModerationCommands class object: {ModerationCommands}")
                        remove_attr = getattr(ModerationCommands, 'remove', None)
                        logger.debug(f"ModerationCommands.remove attribute: {remove_attr!r}")
                        logger.debug(f"isfunction(remove): {inspect.isfunction(remove_attr)}")
                        if hasattr(remove_attr, 'callback'):
                            logger.debug(f"remove is a Command, callback={remove_attr.callback}")
                    except Exception:
                        logger.exception("Failed to introspect ModerationCommands in on_ready")

                    try:
                        await self.bot.add_cog(ModerationCommands(self.bot))
                        logger.info("ModerationCommands cog added in on_ready")
                        logger.debug(f"Cogs registered at on_ready: {list(self.bot.cogs.keys())}")
                        logger.debug(f"Commands registered at on_ready: {[c.name for c in self.bot.commands]}")
                    except Exception:
                        logger.exception("Failed to add ModerationCommands in on_ready")
        
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
        
        @self.bot.event
        async def on_message(message: discord.Message):
            """Log incoming messages for debugging and ensure command processing

            This helps diagnose why commands like `!remove` may not be recognized
            (for example when message content intent is missing or another
            on_message handler failed to call process_commands).
            """
            # Ignore bot messages
            if message.author.bot:
                return

            # Basic debug information
            channel_name = getattr(message.channel, "name", "DM")
            logger.debug(
                f"on_message from {message.author} (id={message.author.id}) in {channel_name}: content={message.content!r} reference={getattr(message, 'reference', None)}"
            )

            # Log registered commands and prefix to help debug registration issues
            try:
                registered = [c.name for c in self.bot.commands]
                logger.debug(f"Registered commands: {registered}, command_prefix={bot_config.command_prefix!r}")
            except Exception:
                logger.debug("Failed to enumerate registered commands", exc_info=True)

            # Ensure commands are processed by the commands extension
            try:
                await self.bot.process_commands(message)
            except Exception as e:
                logger.exception(f"Error while processing commands: {e}")
        
    def run(self):
        """Run the bot."""
        logger.info("Starting bot...")
        
        # Connect to Discord
        self.bot.run(bot_config.token)


if __name__ == "__main__":
    bot = ModerationBot()
    bot.run()