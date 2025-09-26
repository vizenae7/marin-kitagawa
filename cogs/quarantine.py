import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger('Quarantine')

class Quarantine(commands.Cog):
    """Quarantine system to restrict user access"""
    
    def __init__(self, bot):
        self.bot = bot

    async def setup_quarantine_role(self, guild):
        """Create and configure the quarantine role"""
        quarantine_role = discord.utils.get(guild.roles, name="Quarantined")
        
        if not quarantine_role:
            try:
                # Create the quarantine role
                quarantine_role = await guild.create_role(
                    name="Quarantined",
                    color=discord.Color.dark_red(),
                    reason="Quarantine role setup"
                )
                
                # Set permissions for all channels
                for channel in guild.channels:
                    try:
                        if isinstance(channel, discord.TextChannel):
                            # Deny all text permissions
                            await channel.set_permissions(
                                quarantine_role,
                                send_messages=False,
                                add_reactions=False,
                                create_public_threads=False,
                                create_private_threads=False,
                                send_messages_in_threads=False,
                                reason="Quarantine setup"
                            )
                        elif isinstance(channel, discord.VoiceChannel):
                            # Deny voice permissions
                            await channel.set_permissions(
                                quarantine_role,
                                connect=False,
                                speak=False,
                                stream=False,
                                use_voice_activation=False,
                                reason="Quarantine setup"
                            )
                    except discord.Forbidden:
                        logger.warning(f"Cannot set permissions for {channel.name}")
                
                logger.info(f"Quarantine role created and configured in {guild.name}")
                
            except discord.Forbidden:
                logger.error(f"Missing permissions to create quarantine role in {guild.name}")
                return None
        
        return quarantine_role

    @commands.command(name='quarantine')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def quarantine_user(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Quarantine a user (restrict their access to channels)"""
        if member == ctx.author:
            await ctx.send("❌ You cannot quarantine yourself.")
            return
        
        if member.bot:
            await ctx.send("❌ You cannot quarantine bots.")
            return

        # Check if user is higher in hierarchy
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot quarantine someone with equal or higher roles.")
            return

        # Setup quarantine role
        quarantine_role = await self.setup_quarantine_role(ctx.guild)
        if not quarantine_role:
            await ctx.send("❌ Failed to setup quarantine role. Check my permissions.")
            return

        # Check if already quarantined
        if quarantine_role in member.roles:
            await ctx.send(f"❌ {member.mention} is already quarantined.")
            return

        try:
            # Add quarantine role
            await member.add_roles(quarantine_role, reason=f"Quarantined by {ctx.author}: {reason}")
            
            # Try to send DM to user
            try:
                dm_embed = discord.Embed(
                    title="🔒 You have been quarantined",
                    description=f"You have been quarantined in **{ctx.guild.name}**",
                    color=discord.Color.dark_red()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                dm_embed.add_field(
                    name="What does this mean?",
                    value="You have restricted access to channels until further notice.",
                    inline=False
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled

            # Send confirmation
            embed = discord.Embed(
                title="User Quarantined",
                description=f"{member.mention} has been quarantined.",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"{member} quarantined by {ctx.author} for: {reason}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to quarantine this member.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error quarantining {member}: {e}")

    @commands.command(name='unquarantine')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unquarantine_user(self, ctx, member: discord.Member):
        """Remove quarantine from a user"""
        quarantine_role = discord.utils.get(ctx.guild.roles, name="Quarantined")
        
        if not quarantine_role:
            await ctx.send("❌ Quarantine role not found.")
            return

        if quarantine_role not in member.roles:
            await ctx.send(f"❌ {member.mention} is not quarantined.")
            return

        try:
            await member.remove_roles(quarantine_role, reason=f"Unquarantined by {ctx.author}")
            
            # Try to send DM to user
            try:
                dm_embed = discord.Embed(
                    title="🔓 Quarantine Removed",
                    description=f"Your quarantine has been lifted in **{ctx.guild.name}**",
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

            # Send confirmation
            embed = discord.Embed(
                title="Quarantine Removed",
                description=f"{member.mention} has been unquarantined.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"{member} unquarantined by {ctx.author}")

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unquarantine this member.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error unquarantining {member}: {e}")

    @commands.command(name='quarantined')
    @commands.has_permissions(manage_roles=True)
    async def list_quarantined(self, ctx):
        """List all quarantined users"""
        quarantine_role = discord.utils.get(ctx.guild.roles, name="Quarantined")
        
        if not quarantine_role:
            await ctx.send("❌ Quarantine role not found.")
            return

        quarantined_members = [member for member in ctx.guild.members if quarantine_role in member.roles]

        if not quarantined_members:
            await ctx.send("✅ No users are currently quarantined.")
            return

        embed = discord.Embed(
            title="Quarantined Users",
            color=discord.Color.dark_red()
        )

        member_list = []
        for member in quarantined_members[:15]:  # Limit to 15 users
            member_list.append(f"{member.mention} ({member.display_name})")

        embed.description = "\n".join(member_list)
        
        if len(quarantined_members) > 15:
            embed.add_field(
                name="Note",
                value=f"Showing 15 of {len(quarantined_members)} quarantined users.",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Automatically set quarantine permissions for new channels"""
        quarantine_role = discord.utils.get(channel.guild.roles, name="Quarantined")
        
        if quarantine_role:
            try:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(
                        quarantine_role,
                        send_messages=False,
                        add_reactions=False,
                        create_public_threads=False,
                        create_private_threads=False,
                        send_messages_in_threads=False,
                        reason="Auto-setup quarantine permissions"
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    await channel.set_permissions(
                        quarantine_role,
                        connect=False,
                        speak=False,
                        stream=False,
                        use_voice_activation=False,
                        reason="Auto-setup quarantine permissions"
                    )
                logger.info(f"Set quarantine permissions for new channel: {channel.name}")
            except discord.Forbidden:
                logger.warning(f"Cannot set quarantine permissions for new channel: {channel.name}")

async def setup(bot):
    await bot.add_cog(Quarantine(bot))
