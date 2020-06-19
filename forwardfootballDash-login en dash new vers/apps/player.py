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
player_id = "72264"
player_number = 11
team = "AFCU9-1"

# check latest match table
latest_matches, matchDates = db.latest_matches_per_team(team)
external_df, internal_df, ball_df, performance_df, stamina_AC, fit_score_df, gauge_val_dict, trend_df = db.latest_matches_per_player(player_id, latest_matches)
combined_sums_df = pd.concat([external_df['SumE'], internal_df['SumI'], ball_df['SumB']], axis=1)

internal_performance = performance_df[performance_df['Parameters'].isin(['exerciseLoad', 'calories', 'maxVO2'])]
external_performance = performance_df[performance_df['Parameters'].isin(['imaAccMid', 'imaAccHigh', 'imaDecMid', 'imaDecHigh',\
                                        'imaRighMid', 'imaRighHigh', 'imaLeftMid', 'imaLeftHigh', 'runningDistance',\
                                        'maxRunningSpeed', 'maxDribbleSpeed'])]
ball_performance = performance_df[performance_df['Parameters'].isin(['touches', 'passes', 'shots', 'tackles'])]


# available matches for player
player_matches = db.possible_games_player(player_id)

# match data per match
match_df = db.select_match_data(player_matches[0])
available_metrics = db.match_metrics_data(match_df)

# radar chart externalLoad
ext_cat = external_df.columns

external_radar = go.Figure()

external_radar.add_trace(go.Scatterpolar(
    r=external_df.loc['latest', external_df.columns != 'SumE'],
    theta=ext_cat,
    fill='toself',
    name='Latest Game',
    line_color = 'orange'
))

external_radar.add_trace(go.Scatterpolar(
    r=external_df.loc['meanLast5', external_df.columns!= 'SumE'],
    theta=ext_cat,
    fill='toself',
    name='Average over last 5 games',
    line_color = 'blue'
))

external_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[external_df.min(), external_df.max()]
        )),
    showlegend=False,
    template='seaborn',
    margin=dict(t=10, b=10)
)

# radarChart internalLoad
int_cat = internal_df.columns

internal_radar = go.Figure()

internal_radar.add_trace(go.Scatterpolar(
    r=internal_df.loc['latest', internal_df.columns!= 'SumI'],
    theta=int_cat,
    fill='toself',
    name='Latest Game',
    line_color = 'orange'
))

internal_radar.add_trace(go.Scatterpolar(
    r=internal_df.loc['meanLast5', internal_df.columns != 'SumI'],
    theta=int_cat,
    fill='toself',
    name='Average over last 5 games',
    line_color = 'blue'
))

internal_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[internal_df.min(), internal_df.max()]
        )),
    showlegend=False,
    template='seaborn',
    margin=dict(t=10, b=10)
)

# radar chart Ball Data
ball_cat = ball_df.columns

ball_radar = go.Figure()

ball_radar.add_trace(go.Scatterpolar(
    r=ball_df.loc['latest', ball_df.columns!= 'SumB'],
    theta=ball_cat,
    fill='toself',
    name='Latest Game',
    line_color = 'orange'
))

ball_radar.add_trace(go.Scatterpolar(
    r=ball_df.loc['meanLast5', ball_df.columns!= 'SumB'],
    theta=ball_cat,
    fill='toself',
    name='Average over last 5 games',
    line_color = 'blue'
))

ball_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[ball_df.min(), ball_df.max()]
        )),
    showlegend=False,
    template='seaborn',
    margin=dict(t=10, b=10)
)


categories = ['imaLeftMid', 'imaLeftHigh', 'imaRightMid', 'imaRightHigh',\
              'imaAccMid', 'imaAccHigh', 'imaDecMid', 'imaDecHigh', 'distanceCovered']
    

external_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=gauge_val_dict['external'],
        domain={'x': [0,1], 'y':[0,1]},
        gauge={
            'axis': {'range': [None, 2], 'tickvals': [0, 0.95, 1.05, 2]},
            'bar': {'color': "black"},
            'borderwidth': 1,
            'bordercolor': 'gray',
            
            'steps': [
                {'range': [0, 0.95], 'color': 'red'},
                {'range': [0.95, 1.05], 'color': 'orange'},
                {'range': [1.05, 2], 'color': 'green'},
            ],
        }
    ),
    go.Layout(
        height=400,
        margin=dict(t=50, b=50),
        template='seaborn'
    ),
)


internal_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=gauge_val_dict['internal'],
        domain={'x': [0,1], 'y':[0,1]},
        gauge={
            'axis': {'range': [None, 2], 'tickvals': [0, 0.8, 1.0, 1.3 ,2]},
            'bar': {'color': "black"},
            'borderwidth': 1,
            'bordercolor': 'gray',
            
            'steps': [
                {'range': [0, 0.8], 'color': 'blue'},
                {'range': [0.8, 1.0], 'color': 'orange'},
                {'range': [1.0, 1.3], 'color': 'green'},
                {'range': [1.3, 2], 'color': 'red'},
            ],
        }
    ),
    go.Layout(
        height=400,
        margin=dict(t=50, b=50),
        template='seaborn'
    ),
)

ball_avg = stamina_AC.loc['meanLast5', 'touches']
ball_last = stamina_AC.loc['Latest', 'touches']

ball_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=gauge_val_dict['ball'],
        domain={'x': [0,1], 'y':[0,1]},
        gauge={
            'axis': {'range': [None, 2], 'tickvals': [0, 0.95, 1.05, 2]},
            'bar': {'color': "black"},
            'borderwidth': 1,
            'bordercolor': 'gray',
            
            'steps': [
                {'range': [0, 0.95], 'color': 'red'},
                {'range': [0.95, 1.05], 'color': 'orange'},
                {'range': [1.05, 2], 'color': 'green'},
            ],
        }
    ),
    go.Layout(
        height=400,
        margin=dict(t=50, b=50),
        template='seaborn' 
    ),
)

# internal bar charts ##
internal_bar_df = internal_performance[internal_performance['Parameters'].isin(['maxVO2', 'exerciseLoad', 'calories'])]
internal_x = internal_bar_df['Parameters'].to_list()
internal_y_player = internal_bar_df['Latest Match'].to_list()
internal_y_max = internal_bar_df['Max Performance'].to_list()

