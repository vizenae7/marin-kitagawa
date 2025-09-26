import discord
from discord.ext import commands
from discord import app_commands

class CheckPerms(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="checkperms", description="Scan a user's permissions with dramatic flair.")
    @app_commands.describe(user="The user whose permissions you want to inspect")
    async def checkperms(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        perms = target.guild_permissions

        embed = discord.Embed(
            title=f"🔍 Permission Scan: {target.display_name}",
            description="Behold the power they wield...",
            color=discord.Color.purple()
        )

        key_perms = [
            "administrator", "manage_guild", "manage_roles", "kick_members",
            "ban_members", "manage_channels", "manage_messages", "mention_everyone"
        ]

        for perm in key_perms:
            value = getattr(perms, perm)
            status = "✅ Granted" if value else "❌ Denied"
            embed.add_field(name=perm.replace("_", " ").title(), value=status, inline=True)

        embed.set_footer(text="Scan complete. Power levels assessed.")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CheckPerms(bot))
