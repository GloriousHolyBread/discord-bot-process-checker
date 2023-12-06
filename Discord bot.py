import psutil
import discord
import asyncio
from discord.ext import commands

# Discord bot token
TOKEN = 'TOKEN'

# Process name to check
PROCESS_NAME = 'Process ID'  # Replace with your process name

# Initialize intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Variable to keep track of previous process state
process_running = False

# Function to check if a process is running
def is_process_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False

# Function to send a message to Discord
async def send_discord_message(message):
    channel = bot.get_channel(CHANNEL_ID)  # Replace YOUR_CHANNEL_ID with your channel ID
    await channel.send(message)

# Command to check if the process is running
@bot.command()
async def check(ctx):
    if is_process_running(PROCESS_NAME):
        await ctx.send(f"MC Server is running.")
    else:
        await ctx.send(f"MC Server is not running.")

# Background task to periodically check the process and send messages
async def check_process_task():
    global process_running
    await bot.wait_until_ready()
    while not bot.is_closed():
        current_state = is_process_running(PROCESS_NAME)
        if not process_running and current_state:
            process_running = True
            await send_discord_message(f"MC Server has started running.")
        elif process_running and not current_state:
            process_running = False
            await send_discord_message(f"MC Server has stopped running.")
            # Add an additional check to confirm process stopped (to avoid false positives)
            while not is_process_running(PROCESS_NAME):
                await asyncio.sleep(2)  # Check again after 2 seconds
                if not is_process_running(PROCESS_NAME):
                    await send_discord_message(f"MC Server has confirmed stopped.")
                    break
        await asyncio.sleep(60)  # Adjust the time interval (in seconds) as needed

# Event for bot startup
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.loop.create_task(check_process_task())

# Run the bot
bot.run(TOKEN)
