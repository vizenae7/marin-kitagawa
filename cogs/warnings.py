import discord
from discord.ext import commands
from utils.logger import setup_logger
from config import MAX_WARNINGS, WARNING_ACTIONS

logger = setup_logger('Warnings')

class Warnings(commands.Cog):
    """Warning system for user management"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Issue a warning to a user"""
        if member == ctx.author:
            await ctx.send("❌ You cannot warn yourself.")
            return
        
        if member.bot:
            await ctx.send("❌ You cannot warn bots.")
            return

        user_id = member.id
        
        # Initialize warning count if needed
        if user_id not in self.bot.warning_count:
            self.bot.warning_count[user_id] = 0
        
        # Increment warning count
        self.bot.warning_count[user_id] += 1
        warning_count = self.bot.warning_count[user_id]

        try:
            # Send warning to user via DM
            dm_embed = discord.Embed(
                title="⚠️ Warning Received",
                description=f"You have been warned in **{ctx.guild.name}**",
                color=discord.Color.yellow()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Total Warnings", value=str(warning_count), inline=True)
            dm_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # User has DMs disabled
            pass

        # Send confirmation in channel
        embed = discord.Embed(
            title="Warning Issued",
            description=f"{member.mention} has been warned.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=str(warning_count), inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        logger.info(f"{member} warned by {ctx.author} for: {reason} (Total: {warning_count})")

        # Check for escalation
        await self.check_warning_escalation(ctx, member, warning_count)

    async def check_warning_escalation(self, ctx, member, warning_count):
        """Check if warning count requires escalation"""
        if warning_count >= MAX_WARNINGS:
            # Auto-ban for max warnings
            try:
                await member.ban(reason=f"Reached maximum warnings ({MAX_WARNINGS})")
                
                embed = discord.Embed(
                    title="Auto-Ban",
                    description=f"{member.mention} has been automatically banned for reaching {MAX_WARNINGS} warnings.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                logger.info(f"{member} auto-banned for reaching max warnings")
                
            except discord.Forbidden:
                await ctx.send(f"❌ Cannot ban {member.mention} - missing permissions.")
        
        elif warning_count == 2:
            # Auto-mute for 2 warnings
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            
            if not mute_role:
                try:
                    mute_role = await ctx.guild.create_role(name="Muted")
                    for channel in ctx.guild.channels:
                        await channel.set_permissions(mute_role, send_messages=False, speak=False)
                except discord.Forbidden:
                    await ctx.send("❌ Cannot create Muted role - missing permissions.")
                    return

            try:
                await member.add_roles(mute_role, reason="Auto-mute for 2 warnings")
                
                embed = discord.Embed(
                    title="Auto-Mute",
                    description=f"{member.mention} has been automatically muted for receiving 2 warnings.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                logger.info(f"{member} auto-muted for 2 warnings")
                
            except discord.Forbidden:
                await ctx.send(f"❌ Cannot mute {member.mention} - missing permissions.")

    @commands.command(name='warnings', aliases=['warns'])
    async def check_warnings(self, ctx, member: discord.Member = None):
        """Check warning count for a user"""
        if member is None:
            member = ctx.author

        user_id = member.id
        warning_count = self.bot.warning_count.get(user_id, 0)

        embed = discord.Embed(
            title="Warning Information",
            description=f"**User:** {member.mention}\n**Warnings:** {warning_count}/{MAX_WARNINGS}",
            color=discord.Color.blue()
        )
        
        if warning_count > 0:
            embed.color = discord.Color.yellow()
            if warning_count >= MAX_WARNINGS - 1:
                embed.color = discord.Color.red()
                embed.add_field(
                    name="⚠️ Warning",
                    value="User is close to maximum warnings!",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name='clearwarns')
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear all warnings for a user"""
        user_id = member.id
        
        if user_id in self.bot.warning_count:
            old_count = self.bot.warning_count[user_id]
            self.bot.warning_count[user_id] = 0
            
            embed = discord.Embed(
                title="Warnings Cleared",
                description=f"Cleared {old_count} warning(s) for {member.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"Cleared {old_count} warnings for {member} by {ctx.author}")
        else:
            await ctx.send(f"❌ {member.mention} has no warnings to clear.")

    @commands.command(name='removewarn')
    @commands.has_permissions(manage_messages=True)
    async def remove_warning(self, ctx, member: discord.Member, amount: int = 1):
        """Remove a specific number of warnings from a user"""
        if amount < 1:
            await ctx.send("❌ Amount must be at least 1.")
            return

        user_id = member.id
        
        if user_id not in self.bot.warning_count or self.bot.warning_count[user_id] == 0:
            await ctx.send(f"❌ {member.mention} has no warnings to remove.")
            return

        old_count = self.bot.warning_count[user_id]
        self.bot.warning_count[user_id] = max(0, old_count - amount)
        new_count = self.bot.warning_count[user_id]
        removed = old_count - new_count

        embed = discord.Embed(
            title="Warnings Removed",
            description=f"Removed {removed} warning(s) from {member.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="Previous Warnings", value=str(old_count), inline=True)
        embed.add_field(name="Current Warnings", value=str(new_count), inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        logger.info(f"Removed {removed} warnings from {member} by {ctx.author}")

    @commands.command(name='warnlist')
    @commands.has_permissions(manage_messages=True)
    async def warning_list(self, ctx):
        """List all users with warnings in the server"""
        guild_warnings = []
        
        for user_id, count in self.bot.warning_count.items():
            if count > 0:
                member = ctx.guild.get_member(user_id)
                if member:
                    guild_warnings.append((member, count))

        if not guild_warnings:
            await ctx.send("✅ No users currently have warnings in this server.")
            return

        # Sort by warning count (descending)
        guild_warnings.sort(key=lambda x: x[1], reverse=True)

        embed = discord.Embed(
            title="Server Warning List",
            color=discord.Color.orange()
        )

        warning_text = []
        for member, count in guild_warnings[:15]:  # Limit to 15 users
            warning_text.append(f"{member.mention} - {count} warning(s)")

        embed.description = "\n".join(warning_text)
        
        if len(guild_warnings) > 15:
            embed.add_field(
                name="Note",
                value=f"Showing top 15 users. {len(guild_warnings) - 15} more users have warnings.",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Warnings(bot))
