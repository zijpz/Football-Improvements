import pandas as pd
import numpy as np
import sqlalchemy as sql
import MySQLdb
import mysql.connector
import yaml
import os.path
from sklearn.preprocessing import MinMaxScaler

# get configurations from yaml file
# cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml')))
# sql_engine = sql.create_engine(cfg['mysql'])

sql_engine = sql.create_engine('mysql://root:admin@localhost:3306/forwardfootball')

db=mysql.connector.connect(host = "localhost", user = "root", passwd="admin", db= "forwardfootball")


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
def teams_and_matches(team='AFCU9-1', engine=sql_engine):  
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

def matches_and_players(matchId, engine=sql_engine):    
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

    # turn id colum to strings
    match_df['playerId'] = match_df['playerId'].astype(str)

    # summary_df = match_df.copy()
    # summary_df.loc['latest'] = summary_df.loc[0,:]

    # ### need to refine filtering for the following two ###
    # summary_df.loc['averageFourWeeks'] = latest_df.mean()
    # summary_df.loc['averageLastWeek'] = mean_df.loc['meanLast5']
    # display_df = pd.DataFrame(summary_df.transpose())
    
    # final_display_df = pd.DataFrame({'Last Week ': display_df['averageLastWeek'], 'Parameters': summary_df.columns, 'Average Last 4 Weeks': display_df['averageFourWeeks'],\
    #                                 'averageFourWeeks': display_df['averageFourWeeks']})
    # final_display_df['Percent Change'] = ((final_display_df['Average Last 4 Weeks'] / final_display_df['Last Week']) / final_display_df['Last Week']) * 100
    # final_display_df['Average Last 4 Weeks'] = final_display_df['Average Last 4 Weeks'].astype(float).round(2)
    # final_display_df['Last Week'] = final_display_df['Last Week'].astype(float).round(2)
    # final_display_df['Percent Change'] = final_display_df['Percent Change'].astype(float).round(0)

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
# need a parameter that can specify how many latest games should be pulled
def latest_matches_per_team(team, engine=sql_engine):
    latest_matches = "SELECT Match_date, match_time, matchID FROM clean_match WHERE team1='" +  team + "' OR team2='" + team + "'" \
                     + " ORDER BY match_time DESC"
    latest_df = pd.read_sql_query(latest_matches, engine)
    set_of_matches = latest_df['matchID'].to_list()
    set_of_matches_str = stringify_list_for_sql(set_of_matches)
    # set_of_matches = ["'" + m for m in set_of_matches]
    # set_of_matches = [m + "'" for m in set_of_matches]
    # set_of_matches_str = ','.join(set_of_matches)
    match_dates = latest_df['Match_date'].to_list()
    return set_of_matches_str, match_dates

# return all match data fro
def all_match_data_per_team(team, player_id, engine=sql_engine):
    # if isinstance(player_ids, str):
    #     all_matches = "SELECT * FROM clean_match_teammates_statistics" \
    #               #"WHERE playerId ='" + player_ids + "'"
    # else:
    #     players = player_ids
    #     set_of_players = stringify_list_for_sql(players)
    #     #all_matches = "SELECT * FROM clean_match_teammates_statistics" \
    #     #          "WHERE playerId in (" + set_of_players + ")"
    all_matches = "SELECT * FROM clean_match_teammates_statistics"
    all_matches = pd.read_sql_query(all_matches, engine)

    
    ### get all the player info ###
    player_df = all_matches[all_matches['playerId'] == player_id]
    #player_df = all_matches.copy()
    player_df.drop(columns=['name', 'team'], inplace=True)
    match_list = player_df['matchId'].to_list()

    ### get all the means per game ###
    # only select matches for which that player has played
    avg_df = all_matches[all_matches['matchId'].isin(match_list)]
    avg_df = avg_df.groupby('matchId')[all_matches.columns].mean().reset_index()
    avg_df['playerId'] = 'mean'
    cols = avg_df.columns.to_list()
    cols[0] = 'playerId'
    cols[-1] = 'matchId'
    avg_df = avg_df[cols]


    ### final_df only contains the player and and game averages ###
    final_df = pd.concat([player_df, avg_df])

    return final_df 


