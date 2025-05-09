import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from prompts import CODE_OF_CONDUCT

# Load environment variables
load_dotenv()

# Configure Discord bot with properly configured intents
intents = discord.Intents.default()
intents.message_content = True  # This is critical for commands to work
intents.messages = True

# Create the bot with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the Ollama client for the Gemma model
print("Connecting to Ollama service for Gemma model...")
model = Ollama(
    model="gemma3:4b-it-qat",
    temperature=0.1,
    num_ctx=4096,  # Context window
    num_predict=4000,  # Equivalent to max_tokens
)

# The Code of Conduct template is imported from the prompts module
coc_template = CODE_OF_CONDUCT


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # Test the connection to Ollama
    try:
        print("Ollama connection successful! Model is ready.")
    except Exception as e:
        print(f"ERROR: Could not connect to Ollama service: {str(e)}")
        print("Make sure Ollama is running and the model is available.")
        print("You can pull the model with: ollama pull gemma:3-4b-it-qat")


@bot.command(name='remove')
@commands.has_permissions(ban_members=True)
async def remove(ctx):
    """Request to ban a user for Code of Conduct violation"""
    # Check if a message was replied to
    referenced_message = ctx.message.reference
    
    if not referenced_message:
        await ctx.send("Please reply to the message that violates the Code of Conduct.")
        return
    
    try:
        # Get the message and surrounding context
        channel = ctx.channel
        referenced_msg = await channel.fetch_message(referenced_message.message_id)
        
        # Store the offender's information
        offender_name = referenced_msg.author.name
        offender_id = referenced_msg.author.id
        
        # Get up to 10 surrounding messages for context
        surrounding_messages = []
        async for msg in channel.history(limit=20, around=referenced_msg):
            if len(surrounding_messages) < 10 and msg.id != referenced_msg.id:
                surrounding_messages.append(f"{msg.author.name}: {msg.content}")
        
        # Format the input for the LLM
        reported_message = f"{offender_name}: {referenced_msg.content}"
        
        # Create the prompt with the Code of Conduct template
        prompt = coc_template + f"""

reported_message: {reported_message}
surrounding_messages: {surrounding_messages}
"""

        # Send a message indicating the bot is analyzing
        analysis_msg = await ctx.send(f"Analyzing reported message for Code of Conduct violations...")
        
        # Process with LLM
        print("Sending prompt to Ollama...")
        response_text = model.invoke(prompt)
        print("Received response from Ollama.")
        
        # Extract JSON from the response with improved parsing logic
        json_text = ""
        
        # First, try to extract JSON from code blocks
        if "```json" in response_text and "```" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        # If that fails, check for plain code blocks
        elif "```" in response_text and "```" in response_text[response_text.find("```")+3:]:
            json_text = response_text.split("```")[1].strip()
        # If that fails too, try to find JSON patterns directly
        elif "{" in response_text and "}" in response_text:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > 0:
                json_text = response_text[start_idx:end_idx].strip()
        else:
            json_text = response_text.strip()
            
        print(f"Extracted JSON: {json_text[:100]}...")  # Print first 100 chars for debugging
        
        try:
            decision = json.loads(json_text)
            
            # Add offender information to the decision object
            decision["offender_name"] = offender_name
            decision["offender_id"] = str(offender_id)
            
            # Act based on the LLM's decision
            if decision["action"] == "none":
                await ctx.send(f"**Decision**: No action needed against **{offender_name}**.\nReason: {decision['reason'] if 'reason' in decision else 'No violation detected'}")
            elif decision["action"] == "temp-mute":
                await ctx.send(f"**Decision**: Temporary mute recommended for **{offender_name}**.\nReason: {decision['reason']}")
                # Implement mute functionality if desired
            elif decision["action"] == "temp-ban":
                await ctx.send(f"**Decision**: Temporary ban recommended for **{offender_name}**.\nReason: {decision['reason']}")
                # Here you could implement automatic banning if desired
                # await member.ban(reason=decision["reason"])
            else:
                await ctx.send(f"**Decision**: {decision['action']} for **{offender_name}**.\nReason: {decision['reason'] if 'reason' in decision else 'Not specified'}")
            
            # Print the complete decision object for debugging
            print(f"Complete decision: {json.dumps(decision)}")
        
        except json.JSONDecodeError:
            await ctx.send("Error: The model did not return a valid JSON response. Please try again.")
            print(f"Invalid JSON response: {response_text}")
            
    except Exception as e:
        await ctx.send(f"Error processing request: {str(e)}")
        print(f"Error details: {str(e)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Available commands: `!remove`")
    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'remove':
            await ctx.send("Usage: !remove @username (while replying to a message)")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid arguments. For !remove, please mention a valid user.")
    else:
        error_details = str(error)
        await ctx.send(f"An error occurred: {error_details}")
        print(f"Command error details: {type(error).__name__}: {error_details}")


# Run the bot
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))