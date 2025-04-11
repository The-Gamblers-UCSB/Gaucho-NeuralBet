from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguegamefinder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from scipy.stats import shapiro
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LeakyReLU, Embedding, Flatten
from tensorflow.keras.regularizers import l2
from tensorflow.keras import Input
import random
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

# Retrieve players and player id
all_players = players.get_players()
player_dict = {player['full_name'].upper(): player['id'] for player in all_players}

player_To_Check = input("Type an NBA Player: ")
player_id = player_dict.get(player_To_Check.upper())

if not player_id:
    raise ValueError("Player not found. Please check the spelling.")

stat_To_Check = input("What stat do you want to predict(PTS, REB, AST, STL, BLK, FG3M, FTM): ")

# Build mapping from team abbreviation to full team name
all_teams = teams.get_teams()
team_abbrev_to_name = {team["abbreviation"]: team["full_name"] for team in all_teams}

# Get games for the player
gamefinder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id)
games = gamefinder.get_dict()['resultSets'][0]['rowSet']
columns = ["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME", "GAME_ID", "GAME_DATE",
           "MATCHUP", "WL", "MIN", "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
           "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "PLUS_MINUS"]
data = pd.DataFrame(games, columns=columns)

data["GAME_DATE"] = pd.to_datetime(data["GAME_DATE"])
data = data.sort_values(by="GAME_DATE")

lag_features = ['PTS', 'AST', 'REB']
lag_period = 1  # Using a one-game lag

for feature in lag_features:
    data[f'{feature}_lag{lag_period}'] = data[feature].shift(lag_period)

# Create rolling averages for points, assists, and rebounds
data["Rolling_PTS"] = data["PTS"].rolling(window=3, min_periods=1).mean()
data["Rolling_AST"] = data["AST"].rolling(window=3, min_periods=1).mean()
data["Rolling_REB"] = data["REB"].rolling(window=3, min_periods=1).mean()

# Identify home games and back-to-back scenarios
data['HOME_GAME'] = data['MATCHUP'].apply(lambda x: 1 if "vs." in x else 0)
data['Back_to_Back'] = data['GAME_DATE'].diff().dt.days.fillna(0).apply(lambda x: 1 if x == 1 else 0)

# Extract opponent team from the MATCHUP column and convert to full team name
def extract_opponent(matchup):
    if "vs." in matchup:
        opp_abbrev = matchup.split("vs. ")[1]
    elif "@" in matchup:
        opp_abbrev = matchup.split("@ ")[1]
    else:
        opp_abbrev = None
    # Use the mapping to get the full team name; if not found, return the abbreviation
    return team_abbrev_to_name.get(opp_abbrev, opp_abbrev)

data['OPPONENT'] = data['MATCHUP'].apply(extract_opponent)


def convert_season_id(season_id):
    year = int(season_id[-4:])  # Extract the last 4 digits
    return f"{year}-{str(year + 1)[-2:]}"  # Format as "xxxx-xx"

data["SEASON_ID"] = data["SEASON_ID"].apply(convert_season_id)

# Load opponent defensive ratings and rename season column to match our data
all_defensive_ratings = pd.read_csv("estimated_defensive_ratings_since_2003.csv")

all_defensive_ratings.rename(columns={"SEASON": "SEASON_ID"}, inplace=True)
# Keep only the necessary columns from defensive ratings
opp_def_stats = all_defensive_ratings[['TEAM_NAME', 'SEASON_ID', 'E_DEF_RATING']]

team_name_replacements = {
    "Charlotte Bobcats": "Charlotte Hornets",
    "Seattle SuperSonics": "Oklahoma City Thunder",
    "New Orleans/Oklahoma City Hornets": "New Orleans Pelicans",
    "New Jersey Nets": "Brooklyn Nets",
    "New Orleans Hornets": "New Orleans Pelicans"
}

# Replace team names in the TEAM_NAME column
opp_def_stats["TEAM_NAME"] = opp_def_stats["TEAM_NAME"].replace(team_name_replacements)

# Merge opponent defensive rating stats on opponent full name and season
data = data.merge(opp_def_stats,left_on=["OPPONENT", "SEASON_ID"],right_on=["TEAM_NAME", "SEASON_ID"],
    how="left",
    suffixes=("", "_opp")
)

# Rename the defensive rating column
data.rename(columns={"E_DEF_RATING": "OPP_E_DEF_RATING"}, inplace=True)
data.drop(columns=["TEAM_NAME_opp"], inplace=True)

valid_team_names = all_defensive_ratings["TEAM_NAME"].unique()
data = data[data["OPPONENT"].isin(valid_team_names)]

# Load opponent team stats and adjust column names
all_team_stats = pd.read_csv("nba_team_stats_since_2003.csv")
all_team_stats.rename(columns={"YEAR": "SEASON_ID"}, inplace=True)
all_team_stats.rename(columns={"STL": "TEAM_STL", "BLK": "TEAM_BLK", "WIN_PCT": "TEAM_WIN_PCT"}, inplace=True)
# Keep only needed columns for the opponent
opp_team_stats = all_team_stats[['TEAM_NAME', 'SEASON_ID', 'TEAM_STL', 'TEAM_BLK', 'TEAM_WIN_PCT']]


data["OPPONENT"] = data["OPPONENT"].replace({"Los Angeles Clippers": "LA Clippers"})
# Merge opponent team stats on opponent full name and season
data = data.merge(opp_team_stats, left_on=["OPPONENT", "SEASON_ID"], right_on=["TEAM_NAME", "SEASON_ID"],
                  how="left", suffixes=("", "_opp"))
data.rename(columns={"TEAM_STL": "OPP_TEAM_STL", "TEAM_BLK": "OPP_TEAM_BLK", "TEAM_WIN_PCT": "OPP_TEAM_WIN_PCT"}, inplace=True)
data.drop(columns=["TEAM_NAME_opp"], inplace=True)

# Fill missing values for opponent stats with their mean values
data["OPP_E_DEF_RATING"] = data["OPP_E_DEF_RATING"].fillna(data["OPP_E_DEF_RATING"].mean())
data["OPP_TEAM_STL"] = data["OPP_TEAM_STL"].fillna(data["OPP_TEAM_STL"].mean())
data["OPP_TEAM_BLK"] = data["OPP_TEAM_BLK"].fillna(data["OPP_TEAM_BLK"].mean())
data["OPP_TEAM_WIN_PCT"] = data["OPP_TEAM_WIN_PCT"].fillna(data["OPP_TEAM_WIN_PCT"].mean())

# Drop any remaining rows without points (if any)
data = data.dropna(subset=["PTS"])
# Update the features list to include opponent stats instead of the player's own defensive metrics
features = ["Rolling_PTS", "Rolling_AST", "Rolling_REB", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
           "FTM", "FTA", "FT_PCT", "OREB", "DREB", "STL", "BLK", "TO", "PF", "PLUS_MINUS", "PTS_lag1", "AST_lag1", "REB_lag1", 
           "HOME_GAME", "Back_to_Back", "OPP_E_DEF_RATING", "OPP_TEAM_STL", "OPP_TEAM_BLK", "OPP_TEAM_WIN_PCT"]
target = stat_To_Check.upper()
data[features] = data[features].fillna(0)

# Prepare training data
X = data[features]
y = data[target]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Build the neural network model
model = Sequential([
    Dense(128, input_shape=(X_train.shape[1],), kernel_regularizer=l2(0.01)),
    BatchNormalization(),
    LeakyReLU(),
    Dropout(0.3),
    Dense(64, kernel_regularizer=l2(0.01)),
    BatchNormalization(),
    LeakyReLU(),
    Dropout(0.3),
    Dense(32, kernel_regularizer=l2(0.01)),
    BatchNormalization(),
    LeakyReLU(),
    Dropout(0.2),
    Dense(1)
])

model.compile(optimizer='adam', loss='mae', metrics=['mae'])

model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=1, validation_data=(X_test, y_test))

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

