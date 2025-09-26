import discord
from discord import app_commands
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger('SlashCommands')

class SlashCommands(commands.Cog):
    """Slash commands implementation"""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: {latency}ms",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Get server information")
    async def server_info(self, interaction: discord.Interaction):
        """Display server information"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"Server Information - {guild.name}",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get user information")
    @app_commands.describe(member="The member to get information about")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        """Display user information"""
        if member is None:
            if isinstance(interaction.user, discord.Member):
                member = interaction.user
            else:
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return

        embed = discord.Embed(
            title=f"User Information - {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="Username", value=str(member), inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:F>", inline=True)
        embed.add_field(name="Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:F>", inline=True)
        embed.add_field(name="Roles", value=len(member.roles) - 1, inline=True)  # -1 to exclude @everyone
        
        if member.premium_since:
            embed.add_field(name="Boosting Since", value=f"<t:{int(member.premium_since.timestamp())}:F>", inline=True)
        
        # Show top role (excluding @everyone)
        top_role = member.top_role if member.top_role.name != "@everyone" else None
        if top_role:
            embed.add_field(name="Top Role", value=top_role.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(member="The member to get the avatar of")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        """Display user's avatar"""
        if member is None:
            if isinstance(interaction.user, discord.Member):
                member = interaction.user
            else:
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return

        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=discord.Color.blue()
        )
        
        if member.avatar:
            embed.set_image(url=member.avatar.url)
            embed.add_field(
                name="Download Links",
                value=f"[PNG]({member.avatar.replace(format='png', size=1024).url}) | "
                      f"[JPG]({member.avatar.replace(format='jpg', size=1024).url}) | "
                      f"[WEBP]({member.avatar.replace(format='webp', size=1024).url})",
                inline=False
            )
        else:
            embed.description = "This user has no custom avatar."
            embed.set_image(url=member.default_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quickpoll", description="Create a quick yes/no poll")
    @app_commands.describe(question="The poll question")
    async def quick_poll_slash(self, interaction: discord.Interaction, question: str):
        """Create a quick yes/no poll using slash commands"""
        embed = discord.Embed(
            title="📊 Quick Poll",
            description=question,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Poll created by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        
        # Get the message to add reactions
        message = await interaction.original_response()
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(
        time="Time until reminder (e.g., 10m, 1h, 30s)",
        reminder="What to remind you about"
    )
    async def remind(self, interaction: discord.Interaction, time: str, reminder: str):
        """Set a reminder (basic implementation)"""
        # This is a simplified version - in a full implementation, you'd want to store reminders
        # and have a background task to check and send them
        
        embed = discord.Embed(
            title="⏰ Reminder Set",
            description=f"I'll try to remind you about: {reminder}",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Time", value=time, inline=True)
        embed.add_field(
            name="Note",
            value="This is a basic implementation. Reminder functionality would need a proper database and background tasks.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="botinfo", description="Get information about the bot")
    async def botinfo(self, interaction: discord.Interaction):
        """Display bot information"""
        embed = discord.Embed(
            title="Bot Information",
            color=discord.Color.purple()
        )
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text="Created by @vizenn_ae")

        
        embed.add_field(
            name="Features",
            value="• Moderation Commands\n• Anti-Nuke Protection\n• Auto-Moderation\n• Warning System\n• And more!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Error handler for slash commands"""
        try:
            if isinstance(error, app_commands.CommandOnCooldown):
                embed = discord.Embed(
                    title="Command on Cooldown",
                    description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
                    color=discord.Color.red()
                )
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(embed=embed, ephemeral=True)
            elif isinstance(error, app_commands.MissingPermissions):
                embed = discord.Embed(
                    title="Missing Permissions",
                    description="You don't have permission to use this command.",
                    color=discord.Color.red()
                )
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                logger.error(f"Slash command error: {error}")
                embed = discord.Embed(
                    title="Command Error",
                    description="An unexpected error occurred while executing this command.",
                    color=discord.Color.red()
                )
                
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

    def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Sync error handler for the cog"""
        import asyncio
        asyncio.create_task(self.on_app_command_error(interaction, error))

    @app_commands.command(name="purge", description="Delete a specified number of messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    async def purge_slash(self, interaction: discord.Interaction, amount: int):
        """Delete a specified number of messages using slash commands"""
        if not interaction.user.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Messages' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount > 100:
            embed = discord.Embed(
                title="❌ Invalid Amount", 
                description="Cannot delete more than 100 messages at once.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount < 1:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Amount must be at least 1.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await interaction.response.defer()
            deleted = await interaction.channel.purge(limit=amount)
            
            embed = discord.Embed(
                title="✅ Messages Purged",
                description=f"Successfully deleted {len(deleted)} messages.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{len(deleted)} messages purged by {interaction.user} in {interaction.channel}")
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to delete messages in this channel.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.error(f"Error purging messages: {e}")

    @app_commands.command(name="nuke", description="Delete all messages and recreate the channel")
    @app_commands.describe(confirmation="Type 'confirm' to proceed with nuking the channel")
    async def nuke_slash(self, interaction: discord.Interaction, confirmation: str):
        """Nuke a channel using slash commands"""
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Channels' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if confirmation.lower() != "confirm":
            embed = discord.Embed(
                title="⚠️ Nuke Confirmation Required",
                description=f"This will delete ALL messages in {interaction.channel.mention} and recreate the channel.\n\n"
                           f"Use `/nuke confirm` to proceed.",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await interaction.response.defer()
            
            # Store channel information
            channel = interaction.channel
            channel_name = channel.name
            channel_position = channel.position
            channel_category = channel.category
            channel_topic = channel.topic
            channel_overwrites = channel.overwrites

            # Create new channel
            new_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=channel_category,
                topic=channel_topic,
                position=channel_position,
                overwrites=channel_overwrites
            )

            # Delete old channel
            await channel.delete()

            # Send confirmation in new channel
            embed = discord.Embed(
                title="💥 Channel Nuked",
                description="This channel has been successfully nuked and recreated!",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            await new_channel.send(embed=embed)
            
            logger.info(f"Channel {channel_name} nuked by {interaction.user}")

        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permission Error",
                description="I don't have permission to manage channels.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while nuking the channel: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.error(f"Error nuking channel: {e}")

    @app_commands.command(name="antinuke", description="Check or toggle anti-nuke protection")
    @app_commands.describe(status="Set anti-nuke status: on/off (leave empty to check current status)")
    async def antinuke_slash(self, interaction: discord.Interaction, status: str = None):
        """Toggle anti-nuke protection using slash commands"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get the anti-nuke cog
        antinuke_cog = self.bot.get_cog('AntiNuke')
        if not antinuke_cog:
            embed = discord.Embed(
                title="❌ Error",
                description="Anti-nuke system is not available.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if status is None:
            # Show current status
            protection_status = "enabled" if antinuke_cog.protection_enabled else "disabled"
            embed = discord.Embed(
                title="🛡️ Anti-Nuke Status",
                description=f"Anti-nuke protection is currently **{protection_status}**.",
                color=discord.Color.blue()
            )
        elif status.lower() in ['on', 'enable', 'true']:
            antinuke_cog.protection_enabled = True
            embed = discord.Embed(
                title="✅ Anti-Nuke Enabled",
                description="Anti-nuke protection has been **enabled**.",
                color=discord.Color.green()
            )
        elif status.lower() in ['off', 'disable', 'false']:
            antinuke_cog.protection_enabled = False
            embed = discord.Embed(
                title="❌ Anti-Nuke Disabled",
                description="Anti-nuke protection has been **disabled**.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="❌ Invalid Status",
                description="Please use 'on' or 'off' to set the status.",
                color=discord.Color.red()
            )

        await interaction.response.send_message(embed=embed)

    # === QUARANTINE SLASH COMMANDS ===
    
    @app_commands.command(name="quarantine", description="Quarantine a user (restrict their channel access)")
    @app_commands.describe(member="The member to quarantine", reason="Reason for quarantine")
    async def quarantine_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Quarantine a user using slash commands"""
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Roles' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member == interaction.user:
            embed = discord.Embed(title="❌ Error", description="You cannot quarantine yourself.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member.bot:
            embed = discord.Embed(title="❌ Error", description="You cannot quarantine bots.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get quarantine cog for the actual implementation
        quarantine_cog = self.bot.get_cog('Quarantine')
        if not quarantine_cog:
            embed = discord.Embed(title="❌ Error", description="Quarantine system is not available.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            quarantine_role = await quarantine_cog.setup_quarantine_role(interaction.guild)
            if not quarantine_role:
                embed = discord.Embed(title="❌ Error", description="Failed to setup quarantine role.", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return

            await member.add_roles(quarantine_role, reason=f"Quarantined by {interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="🔒 User Quarantined",
                description=f"{member.mention} has been quarantined.",
                color=discord.Color.red()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"{member} quarantined by {interaction.user}: {reason}")

        except discord.Forbidden:
            embed = discord.Embed(title="❌ Permission Error", description="I don't have permission to assign roles.", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=discord.Color.red())
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="unquarantine", description="Remove quarantine from a user")
    @app_commands.describe(member="The member to unquarantine", reason="Reason for removing quarantine")
    async def unquarantine_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Remove quarantine from a user using slash commands"""
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Roles' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        quarantine_role = discord.utils.get(interaction.guild.roles, name="Quarantined")
        if not quarantine_role or quarantine_role not in member.roles:
            embed = discord.Embed(title="❌ Error", description="This user is not quarantined.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await member.remove_roles(quarantine_role, reason=f"Unquarantined by {interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="🔓 User Unquarantined",
                description=f"{member.mention} has been removed from quarantine.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{member} unquarantined by {interaction.user}: {reason}")

        except discord.Forbidden:
            embed = discord.Embed(title="❌ Permission Error", description="I don't have permission to remove roles.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # === AFK SLASH COMMANDS ===

    @app_commands.command(name="afk", description="Set yourself as AFK")
    @app_commands.describe(reason="Reason for being AFK")
    async def afk_slash(self, interaction: discord.Interaction, reason: str = "AFK"):
        """Set AFK status using slash commands"""
        user_id = interaction.user.id
        
        if not hasattr(self.bot, 'afk_users'):
            self.bot.afk_users = {}
        
        # Store AFK status
        import time
        self.bot.afk_users[user_id] = {
            'reason': reason,
            'time': time.time()
        }
        
        embed = discord.Embed(
            title="😴 AFK Status Set",
            description=f"{interaction.user.mention} is now AFK: {reason}",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user} set AFK: {reason}")

    @app_commands.command(name="afkremove", description="Remove AFK status from a user (moderators only)")
    @app_commands.describe(member="The member to remove AFK status from")
    async def afkremove_slash(self, interaction: discord.Interaction, member: discord.Member):
        """Remove AFK status from a user using slash commands"""
        if not interaction.user.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Messages' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not hasattr(self.bot, 'afk_users') or member.id not in self.bot.afk_users:
            embed = discord.Embed(title="❌ Error", description="This user is not AFK.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        del self.bot.afk_users[member.id]
        embed = discord.Embed(
            title="✅ AFK Removed",
            description=f"{member.mention} is no longer AFK.",
            color=discord.Color.green()
        )
        embed.add_field(name="Removed by", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{member} AFK status removed by {interaction.user}")

    # === TIMEOUT SLASH COMMANDS ===

    @app_commands.command(name="timeout", description="Timeout a user for a specified duration")
    @app_commands.describe(member="The member to timeout", duration="Duration (e.g., 10m, 1h, 30s)", reason="Reason for timeout")
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        """Timeout a user using slash commands"""
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Moderate Members' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member == interaction.user:
            embed = discord.Embed(title="❌ Error", description="You cannot timeout yourself.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get timeout cog for duration parsing
        timeout_cog = self.bot.get_cog('Timeout')
        if not timeout_cog:
            embed = discord.Embed(title="❌ Error", description="Timeout system is not available.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        duration_seconds = timeout_cog.parse_time(duration)
        if not duration_seconds:
            embed = discord.Embed(title="❌ Invalid Duration", description="Use formats like: `10m`, `1h`, `30s`, `2d`", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            from datetime import datetime, timedelta
            timeout_until = datetime.now() + timedelta(seconds=duration_seconds)
            await member.timeout(timeout_until, reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="⏰ User Timed Out",
                description=f"{member.mention} has been timed out for {duration}.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{member} timed out by {interaction.user} for {duration}: {reason}")

        except discord.Forbidden:
            embed = discord.Embed(title="❌ Permission Error", description="I don't have permission to timeout this user.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="untimeout", description="Remove timeout from a user")
    @app_commands.describe(member="The member to remove timeout from", reason="Reason for removing timeout")
    async def untimeout_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Remove timeout from a user using slash commands"""
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Moderate Members' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not member.timed_out:
            embed = discord.Embed(title="❌ Error", description="This user is not timed out.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await member.timeout(None, reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"Timeout has been removed from {member.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Timeout removed from {member} by {interaction.user}: {reason}")

        except discord.Forbidden:
            embed = discord.Embed(title="❌ Permission Error", description="I don't have permission to remove timeout from this user.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # === MODERATION SLASH COMMANDS ===

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(member="The member to kick", reason="Reason for kicking")
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a user using slash commands"""
        if not interaction.user.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Kick Members' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member == interaction.user:
            embed = discord.Embed(title="❌ Error", description="You cannot kick yourself.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await member.kick(reason=f"{interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{member} kicked by {interaction.user}: {reason}")

        except discord.Forbidden:
            embed = discord.Embed(title="❌ Permission Error", description="I don't have permission to kick this user.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(member="The member to ban", reason="Reason for banning", delete_days="Days of messages to delete (0-7)")
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        """Ban a user using slash commands"""
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Ban Members' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member == interaction.user:
            embed = discord.Embed(title="❌ Error", description="You cannot ban yourself.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if delete_days < 0 or delete_days > 7:
            embed = discord.Embed(title="❌ Error", description="Delete days must be between 0 and 7.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await member.ban(reason=f"{interaction.user}: {reason}", delete_message_days=delete_days)
            
            embed = discord.Embed(
                title="🔨 User Banned",
                description=f"{member.mention} has been banned from the server.",
                color=discord.Color.red()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            if delete_days > 0:
                embed.add_field(name="Messages Deleted", value=f"{delete_days} days", inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"{member} banned by {interaction.user}: {reason}")

        except discord.Forbidden:
            embed = discord.Embed(title="❌ Permission Error", description="I don't have permission to ban this user.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=f"An error occurred: {str(e)}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(member="The member to warn", reason="Reason for warning")
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Warn a user using slash commands"""
        if not interaction.user.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Messages' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member == interaction.user:
            embed = discord.Embed(title="❌ Error", description="You cannot warn yourself.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get warnings cog for the actual implementation
        warnings_cog = self.bot.get_cog('Warnings')
        if not warnings_cog:
            embed = discord.Embed(title="❌ Error", description="Warning system is not available.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not hasattr(self.bot, 'warnings'):
            self.bot.warnings = {}

        # Add warning
        if member.id not in self.bot.warnings:
            self.bot.warnings[member.id] = []
        
        warning_data = {
            'reason': reason,
            'moderator': str(interaction.user),
            'timestamp': discord.utils.utcnow().isoformat()
        }
        self.bot.warnings[member.id].append(warning_data)
        
        warning_count = len(self.bot.warnings[member.id])
        
        embed = discord.Embed(
            title="⚠️ User Warned",
            description=f"{member.mention} has been warned.",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Total Warnings", value=str(warning_count), inline=True)
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"{member} warned by {interaction.user}: {reason} (Total: {warning_count})")

    # === AUTO ROLE SLASH COMMANDS ===

    @app_commands.command(name="autorole", description="Manage auto-role assignment for new members")
    @app_commands.describe(action="Action to perform", role="Role to set/remove")
    @app_commands.choices(action=[
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="info", value="info")
    ])
    async def autorole_slash(self, interaction: discord.Interaction, action: str, role: discord.Role = None):
        """Manage auto-role assignment using slash commands"""
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You need the 'Manage Roles' permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        autorole_cog = self.bot.get_cog('AutoRole')
        if not autorole_cog:
            embed = discord.Embed(title="❌ Error", description="Auto role system is not available.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if action == "set":
            if not role:
                embed = discord.Embed(title="❌ Error", description="You must specify a role to set.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            autorole_cog.auto_roles[interaction.guild.id] = role.id
            embed = discord.Embed(
                title="✅ Auto Role Set",
                description=f"New members will automatically receive the {role.mention} role.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"Auto role set to {role.name} in {interaction.guild}")

        elif action == "remove":
            if interaction.guild.id in autorole_cog.auto_roles:
                del autorole_cog.auto_roles[interaction.guild.id]
                embed = discord.Embed(title="✅ Auto Role Removed", description="Auto role assignment has been disabled.", color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
                logger.info(f"Auto role removed in {interaction.guild}")
            else:
                embed = discord.Embed(title="❌ Error", description="No auto role is currently set.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)

        elif action == "info":
            if interaction.guild.id in autorole_cog.auto_roles:
                role_id = autorole_cog.auto_roles[interaction.guild.id]
                role = interaction.guild.get_role(role_id)
                
                if role:
                    embed = discord.Embed(
                        title="🤖 Auto Role Information",
                        description=f"Current auto role: {role.mention}",
                        color=discord.Color.blue()
                    )
                else:
                    embed = discord.Embed(title="❌ Error", description="Auto role was deleted. Please set a new one.", color=discord.Color.red())
            else:
                embed = discord.Embed(title="ℹ️ No Auto Role", description="No auto role is currently set for this server.", color=discord.Color.blue())
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
