import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from apps import commonmodules
from database import database as db

from app import app
import numpy as np
import pandas as pd

external_stylesheets = [dbc.themes.BOOTSTRAP]

# player IDS
player_id = '72372'
player_number = 11

# check latest match table
latest_matches, matchDates = db.latest_matches_per_team("AFCU13-7")
external_df, internal_df, ball_df, performance_df = db.latest_matches_per_player(player_id, latest_matches)
combined_sums_df = pd.concat([external_df['SumE'], internal_df['SumI'], ball_df['SumB']], axis=1)
print(combined_sums_df)
externalPie_value = external_df.loc['difference', 'SumE']
internalPie_value = internal_df.loc['difference', 'SumI']
ballPie_value = ball_df.loc['difference', 'SumB']


# if externalPie_value >= 0:
#     externalPie_color = '#11BF25' # green
# else:
#     externalPie_color = '#FF2727' # red

# def create_pie_chart(match_df):
#     value = match_df.loc['difference', 'Sum']
#     if value >= 0:
#         color = '#11BF25' # green
#     else:
#         color = '#FF2727' # red

#     pie = go.Figure(data=[go.Pie(values=[value], hole=0.3)])
#     pie.update_layout(showlegend=False)
#     pie.update_traces(marker=dict(colors=[color]))

#     return pie

def check_color_pie(value):
    if value >= 0:
        color = '#11BF25' # green
        return color
    else:
        color = '#FF2727' # red
        return color

# available matches for player
player_matches = db.possible_games_player(player_id)

# match data per match
match_df = db.select_match_data(player_matches[0])
available_metrics = db.match_metrics_data(match_df)

# pie charts
externalPie = go.Figure(data=[go.Pie(values=[100], hole=0.3)])
externalPie.update_layout(showlegend=False) 
externalPie.update_traces(marker=dict(colors=[check_color_pie(externalPie_value)]))

internalPie = go.Figure(data=[go.Pie(values=[100], hole=0.3)])
internalPie.update_layout(showlegend=False) 
internalPie.update_traces(marker=dict(colors=[check_color_pie(internalPie_value)]))

ballPie = go.Figure(data=[go.Pie(values=[100], hole=0.3)])
ballPie.update_layout(showlegend=False) 
ballPie.update_traces(marker=dict(colors=[check_color_pie(ballPie_value)]))

# radar chart externalLoad
ext_cat = external_df.columns

external_fig = go.Figure()

external_fig.add_trace(go.Scatterpolar(
    r=external_df.loc['latest', external_df.columns!= 'Sum'],
    theta=ext_cat,
    fill='toself',
    name='Latest Game'
))

external_fig.add_trace(go.Scatterpolar(
    r=external_df.loc['mean', external_df.columns!= 'Sum'],
    theta=ext_cat,
    fill='toself',
    name='Average over last 5 games'
))

external_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[external_df.min(), external_df.max()]
        )),
        showlegend=False
)

# radarChart internalLoad
int_cat = internal_df.columns

internal_fig = go.Figure()

internal_fig.add_trace(go.Scatterpolar(
    r=internal_df.loc['latest', internal_df.columns!= 'Sum'],
    theta=int_cat,
    fill='toself',
    name='Latest Game'
))

internal_fig.add_trace(go.Scatterpolar(
    r=internal_df.loc['mean', internal_df.columns!= 'Sum'],
    theta=int_cat,
    fill='toself',
    name='Average over last 5 games'
))

internal_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[internal_df.min(), internal_df.max()]
        )),
        showlegend=False
)

# radar chart Ball Data
ball_cat = ball_df.columns

ball_fig = go.Figure()

ball_fig.add_trace(go.Scatterpolar(
    r=ball_df.loc['latest', ball_df.columns!= 'Sum'],
    theta=ball_cat,
    fill='toself',
    name='Latest Game'
))

ball_fig.add_trace(go.Scatterpolar(
    r=ball_df.loc['mean', ball_df.columns!= 'Sum'],
    theta=ball_cat,
    fill='toself',
    name='Average over last 5 games'
))

ball_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[ball_df.min(), ball_df.max()]
        )),
        showlegend=False
)

categories = ['intensity', 'Mid And High Acc', 'Mid And High Dec','Mid And High Turns',
            'Distance Covered', 'Effective Running Distance']
radarFig = go.Figure()
radarFig.add_trace(go.Scatterpolar(
      r=[1, 5, 2, 2, 3],
      theta=categories,
      fill='toself',
      name='Player A'
))
radarFig.add_trace(go.Scatterpolar(
      r=[4, 3, 2.5, 1, 2],
      theta=categories,
      fill='toself',
      name='Player B'
))

radarFig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 5]
    )),
  showlegend=False
)

