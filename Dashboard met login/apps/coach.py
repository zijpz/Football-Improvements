import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from apps import commonmodules

from server import app
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from database import database as db

my_team_name = 'AFCU13-7'

# Possible matches for his team
possible_team_matches = db.teams_and_matches(my_team_name)

# possible players
possible_match_players = db.matches_and_players()

# game data for single selected match
match_df = db.select_match_data(possible_team_matches[0])

# possible metrics to select
available_metrics = db.match_metrics_data(match_df)

# available dates 
available_dates = db.time_range_matches(my_team_name)

# Snapshot Pie Charts
externalPie = go.Figure(data=[go.Pie(values=[100])])
internalPie = go.Figure(data=[go.Pie(values=[100])])
ballPie = go.Figure(data=[go.Pie(values=[100])])

layout = html.Div([
    commonmodules.get_header(),
    commonmodules.get_menu(),   
    html.Div(id="intermediate-table-coach", style={'display': 'none'}),
    dbc.Row(dbc.Col(html.H3("Coach"))),
    dcc.Tabs(id='coachMenu', children=[
        dcc.Tab(label='My Profile', children=[
        html.H3(" Flip de Bruijn", style={
                                        'textAlign': 'center',
                                    }),

                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3("Team Picture", style={
                                        'textAlign': 'center'
                                    }),
                                    html.Img(src='/assets/nederland.png', style={'textAlign': 'center', 'height': 250, 'width': 400,}),
                                ])
                            ]), width=5,  
                        ),
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3("Coach Info", style={
                                        'textAlign': 'center',
                                    }),
                                    html.H6("Position:"),
                                    html.H6("Age:"),
                                ])
                            ]), width=5,
                        ),
                    ],
                    justify="center",
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(id="performance-snapshot-coach",children=[
                                dbc.CardBody([
                                    html.H3("Performance Snapshot", style={
                                        'textAlign': 'center',
                                    }),
                                    dbc.Row([
                                        dbc.Col([
                                            html.H6("External", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='pie-external-coach',
                                                figure=externalPie
                                                ),
                                            dcc.Graph(
                                                id='radar-external-coach',
                                            )
                                        ]),
                                        dbc.Col([
                                            html.H6("Internal", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='pie-internal-coach',
                                                figure=internalPie
                                                ),
                                            dcc.Graph(
                                                id='radar-external-coach',
                                            )
                                        ]),
                                        dbc.Col([
                                            html.H6("Ball", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='pie-ball-coach',
                                                figure=ballPie
                                                ),
                                            dcc.Graph(
                                                id='radar-external-coach',
                                            )
                                        ])
                                    ])
                                    
                                ])
                            ]),width = 10,
                        ), justify="center",
                    ),
                    dbc.Row([
                        dbc.Card([
                            dbc.CardBody([
                                html.H3("Seasonal Development", style={
                                    'textAlign': 'center',
                                }),
                                dcc.Graph(id='season-development-coach'),
                            ])
                        ])
                    ],
                    justify="center",
                    ),
        ]),

        dcc.Tab(label='Analysis', children=[
            dbc.Row(
            [
            dbc.Col(dbc.Card(
                [
                    dbc.CardBody(
                        [
                            #html.H3("Sidebar"),
                            html.H6('Your Team'),
                            html.H6(my_team_name),

                            html.H6('Select Time Period Start'),
                            dcc.Dropdown(
                                id='select-start-time-coach',
                                options=[{'label': i, 'value': i} for i in available_dates],
                                value=available_dates[0]
                            ),

                            html.H6('Select Time Period End'),
                            dcc.Dropdown(
                                id='select-end-time-coach',
                                options=[{'label': i, 'value': i} for i in available_dates],
                                value=available_dates[-1]
                            ),

                            dcc.Tabs(children=[
                                dcc.Tab(label='Match', children=[
                                    html.H6('Select Match'),
                                    dcc.Dropdown(
                                        id='match-select-coach',
                                        options=[{'label': i, 'value': i} for i in possible_team_matches],
                                        value='61614647-8504-4983-8976-143056946FF0',
                                        clearable=False
                                    ),
                                    ]),

                                    dcc.Tab(label='Train', children=[
                                        html.H6('Select Training'),
                                        dcc.Dropdown(
                                            id='training-select-coach',
                                            clearable=False
                                        ),
                                    ])
                                ]),

                                html.H6('Select Team to Compare'),
                                dcc.Dropdown(
                                    id='team-select-2-coach',
                                    clearable=False
                                ),

                                html.H6('Select Position Type'),
                                dcc.Dropdown(
                                    id='position-type-select-coach',
                                ),

                                html.H6('Select Position'),
                                dcc.Dropdown(
                                    id='position-select-coach',
                                    clearable=False
                                ),
                        
                                html.H6('Select Player'),
                                dcc.Dropdown(
                                    id='player-select-1-coach',
                                    options=[{'label': i, 'value': i} for i in possible_match_players],
                                    multi=True
                                ),

                                html.H6('Select Player to Compare'),
                                dcc.Dropdown(
                                    id='player-select-2-coach',
                                ),
                        ]
                    )
                ]), width=3),
        
            dbc.Col(dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H3("Plots"),
                            dcc.Tabs(id='tabs', children=[
                                    dcc.Tab(label='Compare Teams', children=[
                                    dcc.Dropdown(
                                        id='team-metric-select-coach'
                                    ),
                                    dcc.Graph(id='player-metric'),
                            ]), # closes team-comparion tab
                                    dcc.Tab(label='Compare Player', children=[
                                        html.H6("Select one parameter"),
                                        dcc.Dropdown(
                                            id='player-metric-1-coach',
                                            options=[{'label': i, 'value':i} for i in available_metrics],
                                            value=available_metrics[0],
                                            clearable=False
                                        ),
                                        html.H6("Select another parameter"),
                                        dcc.Dropdown(
                                            id='player-metric-2-coach',
                                            options=[{'label': i, 'value':i} for i in available_metrics],
                                            value=available_metrics[1],
                                            clearable=False
                                        ),
                                        dcc.Graph(id='quadrant-plot-coach')
                                    ]), # closes player comparison tab
                                ]), # closes dcc.Tabs
                        ]
                    ),
                ]), width=7),

        ]),# closes row
        ]) # closes Analysis Tab

    ]) # closes big Tabs Menu

])

