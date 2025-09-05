from nba_api.stats.endpoints import playercareerstats
career = playercareerstats.PlayerCareerStats(player_id='203999') 


career.get_data_frames()[0]

# json
career.get_json()

# dictionary
career.get_dict()