internal_bar = go.Figure()
internal_bar.add_trace(
    go.Bar(name='Maximum', x=internal_x, y=internal_y_max),
)

internal_bar.add_trace(
    go.Bar(name='You', x=internal_x, y=internal_y_player, width=0.6),
)

internal_bar.update_layout(template='seaborn', barmode='overlay', hovermode='x')

## contribution bar charts ##

# speed 
speed_bar_df = external_performance[external_performance['Parameters'].isin(['runningDistance'])]
speed_x = speed_bar_df['Parameters'].to_list()
speed_y_player = speed_bar_df['Latest Match'].to_list()
speed_y_max = speed_bar_df['Max Performance'].to_list()
speed_contribution_bar = go.Figure()

speed_contribution_bar.add_trace(
    go.Bar(name='Maximum', x=speed_x, y=speed_y_max)
)

speed_contribution_bar.add_trace(
    go.Bar(name='You', x=speed_x, y=speed_y_player)
)

speed_contribution_bar.update_layout(template='seaborn', barmode='overlay', hovermode='x')

# IMA Turns
turns_bar_df = external_performance[external_performance['Parameters'].isin(['imaLeftMid', 'imaLeftHigh', 'imaRighMid', 'imaRighHigh'])]
turns_x = turns_bar_df['Parameters'].to_list()
turns_y_player = turns_bar_df['Latest Match'].to_list()
turns_y_max = turns_bar_df['Max Performance'].to_list()
turns_contribution_bar = go.Figure()

turns_contribution_bar.add_trace(
    go.Bar(name='Maximum', x=turns_x, y=turns_y_max),
)

turns_contribution_bar.add_trace(
    go.Bar(name='You', x=turns_x, y=turns_y_player, width=0.6),
)

turns_contribution_bar.update_layout(template='seaborn', barmode='overlay', hovermode='x')
turns_contribution_bar.update_xaxes(tickangle=45)

## acceleration contribution ##
acc_bar_df = external_performance[external_performance['Parameters'].isin(['imaAccMid', 'imaAccHigh', 'imaDecMid', 'imaDecHigh'])]
acc_x = acc_bar_df['Parameters'].to_list()
acc_y_player = acc_bar_df['Latest Match'].to_list()
acc_y_max = acc_bar_df['Max Performance'].to_list()
acc_contribution_bar = go.Figure()

acc_contribution_bar.add_trace(
    go.Bar(name='Maximum', x=acc_x, y=acc_y_max),
)

acc_contribution_bar.add_trace(
    go.Bar(name='You', x=acc_x, y=acc_y_player, width=0.6),
)

acc_contribution_bar.update_layout(template='seaborn', barmode='overlay', hovermode='x')
acc_contribution_bar.update_xaxes(tickangle=45)

ball_bar_df = ball_performance[ball_performance['Parameters'].isin(['shots', 'touches', 'passes', 'tackles'])]
ball_x = ball_bar_df['Parameters'].to_list()
ball_y_player = ball_bar_df['Latest Match'].to_list()
ball_y_max = ball_bar_df['Max Performance'].to_list()

ball_bar = go.Figure()
ball_bar.add_trace(
    go.Bar(name='Maximum', x=ball_x, y=ball_y_max),
)
ball_bar.add_trace(
    go.Bar(name='You', x=ball_x, y=ball_y_player, width=0.6),
)

ball_bar.update_layout(template='seaborn', barmode='overlay', hovermode='x')

# Performance Line Chart Snapshot
dates = np.linspace(1,12,12)
performance_trend_chart = make_subplots(rows=3, cols=1, shared_xaxes=True)

performance_trend_chart.add_trace(go.Scatter(x=trend_df['matchId'], y=trend_df['exerciseLoad'],
             mode='lines+markers', name='Internal'), row=1, col=1)

performance_trend_chart.add_trace(go.Scatter(x=trend_df['matchId'], y=trend_df['imaSum'],
             mode='lines+markers', name='External'), row=2, col=1)

performance_trend_chart.add_trace(go.Scatter(x=trend_df['matchId'], y=trend_df['ballSum'],
             mode='lines+markers', name='Ball'), row=3, col=1)

performance_trend_chart.update_layout(
    template='seaborn',
    height=750,
    hovermode='x'
)

### EXCLUDE MAX FROM PERFORMANCE TABLES ###
internal_performance_current = internal_performance[['Latest Match', 'Parameters', 'FIT Score']]
external_performance_current = external_performance[['Latest Match', 'Parameters', 'FIT Score']]
ball_performance_current = ball_performance[['Latest Match', 'Parameters', 'FIT Score']]

internal_performance_development = internal_performance[['Last Week', 'Parameters', 'Average 4 Weeks', 'Percent Change', 'percentChange']]
external_performance_development = external_performance[['Last Week', 'Parameters', 'Average 4 Weeks', 'Percent Change', 'percentChange']]
ball_performance_development = ball_performance[['Last Week', 'Parameters', 'Average 4 Weeks', 'Percent Change', 'percentChange']]
development_columns = ['Last Week', 'Parameters', 'Average 4 Weeks', 'Percent Change']

### Performance Development STUFF ###
all_matches = db.all_match_data_per_team(team, player_id)
all_matches_list = all_matches['matchId'].to_list()
internal_parameters = ['exerciseLoad', 'maxVO2']
external_parameters = ['imaAccMid', 'imaAccHigh', 'imaDecMid', 'imaDecHigh',\
                                        'imaRighMid', 'imaRighHigh', 'imaLeftMid', 'imaLeftHigh']
ball_parameters = ['touches', 'passes', 'shots', 'tackles']


#### DIVERGING BAR CHART ###
positive_fit = fit_score_df[fit_score_df['FIT Score'] >= 0]
negative_fit = fit_score_df[fit_score_df['FIT Score'] < 0]