# Performance Line Chart Snapshot
dates = np.linspace(1,12,12)
lineFig = make_subplots(rows=3, cols=1, shared_xaxes=True)
lineFig.append_trace(go.Scatter(x=dates, y=combined_sums_df['SumE'],
             mode='lines+markers', name='External'), row=1, col=1)
lineFig.append_trace(go.Scatter(x=dates, y=combined_sums_df['SumI'],
             mode='lines+markers', name='Internal'), row=2, col=1)
lineFig.append_trace(go.Scatter(x=dates, y=combined_sums_df['SumB'],
             mode='lines+markers', name='Ball'), row=3, col=1)



layout = html.Div([
    commonmodules.get_header(),
    commonmodules.get_menu(),

    html.Div(id='intermediate-table-player', style={'display': 'none'}),

    dbc.Row(dbc.Col(html.H3("Player"))),
    #html.H3('Player'), 
      
            dcc.Tabs(id='playerMenu', children=[
                dcc.Tab(label='My Profile', children=[
                    html.H3(str(player_number) + " Flip de Bruijn", style={
                                        'textAlign': 'center',
                                    }),

                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3("Profile Picture", style={
                                        'textAlign': 'center',
                                    }),
                                    html.Img(src='/assets/flip.png', style={'textAlign': 'center'}),
                                ])
                            ]), width=5,  
                        ),
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3("Player Info", style={
                                        'textAlign': 'center',
                                    }),
                                    html.H6("Position:"),
                                    html.H6("Height:"),
                                    html.H6("Weight:"),
                                    html.H6("Age:"),
                                ])
                            ]), width=5,
                        ),
                    ],
                    justify="center",
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(id="performance-snapshot-player",children=[
                                dbc.CardBody([
                                    html.H3("Performance Snapshot", style={
                                        'textAlign': 'center',
                                    }),
                                    dbc.Row([
                                        dbc.Col([
                                            html.H6("External", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='pie-external-player',
                                                figure=externalPie
                                                ),
                                            dcc.Graph(
                                                id='radar-external-player',
                                                figure=external_fig
                                                
                                            )
                                        ]),
                                        dbc.Col([
                                            html.H6("Internal", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='pie-internal-player',
                                                figure=internalPie
                                                ),
                                            dcc.Graph(
                                                id='radar-external-player',
                                                figure=internal_fig
                                            )
                                        ]),
                                        dbc.Col([
                                            html.H6("Ball", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='pie-ball-player',
                                                figure=ballPie
                                                ),
                                            dcc.Graph(
                                                id='radar-external-player',
                                                figure=ball_fig
                                                
                                            )
                                        ])
                                    ]),
                                ])
                            ]),width = 10,
                        ), justify="center",
                    ),
                    #dbc.Row(

                       
                        dbc.Card([
                            dbc.CardBody([
                                html.H3("Seasonal Development", style={
                                'textAlign': 'center',
                                }),
                                dcc.Graph(
                                    id='season-development-player',
                                    figure=lineFig
                                ),
                            ])
                        ]), #style={'width': 800},
                    #), 

                ]),
                dcc.Tab(label='Analysis', children=[
                    dcc.Tabs(id='Analysis', children=[
                    dcc.Tab(label='Development', children=[
                        dbc.Row(
                            [
                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H3("Sidebar"),
                                                html.H6("Time Range"),
                                                dcc.Slider(
                                                    id="time-range-personal-player",
                                                ),
                                                html.H6("Select a range of matches"),
                                                dcc.Dropdown(
                                                    id="select-match-personal-player",
                                                ),
                                                html.H6("Select a second range of matches"),
                                                dcc.Dropdown(
                                                    id="select-match-2-personal-player",
                                                ),
                                                html.H6("Select a range of training sessions"),
                                                dcc.Dropdown(
                                                    id="select-training-personal-player",
                                                ),
                                                html.H6("Select a second range of training sessions"),
                                                dcc.Dropdown(
                                                    id="select-training-2-personal-player",
                                                ),
                                                html.H6("Select External Parameter"),
                                                dcc.Dropdown(
                                                    id="external-personal-player",
                                                ),
                                                html.H6("Select Internal Parameter"),
                                                dcc.Dropdown(
                                                    id="internal-personal-player",
                                                ),
                                                html.H6("Select Ball Parameter"),
                                                dcc.Dropdown(
                                                    id="ball-personal-player",
                                                ),
                                            ]
                                        )
                                    ]
                                ), width=3,
                                ),

                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [   
                                                dash_table.DataTable(
                                                    id='performance-data-table',
                                                    columns = [
                                                        {"name": i, "id": i, "deletable": False, "selectable": True} for i in performance_df.columns
                                                    ],
                                                    data=performance_df.to_dict('records'),
                                                    style_cell={'textAlign': 'center', 'padding': '5px'},
                                                    style_as_list_view=True,
                                                    style_header={
                                                        'backgroundColor': 'white',
                                                        'font': 14,
                                                        'fontWeight': 'bold'
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                        "if": {
                                                            'column_id': 'Parameters',
                                                            'filter_query': "{Average Last 5 matches} <= {Latest Match}"
                                                        },
                                                        'backgroundColor': "#3D9970",
                                                        'color': 'white',
                                                        },
                                                        {
                                                        "if": {
                                                            'column_id': 'Parameters',
                                                            'filter_query': "{Average Last 5 matches} > {Latest Match}"
                                                        },
                                                        'backgroundColor': "#ff4f4f",
                                                        'color': 'white',
                                                        }
                                                    ]
                                                ),
                                                dcc.Tabs(children=[
                                                    dcc.Tab(label="Mirror-Analysis", children=[
                                                        dcc.Graph(
                                                            id="bar-chart-1",
                                                        ),
                                                    ]),
                                                    dcc.Tab(label="Causality-Analysis", children=[
                                                        dcc.Graph(
                                                            id='bar-chart-2',
                                                        ),
                                                    ]),
                                                    dcc.Tab(label="Trend-Analysis", children=[
                                                        dcc.Graph(
                                                            id='trend-chart',
                                                        )
                                                    ])
                                                ]),
                                            ]
                                        )
                                    ]
                                ), width=7,
                                )
                            ]
                        )
                    ]),
                    dcc.Tab(label='Compare to Team', children=[
                        dbc.Row(
                            [
                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H3("Sidebar"),
                                                html.H6("Time Range"),
                                                dcc.Slider(
                                                    id="time-range-team-player",
                                                ),
                                                html.H6("Select a range of matches"),
                                                dcc.Dropdown(
                                                    id="select-match-team-player",
                                                ),
                                                html.H6("Select another range of match"),
                                                dcc.Dropdown(
                                                    id="select-match-2-team-player",
                                                ),
                                                html.H6("Select a range of training sessions"),
                                                dcc.Dropdown(
                                                    id="select-training-team-player",
                                                ),
                                                html.H6("Select another range of training sessions"),
                                                dcc.Dropdown(
                                                    id="select-training-2-team-player",
                                                ),
                                                html.H6("Select External Parameter"),
                                                dcc.Dropdown(
                                                    id="external-team-player",
                                                ),
                                                html.H6("Select Internal Parameter"),
                                                dcc.Dropdown(
                                                    id="internal-team-player",
                                                ),
                                                html.H6("Select Ball Parameter"),
                                                dcc.Dropdown(
                                                    id="ball-team-player",
                                                ),
                                            ]
                                        )
                                    ]
                                    ), width=3,
                                ),

                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                dcc.Tabs(children=[
                                                    dcc.Tab(label="Mirror-Analysis", children=[
                                                        dcc.Graph(
                                                            id="bar-chart-1",
                                                        ),
                                                    ]),
                                                    dcc.Tab(label="Causality-Analysis", children=[
                                                        dcc.Graph(
                                                            id='bar-chart-2',
                                                        ),
                                                    ]),
                                                    dcc.Tab(label="Trend-Analysis", children=[
                                                        dcc.Graph(
                                                            id='trend-chart',
                                                        )
                                                    ])
                                                ]),
                                            ]
                                        )
                                    ]
                                ), width=7,
                                )
                            ]
                        )
            ]),
        ]),
    ]), # closes analysis tab 
]),
])


# callback to update the match data
@app.callback(
    Output('intermediate-table-player', 'children'),
    [Input('match-select-player', 'value')])
def update_match_data_player(matchId):
    new_data = db.select_match_data(matchId)
    return new_data.to_json(date_format='iso', orient='split') 

# callback to update the performance metric graph which compares player to team
@app.callback(
    Output('player-metric-player', 'figure'),
    [Input('intermediate-table-player', 'children'),
     Input('match-metric-player', 'value')])
def update_graph(data, metric_value):
    complete_df = pd.read_json(data, orient='split')
    complete_df['playerId'] = complete_df['playerId'].astype(str)
    player_data = complete_df[complete_df['playerId'] == player_id]
    team_average = complete_df[metric_value].mean()
    player_value = player_data.iloc[0][metric_value]
    y_values = [player_value, team_average]
    x_values = [player_id, 'Team Average']
    
    return {
        'data': [dict(
            x=x_values,
            y=y_values,
            type='bar' 
        )],
        'layout': dict(
            xaxis={
                'type':'category',
            },
            yaxis={
                'title': metric_value,
            },
            transition = {'duration': 500}
        )
    }