# show date output
@app.callback(
    Output('output-time-slider', 'children'),
    [Input('time-slider-coach', 'value')])
def update_output(value):
    return "You have selected '{}'".format(value)
# callback to update the match data in intermediate table
@app.callback(
    Output('intermediate-table-coach', 'table'),
    [Input('match-select-coach', 'value')])
def update_match_data(selectedMatch):
    new_data = db.select_match_data(selectedMatch)
    return new_data.to_json(date_format='iso', orient='split')
    
# Callback to update player selection
@app.callback(
    Output('player-select-1-coach', 'options'),
    [Input('match-select-coach', 'value')])
def set_player_options(selected_match):
    players = db.matches_and_players(selected_match)
    return [{'label': i, 'value': i} for i in players]



# Callback to update the player comparison plot
@app.callback(
    Output('quadrant-plot-coach', 'figure'),
    [Input('intermediate-table-coach', 'table'),
     Input('player-metric-1-coach', 'value'),
     Input('player-metric-2-coach', 'value')])
def update_quadrant_plot(data, y_axis_value, x_axis_value):
    complete_df = pd.read_json(data, orient='split')
    filtered_df = complete_df[['playerId', y_axis_value, x_axis_value]]
    mean_y = filtered_df[y_axis_value].mean()
    mean_x = filtered_df[x_axis_value].mean()
    
    # add random position to filtered_df to be able to show position hue
    position_list = ['Goalkeeper', 'Defender', 'Attacker', 'Midfielder']
    filtered_df['position'] = np.random.choice(position_list, size=len(filtered_df))

    traces=[] 

    for i in filtered_df.position.unique():
        df_by_position = filtered_df[filtered_df['position'] == i]
        traces.append(dict(
            x=df_by_position[x_axis_value],
            y=df_by_position[y_axis_value],
            text=df_by_position['playerId'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))
    
    # append mean line fore yaxis
    # traces.append(dict(
    #     x=[filtered_df[x_axis_value].min(), filtered_df[x_axis_value].min()]
    #     y= 
    # ))
    fig = go.Figure(data=traces, layout=dict(
              xaxis={
                'title': x_axis_value
                },
            yaxis={
                'title': y_axis_value
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition = {'duration': 500},
    ))
    fig.add_shape(
        dict(
            type= 'line',
            x0= filtered_df[x_axis_value].min(),
            y0= mean_y,
            x1= filtered_df[x_axis_value].max(),
            y1= mean_y,
            line= dict(
                color="RoyalBlue",
                width= 3
            ) 
        )
    )
    fig.add_shape(
        dict(
            type= 'line',
            x0= mean_x,
            y0= filtered_df[y_axis_value].min(),
            x1= mean_x,
            y1= filtered_df[y_axis_value].max(),
            line= dict(
                color="RoyalBlue",
                width= 3
            )
        )
    )
    fig.update_shapes(dict(xref='x', yref='y'))

    return fig