diverging_bar_fig = go.Figure()
diverging_bar_fig.add_trace(
    go.Bar(
        x=positive_fit['FIT Score'],
        y=positive_fit['Parameters'],
        orientation='h',
        marker_color='green',
        customdata=np.stack((positive_fit['Latest Match'], positive_fit['Max Performance'], positive_fit['FIT Score']), axis=-1),
        hovertemplate="<br>Latest Match:%{customdata[0]}<br>Max:%{customdata[1]}<br>FIT Score:%{customdata[2]}",
    ),
)
diverging_bar_fig.add_trace(
    go.Bar(
        x=negative_fit['FIT Score'],
        y=negative_fit['Parameters'],
        orientation='h',
        marker_color='red',
        customdata=np.stack((negative_fit['Latest Match'], negative_fit['Max Performance'], negative_fit['FIT Score']), axis=-1),
        hovertemplate="<br>Latest Match:%{customdata[0]}<br>Max:%{customdata[1]}<br>FIT Score:%{customdata[2]}",
    )
)

diverging_bar_fig.update_layout(
    template='plotly_white',
    height=1000,
    barmode='relative', 
    yaxis_autorange='reversed',
    bargap=0.01,
    legend_orientation ='h',
    legend_x=-0.05, legend_y=1.1
)
diverging_bar_fig.update_xaxes(range=[-100, 100])


def scaling_function(arr, minAllowed, maxAllowed):
    # get array min and max
    arrMin = min(arr)
    arrMax = max(arr)
    print(arrMin)
    print(arrMax)
    transformation = lambda x: ((maxAllowed - minAllowed) * (x - arrMin)) / (arrMax-arrMin) + minAllowed

    scaled_list = list(map(transformation, arr))

    return scaled_list


def data_bars_diverging_pos_neg(df, column, side, color_above='#3D9970', color_below='#FF4136'):
    numeric_values = df[column].to_list()

    styles = []
    for i in numeric_values:
        style = {
           'if': {
                'filter_query': (
                    '{{{column}}} = {value}'
                ).format(column=column, value=i),
                'column_id': column
            },
            'paddingBottom': 2,
            'paddingTop': 2
        }

        if side=='left':
            background = (
                """
                    linear-gradient(90deg,
                    white 0%, 
                    white {scalar}%,
                    {color_below} {scalar}%,
                    {color_below} 100%)
                """.format(
                    color_below=color_below, scalar= i
                )
            )
        elif side=='right' and i > 200:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%, 
                    {color_above} 100%,
                    )
                """.format(
                    color_above=color_above
                )
            )
        else:
            background = (
                """
                    linear-gradient(90deg,
                    {color_above} 0%,
                    {color_above} {scalar}%,
                    white {scalar}%,
                    white 100%)
                """.format(
                    color_above=color_above, scalar= i-100
                )
            )

        style['background'] = background
        styles.append(style)

    return styles
    
    


# FUNCTION FOR DIVERGING DATA BARS
def data_bars_diverging(df, column, color_above='#3D9970', color_below='#FF4136'):
    n_bins = 2
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    col_max = df[column].max()
    col_min = df[column].min()
    ranges = [
        ((col_max - col_min) * i) + col_min
        for i in bounds
    ]
    #midpoint = (col_max + col_min) / 2.
    midpoint = 0

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        min_bound_percentage = bounds[i - 1] * 100
        max_bound_percentage = bounds[i] * 100

        style = {
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'paddingBottom': 2,
            'paddingTop': 2
        }
        if max_bound > midpoint:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white 50%,
                    {color_above} 50%,
                    {color_above} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                    max_bound_percentage=max_bound_percentage,
                    color_above=color_above
                )
            )
        else:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white {min_bound_percentage}%,
                    {color_below} {min_bound_percentage}%,
                    {color_below} 50%,
                    white 50%,
                    white 100%)
                """.format(
                    min_bound_percentage=min_bound_percentage,
                    color_below=color_below
                )
            )
        style['background'] = background
        styles.append(style)

        #print(styles)

    return styles

fit_score_df.drop(columns=['FIT Score'], inplace=True)

