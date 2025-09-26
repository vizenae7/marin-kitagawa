import discord
from discord.ext import commands
from discord import app_commands
import os

# Load owner ID from environment or hardcode it
OWNER_ID = int(os.getenv("OWNER_ID", 828835928331255818))  # Replace with your actual ID if not using .env

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 1382979405453987972  # Replace with your test server ID

    @app_commands.command(name="sync_commands", description="Force sync slash commands to this server (owner only)")
    async def sync_commands(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can sync commands.", ephemeral=True)
            return

        try:
            guild = discord.Object(id=self.guild_id)
            synced = await self.bot.tree.sync(guild=guild)
            await interaction.response.send_message(
                f"✅ Synced {len(synced)} command(s) to this server.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Sync failed: `{e}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AdminTools(bot))
