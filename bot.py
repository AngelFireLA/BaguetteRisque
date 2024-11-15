import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Discord bot token from the environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the bot with the intents required
intents = discord.Intents.all()
intents.messages = True  # Ensure message events are enabled

# Define the prefix
PREFIX = "br$"

# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Event that runs when a message is sent
@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the message starts with the defined prefix
    if message.content.startswith(PREFIX):
        # Remove the prefix from the message to get the command part
        command = message.content[len(PREFIX):].strip()

        # Respond to "hello" command
        if command.lower() == "hello":
            await message.channel.send("Hello!")

    # Process commands normally if any other handler is added
    await bot.process_commands(message)

# Run the bot with the specified token
bot.run(TOKEN)