layout = html.Div([
    commonmodules.get_menu(),

    html.Div(id='intermediate-table-player', style={'display': 'none'}),

    dbc.Row(dbc.Col(html.H3("Player"))),
    #html.H3('Player'), 
      
            dcc.Tabs(id='playerMenu', children=[
                dcc.Tab(label='My Profile', children=[
                    html.H3(str(player_number) + " Flip de Bruijn", style={
                                        'textAlign': 'center',
                                    }),
                    html.Div([
                        html.Div([
                            html.H3("Profile Picture", style={
                                        'textAlign': 'center',
                                    }),
                            html.Img(src='/assets/flip.png', style={'textAlign': 'center'}),
                        ], style={'display': 'inline-block', 'width':'49%', 'border-style': 'solid', 'border-color':'#7A7D7B', 'border-radius': '8px', 'border-width': '1px', 'vertical-align': 'top'},),

                        html.Div([
                            html.H3("Player Info", style={
                                        'textAlign': 'center',
                                    }),
                            html.H6("Position: Forward"),
                            html.H6("Height: 190cm"),
                            html.H6("Age:20"),
                        ], style={'display':'inline-block', 'width': '49%', 'border-style': 'solid', 'border-color': '#7A7D7B', 'border-radius': '8px', 'border-width': '1px', 'vertical-align': 'top'})
                    ]),
        
                            html.Div([
                                    html.H3("Match Performance Development", style={
                                        'textAlign': 'center',
                                    }),
                                    html.Div([
                                        html.Div([
                                            html.H6("Internal", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='gauge-internal-player',
                                                figure=internal_gauge
                                                ),
                                                dcc.Graph(
                                                    id='radar-internal-player',
                                                    figure=internal_radar
                                                )
                                            
                                        ], style={'width': '33%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H6("External", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='gauge-external-player',
                                                figure=external_gauge
                                                ),
                                            dcc.Graph(
                                                id='radar-external-player',
                                                figure=external_radar
                                                
                                            ),
                                        ], style={'width': '33%', 'display': 'inline-block'}),
        
                                        html.Div([
                                            html.H6("Ball", style={'textAlign': 'center'}),
                                            dcc.Graph(
                                                id='gauge-ball-player',
                                                figure=ball_gauge
                                            ),
                                            dcc.Graph(
                                                id='radar-ball-player',
                                                figure=ball_radar 
                                            )
                                        ], style={'width': '33%', 'display': 'inline-block'})
                                    ]),

                                ], style={'margin-bottom': '50px'}),
                    html.Div([
                                html.H3("Seasonal Development", style={
                                'textAlign': 'center',
                                }),
                                dcc.Graph(
                                    id='season-development-player',
                                    figure=performance_trend_chart
                                ),
                    ], style={'margin-top': '50px'}),

                ]),
                dcc.Tab(label='Analysis', children=[
                    dcc.Tabs(id='Analysis', children=[
                    dcc.Tab(label='Current Performance', children=[
                        html.Div([   
                        dbc.Card([
                                dbc.CardBody([

                        html.H5('Current Performance Table', style={
                                        'textAlign': 'center',
                                    }),
                        html.Div([
                            dbc.Button("Total Match Data", id='internal-raw-current', outline=True, color="dark", size="sm", \
                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                           'margin': '2px 2px'}),
                            dbc.Button("Per Minute Data", id='internal-minute_current', outline=True, color="dark", size="sm", \
                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                           'margin': '2px 2px'}),
                                ], style={'textAlign': 'center'}),
                            html.Div([
                            dash_table.DataTable(
                                            id='internal-data-table-current',
                                                    columns = [
                                                        {"name": i, "id": i, "deletable": False, "selectable": True} for i in fit_score_df.columns
                                                    ],
                                                    data=fit_score_df.to_dict('records'),
                                                    sort_action="native",
                                                    style_cell={'textAlign': 'center', 'padding': '5px'},
                                                    style_as_list_view=False,
                                                    style_header={
                                                        'backgroundColor': 'white',
                                                        'font': 14,
                                                        'fontWeight': 'bold'
                                                    },
                                                    style_data_conditional= (
                                                        data_bars_diverging_pos_neg(fit_score_df, 'belowFIT', 'left') +
                                                        data_bars_diverging_pos_neg(fit_score_df, 'aboveFIT', 'right') +
                                                        [
                                                        {'if': {'column_id': 'Latest Match'},
                                                        'width': '19%'},
                                                        {'if': {'column_id': 'Parameters'},
                                                        'width': '10%'},
                                                        {'if': {'column_id': 'belowFIT'},
                                                        'width': '19%'},
                                                        {'if': {'column_id': 'aboveFit'},
                                                        'width': '19%'},
                                                        {'if': {'column_id': 'Max'},
                                                        'width': '19%'},
                                                        ]
                                                    )
                                        ),
                                ], style={"width": "90%", 'textAling':'center'}),
                                # dcc.Graph(
                                #             id='diverging-bars-fit',
                                #             figure=diverging_bar_fig
                                # ),
                                  ]),
                                ]),
                                dcc.Graph(
                                    id = 'internal-bar',
                                    figure = internal_bar
                                )
                            ],style={'width':'100%', 'textAlign': 'center'}),
                            html.Div([
                            dbc.Card([
                                dbc.CardBody([

                            html.H5('External', style={
                                        'textAlign': 'center',
                                    }),
                            html.Div([
                                dbc.Button("Total Match Data", id='external-raw-current', outline=True, color="dark", size="sm", \
                                    style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                           'margin': '2px 2px'}),
                                dbc.Button("Per Minute Data", id='external-minute-current', outline=True, color="dark", size="sm", \
                                    style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                           'margin': '2px 2px'}),
                            ], style={'textAlign': 'center'}),
                            dash_table.DataTable(
                                                    id='external-data-table-current',
                                                    columns = [
                                                        {"name": i, "id": i, "deletable": False, "selectable": True} for i in external_performance_current.columns
                                                    ],
                                                    data=external_performance_current.to_dict('records'),
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
                                                            'filter_query': "{FIT Score} < 100"
                                                        },
                                                        'backgroundColor': "#ed4734",
                                                        'color': 'white',
                                                        },
                                                        {
                                                        "if": {
                                                            'column_id': 'Parameters',
                                                            'filter_query': "{FIT Score} >= 100"
                                                        },
                                                        'backgroundColor': "#1ABE0C",
                                                        'color': 'white',
                                                        },
                                                        {'if': {'column_id': 'Latest Match'},
                                                        'width': '33%'},
                                                        {'if': {'column_id': 'Parameters'},
                                                        'width': '33%'},
                                                        {'if': {'column_id': 'FIT Score'},
                                                        'width': '33%'},
                                                    ]
                                                ),
                                    ]),
                                ]),
                                dbc.Row([
                                dbc.Col([
 
                                    html.H6('Speed in Match', style={'textAlign': 'center'}),
                                    dcc.Graph(
                                        id='team-contribution-speed',
                                        figure=speed_contribution_bar
                                    ),
                                ]),
                                dbc.Col([
    
                                    html.H6('Turns in Match', style={'textAlign': 'center'}),
                                    dcc.Graph(
                                        id='team-contribution-turns',
                                        figure=turns_contribution_bar
                                    ),
                                ]),
                                dbc.Col([
                             
                                    html.H6('Accelerations in Match', style={'textAlign': 'center'}),
                                    dcc.Graph(
                                        id='team-contribution-acc',
                                        figure=acc_contribution_bar
                                    ),
                                ]),
                            ])
                            ], style={'width': '100%', 'textAlign': 'center'}),
                            dbc.Card([
                            html.Div([
                                dbc.CardBody([
                            html.H5('Ball', style={
                                        'textAlign': 'center',
                                    }),
                            html.Div([
                                dbc.Button("Total Match Data", id='ball-raw-current', outline=True, color="dark", size="sm", \
                                    style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                           'margin': '2px 2px'}),
                                dbc.Button("Per Minute Data", id='ball-minute-current', outline=True, color="dark", size="sm", \
                                    style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                           'margin': '2px 2px'}),
                            ], style={'textAlign': 'center'}),
                            dash_table.DataTable(
                                                    id='ball-data-table-current',
                                                    columns = [
                                                        {"name": i, "id": i, "deletable": False, "selectable": True} for i in ball_performance_current.columns
                                                    ],
                                                    data=ball_performance_current.to_dict('records'),
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
                                                            'filter_query': "{FIT Score} < 100"
                                                        },
                                                        'backgroundColor': "#ed4734",
                                                        'color': 'white',
                                                        },
                                                        {
                                                        "if": {
                                                            'column_id': 'Parameters',
                                                            'filter_query': "{FIT Score} >= 100"
                                                        },
                                                        'backgroundColor': "#1ABE0C",
                                                        'color': 'white',
                                                        },
                                                        {'if': {'column_id': 'Latest Match'},
                                                        'width': '33%'},
                                                        {'if': {'column_id': 'Parameters'},
                                                        'width': '33%'},
                                                        {'if': {'column_id': 'FIT Score'},
                                                        'width': '33%'},
                                                    ]
                                                ), 
                                    ]),
                                ])
                            ], style={'width': '100%', 'textAlign': 'center'}),
                            dcc.Graph(
                                id='ball-bar',
                                figure=ball_bar,
                            ),   
                    ]),
                    dcc.Tab(label='Performance Development', children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(id='sidebar-development', children=[
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H3("Sidebar"),
                                                html.H6("Time Range"),
                                                dcc.RangeSlider(
                                                    id="time-range-player",
                                                    min=1,
                                                    max=10,
                                                    step=1,
                                                    value=[1, 10]
                                                ),
                                                html.Div(id='slider-output-player'),
                                                html.H6("Select Internal Parameter"),
                                                dcc.Dropdown(
                                                    id="internal-personal-player",
                                                    options=[{'label': i, 'value': i} for i in internal_parameters],
                                                    value='exerciseLoad',
                                                    multi=True,
                                                ),
                                                html.H6("Select External Parameter"),
                                                dcc.Dropdown(
                                                    id="external-personal-player",
                                                    options=[{'label': i, 'value': i} for i in external_parameters],
                                                    value='imaAccHigh',
                                                    multi=True
                                                ),
                                                html.H6("Select Ball Parameter"),
                                                dcc.Dropdown(
                                                    id="ball-personal-player",
                                                    options=[{'label': i, 'value': i} for i in ball_parameters],
                                                    value='passes',
                                                    multi=True
                                                ),
                                            ]
                                        )
                                    )
                                    ], style={'display': 'block'}),
                                width=3,
                                ),

                                dbc.Col(dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [   
                                                dcc.Tabs(id='development-tabs', value='overview-tab-development', children=[
                                                    dcc.Tab(value='overview-tab-development', label='Player Development', children=[
                                                        html.H5('Internal', style={'textAlign': 'center'}),
                                                        html.Div([
                                                            dbc.Button("Total Match Data", id='internal-raw-development', outline=True, color="dark", size="sm", \
                                                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                                                    'margin': '2px 2px'}),
                                                            dbc.Button("Per Minute Data", id='internal-minute-development', outline=True, color="dark", size="sm", \
                                                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                                                    'margin': '2px 2px'}),
                                                        ], style={'textAlign': 'center'}),
                                                        dash_table.DataTable(
                                                            id='internal-data-table-performance',
                                                            columns = [
                                                                {"name": i, "id": i, "deletable": False, "selectable": True} for i in development_columns
                                                            ],
                                                            data=internal_performance_development.to_dict('records'),
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
                                                                    'filter_query': "{percentChange} <= 0"
                                                                },
                                                                'backgroundColor': "#ed4734",
                                                                'color': 'white',
                                                                },
                                                                {
                                                                "if": {
                                                                    'column_id': 'Parameters',
                                                                    'filter_query': "{percentChange} > 0"
                                                                },
                                                                'backgroundColor': "#1ABE0C",
                                                                'color': 'white',
                                                                },
                                                                {'if': {'column_id': 'Last Week'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Parameters'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Average 4 Weeks'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Percent Change'},
                                                                'width': '24%'},
                                                            ]
                                                        ),
                                                        html.H5('External', style={'textAlign': 'center'}),
                                                        html.Div([
                                                            dbc.Button("Total Match Data", id='external-raw-development', outline=True, color="dark", size="sm", \
                                                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                                                    'margin': '2px 2px'}),
                                                            dbc.Button("Per Minute Data", id='external-minute-development', outline=True, color="dark", size="sm", \
                                                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                                                    'margin': '2px 2px'}),
                                                        ], style={'textAlign': 'center'}),
                                                        dash_table.DataTable(
                                                            id='external-data-table-performance',
                                                            columns = [
                                                                {"name": i, "id": i, "deletable": False, "selectable": True} for i in development_columns
                                                            ],
                                                            data=external_performance_development.to_dict('records'),
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
                                                                    'filter_query': "{percentChange} <= 0"
                                                                },
                                                                'backgroundColor': "#ed4734",
                                                                'color': 'white',
                                                                },
                                                                {
                                                                "if": {
                                                                    'column_id': 'Parameters',
                                                                    'filter_query': "{percentChange} > 0"
                                                                },
                                                                'backgroundColor': "#1ABE0C",
                                                                'color': 'white',
                                                                },
                                                                {'if': {'column_id': 'Last Week'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Parameters'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Average 4 Weeks'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Percent Change'},
                                                                'width': '24%'},
                                                            ]
                                                        ),
                                                        html.H5('Ball', style={'textAlign': 'center'}),
                                                        html.Div([
                                                            dbc.Button("Total Match Data", id='ball-raw-development', outline=True, color="dark", size="sm", \
                                                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                                                    'margin': '2px 2px'}),
                                                            dbc.Button("Per Minute Data", id='ball-minute-development', outline=True, color="dark", size="sm", \
                                                                style={'width': '150px', 'padding': '5px 5px', 'text-align': 'center', 'display': 'inline-block', \
                                                                    'margin': '2px 2px'}),
                                                        ], style={'textAlign': 'center'}),
                                                        dash_table.DataTable(
                                                            id='ball-data-table-performance',
                                                            columns = [
                                                                {"name": i, "id": i, "deletable": False, "selectable": True} for i in development_columns
                                                            ],
                                                            data=ball_performance_development.to_dict('records'),
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
                                                                    'filter_query': "{percentChange} <= 0"
                                                                },
                                                                'backgroundColor': "#ed4734",
                                                                'color': 'white',
                                                                },
                                                                {
                                                                "if": {
                                                                    'column_id': 'Parameters',
                                                                    'filter_query': "{percentChange} > 0"
                                                                },
                                                                'backgroundColor': "#1ABE0C",
                                                                'color': 'white',
                                                                },
                                                                {'if': {'column_id': 'Last Week'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Parameters'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Average 4 Weeks'},
                                                                'width': '24%'},
                                                                {'if': {'column_id': 'Percent Change'},
                                                                'width': '24%'},
                                                            ]
                                                        ),
                                                    ]),
                                                    dcc.Tab(label="Match Performance Trend", children=[
                                                        dcc.Dropdown(
                                                                id='match-select-player',
                                                                options=[{'label': i, 'value': i} for i in all_matches_list],
                                                                value=all_matches_list[0]
                                                        ),
                                                        html.Div(id='match-bar-chart-player', children=[
                                                        ], style={'width': '39%', 'display': 'inline-block'}),

                                                        html.Div(id='development-trend-player', children=[
                                                        ], style={'width': '59%', 'display': 'inline-block'}),
                                                    ]),

                                                    dcc.Tab(label="Match Comparison", children=[
                                                        html.Div([
                                                            html.H4("Select Match 1", style={'textAlign':'center'}),
                                                            dcc.Dropdown(
                                                                id='match-select-1-player',
                                                                options=[{'label': i, 'value': i} for i in all_matches_list],
                                                                value=all_matches_list[0]
                                                            ),
                                                        ], style={'width': '49%', 'display': 'inline-block'}),
                                                        html.Div([
                                                            html.H4("Select Match 2", style={'textAlign':'center'}),
                                                            dcc.Dropdown(
                                                                id='match-select-2-player',
                                                                options=[{'label': i, 'value': i} for i in all_matches_list],
                                                                value=all_matches_list[1]
                                                            ),
                                                        ], style={'width': '49%', 'display': 'inline-block'}),
                                                        html.Div(id='score-match-select'),
                                                        dcc.Graph(
                                                            id='match-select-chart',
                                                        ),
                                                    ]),
                                                ]),
                                            ]
                                        )
                                    ]
                                ), width=9,
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

