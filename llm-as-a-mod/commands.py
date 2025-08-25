"""
Discord command handlers for the moderation bot.

This module is the primary command cog (restored from moderation_commands.py).
"""

import logging
from typing import List, Dict, Any
import asyncio

import discord
from discord.ext import commands
from prompts import CODE_OF_CONDUCT
from llm_handler import llm_handler

# Configure logger
logger = logging.getLogger(__name__)


class ModerationCommands(commands.Cog):
    """Contains commands related to moderation activities."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize the cog with bot reference."""
        self.bot = bot
        
    @commands.command(name="remove")
    #@commands.has_permissions(ban_members=True)
    async def remove(self, ctx: commands.Context):
        """
        Evaluate a message for Code of Conduct violations.
        
        This command must be used as a reply to the message being evaluated.
        """
        # Check if message is a reply
        if not ctx.message.reference:
            await ctx.send("Please reply to the message that violates the Code of Conduct.")
            return
            
        try:
            # Analyze the message
            decision = await self._analyze_message(ctx)
            
            # Handle the decision
            await self._handle_decision(ctx, decision)
            
        except Exception as e:
            logger.error(f"Error in remove command: {e}", exc_info=True)
            await ctx.send(f"Error processing request: {str(e)}")
            
    async def _analyze_message(self, ctx: commands.Context) -> Dict[str, Any]:
        """
        Analyze the message being replied to.
        
        Args:
            ctx: The command context
            
        Returns:
            A dictionary containing the analysis decision
            
        Raises:
            ValueError: If analysis fails
        """
        # Get the message and context
        channel = ctx.channel
        referenced_msg = await channel.fetch_message(ctx.message.reference.message_id)
        
        # Store offender information
        offender_name = referenced_msg.author.name
        offender_id = referenced_msg.author.id
        
        # Get surrounding messages for context
        surrounding_messages = await self._get_surrounding_messages(channel, referenced_msg)
        
        # Format the reported message
        reported_message = f"{offender_name}: {referenced_msg.content}"
        
        # Create the prompt
        prompt = self._create_prompt(reported_message, surrounding_messages)
        
        # Send analysis message
        await ctx.send("Analyzing reported message for Code of Conduct violations...")
        
        # Analyze with LLM
        # llm_handler.analyze_message is blocking (uses requests). Run it in a thread
        try:
            decision = await asyncio.to_thread(llm_handler.analyze_message, prompt)
        except Exception as e:
            logger.exception("LLM analysis failed")
            raise
        
        # Add offender information
        decision["offender_name"] = offender_name
        decision["offender_id"] = str(offender_id)
        
        return decision
        
    async def _get_surrounding_messages(
        self, 
        channel: discord.TextChannel, 
        message: discord.Message
    ) -> List[str]:
        """
        Get surrounding messages for context.
        
        Args:
            channel: The channel to get messages from
            message: The message to get context around
            
        Returns:
            List of message strings
        """
        surrounding_messages = []
        async for msg in channel.history(limit=20, around=message):
            if len(surrounding_messages) < 10 and msg.id != message.id:
                surrounding_messages.append(f"{msg.author.name}: {msg.content}")
                
        return surrounding_messages
        
    def _create_prompt(self, reported_message: str, surrounding_messages: List[str]) -> str:
        """
        Create the prompt for LLM analysis.
        
        Args:
            reported_message: The message being reported
            surrounding_messages: List of context messages
            
        Returns:
            The formatted prompt string
        """
        return CODE_OF_CONDUCT + f"""

        reported_message: {reported_message}
        surrounding_messages: {surrounding_messages}
        """
        
    async def _handle_decision(self, ctx: commands.Context, decision: Dict[str, Any]):
        """
        Handle the decision from LLM analysis.
        
        Args:
            ctx: The command context
            decision: The decision dictionary from LLM
        """
        offender_name = decision.get("offender_name", "Unknown user")
        action = decision.get("action", "none")
        reason = decision.get("reason", "Not specified")
        
        # Log the decision
        logger.info(
            f"Decision for {offender_name}: action={action}, reason={reason}"
        )
        
        # Handle based on action type
        if action == "none":
            await ctx.send(
                f"**Decision**: No action needed against **{offender_name}**.\n"
            )
        elif action == "temp-mute":
            await ctx.send(
                f"**Decision**: Temporary mute recommended for **{offender_name}**.\n"
                f"Reason: {reason}"
            )
            # Implement mute functionality if desired
        elif action == "temp-ban":
            await ctx.send(
                f"**Decision**: Temporary ban recommended for **{offender_name}**.\n"
                f"Reason: {reason}"
            )
            # Implement ban functionality if desired
        else:
            await ctx.send(
                f"**Decision**: {action} for **{offender_name}**.\n"
                f"Reason: {reason}"
            )


# keep the simple extension-style setup function for backwards compatibility
def setup(bot: commands.Bot):
    """Register cogs with the bot."""
    bot.add_cog(ModerationCommands(bot))