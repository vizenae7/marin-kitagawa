import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('BOT_TOKEN')
PREFIX = os.getenv('PREFIX', 'V!')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Discord intents configuration
INTENTS = {
    "guilds": True,
    "guild_messages": True,
    "guild_message_reactions": True,
    "guild_members": True,
    "guild_presences": True,
    "message_content": True,
}

# Channel and role IDs (replace with actual IDs when deploying)
ANNOUNCEMENT_CHANNEL_ID = int(os.getenv('ANNOUNCEMENT_CHANNEL_ID', '0'))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', '0'))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', '0'))

# Default whitelisted commands
DEFAULT_WHITELISTED_COMMANDS = ["afk", "help", "ping"]

# Auto-moderation settings
BAD_WORDS = [
    'spam', 'inappropriate', 'badword'  # Add actual bad words here
]

# Warning system settings
MAX_WARNINGS = 3
WARNING_ACTIONS = {
    1: "warn",
    2: "mute",
    3: "ban"
}
