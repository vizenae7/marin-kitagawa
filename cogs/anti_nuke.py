import discord
from discord.ext import commands
from utils.logger import setup_logger
import asyncio

logger = setup_logger('AntiNuke')

class AntiNuke(commands.Cog):
    """Anti-nuke protection system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.recent_deletions = {}  # Track recent channel deletions
        self.recent_bans = {}       # Track recent bans
        self.protection_enabled = True

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Monitor channel deletions"""
        if not self.protection_enabled:
            return

        guild_id = channel.guild.id
        current_time = asyncio.get_event_loop().time()

        # Initialize tracking for this guild if needed
        if guild_id not in self.recent_deletions:
            self.recent_deletions[guild_id] = []

        # Add this deletion to the list
        self.recent_deletions[guild_id].append(current_time)

        # Remove deletions older than 60 seconds
        self.recent_deletions[guild_id] = [
            t for t in self.recent_deletions[guild_id] 
            if current_time - t < 60
        ]

        # Check if too many channels were deleted recently
        if len(self.recent_deletions[guild_id]) > 3:
            await self.trigger_anti_nuke(channel.guild, "Mass channel deletion detected")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Monitor mass bans"""
        if not self.protection_enabled:
            return

        guild_id = guild.id
        current_time = asyncio.get_event_loop().time()

        # Initialize tracking for this guild if needed
        if guild_id not in self.recent_bans:
            self.recent_bans[guild_id] = []

        # Add this ban to the list
        self.recent_bans[guild_id].append(current_time)

        # Remove bans older than 60 seconds
        self.recent_bans[guild_id] = [
            t for t in self.recent_bans[guild_id] 
            if current_time - t < 60
        ]

        # Check if too many bans happened recently
        if len(self.recent_bans[guild_id]) > 5:
            await self.trigger_anti_nuke(guild, "Mass ban detected")

    async def trigger_anti_nuke(self, guild, reason):
        """Trigger anti-nuke protection"""
        logger.warning(f"Anti-nuke triggered in {guild.name}: {reason}")

        # Find a channel to send alert
        alert_channel = None
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                alert_channel = channel
                break

        if alert_channel:
            embed = discord.Embed(
                title="🚨 Anti-Nuke Protection Activated",
                description=f"**Reason:** {reason}\n\n"
                           "Suspicious activity detected. Please review recent actions.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Recommended Actions",
                value="• Check audit logs\n• Review staff permissions\n• Consider enabling slowmode",
                inline=False
            )
            await alert_channel.send(embed=embed)

    @commands.command(name='antinuke')
    @commands.has_permissions(administrator=True)
    async def toggle_anti_nuke(self, ctx, status: str = None):
        """Toggle anti-nuke protection on/off"""
        if status is None:
            status_text = "enabled" if self.protection_enabled else "disabled"
            await ctx.send(f"Anti-nuke protection is currently **{status_text}**.")
            return

        if status.lower() in ['on', 'enable', 'true']:
            self.protection_enabled = True
            await ctx.send("✅ Anti-nuke protection **enabled**.")
        elif status.lower() in ['off', 'disable', 'false']:
            self.protection_enabled = False
            await ctx.send("❌ Anti-nuke protection **disabled**.")
        else:
            await ctx.send("❌ Invalid status. Use `on` or `off`.")

    @commands.command(name='nukestatus')
    @commands.has_permissions(manage_guild=True)
    async def nuke_status(self, ctx):
        """Check current anti-nuke status and recent activity"""
        guild_id = ctx.guild.id
        
        recent_deletions = len(self.recent_deletions.get(guild_id, []))
        recent_bans = len(self.recent_bans.get(guild_id, []))
        
        embed = discord.Embed(
            title="Anti-Nuke Status",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Protection Status",
            value="✅ Enabled" if self.protection_enabled else "❌ Disabled",
            inline=True
        )
        embed.add_field(
            name="Recent Deletions (1min)",
            value=str(recent_deletions),
            inline=True
        )
        embed.add_field(
            name="Recent Bans (1min)",
            value=str(recent_bans),
            inline=True
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