### show and hide ###
@app.callback(
    Output('sidebar-development', 'style'),
    [Input('development-tabs', 'value')]
)
def update_sidebar(value):
    if value == 'overview-tab-development':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

### show time selection ###
@app.callback(
    Output('slider-output-player', 'children'),
    [Input('time-range-player', 'value')]
)
def update_slider_output(value):
    return 'You have selected "{}"'.format(value)

# update chart for performance trend on match select
@app.callback(
    Output('match-bar-chart-player', 'children'),
    [Input('match-select-player', 'value'),
    Input('external-personal-player', 'value'),
    Input('internal-personal-player', 'value'),
    Input('ball-personal-player', 'value')]
)
def update_match_bar_chart(matchId, external, internal, ball):
    # if external, internal, ball are just one element than it is a string and not a list
    if isinstance(internal, str):
        internal_params = [internal]
    else:
        internal_params = internal
    
    if isinstance(external, str):
        external_params = [external]
    else:
        external_params = external

    if isinstance(ball, str):
        ball_params = [ball]
    else:
        ball_params = ball

    # get data from all_matches, this will be changed when averages are already in database
    # this will be data for that one selected game
    match_data = all_matches[all_matches['matchId']==matchId]

    # # external
    # external_data = match_data[external_params]

    # # internal
    # internal_data = match_data[internal_params]

    # # ball
    # ball_data = match_data[ball_params]

    parameter_list = [internal_params, external_params, ball_params]
    parameter_labels = ["Internal", "External", "Ball"]

    # get bar chart, one for each category
    children_bar = []

    # # external chart
    # fig_external = go.Figure()

    # # add player trace
    # fig.add_trace(
    #     go.Bar(
    #         x=external_params, y=match_data[match_data['playerId']==player_id], name='You'
    #     )
    # )
    for l in parameter_list:
        temp_params = l.copy()
        temp_params.append('playerId')
        plot_df = match_data[temp_params]
        player_df = plot_df[plot_df['playerId']==player_id]
        player_df.drop(columns=['playerId'], inplace=True)
        #print(player_df)
        player_data = player_df.values.flatten()
        #print(player_data)
        mean_df = plot_df[plot_df['playerId']=='mean']
        mean_df.drop(columns=['playerId'], inplace=True)
        mean_data = mean_df.values.flatten()
        #print(mean_df)
        temp_params.remove('playerId')

        fig = go.Figure()

        # add mean trace
        fig.add_trace(
            go.Bar(
                x=temp_params, y=mean_data, name='Team Average', marker_color='blue'
            )
        )

        # add player trace
        fig.add_trace(
            go.Bar(
                x=temp_params, y=player_data, name='You', marker_color='orange', width=0.6,
            )
        )

        # layout
        fig.update_layout(
            height=300,
            template='seaborn',
            hovermode='x',
            barmode='overlay',
            showlegend=False,
            margin=dict(t=20, b=20, r=0),
        )

        chart_bar = dcc.Graph(
            figure=fig
        )

        children_bar.append(chart_bar)

    return children_bar
        
