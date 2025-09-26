import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger('Moderation')

class Moderation(commands.Cog):
    """Moderation commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kicks a user from the server"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{member} kicked by {ctx.author} for: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error kicking {member}: {e}")

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Mutes a user in the server"""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        # Create mute role if it doesn't exist
        if not mute_role:
            try:
                mute_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
            except discord.Forbidden:
                await ctx.send("❌ I don't have permission to create the Muted role.")
                return

        try:
            await member.add_roles(mute_role, reason=reason)
            embed = discord.Embed(
                title="Member Muted",
                description=f"{member.mention} has been muted.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{member} muted by {ctx.author} for: {reason}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to mute this member.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error muting {member}: {e}")

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute_user(self, ctx, member: discord.Member):
        """Unmutes a user in the server"""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not mute_role:
            await ctx.send("❌ Muted role not found.")
            return

        if mute_role not in member.roles:
            await ctx.send("❌ This member is not muted.")
            return

        try:
            await member.remove_roles(mute_role)
            embed = discord.Embed(
                title="Member Unmuted",
                description=f"{member.mention} has been unmuted.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"{member} unmuted by {ctx.author}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unmute this member.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error unmuting {member}: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
