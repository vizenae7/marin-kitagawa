import logging
import os
from datetime import datetime

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(level)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create file handler with daily rotation-like naming
    today = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'logs/discord_bot_{today}.log'
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Console handler for important logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create detailed formatter
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create simple formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Add formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_command_usage(command_name: str, user: str, guild: str = None, channel: str = None):
    """Log command usage with context"""
    logger = setup_logger('CommandUsage')
    
    context_info = []
    if guild:
        context_info.append(f"Guild: {guild}")
    if channel:
        context_info.append(f"Channel: {channel}")
    
    context_str = f" ({', '.join(context_info)})" if context_info else ""
    logger.info(f"Command '{command_name}' used by {user}{context_str}")

def log_moderation_action(action: str, moderator: str, target: str, reason: str = None, guild: str = None):
    """Log moderation actions"""
    logger = setup_logger('Moderation')
    
    reason_str = f" - Reason: {reason}" if reason else ""
    guild_str = f" in {guild}" if guild else ""
    
    logger.info(f"{action}: {target} by {moderator}{guild_str}{reason_str}")

def log_error(error: Exception, context: str = None):
    """Log errors with context"""
    logger = setup_logger('Errors')
    
    context_str = f" - Context: {context}" if context else ""
    logger.error(f"Error occurred{context_str}: {str(error)}", exc_info=True)

def log_security_event(event_type: str, details: str, user: str = None, guild: str = None):
    """Log security-related events"""
    logger = setup_logger('Security')
    
    user_str = f" - User: {user}" if user else ""
    guild_str = f" - Guild: {guild}" if guild else ""
    
    logger.warning(f"Security Event - {event_type}: {details}{user_str}{guild_str}")

def log_bot_event(event_type: str, details: str):
    """Log general bot events"""
    logger = setup_logger('BotEvents')
    logger.info(f"{event_type}: {details}")

# Create a main logger instance for the bot
main_logger = setup_logger('DiscordBot')

# Export commonly used logging functions
def info(message: str):
    """Log info message"""
    main_logger.info(message)

def warning(message: str):
    """Log warning message"""
    main_logger.warning(message)

def error(message: str, exc_info: bool = False):
    """Log error message"""
    main_logger.error(message, exc_info=exc_info)

def debug(message: str):
    """Log debug message"""
    main_logger.debug(message)

def critical(message: str):
    """Log critical message"""
    main_logger.critical(message)

# Cleanup old log files (optional)
def cleanup_old_logs(days_to_keep: int = 7):
    """Remove log files older than specified days"""
    import glob
    from pathlib import Path
    
    if not os.path.exists('logs'):
        return
    
    cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
    
    for log_file in glob.glob('logs/*.log'):
        file_path = Path(log_file)
        if file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                info(f"Cleaned up old log file: {log_file}")
            except OSError as e:
                error(f"Failed to cleanup log file {log_file}: {e}")

# Initialize cleanup on import (run once when the module is loaded)
def init_logger():
    """Initialize logger with cleanup"""
    cleanup_old_logs()
    info("Logger initialized successfully")

# Auto-initialize when module is imported
init_logger()
