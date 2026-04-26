"""
Configuration and constants module for Telegram Football Bot.

This module centralizes all constants, credentials, and configuration parameters
to reduce duplication and improve maintainability.
"""

import os
from typing import Set, Dict

# ============================================================
# CREDENTIALS (load from environment variables)
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_token_here')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '@FPL_EDITS')

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'YOUR_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', 'YOUR_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', 'YOUR_ACCESS_SECRET')

# ============================================================
# PREMIER LEAGUE TEAMS
# ============================================================

PREMIER_LEAGUE_TEAMS: Set[str] = {
    "Manchester City",
    "Manchester United",
    "Liverpool",
    "Arsenal",
    "Chelsea",
    "Tottenham Hotspur",
    "Newcastle United",
    "Aston Villa",
    "Brighton & Hove Albion",
    "West Ham United",
    "Wolverhampton Wanderers",
    "Crystal Palace",
    "Fulham",
    "Brentford",
    "Everton",
    "Nottingham Forest",
    "Bournemouth",
    "Sunderland",
    "Leeds United",
    "Burnley",
}

# ============================================================
# TIME WINDOWS (in seconds)
# ============================================================

# Time window for checking upcoming matches in check_pl_game.py
PL_CHECK_TIME_WINDOW = 2 * 60 * 60  # 2 hours

# Time window for checking non-PL games in check_no_pl_game.py
NO_PL_CHECK_TIME_WINDOW = 60 * 60  # 1 hour

# Time window for checking recent/upcoming matches
MATCH_LOOKUP_PAST = 2 * 3600  # 2 hours before now
MATCH_LOOKUP_FUTURE = 1 * 3600  # 1 hour after now

# Delay for fetching goal details after goal event (allows assists to be recorded)
GOAL_UPDATE_DELAY = 20  # seconds

# Runtime for live match tracker
TRACKER_RUNTIME_MINUTES = 3 * 60 + 15  # 3 hours 15 minutes

# ============================================================
# API ENDPOINTS
# ============================================================

SOFASCORE_BASE_URL = "https://fantasy.premierleague.com/api"
FPL_FIXTURES_URL = f"{SOFASCORE_BASE_URL}/fixtures/"
FPL_BOOTSTRAP_URL = f"{SOFASCORE_BASE_URL}/bootstrap-static/"

# ============================================================
# POLLING INTERVALS (in seconds)
# ============================================================

LIVE_MATCH_CHECK_INTERVAL = 15  # Check for new matches every 15 seconds
FPL_UPDATE_CHECK_INTERVAL = 10  # Check for FPL stats updates every 10 seconds
UPCOMING_GAMES_REFRESH_INTERVAL = 300  # Refresh upcoming games every ~5 minutes
SLEEP_POST_LINEUP = 2  # Delay between posting multiple lineups

# ============================================================
# ERROR HANDLING & RETRY
# ============================================================

MAX_API_RETRIES = 3
API_RETRY_DELAY = 1  # seconds

# ============================================================
# TWITTER/TELEGRAM TEXT LIMITS
# ============================================================

TWITTER_CHAR_LIMIT = 280
TELEGRAM_TEXT_SEPARATOR = "|"  # Used to split Telegram messages

# ============================================================
# EMOJI CONSTANTS
# ============================================================

EMOJI_MAP: Dict[str, str] = {
    'yellow_cards': '🟨 YELLOW CARD: ',
    'red_cards': '🟥 RED CARD: ',
    'penalties_missed': '❌ PENALTY MISSED : ',
    'penalties_saved': '🧤 PENALTY SAVED :',
    'goals_scored': '⚽️ GOAL :',
    'assists': '🅰️ Assist :',
    'own_goals': '⚽️ OWN GOAL :',
    'lineups': '📋',
    'halftime': '⏸ HT: ',
    'fulltime': '🏁 FT: ',
    'goal': '⚽️',
    'penalty': '✅',
    'missed_penalty': '❌',
    'assist': '🅰️',
}
