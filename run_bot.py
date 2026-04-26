"""
Live match tracker for non-Premier League matches with PL team players.

This script monitors live football events and posts match updates to Telegram,
including lineups, goals, assists, red cards, halftime scores, and full-time results.
"""

import asyncio
import aiohttp
import sys
import tweepy
import time
from datetime import datetime, timezone
from typing import List, Dict, Set, Optional, Any
from sofascore_wrapper.api import SofascoreAPI
from config import (
    PREMIER_LEAGUE_TEAMS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET,
    TRACKER_RUNTIME_MINUTES,
    MATCH_LOOKUP_PAST,
    MATCH_LOOKUP_FUTURE,
    SLEEP_POST_LINEUP,
)

# Configure stdout for real-time output
sys.stdout.reconfigure(line_buffering=True)

# Initialize Twitter client
_twitter_auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
twitter_api = tweepy.API(_twitter_auth)

# Track state to avoid duplicate posts
seen_incidents: Set[int] = set()
posted_lineups: Set[int] = set()
posted_results: Set[int] = set()
posted_half_times: Set[int] = set()


async def send_telegram_message(text: str) -> None:
    """
    Send a message to the Telegram channel.
    
    Args:
        text: Message text to send
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"Telegram error (status {resp.status}): {error_text}")
    except asyncio.TimeoutError:
        print("Telegram request timed out")
    except Exception as e:
        print(f"Telegram error: {e}")


def post(text: str) -> None:
    """
    Post a message to Telegram asynchronously.
    
    Args:
        text: Message text to post
    """
    print(text)  # Console output
    asyncio.create_task(send_telegram_message(text))


def tweet_update(text: str) -> None:
    """
    Tweet an update via Twitter.
    
    Args:
        text: Tweet text to post
    """
    try:
        twitter_api.update_status(text)
        print(f"Tweeted: {text}")
    except Exception as e:
        print(f"Twitter error: {e}")


def format_hashtags(home_code: str, away_code: str, competition_name: str) -> str:
    """
    Format match hashtags for social media.
    
    Args:
        home_code: Home team code
        away_code: Away team code
        competition_name: Tournament name
        
    Returns:
        Formatted hashtag string
    """
    # Clean competition name for hashtag
    comp_tag = (
        competition_name
        .replace("-", " ")
        .replace(",", "")
        .title()
        .replace(" ", "")
    )
    return f"#{home_code}{away_code} #{comp_tag}"


def clean_name(name: Optional[str]) -> str:
    """
    Clean and validate player/team name.
    
    Args:
        name: Raw name string
        
    Returns:
        Cleaned name or empty string if invalid
    """
    if not name or name.strip() in ["-", "Unknown", ""]:
        return ""
    return name.strip()


async def get_live_matches(api: SofascoreAPI) -> List[Dict[str, Any]]:
    """
    Fetch all live football matches.
    
    Args:
        api: SofaScore API instance
        
    Returns:
        List of live match events
    """
    try:
        data = await api._get("/sport/football/events/live")
        return data.get("events", [])
    except Exception as e:
        print(f"Error fetching live matches: {e}")
        return []


async def get_today_matches(api: SofascoreAPI) -> List[Dict[str, Any]]:
    """
    Fetch all football matches scheduled for today.
    
    Args:
        api: SofaScore API instance
        
    Returns:
        List of today's match events
    """
    try:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = await api._get(f"/sport/football/scheduled-events/{date_str}")
        return data.get("events", [])
    except Exception as e:
        print(f"Error fetching today's matches: {e}")
        return []


async def post_lineup(api: SofascoreAPI, match: Dict[str, Any]) -> None:
    """
    Post confirmed team lineups to Telegram.
    
    Args:
        api: SofaScore API instance
        match: Match event dictionary
    """
    match_id = match["id"]
    if match_id in posted_lineups:
        return

    home_team = match.get("homeTeam", {}).get("shortName", "Home Team")
    away_team = match.get("awayTeam", {}).get("shortName", "Away Team")
    home_code = match.get("homeTeam", {}).get("nameCode", "")
    away_code = match.get("awayTeam", {}).get("nameCode", "")
    tournament_name = match.get("tournament", {}).get("name", "")
    status = match.get("status", {}).get("description", "")
    
    try:
        lineup_data = await api._get(f"/event/{match_id}/lineups")
        
        if lineup_data and "error" not in lineup_data:
            if (lineup_data.get("confirmed") and 
                "home" in lineup_data and 
                "away" in lineup_data):
                
                posted_lineups.add(match_id)
                home_players = [
                    p["player"]["shortName"] 
                    for p in lineup_data["home"].get("players", []) 
                    if not p.get("substitute")
                ]
                away_players = [
                    p["player"]["shortName"] 
                    for p in lineup_data["away"].get("players", []) 
                    if not p.get("substitute")
                ]

                lineup_text = (
                    f"📋 {home_team} vs {away_team} Team News : \n"
                    f"{home_team} XI : " + ", ".join(home_players) + "\n\n"
                    f"{away_team} XI : " + ", ".join(away_players) + "\n\n"
                    f"{format_hashtags(home_code, away_code, tournament_name)}"
                )
                post(lineup_text)
                return
        
        # Mark as posted if match has already started
        if status != "Not started":
            posted_lineups.add(match_id)
            
    except Exception as e:
        print(f"Error posting lineup for match {match_id}: {e}")


async def check_incidents(api: SofascoreAPI, match: Dict[str, Any]) -> None:
    """
    Check for and post match incidents (goals, penalties, red cards, etc).
    
    Args:
        api: SofaScore API instance
        match: Match event dictionary
    """
    match_id = match["id"]
    home_team = match.get("homeTeam", {}).get("shortName", "Home Team")
    away_team = match.get("awayTeam", {}).get("shortName", "Away Team")
    home_code = match.get("homeTeam", {}).get("nameCode", "")
    away_code = match.get("awayTeam", {}).get("nameCode", "")
    tournament_name = match.get("tournament", {}).get("name", "")

    try:
        data = await api._get(f"/event/{match_id}/incidents")
        incidents = data.get("incidents", [])

        for inc in incidents:
            inc_id = inc.get("id")
            incident_type = inc.get("incidentType")

            if not inc_id or inc_id in seen_incidents:
                continue

            # Wait for goal details to be updated (assists, etc)
            if incident_type in ["goal", "penalty"]:
                await asyncio.sleep(20)
                data = await api._get(f"/event/{match_id}/incidents")
                updated_inc = next(
                    (i for i in data.get("incidents", []) if i.get("id") == inc_id),
                    None
                )
                if not updated_inc:
                    continue
            else:
                updated_inc = inc

            seen_incidents.add(inc_id)
            
            # Extract minute from different possible formats
            minute = None
            if isinstance(updated_inc.get("time"), dict):
                minute = updated_inc.get("time", {}).get("minute")
            else:
                minute = updated_inc.get("time") or updated_inc.get("minute", "?")

            incident_type = updated_inc.get("incidentType")
            incident_class = updated_inc.get("incidentClass", "")

            scorer = clean_name(
                updated_inc.get("playerName") or 
                updated_inc.get("player", {}).get("shortName", "")
            )
            assist = clean_name(
                updated_inc.get("assist1", {}).get("shortName", "") 
                if "assist1" in updated_inc else ""
            )

            # Mark own goals
            if incident_type == "goal" and incident_class == "ownGoal":
                scorer = f"{scorer} (OG)" if scorer else "(OG)"

            score = (
                f'{home_team} {updated_inc.get("homeScore")}-'
                f'{updated_inc.get("awayScore")} {away_team} ({minute}")'
            )
            hashtags = format_hashtags(home_code, away_code, tournament_name)

            # Post incident-specific messages
            if incident_type == "goal":
                text = f"⚽️ GOAL: {scorer}" if scorer else "⚽️ GOAL:-"
                text += f"\n🅰️ Assist: {assist if assist else '-'}"
                text += f"\n\n{score}\n{hashtags}"
                post(text)

            elif incident_type == "penalty":
                text = f"✅ PENALTY GOAL: {scorer}" if scorer else "✅ PENALTY GOAL!"
                text += f"\n\n{score}\n{hashtags}"
                post(text)

            elif incident_type == "inGamePenalty" and incident_class == "missed":
                text = f"❌ PENALTY MISSED: {scorer}" if scorer else "❌ PENALTY MISSED!"
                text += f"\n\n{score}\n{hashtags}"
                post(text)
                
    except Exception as e:
        print(f"Error checking incidents for match {match_id}: {e}")


async def check_half_time(api: SofascoreAPI, match: Dict[str, Any]) -> None:
    """
    Post halftime score and goals summary.
    
    Args:
        api: SofaScore API instance
        match: Match event dictionary
    """
    match_id = match["id"]
    if match_id in posted_half_times:
        return

    try:
        match_data = await api._get(f"/event/{match_id}")
        status = match_data.get("event", {}).get("status", {}).get("description", "")

        if status == "Halftime":
            posted_half_times.add(match_id)

            home_team = match_data["event"]["homeTeam"]["shortName"]
            away_team = match_data["event"]["awayTeam"]["shortName"]
            home_code = match_data["event"]["homeTeam"]["nameCode"]
            away_code = match_data["event"]["awayTeam"]["nameCode"]
            tournament_name = match_data["event"]["tournament"]["name"]
            home_score = match_data["event"]["homeScore"]["current"]
            away_score = match_data["event"]["awayScore"]["current"]

            incidents_data = await api._get(f"/event/{match_id}/incidents")
            goals_lines = []
            
            for inc in incidents_data.get("incidents", []):
                if inc.get("incidentType") == "goal":
                    scorer = clean_name(inc.get("player", {}).get("shortName", ""))
                    assist = clean_name(inc.get("assist1", {}).get("shortName", ""))

                    # Mark own goals
                    if inc.get("incidentClass") == "ownGoal":
                        scorer += " (OG)"

                    if scorer:
                        line = f"⚽️ {scorer}"
                        if assist:
                            line += f" | 🅰️ {assist}"
                        goals_lines.append(line)

            goals_text = "\n".join(goals_lines) if goals_lines else ""
            score_line = f"{home_team} {home_score}-{away_score} {away_team}"
            hashtags = format_hashtags(home_code, away_code, tournament_name)

            text = f"⏸ HT: {score_line}\n\n{goals_text}\n\n{hashtags}"
            post(text)
            
    except Exception as e:
        print(f"Error checking halftime for match {match_id}: {e}")


async def check_full_time(api: SofascoreAPI, match: Dict[str, Any]) -> None:
    """
    Post final score and goals summary.
    
    Args:
        api: SofaScore API instance
        match: Match event dictionary
    """
    match_id = match["id"]
    if match_id in posted_results:
        return

    try:
        match_data = await api._get(f"/event/{match_id}")
        status = match_data.get("event", {}).get("status", {}).get("type", "")

        if status == "finished":
            posted_results.add(match_id)

            home_team = match_data["event"]["homeTeam"]["shortName"]
            away_team = match_data["event"]["awayTeam"]["shortName"]
            home_code = match_data["event"]["homeTeam"]["nameCode"]
            away_code = match_data["event"]["awayTeam"]["nameCode"]
            tournament_name = match_data["event"]["tournament"]["name"]
            home_score = match_data["event"]["homeScore"]["current"]
            away_score = match_data["event"]["awayScore"]["current"]

            incidents_data = await api._get(f"/event/{match_id}/incidents")
            goals_lines = []
            
            for inc in incidents_data.get("incidents", []):
                if inc.get("incidentType") == "goal":
                    scorer = clean_name(inc.get("player", {}).get("shortName", ""))
                    assist = clean_name(inc.get("assist1", {}).get("shortName", ""))

                    # Mark own goals
                    if inc.get("incidentClass") == "ownGoal":
                        scorer += " (OG)"

                    if scorer:
                        line = f"⚽️ {scorer}"
                        if assist:
                            line += f" | 🅰️ {assist}"
                        goals_lines.append(line)

            goals_text = "\n".join(goals_lines) if goals_lines else ""
            score_line = f"{home_team} {home_score}-{away_score} {away_team}"
            hashtags = format_hashtags(home_code, away_code, tournament_name)

            text = f"🏁 FT: {score_line}\n\n{goals_text}\n\n{hashtags}"
            post(text)
            
    except Exception as e:
        print(f"Error checking full-time for match {match_id}: {e}")


async def handle_match(api: SofascoreAPI, match: Dict[str, Any]) -> None:
    """
    Process all updates for a single match.
    
    Args:
        api: SofaScore API instance
        match: Match event dictionary
    """
    await post_lineup(api, match)
    await check_incidents(api, match)
    await check_half_time(api, match)
    await check_full_time(api, match)


async def main() -> None:
    """Main loop for live match tracking."""
    api = SofascoreAPI()
    print("Starting non-Premier League live match tracker...")
    
    runtime_seconds = TRACKER_RUNTIME_MINUTES * 60
    start_time = time.time()
    tracked_match_ids: Set[int] = set()
    
    try:
        while True:
            # Stop tracker if runtime exceeded
            if (time.time() - start_time) > runtime_seconds:
                print("Time limit reached. Stopping tracker...")
                break

            try:
                # Get today's matches
                matches = await get_today_matches(api)
                
                current_timestamp = int(time.time())
                # Filter matches within looking window
                recent_matches = [
                    m for m in matches 
                    if current_timestamp - MATCH_LOOKUP_PAST <= m.get("startTimestamp", 0) <= current_timestamp + MATCH_LOOKUP_FUTURE
                ]

                if recent_matches:
                    # Filter for PL team matches
                    pl_team_matches = [
                        m for m in recent_matches
                        if (
                            (m.get("homeTeam", {}).get("name") in PREMIER_LEAGUE_TEAMS or 
                             m.get("awayTeam", {}).get("name") in PREMIER_LEAGUE_TEAMS)
                            and m.get("homeTeam", {}).get("gender") == "M"
                            and m.get("awayTeam", {}).get("gender") == "M"
                        )
                    ]
                    
                    match_ids = {match["id"] for match in pl_team_matches}
                    
                    # Reset timer on new matches
                    if any(mid not in tracked_match_ids for mid in match_ids):
                        start_time = time.time()
                    
                    tracked_match_ids = match_ids

                    # Process matches
                    if pl_team_matches:
                        for match in pl_team_matches:
                            await handle_match(api, match)
                            await asyncio.sleep(SLEEP_POST_LINEUP)
                    else:
                        print("No PL team matches in current window.")
                else:
                    print("No matches in lookup window.")
                    
            except Exception as e:
                print(f"Error in main loop: {e}")
            
            # Wait before next check
            await asyncio.sleep(15)
            
    except KeyboardInterrupt:
        print("Stopping tracker...")
    finally:
        await api.close()
        print("Tracker closed.")


if __name__ == "__main__":
    asyncio.run(main())
