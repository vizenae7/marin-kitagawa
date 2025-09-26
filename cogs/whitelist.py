import discord
from discord import app_commands
from discord.ext import commands
import json, os
from utils.logger import setup_logger

logger = setup_logger("Whitelist")

WHITELIST_FILE = "data/whitelist.json"
whitelisted_users = set()
whitelisted_roles = set()
whitelisted_channels = set()

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as f:
            data = json.load(f)
            whitelisted_users.update(data.get("users", []))
            whitelisted_roles.update(data.get("roles", []))
            whitelisted_channels.update(data.get("channels", []))

def save_whitelist():
    with open(WHITELIST_FILE, "w") as f:
        json.dump({
            "users": list(whitelisted_users),
            "roles": list(whitelisted_roles),
            "channels": list(whitelisted_channels)
        }, f)

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_whitelist()

    @app_commands.command(name="whitelist", description="Toggle automod immunity for a user, role, or channel.")
    @app_commands.describe(user="User to whitelist/unwhitelist", role="Role to whitelist/unwhitelist", channel="Channel to whitelist/unwhitelist")
    async def whitelist(self, interaction: discord.Interaction, user: discord.Member = None, role: discord.Role = None, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("🚫 You need to be an administrator to use this command.", ephemeral=True)
            return

        target = user or role or channel
        if not target:
            await interaction.response.send_message("⚠️ Please specify a user, role, or channel.", ephemeral=True)
            return

        if user:
            if user.id in whitelisted_users:
                whitelisted_users.remove(user.id)
                await self.send_embed(interaction, f"{user.mention} removed from automod whitelist.", False)
            else:
                whitelisted_users.add(user.id)
                await self.send_embed(interaction, f"{user.mention} added to automod whitelist.", True)

        elif role:
            if role.id in whitelisted_roles:
                whitelisted_roles.remove(role.id)
                await self.send_embed(interaction, f"Role **{role.name}** removed from automod whitelist.", False)
            else:
                whitelisted_roles.add(role.id)
                await self.send_embed(interaction, f"Role **{role.name}** added to automod whitelist.", True)

        elif channel:
            if channel.id in whitelisted_channels:
                whitelisted_channels.remove(channel.id)
                await self.send_embed(interaction, f"Channel {channel.mention} removed from automod whitelist.", False)
            else:
                whitelisted_channels.add(channel.id)
                await self.send_embed(interaction, f"Channel {channel.mention} added to automod whitelist.", True)

        save_whitelist()
        logger.info(f"{interaction.user} toggled whitelist for {target} in {interaction.guild.name}")

    @app_commands.command(name="whitelist_status", description="View current automod immunity settings.")
    async def whitelist_status(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛡️ Automod Whitelist Status", color=discord.Color.blurple())
        embed.add_field(name="Users", value="\n".join(f"<@{uid}>" for uid in whitelisted_users) or "None", inline=False)
        embed.add_field(name="Roles", value="\n".join(f"<@&{rid}>" for rid in whitelisted_roles) or "None", inline=False)
        embed.add_field(name="Channels", value="\n".join(f"<#{cid}>" for cid in whitelisted_channels) or "None", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_embed(self, interaction, message: str, added: bool):
        embed = discord.Embed(
            title="Whitelist Updated",
            description=message,
            color=discord.Color.green() if added else discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def is_immune_to_automod(self, member: discord.Member, channel: discord.TextChannel):
        return (
            member.id in whitelisted_users or
            any(role.id in whitelisted_roles for role in member.roles) or
            channel.id in whitelisted_channels
        )

async def setup(bot):
    await bot.add_cog(Whitelist(bot))