# For prediction, we take the average of the last 10 games
next_game_features = data[features].iloc[-10:].mean()
next_game_features_scaled = scaler.transform([next_game_features])
predicted_points = model.predict(next_game_features_scaled)[0][0]
stat = "points"
if stat_To_Check.upper() == "AST":
    stat = "assists"
elif stat_To_Check.upper() == "REB":
    stat = "rebounds"
elif stat_To_Check.upper() == "STL":
    stat = "steals"
elif stat_To_Check.upper() == "BLK":
    stat = "blocks"
elif stat_To_Check.upper() == "FG3M":
    stat = "3-point field goals made"
elif stat_To_Check.upper() == "FTM":
    stat = "free throws made"
print(f"Predicted {stat} for {player_To_Check.upper()} in the next game: {predicted_points:.2f}.")
print(f"On average, the model's predictions are off by {mae:.2f} {stat}.")
print(f'So...{player_To_Check.upper()} should get within {predicted_points - mae:.2f} - {predicted_points + mae:.2f} {stat}.')

# ----------------------------------------------THIS PART IS FOR TESTING: UN-COMMENT TO TEST-------------------------------------------------


# INPUT 5 PLAYERS OF DIFFERENT SKILL LEVELS
# player_inputs = []
# player_name = input(f"Type NBA Player: ")
# player_inputs.append(player_name)

