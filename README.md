# Discord Bot Project

This project is a custom Discord bot designed to provide various features for server management and moderation. Below are the details regarding its setup, features, and usage.

## Features

- **Nuke Command**: Deletes all messages in a channel and can recreate it.
- **Anti-Nuke**: Monitors and prevents nuke attempts.
- **AFK Command**: Allows users to set themselves as AFK and manage their status.
- **Moderation Actions**: Includes kick, mute, and unmute functionalities.
- **Quarantine**: Restricts user access to certain channels.
- **Timeout**: Temporarily restricts a user's ability to send messages.
- **Warning System**: Issues warnings to users and tracks their warning count.
- **Banning**: Bans users from the server.
- **Whitelisting**: Allows certain commands to bypass restrictions.
- **Announcements**: Sends messages to designated announcement channels.
- **Auto Moderation**: Automatically manages user behavior based on predefined rules.
- **Auto Role Assignment**: Automatically assigns roles to users upon joining.
- **Logging**: Logs events, errors, and other important information.
- **Slash Commands**: Implements various slash commands for enhanced interaction.

## Setup Instructions

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd discord-bot-project
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8 or higher installed. Then, install the required packages using:
   ```
   pip install -r requirements.txt
   ```

3. **Configuration**:
   Edit the `src/config.py` file to set your bot token and any other customizable options.

4. **Run the Bot**:
   Start the bot by running:
   ```
   python src/bot.py
   ```

## Usage

- Use the commands as specified in the bot's documentation.
- Ensure the bot has the necessary permissions to perform moderation actions.
- Customize the bot's behavior by modifying the command implementations in the `src/commands` directory.

## Contributing

Feel free to submit issues or pull requests to enhance the bot's functionality. 

## License

This project is licensed under the MIT License. See the LICENSE file for more details.