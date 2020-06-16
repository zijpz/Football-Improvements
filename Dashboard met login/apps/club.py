import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from apps import commonmodules

import pandas as pd
import numpy as np

from server import app

from database import database as db


team = "AFCU13-7"

# select dataframe
print('initial db call')

# dataframe for possible matches per team
team_matches = db.teams_and_matches('AFCU13-7')

# Possible teams
possible_teams = db.team_selection_club()

# possible matches per team
possible_team_matches = db.teams_and_matches(team)

possible_matches_players = db.matches_and_players(possible_team_matches[0])

# game data for the selected match
match_df = db.select_match_data(possible_team_matches[0])
available_metrics = db.match_metrics_data(match_df)



layout = html.Div([
    commonmodules.get_header(),
    commonmodules.get_menu(), 
    html.H3('Club'),

    html.Div(id='intermediate-table-club-1', style={'display': 'none'}),
    html.Div([
        dbc.Row(
            [
            dbc.Col(dbc.Card(
                [
                    dbc.CardBody(
                        [
                        #html.H3("Sidebar"),

                        html.H6("Select Age Group"),
                        dcc.Dropdown(
                            id='age-group-select-club'
                        ),

                        html.H6("Select Time Period"),
                        dcc.RangeSlider(
                            id='time-slider-club',

                        ),

                        html.H6('Select Team'),
                        dcc.Dropdown(
                            id='team-select-1-club',
                            options=[{'label':i, 'value':i} for i in possible_teams],
                            value=team,
                            clearable=False
                        ),

                        html.H6('Select Team to Compare'),
                        dcc.Dropdown(
                            id='team-select-2-club',
                            options=[{'label':i, 'value':i} for i in possible_teams],
                            value=possible_teams[1],
                            clearable=False
                        ),

                        dcc.Tabs(children=[
                            dcc.Tab(label='Match', children=[
                                html.H6('Select Match'),
                                dcc.Dropdown(
                                    id='match-select-club',
                                    options=[{'label': i, 'value': i} for i in possible_team_matches],
                                    value=possible_team_matches[0],
                                    clearable=False
                                ),
                            ]),

                            dcc.Tab(label='Training', children=[
                                html.H6('Select Training'),
                                dcc.Dropdown(
                                    id='training-select-club',
                                    clearable=False
                                ),
                            ])
                        ]),

                            html.H6('Select Position'),
                            dcc.Dropdown(
                                id='position-select-club',
                                clearable=False
                            ),
                    
                            html.H6('Select Player'),
                            dcc.Dropdown(
                                id='player-select-1-club',
                                options=[{'label': i, 'value': i} for i in possible_matches_players],
                                multi=True
                            ),

                        ] 
                    ) # closes card body
                ]
                ), width=3), # closes sidebar column
            
            dbc.Col(dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3("Analytics"),
                                dcc.Tabs(id='tabs', children=[
                                    dcc.Tab(label='Compare Teams', children=[
                                    dcc.Dropdown(
                                        id='team-metric-select-club',
                                        style=dict(
                                            
                                            )
                                    ),
                                    dcc.Graph(id='player-metric-club'),
                            ]), # closes team-comparion tab
                                    dcc.Tab(label='Compare Player', children=[
                                        dcc.Dropdown(
                                            id='player-metric-select-club',
                                            options=[{'label': i, 'value': i} for i in available_metrics],
                                            value='maxVO2',
                                            style=dict(
                                                
                                                ),
                                            clearable=False
                                            ),
                                        dcc.Graph(id='player-metric-club')
                                    ]), # closes player comparison tab
                                ]), # closes dcc.Tabs
                            ]),
                    ]
    ), width=7 # closes card
    ) # closes column
    ]),# closes row    
    ]),
])# closes layout


# callback to update the match data in intermediate table
@app.callback(
    Output('intermediate-table-club-1', 'children'),
    [Input('match-select-club', 'value')])
def update_match_data_club(selectedMatch):
    new_data = db.select_match_data(selectedMatch)
    return new_data.to_json(date_format='iso', orient='split')

# callback to set the availabel games option
@app.callback(
    Output('match-select-club', 'options'),
    [Input('team-select-1-club', 'value')])
def set_matches_option(selected_team):
    #if selected_team != None:    
    matches = db.teams_and_matches(selected_team)
    return [{'label': i, 'value': i} for i in matches]

# callback to set the player selection options
@app.callback(
    Output('player-select-1-club', 'options'),
    [Input('match-select-club', 'value')])
def set_player_options(selected_match):
    #print('possible_matches_players[selected_match]')
    #print(possible_matches_players[selected_match])
    #return [{'label': i, 'value': i} for i in possible_matches[selected_match]]
    #if selected_match != None:    
    players = db.matches_and_players(selected_match)
    return [{'label': i, 'value': i} for i in players]

# callback to set player value
@app.callback(
    Output('player-select-1-club', 'value'),
    [Input('player-select-1-club', 'options')])
def set_players_value(available_players):
    return available_players[0]['value']

# callback for the graph
@app.callback(
    Output('player-metric-club', 'figure'),
    [Input('match-select-club', 'value'),
     Input('player-select-1-club', 'value'),
     Input('player-metric-select-club', 'value'),
     Input('intermediate-table-club-1', 'children')])
def update_graph(matchId, xaxis_column_name, yaxis_column_name, data):
    # turn single value into list because isin selection method needs list
    match_df = pd.read_json(data, orient='split')
    #match_df = data[data['matchId']==matchId]
    if isinstance(xaxis_column_name, str):
        xaxis_column_name = list([xaxis_column_name])
    df_metrics = match_df[['playerId', yaxis_column_name]]
    df_filtered = df_metrics[df_metrics['playerId'].isin(xaxis_column_name)]
    # append team average
    num_rows = len(df_filtered.index)
    mean = df_metrics[yaxis_column_name].mean()
    df_filtered.loc[num_rows+1] = ['Team Average'] + [mean]

    # color the bars depending on if below or above average
    conditions = [
        df_filtered[yaxis_column_name] < mean,
        df_filtered[yaxis_column_name] == mean,
        df_filtered[yaxis_column_name] > mean
    ]

    choices = ['red', 'blue', 'green']

    df_filtered['color'] = np.select(conditions, choices)
    
    return {
        'data': [dict(
            x=df_filtered['playerId'],
            y=df_filtered[yaxis_column_name],
            marker={'color': df_filtered['color']},
            type='bar'
        )],
        'layout': dict(
            xaxis={
                'title': xaxis_column_name,
                'type': 'category'
            },
            yaxis={
                'title': yaxis_column_name
            },
            transition = {'duration': 500}
        )
    }