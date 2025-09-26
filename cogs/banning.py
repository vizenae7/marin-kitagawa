import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger('Banning')

class Banning(commands.Cog):
    """Banning system for permanent user removal"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, delete_days: int = 0, *, reason="No reason provided"):
        """Ban a user from the server"""
        if member == ctx.author:
            await ctx.send("❌ You cannot ban yourself.")
            return
        
        if member.bot and member == ctx.bot.user:
            await ctx.send("❌ I cannot ban myself.")
            return

        # Check if user is higher in hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban someone with equal or higher roles.")
            return

        # Validate delete_days parameter
        if delete_days < 0 or delete_days > 7:
            await ctx.send("❌ Delete days must be between 0 and 7.")
            return

        try:
            # Try to send DM before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 You have been banned",
                    description=f"You have been banned from **{ctx.guild.name}**",
                    color=discord.Color.red()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                if delete_days > 0:
                    dm_embed.add_field(
                        name="Message Deletion",
                        value=f"Your messages from the last {delete_days} day(s) have been deleted.",
                        inline=False
                    )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled

            # Ban the user
            await member.ban(
                reason=f"Banned by {ctx.author}: {reason}",
                delete_message_days=delete_days
            )
            
            # Send confirmation
            embed = discord.Embed(
                title="User Banned",
                description=f"{member.mention} has been banned from the server.",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=f"{member} (ID: {member.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            if delete_days > 0:
                embed.add_field(name="Messages Deleted", value=f"Last {delete_days} day(s)", inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"{member} banned by {ctx.author} for: {reason}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to ban member: {str(e)}")
            logger.error(f"Error banning {member}: {e}")

    @commands.command(name='softban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def soft_ban(self, ctx, member: discord.Member, delete_days: int = 1, *, reason="No reason provided"):
        """Soft ban a user (ban then immediately unban to delete messages)"""
        if member == ctx.author:
            await ctx.send("❌ You cannot soft ban yourself.")
            return

        # Check if user is higher in hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot soft ban someone with equal or higher roles.")
            return

        # Validate delete_days parameter
        if delete_days < 0 or delete_days > 7:
            await ctx.send("❌ Delete days must be between 0 and 7.")
            return

        try:
            # Try to send DM before soft banning
            try:
                dm_embed = discord.Embed(
                    title="⚠️ You have been soft banned",
                    description=f"You have been soft banned from **{ctx.guild.name}**",
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                dm_embed.add_field(
                    name="What is a soft ban?",
                    value=f"Your messages from the last {delete_days} day(s) have been deleted, but you can rejoin the server.",
                    inline=False
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

            # Store member info for the embed
            member_info = f"{member} (ID: {member.id})"
            
            # Ban then immediately unban
            await member.ban(
                reason=f"Soft banned by {ctx.author}: {reason}",
                delete_message_days=delete_days
            )
            await ctx.guild.unban(
                member,
                reason=f"Soft ban unban by {ctx.author}"
            )
            
            # Send confirmation
            embed = discord.Embed(
                title="User Soft Banned",
                description=f"{member_info} has been soft banned.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Messages Deleted", value=f"Last {delete_days} day(s)", inline=True)
            embed.add_field(
                name="Note",
                value="User can rejoin the server but their recent messages have been deleted.",
                inline=False
            )
            
            await ctx.send(embed=embed)
            logger.info(f"{member_info} soft banned by {ctx.author} for: {reason}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to soft ban member: {str(e)}")
            logger.error(f"Error soft banning {member}: {e}")

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_user(self, ctx, user_id: int, *, reason="No reason provided"):
        """Unban a user by their ID"""
        try:
            # Get the banned user
            banned_user = await ctx.bot.fetch_user(user_id)
            
            # Check if user is actually banned
            try:
                ban_entry = await ctx.guild.fetch_ban(banned_user)
            except discord.NotFound:
                await ctx.send(f"❌ User with ID {user_id} is not banned.")
                return

            # Unban the user
            await ctx.guild.unban(banned_user, reason=f"Unbanned by {ctx.author}: {reason}")
            
            # Try to send DM to unbanned user
            try:
                dm_embed = discord.Embed(
                    title="✅ You have been unbanned",
                    description=f"You have been unbanned from **{ctx.guild.name}**",
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                dm_embed.add_field(
                    name="Rejoining",
                    value="You can now rejoin the server if you have an invite link.",
                    inline=False
                )
                await banned_user.send(embed=dm_embed)
            except discord.Forbidden:
                pass

            # Send confirmation
            embed = discord.Embed(
                title="User Unbanned",
                description=f"{banned_user} (ID: {banned_user.id}) has been unbanned.",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"{banned_user} unbanned by {ctx.author} for: {reason}")

        except discord.NotFound:
            await ctx.send(f"❌ User with ID {user_id} not found.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to unban user: {str(e)}")
            logger.error(f"Error unbanning user {user_id}: {e}")

    @commands.command(name='banlist', aliases=['bans'])
    @commands.has_permissions(ban_members=True)
    async def ban_list(self, ctx):
        """List all banned users"""
        try:
            bans = [ban async for ban in ctx.guild.bans()]
            
            if not bans:
                await ctx.send("✅ No users are currently banned.")
                return

            embed = discord.Embed(
                title=f"Banned Users ({len(bans)})",
                color=discord.Color.red()
            )

            ban_list = []
            for ban in bans[:15]:  # Limit to 15 users
                user = ban.user
                reason = ban.reason or "No reason provided"
                ban_list.append(f"**{user}** (ID: {user.id})\n└ Reason: {reason[:50]}{'...' if len(reason) > 50 else ''}")

            embed.description = "\n\n".join(ban_list)
            
            if len(bans) > 15:
                embed.add_field(
                    name="Note",
                    value=f"Showing 15 of {len(bans)} banned users.",
                    inline=False
                )

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to view the ban list.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to retrieve ban list: {str(e)}")
            logger.error(f"Error retrieving ban list: {e}")

    @commands.command(name='baninfo')
    @commands.has_permissions(ban_members=True)
    async def ban_info(self, ctx, user_id: int):
        """Get information about a specific ban"""
        try:
            user = await ctx.bot.fetch_user(user_id)
            
            try:
                ban_entry = await ctx.guild.fetch_ban(user)
                
                embed = discord.Embed(
                    title="Ban Information",
                    color=discord.Color.red()
                )
                embed.add_field(name="User", value=f"{user} (ID: {user.id})", inline=False)
                embed.add_field(name="Reason", value=ban_entry.reason or "No reason provided", inline=False)
                
                await ctx.send(embed=embed)
                
            except discord.NotFound:
                await ctx.send(f"❌ User with ID {user_id} is not banned.")
                
        except discord.NotFound:
            await ctx.send(f"❌ User with ID {user_id} not found.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to view ban information.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to retrieve ban information: {str(e)}")
            logger.error(f"Error retrieving ban info for {user_id}: {e}")

async def setup(bot):
    await bot.add_cog(Banning(bot))
