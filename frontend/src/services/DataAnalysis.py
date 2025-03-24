import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# API endpoint
url = "https://api.sportsgameodds.com/v1/odds"

# API key
api_key = "8685187128765adf03ff2690a8a4c9cf"

# List of players
star_players = [
    "MIKAL_BRIDGES",
    "STEPHEN_CURRY",
    "LUKA_DONCIC",
    "JAYSON_TATUM",
    "ZACH_LAVINE",
    "JALEN_GREEN",
    "DE'AARON_FOX",
    "KEVIN_DURANT",
    "DONOVAN_MITCHELL",
    "MAX_STRUS",
    "ANTHONY_EDWARDS"
]

# Headers
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

# File paths
json_file = "nba_data.json"
csv_file = "nba_player_odds.csv"

# Function to check if cached file is valid and contains all players
def is_valid_cache(file_path, players):
    if os.path.exists(file_path):
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if datetime.now() - file_time < timedelta(days=1):  # Cache is fresh
            with open(file_path, "r") as f:
                try:
                    cached_data = json.load(f)
                    cached_players = {record["Player"] for record in cached_data}
                    # Ensure all players are in the cache
                    if all(player.replace("_", " ") in cached_players for player in players):
                        print("✅ Using cached data from:", file_time)
                        return cached_data
                    else:
                        print("⚠️ Cached data is missing some players. Fetching new data...")
                except json.JSONDecodeError:
                    print("⚠️ Cached file is corrupted. Fetching new data...")
    return None  # Fetch new data if cache is invalid

# Load cached data if valid
data = is_valid_cache(json_file, star_players)

# If no valid cached data, fetch new data
if data is None:
    print("🆕 No valid cached data found. Fetching new data...")
    game_records = []

    for player in star_players:
        odd_id = f"points-{player}_1_NBA-game-ou-under"

        params = {
            "leagueID": "NBA",
            "limit": 15,
           "finalized": "true",
            "oddIDs": odd_id
        }

        response = requests.get(url, params=params, headers=headers)

        # ✅ Debugging: Print API status
        print(f"\n🔍 Requesting Data for {player}... Status Code: {response.status_code}")

        if response.status_code == 200:
            player_data = response.json()

            # ✅ Debugging: Print response structure
            print(f"📊 API Response for {player}:")
            print(json.dumps(player_data, indent=2)[:1000])  # Print first 1000 characters for debugging

            if player_data.get("success") and "data" in player_data and len(player_data["data"]) > 0:
                for game in player_data["data"]:
                    date = game["status"]["startsAt"][:10]

                    for odds_key, odds_info in game["odds"].items():
                        if odds_key.startswith(f"points-{player}"):
                            # Safely get values, default to "N/A" if missing
                            game_records.append({
                                "Date": date,
                                "Player": player.replace("_", " "),
                                "Event ID": game["eventID"],
                                "Actual Points": odds_info.get("score", "N/A"),
                                "Expected Points (Book)": odds_info.get("bookOverUnder", "N/A"),
                                "Expected Points (Fair)": odds_info.get("fairOverUnder", "N/A"),
                                "Fair Odds": odds_info.get("fairOdds", "N/A"),
                                "Book Odds": odds_info.get("bookOdds", "N/A"),
                                "Started": odds_info.get("started", False),
                                "Ended": odds_info.get("ended", False),
                                "Cancelled": odds_info.get("cancelled", False)
                            })

            else:
                print(f"⚠️ No valid game data found for {player} in API response.")

        else:
            print(f"❌ Failed to fetch data for {player}. Status Code: {response.status_code}")
            print("📩 Response:", response.text)

    # Save new data to JSON file only if we fetched records
    if game_records:
        with open(json_file, "w") as f:
            json.dump(game_records, f, indent=4)
        print("💾 New data saved to", json_file)
    else:
        print("⚠️ No valid data fetched. Keeping old cache (if any).")

    data = game_records  # Use newly fetched data

# Convert to DataFrame
df = pd.DataFrame(data)

# ✅ Debugging: Check if DataFrame is empty
if df.empty:
    print("⚠️ WARNING: The DataFrame is empty! No data was retrieved.")

# Ensure expected columns exist before converting to numeric
for col in ["Expected Points (Book)", "Expected Points (Fair)", "Fair Odds", "Book Odds"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

# Display DataFrame in Jupyter Notebook (if available)
try:
    from IPython.display import display
    display(df)
except ImportError:
    print(df)

# Save DataFrame as CSV
df.to_csv(csv_file, index=False)
print("📊 Data saved to", csv_file)
