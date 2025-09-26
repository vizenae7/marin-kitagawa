import discord
from discord.ext import commands
from utils.logger import setup_logger
from config import BAD_WORDS

logger = setup_logger('AutoModeration')

class AutoModeration(commands.Cog):
    """Automatic moderation system"""

    def __init__(self, bot):
        self.bot = bot
        self.automod_enabled = True
        self.bad_words = BAD_WORDS
        self.spam_detection = {}  # Track message frequency per user

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for auto-moderation"""
        if message.author.bot or not self.automod_enabled:
            return

        # Whitelist immunity check
        whitelist_cog = self.bot.get_cog("Whitelist")
        if whitelist_cog and whitelist_cog.is_immune_to_automod(message.author, message.channel):
            logger.info(f"Skipped automod for whitelisted target: {message.author} in {message.channel}")
            return

        if await self.check_bad_words(message): return
        if await self.check_spam(message): return
        if await self.check_caps(message): return
        if await self.check_mass_mentions(message): return

    async def check_bad_words(self, message):
        """Check message for inappropriate content"""
        content_lower = message.content.lower()
        for bad_word in self.bad_words:
            if bad_word in content_lower:
                try:
                    await message.delete()
                    embed = discord.Embed(
                        title="Message Removed",
                        description=f"{message.author.mention}, your message contained inappropriate content and has been removed.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed, delete_after=5)
                    logger.info(f"Removed inappropriate message from {message.author} in {message.channel}")
                    return True
                except discord.Forbidden:
                    logger.warning("Missing permissions to delete messages")
                except discord.NotFound:
                    pass
        return False

    async def check_spam(self, message):
        """Check for spam messages"""
        user_id = message.author.id
        current_time = message.created_at.timestamp()

        if user_id not in self.spam_detection:
            self.spam_detection[user_id] = []

        self.spam_detection[user_id].append(current_time)
        self.spam_detection[user_id] = [
            t for t in self.spam_detection[user_id] if current_time - t < 10
        ]

        if len(self.spam_detection[user_id]) > 5:
            try:
                async for msg in message.channel.history(limit=10):
                    if msg.author == message.author and (current_time - msg.created_at.timestamp()) < 10:
                        try:
                            await msg.delete()
                        except (discord.NotFound, discord.Forbidden):
                            pass

                embed = discord.Embed(
                    title="Spam Detected",
                    description=f"{message.author.mention}, please slow down your messages.",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=5)
                self.spam_detection[user_id] = []
                logger.info(f"Spam detected from {message.author} in {message.channel}")
                return True
            except discord.Forbidden:
                logger.warning("Missing permissions to manage spam")
        return False

    async def check_caps(self, message):
        """Check for excessive caps"""
        if len(message.content) < 10:
            return False

        caps_count = sum(1 for c in message.content if c.isupper())
        caps_percentage = caps_count / len(message.content)

        if caps_percentage > 0.7:
            try:
                await message.delete()
                embed = discord.Embed(
                    title="Excessive Caps",
                    description=f"{message.author.mention}, please don't use excessive capital letters.",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=5)
                logger.info(f"Removed caps message from {message.author} in {message.channel}")
                return True
            except (discord.NotFound, discord.Forbidden):
                pass
        return False

    async def check_mass_mentions(self, message):
        """Check for mass mentions"""
        if len(message.mentions) > 5:
            try:
                await message.delete()
                embed = discord.Embed(
                    title="Mass Mention Detected",
                    description=f"{message.author.mention}, please don't mention too many users at once.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=5)
                logger.info(f"Removed mass mention from {message.author} in {message.channel}")
                return True
            except (discord.NotFound, discord.Forbidden):
                pass
        return False

    @commands.command(name='automod')
    @commands.has_permissions(manage_messages=True)
    async def toggle_automod(self, ctx, status: str = None):
        """Toggle auto-moderation on/off"""
        if status is None:
            status_text = "enabled" if self.automod_enabled else "disabled"
            await ctx.send(f"Auto-moderation is currently **{status_text}**.")
            return

        if status.lower() in ['on', 'enable', 'true']:
            self.automod_enabled = True
            await ctx.send("✅ Auto-moderation **enabled**.")
        elif status.lower() in ['off', 'disable', 'false']:
            self.automod_enabled = False
            await ctx.send("❌ Auto-moderation **disabled**.")
        else:
            await ctx.send("❌ Invalid status. Use `on` or `off`.")

    @commands.command(name='addbadword')
    @commands.has_permissions(manage_messages=True)
    async def add_bad_word(self, ctx, *, word):
        """Add a word to the bad words filter"""
        word_lower = word.lower()
        if word_lower not in self.bad_words:
            self.bad_words.append(word_lower)
            await ctx.send(f"✅ Added `{word}` to the bad words filter.")
            logger.info(f"Added bad word: {word}")
        else:
            await ctx.send(f"❌ `{word}` is already in the filter.")

    @commands.command(name='removebadword')
    @commands.has_permissions(manage_messages=True)
    async def remove_bad_word(self, ctx, *, word):
        """Remove a word from the bad words filter"""
        word_lower = word.lower()
        if word_lower in self.bad_words:
            self.bad_words.remove(word_lower)
            await ctx.send(f"✅ Removed `{word}` from the bad words filter.")
            logger.info(f"Removed bad word: {word}")
        else:
            await ctx.send(f"❌ `{word}` is not in the filter.")

async def setup(bot):
    await bot.add_cog(AutoModeration(bot))
