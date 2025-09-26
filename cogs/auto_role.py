import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger('AutoRole')

class AutoRole(commands.Cog):
    """Automatic role assignment system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.auto_roles = {}  # Guild ID -> Role ID mapping

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Assign roles when a member joins"""
        guild_id = member.guild.id
        
        if guild_id in self.auto_roles:
            role_id = self.auto_roles[guild_id]
            role = member.guild.get_role(role_id)
            
            if role:
                try:
                    await member.add_roles(role, reason="Auto role assignment")
                    logger.info(f"Assigned role {role.name} to {member} in {member.guild}")
                except discord.Forbidden:
                    logger.warning(f"Missing permissions to assign role {role.name} in {member.guild}")
                except discord.HTTPException as e:
                    logger.error(f"Failed to assign role to {member}: {e}")

    @commands.command(name='setautorole')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def set_auto_role(self, ctx, role: discord.Role):
        """Set the auto-assign role for new members"""
        # Check if bot can assign this role
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ I cannot assign this role as it's higher than or equal to my highest role.")
            return

        self.auto_roles[ctx.guild.id] = role.id
        
        embed = discord.Embed(
            title="Auto Role Set",
            description=f"New members will automatically receive the {role.mention} role.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        logger.info(f"Auto role set to {role.name} in {ctx.guild}")

    @commands.command(name='removeautorole')
    @commands.has_permissions(manage_roles=True)
    async def remove_auto_role(self, ctx):
        """Remove the auto-assign role"""
        if ctx.guild.id in self.auto_roles:
            del self.auto_roles[ctx.guild.id]
            await ctx.send("✅ Auto role assignment has been disabled.")
            logger.info(f"Auto role removed in {ctx.guild}")
        else:
            await ctx.send("❌ No auto role is currently set.")

    @commands.command(name='autoroleinfo')
    async def auto_role_info(self, ctx):
        """Show current auto role settings"""
        if ctx.guild.id in self.auto_roles:
            role_id = self.auto_roles[ctx.guild.id]
            role = ctx.guild.get_role(role_id)
            
            if role:
                embed = discord.Embed(
                    title="Auto Role Information",
                    description=f"Current auto role: {role.mention}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Role Name", value=role.name, inline=True)
                embed.add_field(name="Role ID", value=role.id, inline=True)
                embed.add_field(name="Member Count", value=len(role.members), inline=True)
            else:
                embed = discord.Embed(
                    title="Auto Role Information",
                    description="Auto role is set but the role no longer exists.",
                    color=discord.Color.red()
                )
        else:
            embed = discord.Embed(
                title="Auto Role Information",
                description="No auto role is currently set.",
                color=discord.Color.grey()
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='assignrole')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def assign_role_manual(self, ctx, member: discord.Member, role: discord.Role):
        """Manually assign a role to a member"""
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ I cannot assign this role as it's higher than or equal to my highest role.")
            return

        if role in member.roles:
            await ctx.send(f"❌ {member.mention} already has the {role.mention} role.")
            return

        try:
            await member.add_roles(role, reason=f"Manually assigned by {ctx.author}")
            
            embed = discord.Embed(
                title="Role Assigned",
                description=f"Successfully assigned {role.mention} to {member.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            logger.info(f"Manually assigned role {role.name} to {member} by {ctx.author}")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to assign this role.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error assigning role to {member}: {e}")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))
