# Advanced Discord Bot 🤖

A feature-rich Discord bot with moderation, leveling, giveaways, AI, and much more!

## Features 🌟

### Core Features
- **Welcome System** - Customize welcome messages and images
- **Moderation** - Mute, kick, ban, warn, and manage server
- **Leveling System** - AmariBot-like leveling with XP and ranks
- **Giveaways** - Create and manage server giveaways
- **Ticket System** - Support tickets with auto-creation
- **Games** - Guess the number, rock-paper-scissors, dice rolls
- **AI Assistant** - Gemini AI integration for smart responses
- **Logging** - Track chat, mod, and user actions
- **Auto-Mod** - Automatic spam and rule enforcement

### Management Features
- Auto-responder
- Auto-reaction
- Auto-role assignment
- No-prefix commands (server owner only)
- Comprehensive logging

## Installation 📥

### Prerequisites
- Python 3.10+
- Discord Bot Token
- Gemini API Key (for AI features)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/veeragaming621-maker/My-discord-bot7.git
cd My-discord-bot7
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file and add:
```env
DISCORD_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the bot:
```bash
python bot.py
```

## Commands 📝

### Welcome
- `!welcome channel <#channel>` - Set welcome channel
- `!welcome text <text>` - Set welcome text
- `!welcome image <url>` - Set welcome image
- `!welcome test` - Test welcome message

### Moderation
- `!mute <user>` - Mute user
- `!unmute <user>` - Unmute user
- `!kick <user>` - Kick user
- `!ban <user>` - Ban user
- `!unban <user_id>` - Unban user
- `!warn <user>` - Warn user
- `!purge [amount]` - Purge messages
- `!lock` - Lock channel
- `!unlock` - Unlock channel
- And more...

### Leveling
- `!rank [user]` - View rank
- `!leaderboard` - View leaderboard

### Games
- `!game guess` - Guess the number (1-100)
- `!game rps <choice>` - Rock paper scissors
- `!game coin` - Flip a coin
- `!game roll [sides]` - Roll dice

### Giveaways
- `!giveaway create` - Create giveaway
- `!giveaway end <message_id>` - End giveaway
- `!giveaway reroll <message_id>` - Reroll winners

### AI
- `!ask <question>` - Ask AI
- `!summarize <text>` - Summarize text

### Extra
- `!autoresponse add <trigger> <response>` - Add auto-response
- `!autorole add <role>` - Add auto-role
- `!np give <user>` - Give no-prefix access

## Features In Detail

### Guess the Number Game
- User runs `!game guess`
- Bot sends DM with start button
- User guesses 1-100 (10 guesses limit)
- Bot provides feedback (too high/low)
- On correct guess: ✅ reaction and channel lock

### Leveling System
- Earn 5-15 XP per message
- XP scales with level
- Level up announcements in chat
- `!rank` shows progress bar
- `!leaderboard` with medals

### Auto-Moderation
- Detects ALL CAPS messages
- Filters invites & links
- Catches mass mentions
- Removes spam automatically

## Database

The bot uses SQLite for data storage. Database file: `bot.db`

Tables include:
- welcome_settings
- warnings
- mutes
- levels
- tickets
- And more...

## Support

For issues or questions, please create an issue on GitHub.

## License 📄

MIT License

---

**Made with ❤️ by veeragaming621-maker**