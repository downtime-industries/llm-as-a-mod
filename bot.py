import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp
from prompts import CODE_OF_CONDUCT

# Load environment variables
load_dotenv()

# Configure Discord bot with properly configured intents
intents = discord.Intents.default()
intents.message_content = True  # This is critical for commands to work
intents.messages = True

# Create the bot with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Path to the GGUF file - adjust this path as needed
model_path = "./models/gemma-3-4b-it-q4_0.gguf"
# Verify if model exists
if not os.path.exists(model_path):
    print(f"Model file not found at {model_path}")
    print("Please download the model file from HuggingFace and place it in the project root.")
    print("You can use: python download_gemma3_model.py")
    exit(1)

# Initialize the model with llama.cpp
print("Initializing the Gemma-3-4b model - this may take a moment...")
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

model = LlamaCpp(
    model_path=model_path,
    temperature=0.1,
    max_tokens=4000,
    n_ctx=4096,  # 4k context window
    callback_manager=callback_manager,
    verbose=False,  # Set to True for detailed processing logs
    n_gpu_layers=-1,  # Auto-detect and use GPU if available
    n_batch=512,  # Batch size for processing
    f16_kv=True,  # Use half-precision for key/value cache
)

# The Code of Conduct template is imported from the prompts module
coc_template = CODE_OF_CONDUCT


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # Warm up the model with a simple query to keep it in memory
    model("RESPOND WITH ACK AND NOTHING ELSE")
    print("Model is warmed up and ready!")


@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
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
        
        # Get up to 10 surrounding messages for context
        surrounding_messages = []
        async for msg in channel.history(limit=20, around=referenced_msg):
            if len(surrounding_messages) < 10 and msg.id != referenced_msg.id:
                surrounding_messages.append(f"{msg.author.name}: {msg.content}")
        
        # Format the input for the LLM
        reported_message = f"{referenced_msg.author.name}: {referenced_msg.content}"
        
        # Create the prompt with the Code of Conduct template
        prompt = coc_template + f"""
        
            reported_message: {reported_message}
            surrounding_messages: {surrounding_messages}
            """

        # Send a message indicating the bot is analyzing
        analysis_msg = await ctx.send(f"Analyzing reported message for Code of Conduct violations...")
        
        # Process with LLM
        print("Sending prompt to model...")
        response_text = model(prompt)
        print("Received response from model.")
        
        # Extract JSON from the response with improved parsing logic
        json_text = ""
        
        # First, try to extract JSON from code blocks
        if "```json" in response_text and "```" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        # If that fails, check for - answer: prefix
        elif "- answer:" in response_text and "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
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
            
            # Act based on the LLM's decision
            if decision["action"] == "none":
                await ctx.send(f"**Decision**: No action needed. Reason: {decision['reason']}")
            elif decision["action"] == "temp-mute":
                await ctx.send(f"**Decision**: Temporary mute recommended. Reason: {decision['reason']}")
                # Implement mute functionality if desired
            elif decision["action"] == "temp-ban":
                await ctx.send(f"**Decision**: Temporary ban recommended. Reason: {decision['reason']}")
                # Here you could implement automatic banning if desired
                # await member.ban(reason=decision["reason"])
            else:
                await ctx.send(f"**Decision**: {decision['action']}. Reason: {decision['reason']}")
        
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