# total_results = []
# # Define the model outside the loop
# def create_model():
#     model = Sequential([
#         Input(shape=(len(features),)),
#         Dense(128, kernel_regularizer=l2(0.01)),
#         BatchNormalization(),
#         LeakyReLU(),
#         Dropout(0.3),
#         Dense(64, kernel_regularizer=l2(0.01)),
#         BatchNormalization(),
#         LeakyReLU(),
#         Dropout(0.3),
#         Dense(32, kernel_regularizer=l2(0.01)),
#         BatchNormalization(),
#         LeakyReLU(),
#         Dropout(0.2),
#         Dense(1)
#     ])
#     model.compile(optimizer='adam', loss='mae', metrics=['mae'])
#     return model

# # Create the model once
# model = create_model()
# initial_weights = model.get_weights()  # Save the initial weights

# # Loop through players
# for player_To_Check in player_inputs:
#     player_id = player_dict.get(player_To_Check.upper())

#     if not player_id:
#         print(f"Player {player_To_Check} not found. Skipping...")
#         continue

# # Fetch game data for the player
#     all_teams = teams.get_teams()
#     team_abbrev_to_name = {team["abbreviation"]: team["full_name"] for team in all_teams}

#     # Get games for the player
#     gamefinder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id)
#     games = gamefinder.get_dict()['resultSets'][0]['rowSet']
#     columns = ["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME", "GAME_ID", "GAME_DATE",
#             "MATCHUP", "WL", "MIN", "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
#             "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "PLUS_MINUS"]
#     data = pd.DataFrame(games, columns=columns)

#     data["GAME_DATE"] = pd.to_datetime(data["GAME_DATE"])
#     data = data.sort_values(by="GAME_DATE")


#     lag_features = ['PTS', 'AST', 'REB']
#     lag_period = 1  # Using a one-game lag

#     for feature in lag_features:
#         data[f'{feature}_lag{lag_period}'] = data[feature].shift(lag_period)

    
#     data = data.dropna(subset=[f'{feature}_lag{lag_period}' for feature in lag_features])
#     # Create rolling averages for points, assists, and rebounds
#     data["Rolling_PTS"] = data["PTS"].rolling(window=3, min_periods=1).mean()
#     data["Rolling_AST"] = data["AST"].rolling(window=3, min_periods=1).mean()
#     data["Rolling_REB"] = data["REB"].rolling(window=3, min_periods=1).mean()

#     # Identify home games and back-to-back scenarios
#     data['HOME_GAME'] = data['MATCHUP'].apply(lambda x: 1 if "vs." in x else 0)
#     data['Back_to_Back'] = data['GAME_DATE'].diff().dt.days.fillna(0).apply(lambda x: 1 if x == 1 else 0)

#     # Extract opponent team from the MATCHUP column and convert to full team name
#     def extract_opponent(matchup):
#         if "vs." in matchup:
#             opp_abbrev = matchup.split("vs. ")[1]
#         elif "@" in matchup:
#             opp_abbrev = matchup.split("@ ")[1]
#         else:
#             opp_abbrev = None
#         # Use the mapping to get the full team name; if not found, return the abbreviation
#         return team_abbrev_to_name.get(opp_abbrev, opp_abbrev)