# return the data for a player over the last five matches and split them up into three dfs
# for internal, external and ball data
def latest_matches_per_player(playerId, matchIds, engine=sql_engine):
    latest_matches = "SELECT * FROM clean_match_teammates_statistics" \
                    + " WHERE matchID in (" + matchIds + ") AND playerID = " + playerId
    latest_df = pd.read_sql_query(latest_matches, engine)

    # add up the ima events mid and high into one category
    latest_df['Accelerations'] = latest_df['imaAccHigh'] + latest_df['imaAccMid']
    latest_df['Decelerations'] = latest_df['imaDecHigh'] + latest_df['imaDecMid']
    latest_df['Right Turns'] = latest_df['imaRighHigh'] + latest_df['imaRighMid']
    latest_df['Left Turns'] = latest_df['imaLeftHigh'] + latest_df['imaLeftMid']

    # calculate sums for ima and ball evenet
    latest_df['imaSum'] = latest_df['Accelerations'] + latest_df['Decelerations'] + latest_df['Right Turns'] + latest_df['Left Turns']
    latest_df['ballSum'] = latest_df['touches'] + latest_df['passes'] + latest_df['shots'] + latest_df['tackles']

    # exclude latest data from mean calculation
    # select five matches to calculate the average for
    mean_df = latest_df.iloc[1:6,:]
    mean_df.loc['meanLast5'] = mean_df.mean()
    mean_df.loc['latest'] = latest_df.iloc[0,:]

    # get id of the latest match
    match_ids = latest_df['matchId'].to_list()
    latest_match_id = match_ids[0]

    # max_df 
    summary_df = latest_df.copy()
    summary_df = summary_df[summary_df['matchId'] != latest_match_id]
    summary_df.loc['maxValue'] = summary_df.max()
    single_row = latest_df.loc[latest_df['matchId'] == latest_match_id]
    single_row = single_row.rename(index={0: 'latest'})
    # single_row.loc[0, 'playerId'] = 'latest'
    summary_df = summary_df.append(single_row)
    #summary_df.loc['latest'] = latest_df.loc[latest_df['matchId'] == latest_match_id]

    ### need to refine filtering for the following two ###
    summary_df.loc['averageFourWeeks'] = latest_df.mean()
    summary_df.loc['averageLastWeek'] = mean_df.loc['meanLast5']

    # mean_df for A/C ratio
    #mean_AC = latest_df.iloc[1:,:]
    # chronic load needs to be adjusted to load over 4 weeks as of now acute load is calculated as past 5 games
    mean_AC = latest_df.copy()

    acute_df = latest_df.iloc[0:5,:]
    chronic_df = latest_df
    mean_AC.loc['meanChronic'] = chronic_df.mean()
    mean_AC.loc['meanLast5'] = acute_df.mean()

    # Calculations for A/C dataframe
    mean_AC.loc['ACRatio'] = mean_AC.loc['meanLast5'] / mean_AC.loc['meanChronic']
    mean_AC.loc['Latest'] = mean_AC.loc[0,:]
    #mean_AC.loc['monotony'] = 
    
    # only keep the relevant rows (acute, chronic, ac-ratio) for the AC data
    mean_AC = mean_AC[mean_AC.index.isin(['meanLast5', 'meanChronic', 'ACRatio', 'Latest'])]

    # df to display the data in the view
    display_df = pd.DataFrame(summary_df.transpose())

    final_display_df = pd.DataFrame({'Latest Match': display_df['latest'], 'Parameters': summary_df.columns, 'Max Performance': display_df['maxValue'],\
                                    'Average 4 Weeks': display_df['averageFourWeeks'], 'Last Week': display_df['averageLastWeek']})
    
    # remove unneedeed values
    final_display_df = final_display_df[~final_display_df['Parameters'].isin(['name', 'playerId', 'matchId', 'team', 'clearences'])]

    
    final_display_df['Latest Match'] = final_display_df['Latest Match'].astype(float)
    final_display_df['Max Performance'] = final_display_df['Max Performance'].astype(float)
    final_display_df['FIT Score'] = final_display_df['Latest Match'] / final_display_df['Max Performance'] * 100

    # replace zero with nan not permanent change
    final_display_df = final_display_df.replace({'0':np.nan, 0:np.nan})

    # calculate percent change
    final_display_df['percentChange'] = ((final_display_df['Last Week'] - final_display_df['Average 4 Weeks']) / final_display_df['Average 4 Weeks']) * 100
    
    # format data
    final_display_df['Latest Match'] = final_display_df['Latest Match'].astype(float).round(2)
    final_display_df['FIT Score'] = final_display_df['FIT Score'].astype(float).round(0)
    final_display_df['Average 4 Weeks'] = final_display_df['Average 4 Weeks'].astype(float).round(2)
    final_display_df['Last Week'] = final_display_df['Last Week'].astype(float).round(2)
    final_display_df['percentChange'] = final_display_df['percentChange'].astype(float).round(2)
    final_display_df['Percent Change'] = final_display_df['percentChange'].astype(str) + '%'


    # External DataFrame
    external_df = mean_df[['imaAccHigh', 'imaDecHigh', 'imaRighHigh', 'imaLeftHigh']]
    norm_external_df = (external_df-external_df.min())/(external_df.max()-external_df.min()) * 100
    norm_external_df['SumE'] = norm_external_df['imaAccHigh'] + norm_external_df['imaDecHigh'] + norm_external_df['imaRighHigh'] + norm_external_df['imaLeftHigh']
    norm_external_df.loc['difference'] = norm_external_df.loc['latest'] - norm_external_df.loc['meanLast5']

    # Internal DataFrame that needs to be normalized
    internal_df = mean_df[['maxHR', 'exerciseLoad', 'calories', 'maxVO2']]
    norm_internal_df = (internal_df-internal_df.min())/(internal_df.max()-internal_df.min()) * 100
    norm_internal_df['SumI'] = norm_internal_df['maxHR'] + norm_internal_df['exerciseLoad'] + norm_internal_df['calories'] + norm_internal_df['maxVO2']
    norm_internal_df.loc['difference'] = norm_internal_df.loc['latest'] - norm_internal_df.loc['meanLast5']

    # ball DataFrame
    ball_df = mean_df[['touches', 'passes', 'shots', 'tackles']]
    norm_ball_df = (ball_df-ball_df.min())/(ball_df.max()-ball_df.min()) * 100
    norm_ball_df['SumB'] = norm_ball_df['touches'] + norm_ball_df['passes'] + norm_ball_df['shots'] + norm_ball_df['tackles']
    norm_ball_df.loc['difference'] = norm_ball_df.loc['latest'] - norm_ball_df.loc['meanLast5']

    # fit score table
    fit_score_df = final_display_df[['Parameters', 'Latest Match', 'FIT Score', 'Max Performance']]
    #fit_score_table['FIT Score'] = fit_score_table['FIT Score'] - 100
    fit_score_df['belowFIT'] = np.where(fit_score_df['FIT Score']<100, fit_score_df['FIT Score'], np.nan)
    fit_score_df['aboveFIT'] = np.where(fit_score_df['FIT Score']>=100, fit_score_df['FIT Score'], np.nan)
    # fit_score_df['aboveFIT'] = fit_score_df['aboveFIT'] 
    fit_score_df = fit_score_df.round(2)

    # get columns in correct order
    fit_score_df = fit_score_df[['Latest Match', 'belowFIT', 'Parameters', 'aboveFIT', 'Max Performance', 'FIT Score']]
    #fit_score_table['FIT Score'] = fit_score_table['FIT Score'].abs() 

    # calculate the three values for the gauge
    internal_gauge_val = round(mean_AC.loc['meanLast5', 'exerciseLoad'] / mean_AC.loc['Latest', 'exerciseLoad'], 2)

    external_gauge_val = round(
        (mean_AC.loc['meanLast5', 'Accelerations'] + mean_AC.loc['meanLast5', 'Decelerations'] + mean_AC.loc['meanLast5', 'Right Turns'] + mean_AC.loc['meanLast5', 'Left Turns']) / \
        (mean_AC.loc['Latest', 'Accelerations'] + mean_AC.loc['Latest', 'Decelerations'] + mean_AC.loc['Latest', 'Right Turns'] + mean_AC.loc['Latest', 'Left Turns'])      
    , 2)

    ball_gauge_val = round(
        (mean_AC.loc['meanLast5', 'touches'] + mean_AC.loc['meanLast5', 'shots'] + mean_AC.loc['meanLast5', 'passes'] + mean_AC.loc['meanLast5', 'tackles']) / \
        (mean_AC.loc['Latest', 'touches'] + mean_AC.loc['Latest', 'shots'] + mean_AC.loc['Latest', 'passes'] + mean_AC.loc['Latest', 'tackles'])      
    , 2)
    

    gauge_val_dict = {"internal": internal_gauge_val, "external": external_gauge_val, "ball": ball_gauge_val}

    # return needed data for performance trend snapshot
    trend_df = latest_df[['matchId', 'exerciseLoad', 'imaSum', 'ballSum']]

    return norm_external_df, norm_internal_df, norm_ball_df, final_display_df, mean_AC, fit_score_df, gauge_val_dict, trend_df

