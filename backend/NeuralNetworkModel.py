# backend/nba_stat_predictor.py
import os
import pandas as pd
import numpy as np
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import leaguegamefinder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LeakyReLU, Input
from tensorflow.keras.regularizers import l2

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- Public API (imported by nba_prediction_api.py) ----------

def get_player_dict():
    """Return {FULL_NAME_UPPER: player_id} mapping."""
    all_players = players.get_players()
    return {p['full_name'].upper(): p['id'] for p in all_players}

def get_team_abbrev_to_name():
    """Return {TEAM_ABBR: TEAM_FULL_NAME} mapping."""
    all_teams = teams.get_teams()
    return {t["abbreviation"]: t["full_name"] for t in all_teams}

def fetch_and_prepare_data(player_id, team_abbrev_to_name):
    """
    Return a DataFrame of a player's game logs with engineered features.
    Columns produced include:
      Rolling_* , *_lag1, HOME_GAME, Back_to_Back, OPPONENT, SEASON_ID, and box-score cols.
    """
    # --- fetch games
    gf = leaguegamefinder.LeagueGameFinder(player_id_nullable=player_id)
    games = gf.get_dict()['resultSets'][0]['rowSet']
    cols = ["SEASON_ID","TEAM_ID","TEAM_ABBREVIATION","TEAM_NAME","GAME_ID","GAME_DATE",
            "MATCHUP","WL","MIN","PTS","FGM","FGA","FG_PCT","FG3M","FG3A","FG3_PCT",
            "FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TO","PF","PLUS_MINUS"]
    df = pd.DataFrame(games, columns=cols)
    if df.empty:
        return df

    # --- time & sort
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df.sort_values("GAME_DATE").reset_index(drop=True)

    # --- lags
    for feat in ['PTS', 'AST', 'REB']:
        df[f"{feat}_lag1"] = df[feat].shift(1)

    # require lags available
    df = df.dropna(subset=["PTS_lag1","AST_lag1","REB_lag1"])

    # --- rolling means (3-game like your original)
    df["Rolling_PTS"] = df["PTS"].rolling(window=3, min_periods=1).mean()
    df["Rolling_AST"] = df["AST"].rolling(window=3, min_periods=1).mean()
    df["Rolling_REB"] = df["REB"].rolling(window=3, min_periods=1).mean()

    # --- home/back-to-back
    df["MATCHUP"] = df["MATCHUP"].astype(str)
    df["HOME_GAME"] = df["MATCHUP"].str.contains(r"\bvs\.\b", na=False).astype(int)
    df["Back_to_Back"] = (df["GAME_DATE"].diff().dt.days == 1).fillna(False).astype(int)

    # --- opponent full name from matchup
    def extract_opp(matchup: str):
        if "vs." in matchup:
            abbr = matchup.split("vs. ")[1]
        elif "@" in matchup:
            abbr = matchup.split("@ ")[1]
        else:
            return None
        return team_abbrev_to_name.get(abbr, abbr)

    df["OPPONENT"] = df["MATCHUP"].apply(extract_opp)

    # --- normalize season id (e.g., "2023-24")
    def season_fmt(s):
        yr = int(str(s)[-4:])
        return f"{yr}-{str(yr+1)[-2:]}"
    df["SEASON_ID"] = df["SEASON_ID"].apply(season_fmt)

    return df