#     data['OPPONENT'] = data['MATCHUP'].apply(extract_opponent)


#     def convert_season_id(season_id):
#         year = int(season_id[-4:])  # Extract the last 4 digits
#         return f"{year}-{str(year + 1)[-2:]}"  # Format as "xxxx-xx"

#     data["SEASON_ID"] = data["SEASON_ID"].apply(convert_season_id)

#     # Load opponent defensive ratings and rename season column to match our data
#     all_defensive_ratings = pd.read_csv("estimated_defensive_ratings_since_2003.csv")

#     all_defensive_ratings.rename(columns={"SEASON": "SEASON_ID"}, inplace=True)
#     # Keep only the necessary columns from defensive ratings
#     opp_def_stats = all_defensive_ratings[['TEAM_NAME', 'SEASON_ID', 'E_DEF_RATING']]

#     team_name_replacements = {
#     "Charlotte Bobcats": "Charlotte Hornets",
#     "Seattle SuperSonics": "Oklahoma City Thunder",
#     "New Orleans/Oklahoma City Hornets": "New Orleans Pelicans",
#     "New Jersey Nets": "Brooklyn Nets",
#     "New Orleans Hornets": "New Orleans Pelicans"
#     }

#     # Replace team names in the TEAM_NAME column
#     opp_def_stats["TEAM_NAME"] = opp_def_stats["TEAM_NAME"].replace(team_name_replacements)

#     # Merge opponent defensive rating stats on opponent full name and season
#     data = data.merge(opp_def_stats,left_on=["OPPONENT", "SEASON_ID"],right_on=["TEAM_NAME", "SEASON_ID"],
#     how="left",
#     suffixes=("", "_opp")
#     )

#     # Rename the defensive rating column
#     data.rename(columns={"E_DEF_RATING": "OPP_E_DEF_RATING"}, inplace=True)
#     data.drop(columns=["TEAM_NAME_opp"], inplace=True)

#     valid_team_names = all_defensive_ratings["TEAM_NAME"].unique()
#     data = data[data["OPPONENT"].isin(valid_team_names)]

#     # Load opponent team stats and adjust column names
#     all_team_stats = pd.read_csv("nba_team_stats_since_2003.csv")
#     all_team_stats.rename(columns={"YEAR": "SEASON_ID"}, inplace=True)
#     all_team_stats.rename(columns={"STL": "TEAM_STL", "BLK": "TEAM_BLK", "WIN_PCT": "TEAM_WIN_PCT"}, inplace=True)
#     # Keep only needed columns for the opponent
#     opp_team_stats = all_team_stats[['TEAM_NAME', 'SEASON_ID', 'TEAM_STL', 'TEAM_BLK', 'TEAM_WIN_PCT']]


#     data["OPPONENT"] = data["OPPONENT"].replace({"Los Angeles Clippers": "LA Clippers"})
#     # Merge opponent team stats on opponent full name and season
#     data = data.merge(opp_team_stats, left_on=["OPPONENT", "SEASON_ID"], right_on=["TEAM_NAME", "SEASON_ID"],
#                     how="left", suffixes=("", "_opp"))
#     data.rename(columns={"TEAM_STL": "OPP_TEAM_STL", "TEAM_BLK": "OPP_TEAM_BLK", "TEAM_WIN_PCT": "OPP_TEAM_WIN_PCT"}, inplace=True)
#     data.drop(columns=["TEAM_NAME_opp"], inplace=True)

#     # Fill missing values for opponent stats with their mean values
#     data["OPP_E_DEF_RATING"] = data["OPP_E_DEF_RATING"].fillna(data["OPP_E_DEF_RATING"].mean())
#     data["OPP_TEAM_STL"] = data["OPP_TEAM_STL"].fillna(data["OPP_TEAM_STL"].mean())
#     data["OPP_TEAM_BLK"] = data["OPP_TEAM_BLK"].fillna(data["OPP_TEAM_BLK"].mean())
#     data["OPP_TEAM_WIN_PCT"] = data["OPP_TEAM_WIN_PCT"].fillna(data["OPP_TEAM_WIN_PCT"].mean())

