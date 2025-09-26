import discord
from discord.ext import commands
from utils.logger import setup_logger
import time

logger = setup_logger('AFK')

class AFK(commands.Cog):
    """AFK system for users"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='afk')
    async def set_afk(self, ctx, *, reason="AFK"):
        """Set yourself as AFK"""
        user_id = ctx.author.id
        
        # Store AFK status
        self.bot.afk_users[user_id] = {
            'reason': reason,
            'time': time.time()
        }
        
        embed = discord.Embed(
            title="AFK Status Set",
            description=f"{ctx.author.mention} is now AFK: {reason}",
            color=discord.Color.yellow()
        )
        await ctx.send(embed=embed)
        logger.info(f"{ctx.author} set AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Check for AFK users in messages"""
        if message.author.bot:
            return

        # Check if the message author is AFK and should be removed from AFK
        if message.author.id in self.bot.afk_users:
            del self.bot.afk_users[message.author.id]
            embed = discord.Embed(
                title="Welcome Back!",
                description=f"{message.author.mention} is no longer AFK.",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed, delete_after=5)
            logger.info(f"{message.author} removed from AFK")

        # Check if any mentioned users are AFK
        for mentioned_user in message.mentions:
            if mentioned_user.id in self.bot.afk_users:
                afk_data = self.bot.afk_users[mentioned_user.id]
                afk_time = time.time() - afk_data['time']
                
                # Convert time to readable format
                if afk_time < 60:
                    time_str = f"{int(afk_time)} seconds"
                elif afk_time < 3600:
                    time_str = f"{int(afk_time / 60)} minutes"
                else:
                    time_str = f"{int(afk_time / 3600)} hours"
                
                embed = discord.Embed(
                    title="User is AFK",
                    description=f"{mentioned_user.mention} is currently AFK: {afk_data['reason']}",
                    color=discord.Color.orange()
                )
                embed.add_field(name="AFK for", value=time_str, inline=True)
                await message.channel.send(embed=embed, delete_after=10)

    @commands.command(name='afklist')
    async def afk_list(self, ctx):
        """List all AFK users in the server"""
        if not self.bot.afk_users:
            await ctx.send("No users are currently AFK.")
            return

        embed = discord.Embed(
            title="AFK Users",
            color=discord.Color.blue()
        )
        
        guild_afk_users = []
        for user_id, afk_data in self.bot.afk_users.items():
            user = ctx.guild.get_member(user_id)
            if user:
                afk_time = time.time() - afk_data['time']
                if afk_time < 60:
                    time_str = f"{int(afk_time)}s"
                elif afk_time < 3600:
                    time_str = f"{int(afk_time / 60)}m"
                else:
                    time_str = f"{int(afk_time / 3600)}h"
                
                guild_afk_users.append(f"{user.mention} - {afk_data['reason']} ({time_str})")

        if guild_afk_users:
            embed.description = "\n".join(guild_afk_users[:10])  # Limit to 10 users
            if len(guild_afk_users) > 10:
                embed.add_field(name="Note", value=f"And {len(guild_afk_users) - 10} more...", inline=False)
        else:
            embed.description = "No AFK users in this server."

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AFK(bot))