@app.callback(
    Output('development-trend-player', 'children'),
    [Input('match-select-player', 'value'),
    Input('external-personal-player', 'value'),
    Input('internal-personal-player', 'value'),
    Input('ball-personal-player', 'value')]
)
def update_development_trend_player(selected_match, external, internal, ball):
    # if external, internal, ball are just one element than it is a string and not a list
    if isinstance(internal, str):
        internal_params = [internal]
    else:
        internal_params = internal
    
    if isinstance(external, str):
        external_params = [external]
    else:
        external_params = external

    if isinstance(ball, str):
        ball_params = [ball]
    else:
        ball_params = ball


    parameter_list = [internal_params, external_params, ball_params]
    parameter_labels = ["Internal", "External", "Ball"]

    match_data = all_matches[all_matches['playerId']==player_id]
    matches = match_data['matchId'].tolist()

    children_trend = []

    for p in parameter_list:
        plot_df = match_data[p]
        fig = go.Figure()

        for param in p:
            fig.add_trace(
                go.Scatter(
                    x=matches, y=plot_df[param], mode='lines+markers', name=param
                )
            )

            # vertical line marker for selected match
            fig.add_shape(
            # Line Vertical
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=selected_match,
                    y0=0,
                    x1=selected_match,
                    y1=plot_df[param].max(),
                    line=dict(
                        color="Black",
                        width=3,
                        dash="dot",
                    )
                )
            )
        
            

        fig.update_layout(
            legend=dict(x=0.5, y=1),
            legend_orientation="h",
            height=300,
            width=600,
            # template='seaborn',
            # hovermode='x',
            showlegend=False,
            margin=dict(t=20, b=20, r=0),
            hovermode='x unified',
            template='plotly_white',
        )

        chart_trend = dcc.Graph(
            figure=fig,
        )
        
        children_trend.append(chart_trend)


    return children_trend
