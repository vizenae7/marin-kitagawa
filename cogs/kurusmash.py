import discord
from discord.ext import commands
from discord import app_commands

OWNER_ID = 828835928331255818  # Vineet
SIMULATE = False
WHITELIST_ROLES = ["Admin", "Moderator", "Bot"]

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.confirmed = False

    @discord.ui.button(label="💥 Confirm Kurusmash", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can confirm this.", ephemeral=True)
            return
        self.confirmed = True
        await interaction.response.send_message("⚔️ Kurusmash confirmed. Executing...", ephemeral=True)
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛑 Kurusmash cancelled.", ephemeral=True)
        self.stop()

class KuruSmash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kurusmash", description="Owner only.")
    @app_commands.describe(guild_id="The ID of the guild to smash")
    async def kurusmash(self, interaction: discord.Interaction, guild_id: str):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
            return

        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                await interaction.response.send_message("❌ Bot is not in that guild.", ephemeral=True)
                return

            members_to_kick = [
                m for m in guild.members
                if m != guild.owner and not any(r.name in WHITELIST_ROLES for r in m.roles)
            ]

            if SIMULATE:
                embed = discord.Embed(title="🧪 Kurusmash Simulation", color=discord.Color.orange())
                embed.add_field(name="Would Kick", value="\n".join(m.name for m in members_to_kick) or "None", inline=False)
                embed.set_footer(text=f"Total: {len(members_to_kick)} members targeted")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            view = ConfirmView()
            embed = discord.Embed(title="⚔️ Bankai: Kurusmash — Severance of Bonds", color=discord.Color.dark_red())
            embed.description = f"Guild: **{guild.name}**\nMembers targeted: **{len(members_to_kick)}**\n\nPress confirm to execute."
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await view.wait()

            if not view.confirmed:
                return

            kicked = []
            failed = []

            for member in members_to_kick:
                try:
                    await member.kick(reason="Kurusmash command")
                    kicked.append(member.name)
                except Exception as e:
                    failed.append(f"{member.name} ({e})")

            report = discord.Embed(title="☠️ Kurusmash Report", color=discord.Color.red())
            report.add_field(name="Kicked Members", value="\n".join(kicked) or "None", inline=False)
            if failed:
                report.add_field(name="Failed to Kick", value="\n".join(failed), inline=False)
            report.set_footer(text=f"Total: {len(kicked)} kicked, {len(failed)} failed")

            await interaction.followup.send(embed=report, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KuruSmash(bot))
