# 🏟️ Telegram Football Bot

A Python-based automation bot that monitors football matches and sends real-time notifications via Telegram. The bot scans relevant fixtures, detects goals, and alerts subscribers to match updates.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Project Status](#project-status)

---

## ✨ Features

- **🔔 Real-time Match Notifications**: Monitors upcoming football matches and sends Telegram alerts
- **⚽ Match Monitoring**: Tracks relevant tournaments and fixtures for notifications
- **🎯 Goal Tracking**: Detects goals during live matches using SofaScore API
- **🐦 Twitter Integration**: (Optional) Posts match updates to Twitter
- **⏱️ Intelligent Scheduling**: Checks for matches at configurable intervals
- **🔐 Secure Credentials**: Environment-based credential management
- **📊 Clean Code Architecture**: Refactored codebase with type hints and comprehensive documentation

---

## 📁 Project Structure

```
.
├── config.py                    # Centralized configuration and constants
├── check_game.py               # Monitors matches and triggers tracking
├── run_bot.py                  # Tracks live goals and posts updates
├── test.py                     # Testing and validation scripts
├── test2.py                    # Additional test utilities
├── requirements.txt            # Python dependencies
├── REFACTORING_SUMMARY.md      # Recent code quality improvements
└── old/                        # Legacy code archive
```

---

## 📦 Requirements

- **Python 3.8+**
- Operating System: Windows, macOS, or Linux

### Dependencies

```
requests
numpy
pandas
tweepy
sofascore-wrapper
aiohttp
python-dateutil
```

See `requirements.txt` for complete list.

---

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd telegram bot
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Set Environment Variables

The bot requires API credentials and configuration. Set these environment variables:

```bash
# Telegram Bot Credentials
set TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
set TELEGRAM_CHAT_ID=@your_telegram_channel_here

# Twitter API Credentials (Optional)
set TWITTER_API_KEY=your_twitter_api_key
set TWITTER_API_SECRET=your_twitter_api_secret
set TWITTER_ACCESS_TOKEN=your_twitter_access_token
set TWITTER_ACCESS_SECRET=your_twitter_access_secret
```

**On Windows PowerShell:**
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_token_here"
$env:TELEGRAM_CHAT_ID = "@your_channel_here"
```

### 2. Obtaining API Credentials

- **Telegram Bot Token**: Create a bot with [BotFather](https://t.me/botfather) on Telegram
- **Telegram Chat ID**: Your channel ID (e.g., `@YourChannelName`)
- **Twitter API Keys**: Register at [Twitter Developer Portal](https://developer.twitter.com/)

### 3. Configure in config.py

The centralized `config.py` module manages all constants including:
- Premier League teams set
- Time windows for match checks (15 min, 1 hour, 2 hours, etc.)
- Polling intervals
- API endpoints
- Emoji mappings for notifications

---

## 🎮 Usage

### Run Main Scripts

Run match detection:
```bash
python check_game.py
```

Run goal tracking bot:
```bash
python run_bot.py
```

### Automatic Scheduling

For continuous monitoring, schedule the checker scripts using:

- **Windows Task Scheduler**: Schedule `check_game.py` to run at intervals
- **Linux/macOS Cron**: Add to crontab for periodic execution
- **Python APScheduler**: Embed scheduling within a Python script

Example crontab entry (every 15 minutes):
```cron
*/15 * * * * cd /path/to/project && python check_game.py
```

---

## 🔄 How It Works

### 1. Match Detection (`check_game.py`)
- Fetches today's football schedule via SofaScore API
- Identifies relevant matches based on configured rules
- Checks if matches start within the configured time window (default: 15 minutes)
- Sends Telegram notification with match details
- Triggers `run_bot.py` for real-time goal tracking

### 2. Goal Tracking (`run_bot.py`)
- Monitors live match events
- Detects goals scored during the match
- Posts updates to Telegram channel
- (Optional) Posts to Twitter

---

## 📊 Project Status

### ✅ Recently Completed
- **Code Refactoring** (April 2026): Enhanced code quality, maintainability, and security
  - 7 Python files refactored
  - Centralized configuration in `config.py`
  - Improved variable naming and type hints
  - ~50+ quality improvements applied
  - Zero breaking changes - all functionality preserved

### 🔒 Key Improvements
- Credentials moved to environment variables (security)
- Removed duplicate code across files
- Added comprehensive docstrings
- Improved variable naming for clarity
- Added type hints for better code maintainability

---

## 📝 Notes

- The bot uses **SofaScore API** for football match data (requires internet connection)
- **Asyncio** is used for non-blocking API calls to improve efficiency
- Credentials are **never** hardcoded in source files (loaded from environment)
- The bot is designed to run continuously or on a schedule

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not sending messages | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correctly set |
| No matches detected | Check SofaScore API availability and your time window settings |
| Module import errors | Ensure all dependencies are installed: `pip install -r requirements.txt` |
| Matches being missed | Reduce the time window in `config.py` for more frequent checks |

---

## 📄 License

This project is for personal/educational use.

---

## 👤 Author

Created as a Python automation project for monitoring football matches.

---

## 🔗 Resources

- [SofaScore API Wrapper](https://github.com/rnag/sofascore-wrapper)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [Python Asyncio](https://docs.python.org/3/library/asyncio.html)

---

**Last Updated:** April 17, 2026