### update hover chart ###
# @app.callback(
#     Output('match-hover-chart', 'figure'),
#     [Input('time-range-player', 'value'),]
# )
# def update_game_hover_chart(time_slider):

#     ### filter df by time-range (or num of games)###
#     match_list = all_matches['matchId'].to_list()
#     selected_matches = match_list[time_slider[0]:time_slider[1]]

#     filter_by_matches_df = all_matches[all_matches['matchId'].isin(selected_matches)]
#     player_hover_match = filter_by_matches_df[filter_by_matches_df['playerId'] == player_id]

#     fig = go.Figure()
#     x_values = list(range(time_slider[0], time_slider[1]))
#     y_values = player_hover_match['exerciseLoad'].to_list()
#     fig.add_trace(go.Scatter(x=x_values, y=y_values,
#                             mode='lines+markers'))
    
#     fig.update_layout(
#         template='seaborn',
#         hovermode='x'
#     )

#     return fig
# @app.callback(
#     Output('match-development-comparison', 'figure'),
# )

# @app.callback(
#     Output('match-bar-chart', 'figure'),
#     [Input('match-hover-chart', 'hoverData'),
#      Input('time-range-player', 'value'),
#      Input('external-personal-player', 'value'),
#      Input('internal-personal-player', 'value'),
#      Input('ball-personal-player', 'value')]
# )
# def update_game_bar_chart(hoverData, time_slider, external, internal, ball):
#     ## select matches by slider selection
#     #match_list = all_matches['matchId'].to_list()
#     if hoverData is not None:
#         selected_matches_slider = all_matches_list[time_slider[0]:time_slider[1]]
#         x_value_game_hover = hoverData['points'][0]['x'] - 1
#         selected_match = selected_matches_slider[x_value_game_hover]
#     else:
#         selected_matches_slider = all_matches_list[time_slider[0]:time_slider[1]]
#         selected_match = selected_matches_slider[-1]

#     filter_by_match_df = all_matches[all_matches['matchId'] == selected_match]

#     player_data = filter_by_match_df[filter_by_match_df['playerId'] == player_id]
#     player_data.fillna(0, inplace=True)
#     mean_data = filter_by_match_df[filter_by_match_df['playerId'] == 'mean']
#     mean_data.fillna(0, inplace=True)

#     if isinstance(internal, str):
#         internal_params = [internal]
#     else:
#         internal_params = internal
    
#     if isinstance(external, str):
#         external_params = [external]
#     else:
#         external_params = external

#     if isinstance(ball, str):
#         ball_params = [ball]
#     else:
#         ball_params = ball
    
#     external_df_match_player = pd.DataFrame(player_data[external_params].transpose())
#     external_df_match_mean = pd.DataFrame(mean_data[external_params].transpose())
#     num_external_params = len(external_params)

#     internal_df_match_player = pd.DataFrame(player_data[internal_params].transpose())
#     internal_df_match_mean = pd.DataFrame(mean_data[internal_params].transpose())
#     num_internal_params = len(internal_params)

#     ball_df_match_player = pd.DataFrame(player_data[ball_params].transpose())
#     ball_df_match_mean = pd.DataFrame(mean_data[ball_params].transpose())
#     num_ball_params = len(ball_params)

#     fig = make_subplots(
#         rows=2, cols=3,
#         specs=[[{}, {}, {}], [{}, {}, {}]],
#         subplot_titles=("Internal Game", "External Game", "Ball Game", "Internal Training", "External Training", "Ball Training"),
#         horizontal_spacing = 0.05, vertical_spacing = 0.15)

    
#     fig.add_trace(
#         go.Bar(x=internal_params, y=internal_df_match_mean.iloc[:,0], marker_color='blue', name='Mean'),
#         row=1, col=1
#     )

#     fig.add_trace(
#         go.Bar(x=internal_params, y=internal_df_match_player.iloc[:,0], marker_color='orange',
#                  width=[0.6]*num_internal_params, name='You'),
#         row=1, col=1
#     )
    
#     fig.add_trace(
#         go.Bar(x=external_params, y=external_df_match_mean.iloc[:,0], marker_color='blue', name='Mean'),
#         row=1, col=2
#     )

#     fig.add_trace(
#         go.Bar(x=external_params, y=external_df_match_player.iloc[:,0], marker_color='orange',
#              width=[0.6]*num_external_params, name='You'),
#         row=1, col=2
#     )

#     fig.add_trace(
#         go.Bar(x=ball_params, y=ball_df_match_mean.iloc[:,0], marker_color='blue', name='Mean'),
#         row=1, col=3
#     )

#     fig.add_trace(
#         go.Bar(x=ball_params, y=ball_df_match_player.iloc[:,0], marker_color='orange',
#              width=[0.6]*num_ball_params, name='You'),
#         row=1, col=3
#     )


#     fig.update_layout(showlegend=False, template='seaborn', barmode='overlay', hovermode='x')

#     return fig

