"""
Configuration settings for the LLM-as-a-Mod Discord bot.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class ModelConfig:
    """Configuration for the LLM model."""
    name: str = "gemma3:4b-it-qat"
    temperature: float = 0.1
    num_ctx: int = 4096
    num_predict: int = 4000


@dataclass
class BotConfig:
    """Configuration for the Discord bot."""
    token: str = os.getenv("DISCORD_TOKEN", "")
    command_prefix: str = "!"
    
    # Check if token is available
    def validate(self):
        """Validate the configuration settings."""
        if not self.token:
            raise ValueError("DISCORD_TOKEN environment variable is not set")


# Create default configuration instances
model_config = ModelConfig()
bot_config = BotConfig()