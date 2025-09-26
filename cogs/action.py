import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random

TENOR_API_KEY = "AIzaSyAnD_xk8u1n2aU7ZGT03kmCbxfvivFAd_o"
SEARCH_LIMIT = 10

ACTIONS = [
    "cuddle", "hug", "kiss", "lick", "nom", "pat", "poke", "slap", "stare",
    "highfive", "bite", "greet", "punch", "handholding", "tickle", "kill",
    "hold", "pats", "wave", "boop", "snuggle", "bully"
]

EMOJI_MAP = {
    "hug": "💞", "kiss": "💋", "slap": "🗡️", "poke": "👈", "pat": "👋",
    "kill": "💀", "tickle": "😆", "punch": "💥", "wave": "👋", "boop": "🐾",
    "snuggle": "🛌", "bully": "😈", "bite": "🦷", "lick": "👅"
}

BLEACH_INTROS = [
    "Bankai unleashed! 🔥",
    "Spiritual pressure intensifies… 💥",
    "A soul clash begins! ⚔️",
    "The battlefield trembles… 🗡️",
    "Reiatsu surges through the air… 🌪️",
    "Zanpakutō spirit awakens… 🐉"
]

# Custom anime-only search terms for Tenor
CUSTOM_QUERIES = {
    "kiss": "anime kiss",
    "hug": "anime hug",
    "slap": "anime slap",
    "pat": "anime headpat",
    "poke": "anime poke",
    "tickle": "anime tickle",
    "kill": "anime fight kill",
    "lick": "anime lick",
    "bite": "anime bite",
    "snuggle": "anime snuggle",
    "bully": "anime bully",
    "nom": "anime nom",
    "wave": "anime wave",
    "punch": "anime punch",
    "cuddle": "anime cuddle",
    "boop": "anime boop",
    "handholding": "anime handholding",
    "hold": "anime hold",
    "pats": "anime pats",
    "greet": "anime greet",
    "stare": "anime stare",
    "highfive": "anime highfive"
}

class Action(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_gif(self, action):
        query = CUSTOM_QUERIES.get(action, f"{action} anime")
        url = f"https://tenor.googleapis.com/v2/search?q={query}&key={TENOR_API_KEY}&limit={SEARCH_LIMIT}&contentfilter=high"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        return random.choice(results)["media_formats"]["gif"]["url"]
        return None

    def create_prefix_command(self, action):
        @commands.command(name=action)
        @commands.cooldown(1, 10, commands.BucketType.user)
        async def command(ctx, member: discord.Member):
            gif = await self.fetch_gif(action)
            emoji = EMOJI_MAP.get(action, "💫")
            intro = random.choice(BLEACH_INTROS)
            if gif:
                embed = discord.Embed(
                    description=f"{intro}\n**{ctx.author.display_name}** {action}s **{member.display_name}** {emoji}",
                    color=discord.Color.orange()
                )
                embed.set_image(url=gif)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't find a GIF for that action.")
        return command

    def create_slash_command(self, action):
        @app_commands.command(name=action, description=f"{action.capitalize()} someone with an anime GIF")
        @app_commands.describe(member="Who are you targeting?")
        @app_commands.checks.cooldown(1, 10.0)
        async def command(interaction: discord.Interaction, member: discord.Member):
            gif = await self.fetch_gif(action)
            emoji = EMOJI_MAP.get(action, "💫")
            intro = random.choice(BLEACH_INTROS)
            if gif:
                embed = discord.Embed(
                    description=f"{intro}\n**{interaction.user.display_name}** {action}s **{member.display_name}** {emoji}",
                    color=discord.Color.orange()
                )
                embed.set_image(url=gif)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Couldn't find a GIF for that action.", ephemeral=True)
        return command

    async def cog_load(self):
        for action in ACTIONS:
            self.bot.add_command(self.create_prefix_command(action))
            self.bot.tree.add_command(self.create_slash_command(action))

async def setup(bot):
    await bot.add_cog(Action(bot))