# return the data for an entire over the last five matches to calculate last match compared to previoius 4 matches
# matches are ordered from latest to oldest
# can pass in matchIds using latest_matches_per_team()
def match_performance_development(matchIds, engine=sql_engine):
    latest_matches_team = "SELECT * FROM clean_match_teammates_statistics" \
                    + " WHERE matchID in (" + matchIds + ")"
    latest_df = pd.read_sql_query(latest_matches_team, engine)

    latest_df['playerId'] = latest_df['playerId'].astype(str)

    # create ima columns
    latest_df['ima_left'] = latest_df['imaLeftHigh'] + latest_df['imaLeftMid']
    latest_df['ima_right'] = latest_df['imaRighHigh'] + latest_df['imaRighMid']
    latest_df['ima_acc'] = latest_df['imaAccHigh'] + latest_df['imaAccMid']
    latest_df['ima_dec'] = latest_df['imaDecHigh'] + latest_df['imaDecMid']
    

    # get match_ids as list
    match_ids = latest_df['matchId'].unique().tolist()
    latest_matchId = match_ids[0]
    other_four_matchId = match_ids[1:]

    # get first match and mean 
    latest_match_df = latest_df[latest_df['matchId']==latest_matchId]
    latest_match_df.loc['mean_last_match'] = latest_match_df.mean()

    # for that mean_last_four row make playerId to mean_last_match
    latest_match_df.loc['mean_last_match', 'playerId'] = 'mean'

    # get list of players in latest match
    latest_match_players = latest_match_df['playerId'].tolist()

    # get last four matches and mean
    last_four_matches_df = latest_df[latest_df['matchId'].isin(other_four_matchId)]
    last_four_matches_df.loc['mean_last_four'] = last_four_matches_df.mean()

    # for that mean_last_four row make playerId to mean_last_four
    last_four_matches_df.loc['mean_last_four', 'playerId'] = 'mean'

    # get list of players for four_matches
    last_four_players = last_four_matches_df['playerId'].tolist()

    # keep set difference that are present in both player lists
    common_players = intersection(latest_match_players, last_four_players)

    # filter both by these players to make sure only those are kept and sort by player id
    latest_match_df = latest_match_df[latest_match_df['playerId'].isin(common_players)]
    latest_match_df.sort_values(by='playerId', inplace=True)
    latest_match_df.reset_index(inplace=True)
    last_four_matches_df = last_four_matches_df[last_four_matches_df['playerId'].isin(common_players)]
    last_four_matches_df.sort_values(by='playerId', inplace=True)

    # get the mean per player over last_four_matches
    agg_func = {'ima_acc':'mean', 'ima_dec':'mean', 'ima_right':'mean', 'ima_left':'mean', 'runningDistance':'mean', \
                 'exerciseLoad':'mean',  \
                'touches':'mean', 'passes':'mean', 'shots':'mean', 'tackles':'mean'}
    # get aggregations
    player_mean_last_four_df = last_four_matches_df.groupby('playerId').agg(agg_func).reset_index()
    # select only necessary columns for the division for latest_match and drop player_id from last_four
    
    latest_match_df = latest_match_df[['playerId','ima_acc', 'ima_dec', 'ima_right', 'ima_left',\
                 'exerciseLoad', \
                'touches', 'passes', 'shots', 'tackles']]

    # get player Ids
    players = player_mean_last_four_df['playerId'].tolist()
    players.sort()

    # drop player id for the ratio calculation
    latest_match_df.drop(columns=['playerId'], inplace=True)
    player_mean_last_four_df.drop(columns=['playerId'], inplace=True)

    # get external, internal, ball groupings for both player mean and lates_match scaled df
    ratio_df = latest_match_df / player_mean_last_four_df

    # replace division by 0 with nan
    ratio_df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # get categories
    ratio_df['Player ID'] = players
    ratio_df['Player ID'] = ratio_df['Player ID'].astype(str)
    ratio_df['Internal'] = ratio_df['exerciseLoad']
    ratio_df['IMA'] = (ratio_df['ima_acc'] + ratio_df['ima_dec'] + ratio_df['ima_right'] + ratio_df['ima_left']) / 4
    ratio_df['Ball'] = (ratio_df['touches'] + ratio_df['passes'] + ratio_df['shots'] + ratio_df['tackles']) / 4
    ratio_df = ratio_df.round(2)
    ratio_df = ratio_df[['Player ID', 'Internal', 'IMA', 'Ball']]

    return ratio_df

