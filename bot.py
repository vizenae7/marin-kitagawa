import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import subprocess
from utils.logger import setup_logger

# Load environment variables
load_dotenv()
logger = setup_logger('DiscordBot')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.voice_states = True

# Bot setup
prefix = os.getenv('PREFIX', 'V!')
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Global storage
bot.afk_users = {}
bot.warning_count = {}
bot.whitelisted_commands = ["afk", "help"]

# FFmpeg check
def ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# Load cogs
async def load_cogs():
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    if not os.path.exists(cogs_dir):
        logger.error("Cogs directory not found!")
        return
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            extension = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")

# Setup hook
async def setup_hook():
    await load_cogs()
bot.setup_hook = setup_hook

# on_ready event
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guilds')

    # FFmpeg check
    if not ffmpeg_installed():
        channel_id = os.getenv("LOG_CHANNEL_ID")
        if channel_id:
            channel = bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=discord.Embed(
                    title="💥 FFmpeg Missing",
                    description="The Soul Chain cannot be forged. FFmpeg is not installed.",
                    color=discord.Color.red()
                ))
        return

    # Slash sync
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

    # Anime-style presence
    activity = discord.Activity(type=discord.ActivityType.watching, name="MY DARLING VIZEN 💞")
    await bot.change_presence(status=discord.Status.dnd, activity=activity)
    print(f"{bot.user} is now watching MY DARLING VIZEN 💞 in DND mode.")

# Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")
    else:
        logger.error(f"Unhandled error: {error}")
        await ctx.send("❌ An unexpected error occurred.")

# Mention response
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if bot.user in message.mentions:
        await message.channel.send(
            f"Hi {message.author.mention}, my name is Marin 💖\nI was made by vizen https://tenor.com/view/marin-kitagawa-kitagawa-marin-marin-kitagawa-bisque-gif-24604709"
        )
    await bot.process_commands(message)

# Run bot
if __name__ == "__main__":
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN not found in environment variables.")
        raise ValueError("BOT_TOKEN not found.")
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token.")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