#     # Drop any remaining rows without points (if any)
#     data = data.dropna(subset=["PTS"])
#     # Update the features list to include opponent stats instead of the player's own defensive metrics
#     features = ["Rolling_PTS", "Rolling_AST", "Rolling_REB", "MIN", "FGM", "FGA", "FG_PCT", "FG3M", "F3G3A", "FG3_PCT",
#             "FTM", "FTA", "FT_PCT", "OREB", "DREB", "STL", "BLK", "TO", "PF", "PLUS_MINUS", "PTS_lag1", "REB_lag1", "AST_lag1", 
#             "HOME_GAME", "Back_to_Back", "OPP_E_DEF_RATING", "OPP_TEAM_STL", "OPP_TEAM_BLK", "OPP_TEAM_WIN_PCT", "TEAM_VALUE"]
#     target = "PTS"

#     data[features] = data[features].fillna(0)

#     # Determine the current season
#     current_season = data["SEASON_ID"].max()
#     current_season_data = data[data["SEASON_ID"] == current_season]

#     # Exclude dates where 2 or more games were played
#     game_counts = current_season_data["GAME_DATE"].value_counts()
#     valid_dates = game_counts[game_counts == 1].index
#     current_season_data = current_season_data[current_season_data["GAME_DATE"].isin(valid_dates)]

#     # Randomly select up to 5 unique dates - currently a 1
#     random_dates = random.sample(list(current_season_data["GAME_DATE"].unique()), min(25, len(current_season_data["GAME_DATE"].unique())))

    

#     for target_date in random_dates:
#         print(f"\nChecking player: {player_To_Check}")
#         print(f"\nProcessing target date: {target_date.date()}")  # Debug print

#         # Filter training and testing data
#         train_data = data[data["GAME_DATE"] < target_date]
#         test_data = data[data["GAME_DATE"] == target_date]

#         # Debug prints for train_data
#         #print(f"Number of games in train_data: {len(train_data)}")  # Size of train_data
#         #if not train_data.empty:
#             #print(f"Train data range: {train_data['GAME_DATE'].min().date()} to {train_data['GAME_DATE'].max().date()}")  # Date range

#         # Debug prints for test_data
#         #print(f"Number of games in test_data: {len(test_data)}")  # Size of test_data
#         #if not test_data.empty:
#             #print(f"Test data date: {test_data['GAME_DATE'].iloc[0].date()}")  # Target date

#         #if train_data.empty or test_data.empty:
#             #print("Skipping due to insufficient data.")
#             #continue

#         train_data = train_data.copy()
#         test_data = test_data.copy()
#         train_data.loc[:, features] = train_data[features].fillna(0)
#         test_data.loc[:, features] = test_data[features].fillna(0)

#         X_train = train_data[features]
#         y_train = train_data[target]

#         X_test = test_data[features]
#         y_test = test_data[target]

#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)

#         # Reset the model's weights before training
#         model.set_weights(initial_weights)

#         # Train the model
#         model.fit(X_train_scaled, y_train, epochs=50, batch_size=16, verbose=0)

#         y_pred = model.predict(X_test_scaled)

#         actual_points = y_test.values[0]
#         predicted_points = y_pred[0][0]

#         total_results.append({
#             "Player": player_To_Check,
#             "Date": target_date.date(),
#             "Actual Points": actual_points,
#             "Predicted Points": predicted_points,
#             "Prediction Error": abs(actual_points - predicted_points)
#         })


# # Calculate total errors across all players
# total_rmae = mean_absolute_error([result['Actual Points'] for result in total_results],
#                                         [result['Predicted Points'] for result in total_results])
# total_mbe = np.mean([result['Predicted Points'] - result['Actual Points'] for result in total_results])
# total_r2 = r2_score([result['Actual Points'] for result in total_results],
#                     [result['Predicted Points'] for result in total_results])

# print("\n--- Total Results Across All Players ---")
# print(f"Total RMAE: {total_rmae:.2f}")
# print(f"Total MBE: {total_mbe:.2f}")
# print(f"Total R^2 Score: {total_r2:.2f}")