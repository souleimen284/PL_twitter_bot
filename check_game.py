"""
Monitors matches with PL teams and triggers tracking.

This script checks football matches that include Premier League teams and
triggers match tracking when one is detected in the configured time window.
"""

import asyncio
import subprocess
from datetime import datetime, timezone
from sofascore_wrapper.api import SofascoreAPI
from config import PREMIER_LEAGUE_TEAMS, NO_PL_CHECK_TIME_WINDOW, MATCH_LOOKUP_PAST, MATCH_LOOKUP_FUTURE


async def check_non_pl_games() -> None:
    """
    Check for matches with PL teams starting soon.
    
    Fetches today's football schedule and identifies matches where PL teams
    participate, including Premier League competition.
    """
    api = SofascoreAPI()
    
    try:
        # Get today's date in UTC
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = await api._get(f"/sport/football/scheduled-events/{date_str}")
        events = data.get("events", [])

        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        time_buffer = 15 * 60  # 15 minutes buffer for match consideration
        found_match = False

        for match in events:
            home_team = match.get("homeTeam", {}).get("name")
            away_team = match.get("awayTeam", {}).get("name")
            home_gender = match.get("homeTeam", {}).get("gender")
            away_gender = match.get("awayTeam", {}).get("gender")
            start_timestamp = match.get("startTimestamp")
            tournament_name = match.get("tournament", {}).get("name", "")
            
            if not start_timestamp:
                continue

            # Check if it involves PL teams and is in the configured time window
            is_pl_team = (home_team in PREMIER_LEAGUE_TEAMS or 
                         away_team in PREMIER_LEAGUE_TEAMS)
            is_male = home_gender == "M" and away_gender == "M"
            is_upcoming = (abs(start_timestamp - current_timestamp) <= NO_PL_CHECK_TIME_WINDOW 
                          and start_timestamp + time_buffer >= current_timestamp)
            
            if is_pl_team and is_male and is_upcoming:
                match_time = datetime.utcfromtimestamp(start_timestamp)
                print(
                    f"✅ Match with PL team detected ({tournament_name}): "
                    f"{home_team} vs {away_team} at {match_time} UTC"
                )
                
                # Trigger the match tracking script
                subprocess.run(["python", "run_bot.py"])
                found_match = True
                break
        
        if not found_match:
            print(
                f"⚠️  No matches with PL teams found within the next "
                f"{NO_PL_CHECK_TIME_WINDOW // 3600} hour(s)"
            )

    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(check_non_pl_games())
