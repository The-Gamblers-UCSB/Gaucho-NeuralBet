from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, leaguegamefinder, boxscoretraditionalv3
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pandas as pd

# INPUT ANY NBA PLAYER AND THE MODEL WILL MAKE PREDICTIONS ON HOW MANY POINTS THIS PLAYER SCORES IN THEIR NEXT GAME
# USES EVERY NBA GAME EVER PLAYED BY THIS PLAYER
# USES ROLLING AVERAGES INSSTEAD OF HARD VALUES
all_players = players.get_players()

player_dict = {player['full_name'].upper(): player['id'] for player in all_players}

player_To_Check = input("Type an NBA Player:")

player_id = player_dict[player_To_Check.upper()]

gamefinder = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id)
games = gamefinder.get_dict()['resultSets'][0]['rowSet']
print
columns = ["SEASON_ID", "TEAM_ID", "TEAM_ABREVIATION", "TEAM_NAME", "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN", "PTS", "FGM", "FGA", "FG_PCT", 
    "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT", "OREB", "DREB", 
    "REB", "AST", "STL", "BLK", "TO", "PF", "PLUS_MINUS"
]
data = pd.DataFrame(games, columns=columns)

data["GAME_DATE"] = pd.to_datetime(data["GAME_DATE"])

data = data.sort_values(by="GAME_DATE")

data["Rolling_PTS"] = data["PTS"].rolling(window=5, min_periods=1).mean()
data["Rolling_AST"] = data["AST"].rolling(window=5, min_periods=1).mean()
data["Rolling_REB"] = data["REB"].rolling(window=5, min_periods=1).mean()

data = data.dropna(subset=["PTS"])

features = ["Rolling_PTS", "Rolling_AST", "Rolling_REB", "MIN", "FG_PCT", "FG3_PCT", "FT_PCT"]
target = "PTS"

data[features] = data[features].fillna(0) 

X = data[features]
y = data[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model Performance:\nMSE: {mse:.2f}\nR²: {r2:.2f}")