### data for player performance development ####
### for an entire team it fetches both training and match data for a given time period
# def performance_development_team(current_time, match_ids, training_ids, engine=sql_engine):
#     last_week_time = 
#     four_week_time = 

# calculates the averages for external_internal and ball category
def calculate_external_internal_ball(dff):
    df = dff.copy()
    
    return df
# need to implement something to be able to filter by date
# def latest_month_matches_per_team(matchIds, engine=sql_engine):
#     latest_matches_team = "SELECT * FROM clean_match_teammates_statistics" \
#                     + " WHERE matchID in (" + matchIds + ")"
#     latest_df = pd.read_sql_query(latest_matches_team, engine)

#     return final_df

# filter all matches by player_id and a column
def all_match_data_per_player(playerId, column, engine=sql_engine):
    player_matches = "SELECT " + column + " FROM clean_match_teammates_statistics" \
                    + " WHERE playerID = " + playerId
    player_df = pd.read_sql_query(player_matches, engine)

    return player_df

def combine_ball_event_data(matchId, playerId, time_interval, engine=sql_engine):
    # get data from database instead 
    match_id = "'" + matchId + "'"
    ball_events = "SELECT * FROM clean_event WHERE matchId = " + match_id + " and playerId in (" + playerId + ")"

    # also get the type of match to get the right pitch size
    pitch = "SELECT matchType FROM clean_match WHERE matchId = " + match_id
    pitch_size = pd.read_sql_query(pitch, engine)
    pitch_size_str = pitch_size.iloc[0,0]


    full_df = pd.read_sql_query(ball_events, engine)

    # delete clearances
    full_df = full_df[full_df['Type'] != "clearance"]

    # split timestamp and time
    # turn timestamp to string
    full_df['timestamp'] = full_df['timestamp'].astype(str)

    full_df['timestamp'], full_df['time'] = full_df['timestamp'].str.split(' ',1).str
    
    # convert to datetime
    full_df['time'] = pd.to_datetime(full_df['time'], format="%H:%M:%S")

    # rescale the time to start at 0
    full_df['time'] = full_df['time'] - full_df['time'].min()

    # get hours, minutes and seconds from timedelta
    full_df['hour'] = full_df['time'].dt.components['hours']
    full_df['minute'] = full_df['time'].dt.components['minutes']
    full_df['second'] = full_df['time'].dt.components['seconds']
    
    # turn position to numeric and get max for field size
    full_df['posX'] = pd.to_numeric(full_df['posX'], errors='coerce')
    full_df['posY'] = pd.to_numeric(full_df['posY'], errors='coerce')
    max_x_position = full_df['posX'].max()
    max_y_position = full_df['posY'].max()

    # filter df by time interval 
    begin = time_interval[0]
    end = time_interval[1]
    full_df = full_df[full_df['minute'].between(begin, end)]
    
    return full_df, pitch_size_str