@app.callback(
    [Output("match-select-chart", 'figure'),
     Output("score-match-select", 'children')],
    [Input("match-select-1-player", 'value'),
     Input("match-select-2-player", 'value'),
     Input('internal-personal-player', 'value'),
     Input('external-personal-player', 'value'),
     Input('ball-personal-player', 'value')]
)
def update_match_select_chart(match1, match2, internal, external, ball):

    # get the game scores
    score1 = db.get_match_score(match1)
    score2 = db.get_match_score(match2)

    score = html.Div(children=[
                html.Div(score1, style={'display': 'inline-block', 'width':'49%', 'textAlign': 'center'}),
                html.Div(score2, style={'display': 'inline-block', 'width':'49%', 'textAlign': 'center'})
            ], style={"margin-bottom": "5px"})

    ## make sure that it is always a list when selection changes from one to mult ##
    if isinstance(internal, str):
        internal_params = [internal]
    else:
        internal_params = internal
    
    if isinstance(external, str):
        external_params = [external]
    else:
        external_params = external

    if isinstance(ball, str):
        ball_params = [ball]
    else:
        ball_params = ball

    #matches = [match1, match2]
    player_data = all_matches[all_matches['playerId'] == player_id]
    player_data.fillna(0, inplace=True)
    mean_data = all_matches[all_matches['playerId'] == 'mean']
    mean_data.fillna(0, inplace=True)

    player_data_match1 = player_data[player_data['matchId'] == match1]
    player_data_match2 = player_data[player_data['matchId'] == match2]

    mean_data_match1 = mean_data[mean_data['matchId'] == match1]
    mean_data_match2 = mean_data[mean_data['matchId'] == match2]

    internal_mean_match1 = pd.DataFrame(mean_data_match1[internal_params].transpose())
    internal_player_match1 = pd.DataFrame(player_data_match1[internal_params].transpose())
    internal_mean_match2 = pd.DataFrame(mean_data_match2[internal_params].transpose())
    internal_player_match2 = pd.DataFrame(player_data_match2[internal_params].transpose())

    external_mean_match1 = pd.DataFrame(mean_data_match1[external_params].transpose())
    external_player_match1 = pd.DataFrame(player_data_match1[external_params].transpose())
    external_mean_match2 = pd.DataFrame(mean_data_match2[external_params].transpose())
    external_player_match2 = pd.DataFrame(player_data_match2[external_params].transpose())

    ball_mean_match1 = pd.DataFrame(mean_data_match1[ball_params].transpose())
    ball_player_match1 = pd.DataFrame(player_data_match1[ball_params].transpose())
    ball_mean_match2 = pd.DataFrame(mean_data_match2[ball_params].transpose())
    ball_player_match2 = pd.DataFrame(player_data_match2[ball_params].transpose())

    # num_internal_params = len(internal_params)
    # num_external_params = len(external_params)
    # num_ball_params = len(ball_params)
    fig = make_subplots(
        rows=3, cols=2,
        specs=[[{}, {}], [{}, {}], [{}, {}]],
        subplot_titles=("Internal Match 1", "Internal Match 2", "External Match 1", "External Match 2", "Ball Match 1", "Ball Match 2", ),
        horizontal_spacing = 0.05, vertical_spacing = 0.15, shared_yaxes=True)

    ### Plots First Game ###
    # internal #
    fig.add_trace(
        go.Bar(x=internal_params, y=internal_mean_match1.iloc[:,0], marker_color='blue', name='Mean'),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=internal_params, y=internal_player_match1.iloc[:,0], marker_color='orange', name='You', width=0.6),
        row=1, col=1,
    )
    # external #
    fig.add_trace(
        go.Bar(x=external_params, y=external_mean_match1.iloc[:,0], marker_color='blue', name='Mean'),
        row=2, col=1,
    )
    fig.add_trace(
        go.Bar(x=external_params, y=external_player_match1.iloc[:,0], marker_color='orange', name='You', width=0.6),
        row=2, col=1,
    )
    # ball #
    fig.add_trace(
        go.Bar(x=ball_params, y=ball_mean_match1.iloc[:,0], marker_color='blue', name='Mean'),
        row=3, col=1,
    )
    fig.add_trace(
        go.Bar(x=ball_params, y=ball_player_match1.iloc[:,0], marker_color='orange', name='You', width=0.6),
        row=3, col=1,
    )

    ### Plots Second Game ###
     # internal #
    fig.add_trace(
        go.Bar(x=internal_params, y=internal_mean_match2.iloc[:,0], marker_color='blue', name='Mean'),
        row=1, col=2,
    )
    fig.add_trace(
        go.Bar(x=internal_params, y=internal_player_match2.iloc[:,0], marker_color='orange', name='You', width=0.6),
        row=1, col=2,
    )
    # external #
    fig.add_trace(
        go.Bar(x=external_params, y=external_mean_match2.iloc[:,0], marker_color='blue', name='Mean'),
        row=2, col=2,
    )
    fig.add_trace(
        go.Bar(x=external_params, y=external_player_match2.iloc[:,0], marker_color='orange', name='You', width=0.6),
        row=2, col=2,
    )
    # ball #
    fig.add_trace(
        go.Bar(x=ball_params, y=ball_mean_match2.iloc[:,0], marker_color='blue', name='Mean'),
        row=3, col=2,
    )
    fig.add_trace(
        go.Bar(x=ball_params, y=ball_player_match2.iloc[:,0], marker_color='orange', name='You', width=0.6),
        row=3, col=2,
    )

    fig.update_layout(height=800, template='seaborn', showlegend=False, hovermode='x', barmode='overlay')

    return fig, score

# @app.callback(
#     Output('over-time-chart', 'figure'),
#     [Input('time-range-player', 'value'),
#      Input('internal-personal-player', 'value'),
#      Input('external-personal-player', 'value'),
#      Input('ball-personal-player', 'value')]
# )
# def update_over_time_chart(time_slider, internal, external, ball):
#     selected_matches_slider = all_matches_list[time_slider[0]:time_slider[1]]
#     filter_by_matches_df = all_matches[all_matches['matchId'].isin(selected_matches_slider)]
#     player_df = filter_by_matches_df[filter_by_matches_df['playerId'] == player_id]
#     player_df.fillna(0, inplace=True)

#     internal_df = pd.DataFrame(player_df[internal])
#     external_df = pd.DataFrame(player_df[external])
#     ball_df = pd.DataFrame(player_df[ball])

#     fig = make_subplots(
#         rows=3, cols=1,
#         specs=[[{}], [{}], [{}]],
#         shared_xaxes=True,
#         subplot_titles=("Internal", "External", "Ball"),
#         horizontal_spacing = 0.05, vertical_spacing = 0.15)

#     for c in internal_df.columns:
#         plot_data = internal_df[c]
#         fig.add_trace(go.Scatter(x=selected_matches_slider, y=plot_data, name=c, mode='lines+markers'),
#                     row=1, col=1)

#     for c in external_df.columns:
#         plot_data = external_df[c]
#         fig.add_trace(go.Scatter(x=selected_matches_slider, y=plot_data, name=c, mode='lines+markers'),
#                     row=2, col=1)

#     for c in ball_df.columns:
#         plot_data = ball_df[c]
#         fig.add_trace(go.Scatter(x=selected_matches_slider, y=plot_data, name=c, mode='lines+markers'),
#                     row=3, col=1)

#     fig.update_layout(height=600, template='seaborn', hovermode='x')

#     return fig
    
    
