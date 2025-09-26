import discord
from discord import app_commands
from discord.ext import commands
import logging

# Custom check for bot owner
def is_bot_owner():
    def predicate(interaction: discord.Interaction):
        return interaction.user.id == 828835928331255818
    return app_commands.check(predicate)

# Custom check for server administrator
def is_server_admin():
    def predicate(interaction: discord.Interaction):
        if not interaction.guild:
            return False
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

# Custom check for server owner
def is_server_owner():
    def predicate(interaction: discord.Interaction):
        if not interaction.guild:
            return False
        return interaction.user.id == interaction.guild.owner_id
    return app_commands.check(predicate)

class Commands(commands.Cog):
    """A cog providing custom check decorators for bot permissions."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        # Register global error handler for command tree
        self.bot.tree.error(self.tree_error)

    async def tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Global error handler for all application commands."""
        try:
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else discord.utils.MISSING
            )
            if isinstance(error, app_commands.CommandOnCooldown):
                embed.title = "Command on Cooldown"
                embed.description = f"You're on cooldown. Try again in {error.retry_after:.2f} seconds."
            elif isinstance(error, app_commands.CheckFailure):
                embed.title = "Permission Denied"
                embed.description = "This command is restricted to authorized users (e.g., bot owner, server admin, or server owner)."
                self.logger.warning(f"CheckFailure in command {interaction.command.name} by {interaction.user.id}: {error}")
            elif isinstance(error, app_commands.BotMissingPermissions):
                embed.title = "Bot Missing Permissions"
                embed.description = "I don't have the required permissions to perform this action."
            elif isinstance(error, app_commands.MissingPermissions):
                embed.title = "Missing Permissions"
                embed.description = "You don't have the required permissions to use this command."
            elif isinstance(error, app_commands.CommandInvokeError):
                embed.title = "Command Error"
                embed.description = f"An error occurred while processing the command: {str(error)}"
                self.logger.error(f"Command invoke error in {interaction.command.name}: {error}")
            else:
                embed.title = "Unexpected Error"
                embed.description = f"An error occurred while processing the command: {str(error)}"
                self.logger.error(f"Application command error in {interaction.command.name}: {error}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.errors.InteractionResponded:
            self.logger.warning(f"Interaction already responded or expired in tree_error for {interaction.command.name}")
            try:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Error",
                        description="An error occurred and the command could not be processed.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
            except Exception as e:
                self.logger.error(f"Failed to send followup in tree_error: {e}")

async def setup(bot):
    try:
        await bot.add_cog(Commands(bot))
    except Exception as e:
        print(f"Error loading Commands cog: {e}")