## query from clean_ima_event for data table in pitch selection
def combine_ima_events(matchId, players, time_interval, ima, intensity, engine=sql_engine):
    # get match id in right format
    match_id = "'" + matchId + "'"

    ima = "SELECT * FROM clean_ima_event WHERE matchId = " + match_id + \
         " and playerId in (" + players + ") and type in (" + ima + ") and intensity in (" + intensity + ")"

    full_df = pd.read_sql_query(ima, engine)

    # split timestamp and time
    # turn timestamp to string
    full_df['timestamp'] = full_df['timestamp'].astype(str)

    full_df['timestamp'], full_df['time'] = full_df['timestamp'].str.split(' ',1).str
    
    # convert to datetime
    full_df['time'] = pd.to_datetime(full_df['time'], format="%H:%M:%S")

    # rescale the time to start at 0
    full_df['time'] = full_df['time'] - full_df['time'].min()

    # get hours, minutes and seconds from timedelta
    full_df['hour'] = full_df['time'].dt.components['hours']
    full_df['minute'] = full_df['time'].dt.components['minutes']
    full_df['second'] = full_df['time'].dt.components['seconds']

    # concatenate the type and intensity column
    full_df["imaEvent"] = full_df["type"].astype(str) + full_df["intensity"].astype(str)

    # filter df by time interval 
    begin = time_interval[0]
    end = time_interval[1]
    full_df = full_df[full_df['minute'].between(begin, end)]

    # do value count
    ima_df = full_df.groupby('playerId')['imaEvent'].value_counts().reset_index(name='count')
    # make pivot table with imaEvent as column
    ima_df = ima_df.pivot(index='playerId', columns='imaEvent', values='count').reset_index()

    return ima_df

