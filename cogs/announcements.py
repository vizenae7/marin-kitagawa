import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random

BLEACH_INTROS = [
    "Bankai unleashed! 🔥",
    "Spiritual pressure intensifies… 💥",
    "A soul clash begins! ⚔️",
    "Zanpakutō spirit awakens… 🐉",
    "Reiatsu surges through the air… 🌪️"
]

class Announcer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announce", description="Make a dramatic server-wide announcement")
    @app_commands.describe(
        channel="Where should the announcement be posted?",
        title="Title of the announcement",
        message="Main content of the announcement",
        role="Optional role to mention",
        ping_everyone="Do you want to ping @everyone?",
        image_url="Optional image/banner URL",
        delay_seconds="Schedule delay in seconds (0 = immediate)"
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        message: str,
        role: discord.Role = None,
        ping_everyone: bool = False,
        image_url: str = None,
        delay_seconds: int = 0
    ):
        intro = random.choice(BLEACH_INTROS)
        embed = discord.Embed(
            title=f"📢 {title}",
            description=f"{intro}\n\n{message}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Announced by {interaction.user.display_name}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        if image_url:
            embed.set_image(url=image_url)

        mentions = []
        if ping_everyone:
            mentions.append("@everyone")
        if role:
            mentions.append(role.mention)
        content = " ".join(mentions) if mentions else None

        await interaction.response.send_message(
            f"⏳ Announcement scheduled in {delay_seconds} seconds for {channel.mention}",
            ephemeral=True
        )

        await asyncio.sleep(delay_seconds)
        await channel.send(content=content, embed=embed)

async def setup(bot):
    await bot.add_cog(Announcer(bot))
