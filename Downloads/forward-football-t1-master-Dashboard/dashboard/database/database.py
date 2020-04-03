import pandas as pd
import sqlalchemy as sql
import MySQLdb
import yaml
import os.path

# get configurations from yaml file
cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml')))
sql_engine = sql.create_engine(cfg['mysql'])


######## Helper Functions ########
# you can ignore these
def dropdown_options(df, keys, values):
    """
    function to create the dictionary that states all the possible chained dropdown button options
    """
    filter_df = df[[keys, values]]
    group_df = filter_df.groupby(keys)[values].apply(list).reset_index(name=values)
    possible_options = dict(zip(group_df[keys], group_df[values]))
    return possible_options

def match_metrics_data(match_df):
    # return the possible metrics for that selected match
    # takes data and returns list of possible metrics
    available_metrics = list(match_df)
    # exclude playerId, matchId, team, name
    metrics_to_exclude = ['playerId', 'matchId', 'team', 'name']
    available_metrics = list(set(available_metrics)-set(metrics_to_exclude))
    return available_metrics

######## MySQL QUERIES ########
def teams_and_matches(team='AFCU13-7', engine=sql_engine):  
    """Selects all possible matchId where team is found in home(team1) or away(team2)
    Args:
        team: teamId
        engine: sql-engine configuration
    
    Returns:
        A list of possible matchIds for a selected team
    """  
    query = "SELECT matchId from clean_match WHERE team1='" +  team + "' OR team2='" + team + "'"
    df = pd.read_sql_query(query, engine)
    #print(df['matchId'].to_list())
    return df['matchId'].to_list()

def matches_and_players(matchId='61614647-8504-4983-8976-143056946FF0', engine=sql_engine):    
    """Selects all possible playerIds for a selected matchId
    Args:
        matchId: matchId
        engine: sql-engine configuration
    
    Returns:
        A list of possible playerIds for a selected match
    """  
    query = "SELECT playerId from clean_match_teammates_statistics WHERE matchId='" + matchId + "'"
    df = pd.read_sql_query(query, engine)
    return df['playerId'].to_list()

# yield possible options for team selections by club
def team_selection_club(engine=sql_engine):
    """Selects all possible teamns that appear in either team1 or team2 column
    Args:
        engine: sql-engine configuration
    
    Returns:
        A list of possible teamIds
    """  
    select_team1 = 'SELECT team1 FROM clean_match'
    team1_df = pd.read_sql_query(select_team1, engine)

    select_team2 = 'SELECT team2 FROM clean_match'
    team2_df = pd.read_sql_query(select_team2, engine)

    unique_team1 = team1_df['team1'].unique()
    unique_team2 = team2_df['team2'].unique()

    unique_teams = list(set().union(unique_team1, unique_team2))
    return unique_teams

# when the coach picks a match, return full match data 
def select_match_data(matchId, engine=sql_engine):
    """Selects full match data from match_statistics for a selected matchId
    Args:
        matchId: matchId
        engine: sql-engine configuration
    
    Returns:
        A pandas DataFrame with full match data
    """  
    select_match = "SELECT * FROM clean_match_teammates_statistics WHERE matchId='" + matchId + "'"
    match_df = pd.read_sql_query(select_match, engine)
    return match_df


# available matches per player
def possible_games_player(playerId, engine=sql_engine):
    """Selects all possible games for a selected playerId
    Args:
        playerId: playerId
        engine: sql-engine configuration
    
    Returns:
        A list of possible matches for a selected player
    """  
    select_games = "SELECT playerId, matchId FROM clean_match_teammates_statistics WHERE playerId=" + playerId
    games_df = pd.read_sql_query(select_games, engine)
    unique_games = games_df['matchId'].unique()
    return unique_games

# return a dataframe that has averages for all metrics
def quadrant_plot_data_club(engine=sql_engine):
    select_match_and_team = "SELECT matchId, team1, team2 FROM clean_match"
    complete_df = pd.read_sql_query(select_match_and_team, engine)
    all_matches = complete_df['matchId'].to_list()

    return all_matches

# query possible dates for matches for a particular team
def time_range_matches(team, engine=sql_engine):
    select_times = "SELECT Match_date, matchId FROM clean_match WHERE team1='" +  team + "' OR team2='" + team + "'"
    time_df = pd.read_sql_query(select_times, engine)
    dates = time_df['Match_date'].unique()
    #matches = time_df['matchId']
    return dates

# return latest matches from clean_match for the performance screenshot for a club
def latest_matches_per_team(team, engine=sql_engine):
    latest_matches = "SELECT Match_date, match_time, matchID FROM clean_match WHERE team1='" +  team + "' OR team2='" + team + "'" \
                     + " ORDER BY match_time DESC"
    latest_df = pd.read_sql_query(latest_matches, engine)
    set_of_matches = latest_df['matchID'].to_list()
    set_of_matches = ["'" + m for m in set_of_matches]
    set_of_matches = [m + "'" for m in set_of_matches]
    set_of_matches_str = ','.join(set_of_matches)
    match_dates = latest_df['Match_date'].to_list()
    return set_of_matches_str, match_dates

# return the data for a player over the last five matches and split them up into three dfs
# for internal, external and ball data
def latest_matches_per_player(playerId, matchIds, engine=sql_engine):
    latest_matches = "SELECT * FROM clean_match_teammates_statistics" \
                    + " WHERE matchID in (" + matchIds + ") AND playerID = " + playerId
    latest_df = pd.read_sql_query(latest_matches, engine)


    
    # mean_df
    # exclude latest data from mean calculation
    mean_df = latest_df.iloc[1:,:]
    mean_df.loc['mean'] = mean_df.mean()
    # add latest data back in
    mean_df.loc['latest'] = latest_df.iloc[0, :]

    # df to display the data in the view
    display_df = pd.DataFrame(mean_df.transpose())
    print(display_df)
    print(display_df.columns)
    final_display_df = pd.DataFrame({'Average Last 5 matches': display_df['mean'], 'Parameters': mean_df.columns, 'Latest Match': display_df['latest']})
    final_display_df = final_display_df.iloc[2:]
    final_display_df = final_display_df.iloc[:-2]


    # External DataFrame
    external_df = mean_df[['imaAccHigh', 'imaDecHigh', 'imaRighHigh', 'imaLeftHigh']]
    external_df['SumE'] = external_df['imaAccHigh'] + external_df['imaDecHigh'] + external_df['imaRighHigh'] + external_df['imaLeftHigh']
    external_df.loc['difference'] = external_df.loc['latest'] - external_df.loc['mean']

    # Internal DataFrame that needs to be normalized
    internal_df = mean_df[['maxHR', 'exerciseLoad', 'calories']]
    norm_internal_df = (internal_df-internal_df.min())/(internal_df.max()-internal_df.min())
    norm_internal_df['SumI'] = norm_internal_df['maxHR'] + norm_internal_df['exerciseLoad'] + norm_internal_df['calories']
    norm_internal_df.loc['difference'] = norm_internal_df.loc['latest'] - norm_internal_df.loc['mean']

    # ball DataFrame
    ball_df = mean_df[['touches', 'passes', 'shots']]
    ball_df['SumB'] = ball_df['touches'] + ball_df['passes'] + ball_df['shots']
    ball_df.loc['difference'] = ball_df.loc['latest'] - ball_df.loc['mean']

    return external_df, norm_internal_df, ball_df, final_display_df