def merge_with_opponent_data(df):
    """
    Merge opponent defensive rating and team stats. Fills missing with column means.
    Produces columns: OPP_E_DEF_RATING, OPP_TEAM_STL, OPP_TEAM_BLK, OPP_TEAM_WIN_PCT
    """
    if df is None or df.empty:
        return df

    # defensive ratings
    def_stats = pd.read_csv(os.path.join(HERE, "estimated_defensive_ratings_since_2003.csv"))
    def_stats = def_stats.rename(columns={"SEASON": "SEASON_ID"})
    def_stats["TEAM_NAME"] = def_stats["TEAM_NAME"].replace({
        "Charlotte Bobcats": "Charlotte Hornets",
        "Seattle SuperSonics": "Oklahoma City Thunder",
        "New Orleans/Oklahoma City Hornets": "New Orleans Pelicans",
        "New Jersey Nets": "Brooklyn Nets",
        "New Orleans Hornets": "New Orleans Pelicans",
    })
    opp_def = def_stats[["TEAM_NAME","SEASON_ID","E_DEF_RATING"]]

    # merge defensive rating
    df = df.merge(
        opp_def, left_on=["OPPONENT","SEASON_ID"], right_on=["TEAM_NAME","SEASON_ID"], how="left"
    ).rename(columns={"E_DEF_RATING":"OPP_E_DEF_RATING"})
    if "TEAM_NAME" in df.columns:
        df = df.drop(columns=["TEAM_NAME"])

    # filter to valid names (keeps rows with a recognizable opponent)
    valid_names = set(def_stats["TEAM_NAME"].unique())
    df = df[df["OPPONENT"].isin(valid_names)]

    # team box stats
    team_stats = pd.read_csv(os.path.join(HERE, "nba_team_stats_since_2003.csv"))
    team_stats = team_stats.rename(columns={
        "YEAR":"SEASON_ID", "STL":"TEAM_STL", "BLK":"TEAM_BLK", "WIN_PCT":"TEAM_WIN_PCT"
    })
    opp_team = team_stats[["TEAM_NAME","SEASON_ID","TEAM_STL","TEAM_BLK","TEAM_WIN_PCT"]]

    # minor name normalization
    df["OPPONENT"] = df["OPPONENT"].replace({"Los Angeles Clippers":"LA Clippers"})

    # merge team stats
    df = df.merge(
        opp_team, left_on=["OPPONENT","SEASON_ID"], right_on=["TEAM_NAME","SEASON_ID"], how="left"
    ).rename(columns={
        "TEAM_STL":"OPP_TEAM_STL",
        "TEAM_BLK":"OPP_TEAM_BLK",
        "TEAM_WIN_PCT":"OPP_TEAM_WIN_PCT"
    })
    if "TEAM_NAME" in df.columns:
        df = df.drop(columns=["TEAM_NAME"])

    # fill missing opponent features with means
    for col in ["OPP_E_DEF_RATING","OPP_TEAM_STL","OPP_TEAM_BLK","OPP_TEAM_WIN_PCT"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

    return df

def build_model(input_dim: int):
    """Return a compiled Keras model with the architecture you were using."""
    model = Sequential([
        Input(shape=(input_dim,)),
        Dense(128, kernel_regularizer=l2(0.01)),
        BatchNormalization(), LeakyReLU(), Dropout(0.3),
        Dense(64, kernel_regularizer=l2(0.01)),
        BatchNormalization(), LeakyReLU(), Dropout(0.3),
        Dense(32, kernel_regularizer=l2(0.01)),
        BatchNormalization(), LeakyReLU(), Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mae', metrics=['mae'])
    return model

def evaluate_model(model, data, features, target):
    """
    Train/test split, compute MAE, and produce a next-game prediction
    (mean of last 10 rows as input).
    Returns: (prediction_float, mae_float)
    """
    # guard
    for c in features + [target]:
        if c not in data.columns:
            return None, None

    X = data[features].fillna(0)
    y = data[target].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=0, validation_data=(X_test, y_test))
    y_pred = model.predict(X_test, verbose=0)
    mae = float(mean_absolute_error(y_test, y_pred))

    # next-game proxy: average of last 10 rows (pre-scale), then transform
    next_input = X.iloc[-10:].mean().values.reshape(1, -1)
    next_input_scaled = scaler.transform(next_input)
    prediction = float(model.predict(next_input_scaled, verbose=0)[0][0])

    return prediction, mae
