import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta

def check_permissions(member: discord.Member, permission: str) -> bool:
    """Check if a member has a specific permission"""
    return getattr(member.guild_permissions, permission, False)

def format_message(content: str) -> str:
    """Format a message with bold styling"""
    return f"**{content}**"

def is_afk(bot, user_id: int) -> bool:
    """Check if a user is AFK"""
    return user_id in getattr(bot, 'afk_users', {})

def get_user_status(bot, user_id: int) -> str:
    """Get user AFK status"""
    return "AFK" if is_afk(bot, user_id) else "Active"

def log_action(action: str, user: discord.Member):
    """Log an action performed by a user"""
    from utils.logger import setup_logger
    logger = setup_logger('Actions')
    logger.info(f"{action} performed by {user.name} ({user.id})")

def parse_time_string(time_str: str) -> int:
    """
    Parse a time string into seconds
    Supports formats like: 10s, 5m, 2h, 1d
    """
    time_units = {
        's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
        'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
        'h': 3600, 'hr': 3600, 'hour': 3600, 'hours': 3600,
        'd': 86400, 'day': 86400, 'days': 86400,
        'w': 604800, 'week': 604800, 'weeks': 604800
    }
    
    time_str = time_str.lower().strip()
    
    # Extract number and unit
    match = re.match(r'(\d+)([a-z]+)?', time_str)
    if not match:
        return None
    
    number = int(match.group(1))
    unit = match.group(2) or 's'  # Default to seconds if no unit
    
    if unit in time_units:
        return number * time_units[unit]
    
    return None

def format_time_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes}m {remaining_seconds}s"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            return f"{hours}h {remaining_minutes}m"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours == 0:
            return f"{days} day{'s' if days != 1 else ''}"
        else:
            return f"{days}d {remaining_hours}h"

def create_embed(title: str, description: str = None, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Create a standardized embed"""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.timestamp = datetime.utcnow()
    return embed

def create_error_embed(message: str) -> discord.Embed:
    """Create a standardized error embed"""
    return create_embed("❌ Error", message, discord.Color.red())

def create_success_embed(message: str) -> discord.Embed:
    """Create a standardized success embed"""
    return create_embed("✅ Success", message, discord.Color.green())

def create_warning_embed(message: str) -> discord.Embed:
    """Create a standardized warning embed"""
    return create_embed("⚠️ Warning", message, discord.Color.yellow())

def clean_content(content: str, max_length: int = 2000) -> str:
    """Clean and truncate content for Discord messages"""
    # Remove markdown that could break formatting
    content = content.replace('`', '\\`').replace('*', '\\*').replace('_', '\\_')
    
    # Truncate if too long
    if len(content) > max_length:
        content = content[:max_length - 3] + "..."
    
    return content

def get_member_top_role(member: discord.Member) -> discord.Role:
    """Get member's highest role (excluding @everyone)"""
    return member.top_role if member.top_role.name != "@everyone" else None

def has_higher_role(member1: discord.Member, member2: discord.Member) -> bool:
    """Check if member1 has a higher role than member2"""
    return member1.top_role > member2.top_role

def is_bot_higher(guild: discord.Guild, target_member: discord.Member) -> bool:
    """Check if the bot has a higher role than the target member"""
    return guild.me.top_role > target_member.top_role

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def get_guild_prefix(bot, guild_id: int) -> str:
    """Get the command prefix for a guild (with fallback to default)"""
    # In a full implementation, this could check a database for custom prefixes
    return getattr(bot, 'command_prefix', 'V!')

def format_list(items: list, max_items: int = 10) -> str:
    """Format a list into a string with proper truncation"""
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return "\n".join([f"• {item}" for item in items])
    else:
        shown_items = items[:max_items]
        remaining = len(items) - max_items
        formatted = "\n".join([f"• {item}" for item in shown_items])
        formatted += f"\n... and {remaining} more"
        return formatted

def is_url(text: str) -> bool:
    """Check if text is a valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(text) is not None

def extract_id_from_mention(mention: str) -> int:
    """Extract user/role/channel ID from a Discord mention"""
    # Remove < > and any prefixes like @, #, @&
    cleaned = mention.strip('<>@&#!')
    try:
        return int(cleaned)
    except ValueError:
        return None

class Paginator:
    """Simple paginator for long lists"""
    
    def __init__(self, items: list, per_page: int = 10):
        self.items = items
        self.per_page = per_page
        self.total_pages = (len(items) + per_page - 1) // per_page
    
    def get_page(self, page_number: int) -> list:
        """Get items for a specific page (1-indexed)"""
        if page_number < 1 or page_number > self.total_pages:
            return []
        
        start_index = (page_number - 1) * self.per_page
        end_index = start_index + self.per_page
        return self.items[start_index:end_index]
    
    def format_page_info(self, page_number: int) -> str:
        """Get page info string"""
        if self.total_pages == 0:
            return "No items"
        return f"Page {page_number}/{self.total_pages} • {len(self.items)} total items"
