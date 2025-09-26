import discord
from discord.ext import commands
from utils.logger import setup_logger
import asyncio
from datetime import datetime, timedelta

logger = setup_logger('Timeout')

class Timeout(commands.Cog):
    """Timeout system for temporary user restrictions"""
    
    def __init__(self, bot):
        self.bot = bot

    def parse_time(self, time_str):
        """Parse time string into seconds"""
        time_units = {
            's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
            'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
            'h': 3600, 'hr': 3600, 'hour': 3600, 'hours': 3600,
            'd': 86400, 'day': 86400, 'days': 86400
        }
        
        time_str = time_str.lower().strip()
        
        # Extract number and unit
        import re
        match = re.match(r'(\d+)([a-z]+)?', time_str)
        if not match:
            return None
        
        number = int(match.group(1))
        unit = match.group(2) or 's'  # Default to seconds if no unit
        
        if unit in time_units:
            return number * time_units[unit]
        
        return None

    @commands.command(name='timeout')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout_user(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        """Timeout a user for a specified duration"""
        if member == ctx.author:
            await ctx.send("❌ You cannot timeout yourself.")
            return
        
        if member.bot:
            await ctx.send("❌ You cannot timeout bots.")
            return

        # Check if user is higher in hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot timeout someone with equal or higher roles.")
            return

        # Parse duration
        duration_seconds = self.parse_time(duration)
        if not duration_seconds:
            await ctx.send("❌ Invalid duration format. Use formats like: `10m`, `1h`, `30s`, `2d`")
            return

        # Discord timeout limit is 28 days
        max_duration = 28 * 24 * 3600  # 28 days in seconds
        if duration_seconds > max_duration:
            await ctx.send("❌ Timeout duration cannot exceed 28 days.")
            return

        if duration_seconds < 1:
            await ctx.send("❌ Timeout duration must be at least 1 second.")
            return

        # Check if member is already timed out
        if member.timed_out:
            await ctx.send(f"❌ {member.mention} is already timed out.")
            return

        try:
            # Calculate timeout end time
            timeout_end = datetime.utcnow() + timedelta(seconds=duration_seconds)
            
            # Apply timeout
            await member.timeout(timeout_end, reason=f"Timed out by {ctx.author}: {reason}")
            
            # Format duration for display
            duration_text = self.format_duration(duration_seconds)
            
            # Try to send DM to user
            try:
                dm_embed = discord.Embed(
                    title="⏱️ You have been timed out",
                    description=f"You have been timed out in **{ctx.guild.name}**",
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name="Duration", value=duration_text, inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                dm_embed.add_field(
                    name="Timeout ends",
                    value=f"<t:{int(timeout_end.timestamp())}:F>",
                    inline=False
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

            # Send confirmation
            embed = discord.Embed(
                title="User Timed Out",
                description=f"{member.mention} has been timed out for {duration_text}.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(
                name="Timeout ends",
                value=f"<t:{int(timeout_end.timestamp())}:R>",
                inline=True
            )
            
            await ctx.send(embed=embed)
            logger.info(f"{member} timed out by {ctx.author} for {duration_text}: {reason}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to timeout this member.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to timeout member: {str(e)}")
            logger.error(f"Error timing out {member}: {e}")

    @commands.command(name='untimeout', aliases=['removetimeout'])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def remove_timeout(self, ctx, member: discord.Member):
        """Remove timeout from a user"""
        if not member.timed_out:
            await ctx.send(f"❌ {member.mention} is not timed out.")
            return

        try:
            await member.timeout(None, reason=f"Timeout removed by {ctx.author}")
            
            # Try to send DM to user
            try:
                dm_embed = discord.Embed(
                    title="⏱️ Timeout Removed",
                    description=f"Your timeout has been removed in **{ctx.guild.name}**",
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

            # Send confirmation
            embed = discord.Embed(
                title="Timeout Removed",
                description=f"Timeout has been removed from {member.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"Timeout removed from {member} by {ctx.author}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove timeout from this member.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to remove timeout: {str(e)}")
            logger.error(f"Error removing timeout from {member}: {e}")

    @commands.command(name='timeouts')
    @commands.has_permissions(moderate_members=True)
    async def list_timeouts(self, ctx):
        """List all currently timed out users"""
        timed_out_members = [member for member in ctx.guild.members if member.timed_out]

        if not timed_out_members:
            await ctx.send("✅ No users are currently timed out.")
            return

        embed = discord.Embed(
            title="Timed Out Users",
            color=discord.Color.orange()
        )

        member_list = []
        for member in timed_out_members[:10]:  # Limit to 10 users
            timeout_end = member.timed_out_until
            if timeout_end:
                member_list.append(
                    f"{member.mention} - Ends <t:{int(timeout_end.timestamp())}:R>"
                )
            else:
                member_list.append(f"{member.mention} - Unknown end time")

        embed.description = "\n".join(member_list)
        
        if len(timed_out_members) > 10:
            embed.add_field(
                name="Note",
                value=f"Showing 10 of {len(timed_out_members)} timed out users.",
                inline=False
            )

        await ctx.send(embed=embed)

    def format_duration(self, seconds):
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days != 1 else ''}"

    @commands.command(name='timeoutinfo')
    async def timeout_info(self, ctx, member: discord.Member = None):
        """Check timeout information for a user"""
        if member is None:
            member = ctx.author

        if not member.timed_out:
            await ctx.send(f"{member.mention} is not currently timed out.")
            return

        timeout_end = member.timed_out_until
        if not timeout_end:
            await ctx.send(f"{member.mention} is timed out but end time is unknown.")
            return

        embed = discord.Embed(
            title="Timeout Information",
            description=f"**User:** {member.mention}",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="Timeout ends",
            value=f"<t:{int(timeout_end.timestamp())}:F>\n(<t:{int(timeout_end.timestamp())}:R>)",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Timeout(bot))