def combine_interval_events(matchId, players, time_interval, columns, engine=sql_engine):
    # add player_id and timestamp to query columns
    data_col = columns.copy()
    cols = columns.copy()
    cols.append('playerId')
    cols.append('timestamp')
    cols.append('matchId')

    set_of_cols_str = stringify_list_for_sql(cols)
    # set_of_cols = ["'" + m for m in cols]
    # set_of_cols = [m + "'" for m in set_of_cols]
    # set_of_cols_str = ','.join(set_of_cols)

    # get matchId in right format
    match_id = "'" + matchId + "'"

    interval = "SELECT * FROM clean_interval WHERE matchId = " + match_id + \
         " and playerId in (" + players + ")"

    full_df = pd.read_sql_query(interval, engine)

    # filter by columns
    full_df = full_df[cols]

    # turn timestamp to string
    full_df['timestamp'] = full_df['timestamp'].astype(str)

    full_df['timestamp'], full_df['time'] = full_df['timestamp'].str.split(' ',1).str
    
    # convert to datetime
    full_df['time'] = pd.to_datetime(full_df['time'], format="%H:%M:%S")

    # rescale the time to start at 0
    full_df['time'] = full_df['time'] - full_df['time'].min()

    # get hours, minutes and seconds from timedelta
    full_df['hour'] = full_df['time'].dt.components['hours']
    full_df['minute'] = full_df['time'].dt.components['minutes']
    full_df['second'] = full_df['time'].dt.components['seconds']

    # filter df by time interval 
    begin = time_interval[0]
    end = time_interval[1]
    full_df = full_df[full_df['minute'].between(begin, end)]

    # groupby player_id
    # define agg function for columns
    agg_function = {}
    for i in data_col:
        agg_function[i] = 'sum'
        
    final_df = full_df.groupby('playerId').agg(agg_function).reset_index()

    return final_df

##### match data for a list of players #####
def match_data_list_players(players, engine=sql_engine):
    # get players list in correct format
    players_str = stringify_list_for_sql(players)

    # sql query
    query = "SELECT * FROM clean_match_teammates_statistics" \
                    + " WHERE playerId in (" + players_str + ")"

    matches_players_df = pd.read_sql_query(query, engine)
    matches_players_df.drop(columns=['name', 'team'], inplace=True)
    matches_players_df['playerId'] = matches_players_df['playerId'].astype(str)

    # add the mean per game right now, later this will already be in the database
    mean_per_game_df = matches_players_df.groupby('matchId').mean().reset_index()
    mean_per_game_df['playerId'] = 'Team Average'

    # concatenate the two dfs
    final_df = pd.concat([matches_players_df, mean_per_game_df], axis=0, ignore_index=True, sort=True)
    return final_df


# for a selected match get the game score in string format that can be displayed
def get_match_score(match_id, engine=sql_engine):
    score = "SELECT matchId, main_score, guest_score, team1, team2 FROM clean_match" \
            +" WHERE matchId = '" + match_id + "'"
    score_df = pd.read_sql_query(score, engine)
    
    score_home = int(score_df.loc[0, 'main_score'])
    score_away = int(score_df.loc[0, 'guest_score'])

    team_home = score_df.loc[0, 'team1']
    team_away = score_df.loc[0, 'team2']

    final_str = team_home + " " + str(score_home) + ":" + str(score_away) + " " + team_away

    return final_str


def stringify_list_for_sql(lst):
    modified_lst = lst.copy()
    modified_lst = ["'" + m for m in modified_lst]
    modified_lst = [m + "'" for m in modified_lst]
    modified_lst_str = ','.join(modified_lst)
    return modified_lst_str

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2))
