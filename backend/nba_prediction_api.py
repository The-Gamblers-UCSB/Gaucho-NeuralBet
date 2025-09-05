#!/usr/bin/env python3
"""
NBA Prediction API - Wrapper for the neural network model
Called from Node.js: python backend/nba_prediction_api.py "<player_name>" "<stat>"
Prints exactly one JSON object to stdout.
"""

import sys
import json
import os
import warnings

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

try:
    from NeuralNetworkModel import (
        get_player_dict, get_team_abbrev_to_name,
        fetch_and_prepare_data, merge_with_opponent_data,
        build_model, evaluate_model
    )
except ImportError as e:
    print(json.dumps({"success": False, "error": f"Failed to import NeuralNetworkModel: {e}"}))
    sys.exit(1)

STAT_ALIASES = {
    "pts": "PTS", "points": "PTS",
    "reb": "REB", "rebound": "REB", "rebounds": "REB",
    "ast": "AST", "assist": "AST", "assists": "AST",
    "stl": "STL", "steal": "STL", "steals": "STL",
    "blk": "BLK", "block": "BLK", "blocks": "BLK",
    "fg3m": "FG3M", "threes": "FG3M", "3pm": "FG3M",
    "ftm": "FTM", "free throws made": "FTM",
    "fg_pct": "FG_PCT", "fg%": "FG_PCT",
    "fg3_pct": "FG3_PCT", "3p%": "FG3_PCT",
    "ft_pct": "FT_PCT", "ft%": "FT_PCT",
}

READABLE = {
    "PTS": "points", "REB": "rebounds", "AST": "assists",
    "STL": "steals", "BLK": "blocks", "FG3M": "3-point field goals made",
    "FTM": "free throws made", "FG_PCT": "field goal %", "FG3_PCT": "3-point %",
    "FT_PCT": "free throw %",
}

# Must match NeuralNetworkModel.evaluate_model feature expectations
FEATURES = [
    "Rolling_PTS","Rolling_AST","Rolling_REB","MIN","FGM","FGA","FG_PCT",
    "FG3M","FG3A","FG3_PCT","FTM","FTA","FT_PCT","OREB","DREB",
    "STL","BLK","TO","PF","PLUS_MINUS","PTS_lag1","AST_lag1","REB_lag1",
    "HOME_GAME","Back_to_Back","OPP_E_DEF_RATING","OPP_TEAM_STL",
    "OPP_TEAM_BLK","OPP_TEAM_WIN_PCT",
]

def _fail(msg: str):
    print(json.dumps({"success": False, "error": msg}))

def _ok(payload: dict):
    out = {"success": True}
    out.update(payload)
    print(json.dumps(out))

def normalize_player_name(name: str) -> str:
    """Normalize player name with special cases for common names"""
    name = (name or "").strip()
    
    # Handle common name variations
    special_cases = {
        "lebron": "LeBron James",
        "luka": "Luka Dončić", 
        "giannis": "Giannis Antetokounmpo",
        "steph curry": "Stephen Curry",
        "stephen curry": "Stephen Curry",
        "kd": "Kevin Durant",
        "kevin durant": "Kevin Durant",
        "joel embiid": "Joel Embiid",
        "nikola jokic": "Nikola Jokić",
        "jayson tatum": "Jayson Tatum"
    }
    
    name_lower = name.lower()
    if name_lower in special_cases:
        return special_cases[name_lower]
    
    return name.title()

def main():
    if len(sys.argv) != 3:
        _fail("Usage: python nba_prediction_api.py <player_name> <stat>")
        return

    player_name = normalize_player_name(sys.argv[1])
    stat_in = (sys.argv[2] or "").strip().lower()
    stat = STAT_ALIASES.get(stat_in, stat_in.upper())
    readable_stat = READABLE.get(stat, stat)

    try:
        # Lookups
        player_map = get_player_dict()  # {FULL_NAME_UPPER: id}
        team_map = get_team_abbrev_to_name()

        player_id = player_map.get(player_name.upper())
        if not player_id:
            # Try partial matching for common cases
            possible_matches = [name for name in player_map.keys() 
                              if player_name.upper().split()[0] in name]
            if len(possible_matches) == 1:
                player_id = player_map[possible_matches[0]]
                player_name = possible_matches[0].title()
            else:
                _fail(f"Player '{player_name}' not found in NBA database. Possible matches: {possible_matches[:5] if possible_matches else 'None'}")
                return

        # Data prep (signature: (player_id, team_abbrev_to_name))
        df = fetch_and_prepare_data(player_id, team_map)
        if df is None or df.empty:
            _fail(f"No game data found for {player_name}")
            return

        df = merge_with_opponent_data(df)
        if df is None or df.empty:
            _fail(f"Could not merge opponent data for {player_name}")
            return

        # Target and feature checks
        if stat not in df.columns:
            available_stats = [col for col in df.columns if col in STAT_ALIASES.values()]
            _fail(f"Stat '{stat}' not available for {player_name}. Available stats: {available_stats}")
            return

        # Check for required features and fill missing ones
        missing_features = []
        for feature in FEATURES:
            if feature not in df.columns:
                missing_features.append(feature)
        
        # If we have some missing features, we can still proceed with available ones
        available_features = [f for f in FEATURES if f in df.columns]
        
        if len(available_features) < 10:  # Need at least some features
            _fail(f"Too many missing features. Available: {len(available_features)}, Missing: {missing_features[:10]}...")
            return

        # Build + evaluate model (evaluate_model does the training)
        model = build_model(len(available_features))
        if model is None:
            _fail("Failed to build neural network model")
            return
            
        prediction, mae = evaluate_model(model, df, available_features, stat)
        if prediction is None or mae is None:
            _fail("Model training failed or produced no prediction")
            return

        # Ensure we have valid numeric values
        try:
            prediction = float(prediction)
            mae = float(mae)
        except (ValueError, TypeError):
            _fail("Model returned invalid prediction values")
            return

        # Confidence & range calculation
        # Adjust confidence based on stat type
        if stat in ['PTS']:
            max_mae = 8.0
        elif stat in ['REB', 'AST']:
            max_mae = 4.0
        elif stat in ['STL', 'BLK']:
            max_mae = 2.0
        else:
            max_mae = 5.0
            
        confidence = max(60.0, min(95.0, 100.0 - (mae / max_mae) * 35.0))
        
        rng = {
            "min": round(max(0.0, prediction - mae * 1.2), 1),
            "max": round(prediction + mae * 1.2, 1),
        }

        _ok({
            "player": player_name,
            "stat": stat,
            "readable_stat": readable_stat,
            "prediction": round(prediction, 1),
            "confidence": round(confidence, 1),
            "range": rng,
            "mae": round(mae, 2),
            "data_points": int(len(df)),
            "features_used": len(available_features),
        })

    except Exception as e:
        import traceback
        error_details = f"Error processing prediction: {e}"
        if os.getenv('DEBUG'):
            error_details += f"\nTraceback: {traceback.format_exc()}"
        _fail(error_details)

if __name__ == "__main__":
    main()