import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from apps import commonmodules
import dash_table

from app import app
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objs as go

from database import database as db



my_team_name = 'AFCU9-1'

# current time, later should be updated to now

# Possible matches for his team
possible_team_matches = db.teams_and_matches(my_team_name)


# possible players / ##### eed to find a better way of finding possible players per team or coach #####
possible_match_players = db.matches_and_players(possible_team_matches[0])

# game data for single selected match
match_df = db.select_match_data(possible_team_matches[0])

# possible metrics to select
available_metrics = db.match_metrics_data(match_df)

# available dates 
available_dates = db.time_range_matches(my_team_name)

###xy Position data###
# xy_df, max_x_position, max_y_position = db.combine_ball_event_data()
# xy_players = xy_df['playerId'].unique().tolist()

# parameter specification for internal, external, and ball
# running distance shouldnt necessarily be here but for tactical analysis it is useful rn
internal_parameters = ['exerciseLoad', 'maxVO2', 'runningDistance']
external_parameters = ['imaAccMid', 'imaAccHigh', 'imaDecMid', 'imaDecHigh',\
                                        'imaRighMid', 'imaRighHigh', 'imaLeftMid', 'imaLeftHigh']
ball_parameters = ['touches', 'passes', 'shots', 'tackles']

# get the match_ids for the team 
match_id_str, match_dates = db.latest_matches_per_team(my_team_name)

# get data for match performance development
last_five_df = db.match_performance_development(match_id_str)

# get data for performance development


##### function to update color heatmap for values #### 
def discrete_background_color_bins(df, n_bins=5, columns='all'):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq']['Blues'][i - 1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))

(styles_last_five, legend_last_five) = discrete_background_color_bins(last_five_df)


#### diverging bars 
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

# check latest match table
latest_matches, matchDates = db.latest_matches_per_team(my_team_name)
external_df, internal_df, ball_df, performance_df, stamina_AC, fit_score_df, gauge_val_dict, trend_df = db.latest_matches_per_player('72262', latest_matches)
fit_score_df.drop(columns=['FIT Score'], inplace=True)
fit_score_df.columns = ['Training Session', 'belowFIT', 'Parameters', 'aboveFIT', 'Match']

#### custom legend with green red orange
custom_legend = []
custom_bounds = [0, 0.8, 1, 1.3]
custom_bounds = ['<0.8', '0.8-1', '1-1.3', '>1.3']
# custom colors blue, orange, green, red
custom_colors = ['#042A66', '#ff9900', '#006C11', '#ff3333']
for idx, backgroundColor in enumerate(custom_colors):
    custom_legend.append(
                html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                    html.Div(
                        style={
                            'backgroundColor': backgroundColor,
                            'borderLeft': '1px rgb(50, 50, 50) solid',
                            'height': '10px'
                        }
                    ),
                    html.Small(custom_bounds[idx], style={'paddingLeft': '2px'})
                ])
            )

#### matrix player fitness chart ####
mean = last_five_df[last_five_df['Player ID']=='mean']
mean.reset_index(inplace=True)
mean_ima = mean.loc[0, 'IMA']
mean_internal = mean.loc[0, 'Internal']
player_fitness_matrix_plot = go.Figure(
    go.Scatter(
        x=last_five_df['IMA'], 
        y=last_five_df['Internal'], 
        mode='markers', 
        marker_size=10, 
        customdata=np.stack((last_five_df['Player ID'], last_five_df['IMA'], last_five_df['Internal']),axis=-1),
        hovertemplate="<br>Player:%{customdata[0]}<br>IMA:%{customdata[1]}<br>Internal:%{customdata[2]}",
    )
)

# vertical mean for IMA
# player_fitness_matrix_plot.add_shape(
#     dict(
#         type="line",
#         x0=mean_ima,
#         y0=0,
#         x1=mean_ima,
#         y1=last_five_df['Internal'].max(),
#         line=dict(
#             color="RoyalBlue",
#             width=3
#         )
#     )
# )
# # horizontal mean for Internal
# player_fitness_matrix_plot.add_shape(
#     dict(
#         type="line",
#         x0=0,
#         y0=mean_internal,
#         x1=last_five_df['IMA'].max(),
#         y1=mean_internal,
#         line=dict(
#             color="RoyalBlue",
#             width=3
#         )
#     )
# )

player_fitness_matrix_plot.update_layout(
    template='plotly_white',
    height=900,
    xaxis_title="IMA",
    yaxis_title="Exercise Load",
    font= dict(
        size=18,
    )
)



#######        #######
####### LAYOUT #######
#######        #######
layout = html.Div([
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
                                    html.H6("Teams:"),
                                    html.H6("Age:"),
                                ])
                            ]), width=5,
                        ),
                    ],
                    justify="center",
                    ),
                    html.Div([
                        html.H3("Match Performance Development"),
                        html.Div(custom_legend, style={'textAlign': 'center'}),
                        html.Div(children=[
                            dash_table.DataTable(
                                id='match-performance-data',
                                columns = [
                                    {"name": i, "id": i, "selectable": True} for i in last_five_df.columns
                                ],
                                data = last_five_df.to_dict('records'),
                                sort_action='native',
                                #fixed_rows={'headers': True, 'data': 0},
                                style_table={
                                    #'minWidth': '100%',
                                    'minWidth': '100%',
                                    'height': '500px',
                                    'overflowY': 'auto',
                                },
                                style_cell={
                                    'textAlign': 'center',
                                    'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',
                                },
                                style_header={
                                    'fontWeight': 'bold',
                                    # 'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',
                                },
                                #style_data_conditional=styles_last_five
                                style_data_conditional=(
                                    [
                                    {# if value > 1.3 RED
                                        'if': {
                                            'filter_query': "{{{}}} > 1.3".format(col),
                                            'column_id': col
                                        },
                                        'backgroundColor': '#ff3333',
                                        'color': 'white'
                                    } for col in list(last_five_df.select_dtypes(include=[np.number]).columns.values)
                                    ] +
                                    [
                                    {# if value between 1 and 1.3 green
                                        'if': {
                                            'filter_query': '{{{}}} >= 1 && {{{}}} <= 1.3'.format(col, col),
                                            'column_id': col
                                        },
                                        'backgroundColor': '#006C11',
                                        'color': 'white'
                                    } for col in list(last_five_df.select_dtypes(include=[np.number]).columns.values)
                                    ] + 
                                    [
                                    { # if value between 0.8 and 1 orange
                                        'if': {
                                            'filter_query': '{{{}}} >= 0.8 && {{{}}} < 1'.format(col, col),
                                            'column_id': col
                                        },
                                        'backgroundColor': '#ff9900',
                                        'color': 'white'
                                    } for col in list(last_five_df.select_dtypes(include=[np.number]).columns.values)
                                    ] +
                                    [
                                    {# if value < 0.8
                                        'if': {
                                            'filter_query': "{{{}}}<0.8".format(col),
                                            'column_id': col
                                        },
                                        'backgroundColor': '#042A66',
                                        'color': 'white'
                                    } for col in list(last_five_df.select_dtypes(include=[np.number]).columns.values)
                                    ] +
                                    # highlight the mean row
                                    [{
                                        'if': {
                                            'column_id': 'Player ID',
                                            'filter_query': "{Player ID} = 'mean'"
                                        },
                                        'backgroundColor': '#bfbfbf',
                                        'color': 'black'
                                    }]
                                
                                )
                                

                            ),
                        ],style={'width':'90%','margin-left': 'auto', 'margin-right': 'auto'})  
                    ], style={'textAlign':'center'}),

        html.Div([
                        html.H3("Player Performance Development"),
                        html.Div(legend_last_five, style={'textAlign': 'center'}),
                        html.Div(children=[
                            dash_table.DataTable(
                                id='performance-development-data',
                                columns = [
                                    {"name": i, "id": i, "selectable": True} for i in last_five_df.columns
                                ],
                                data = last_five_df.to_dict('records'),
                                sort_action='native',
                                #fixed_rows={'headers': True, 'data': 0},
                                style_table={
                                    #'minWidth': '100%',
                                    'minWidth': '100%',
                                    'height': '500px',
                                    'overflowY': 'auto',
                                },
                                style_cell={
                                    'textAlign': 'center',
                                    'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',
                                },
                                style_header={
                                    'fontWeight': 'bold',
                                    # 'minWidth': '80px', 'width': '100px', 'maxWidth': '120px',
                                },
                                style_data_conditional=(styles_last_five + 
                                    # highlight the mean row
                                    [{
                                        'if': {
                                            'column_id': 'Player ID',
                                            'filter_query': "{Player ID} = 'mean'"
                                        },
                                        'backgroundColor': '#bfbfbf',
                                        'color': 'black'
                                    }]
                                )

                            ),
                        ],style={'width':'90%','margin-left': 'auto', 'margin-right': 'auto'}),  
                    html.Div([
                        html.H3("Player Fitness Performance"),
                        dcc.Graph(
                            id='matrix-player-selection',
                            figure=player_fitness_matrix_plot
                        ),
                    ], style={'textAlign': 'center'}),
                    ], style={'textAlign':'center'}),
        ]),
        ############ #########################
        ########### top bar instead of side bar #########
        dcc.Tab(label='Analysis', children=[


            html.Div([
            dcc.Tabs(id='analysis-tabs-coach', value='player-coach', children=[
                dcc.Tab(label='Player Analysis', id='player-analysis-coach', value='player-coach', children=[
                    dcc.Tabs([
                        dcc.Tab(label='Match Performance', children=[

                            html.Details([
                                html.Summary("Match Selection"),

                                html.Div(id='time-selection-dropdown', children=[
                                    html.Div([
                                        html.H6('Select Time Period Start', style={'textAlign':'center'}),
                                        dcc.Dropdown(
                                            id='select-start-time-coach',
                                            options=[{'label': i, 'value': i} for i in available_dates],
                                            value=available_dates[0]
                                        ),
                                    ], style={'display': 'inline-block', 'width': '33%',}),
                                    html.Div([
                                        html.H6('Select Time Period End', style={'textAlign':'center'}),
                                        dcc.Dropdown(
                                            id='select-end-time-coach',
                                            options=[{'label': i, 'value': i} for i in available_dates],
                                            value=available_dates[-1]
                                        ),
                                    ], style={'display': 'inline-block', 'width': '33%',}),
                                    html.Div([
                                        html.H6('Select Match', style={'textAlign':'center'}),
                                        dcc.Dropdown(
                                            id='match-select-coach',
                                            options=[{'label': i, 'value': i} for i in possible_team_matches],
                                            value=possible_team_matches[0],
                                            clearable=False
                                        ),
                                    ],style={'display': 'inline-block', 'width': '33%',}),

                                ], style={'margin-top':'10px', 'padding-bottom': '10px'}),
                            ]),

                            dash_table.DataTable(
                                                    id='datatable-coach',
                                                    # columns=[
                                                    #     {"name": i, "id": i, "selectable": True} for i in match_df.columns
                                                    # ],
                                                    # data=dummy_df.to_dict('records'),
                                                    sort_action="native",
                                                    sort_mode="multi",
                                                    style_table={
                                                        'overflowX': 'auto',
                                                        'minWidth': '100%',
                                                        'height': '300px',
                                                        'overflowY': 'auto'
                                                    },
                                                    page_action='none',
                                                    selected_columns=[],
                                                    selected_rows=[],
                                                    row_selectable="multi",
                                                    #fixed_columns={'headers': True, 'data':1},
                                                    #fixed_rows={'headers': True, 'data': 0},
                                                    # style_table={'minWidth': '100%'},
                                                    column_selectable="multi",
                                                    style_cell={
                                                        'textAlign': 'center',
                                                        'minWidth': '80px', 'width': '100px', 'maxWidth': '180px',
                                                    },
                                                    # style_cell_conditional=[
                                                    #     {
                                                    #         'if': {'column_id': c},
                                                    #         'textAlign': ''
                                                    #     } for c in ['Date', 'Region']
                                                    # ],
                                                    style_data_conditional=[
                                                        {
                                                            'if': {'row_index': 'odd'},
                                                            'backgroundColor': 'rgb(248, 248, 248)'
                                                        }
                                                    ],
                                                    style_header={
                                                        'backgroundColor': 'rgb(230, 230, 230)',
                                                        'fontWeight': 'bold'
                                                    }
                                                ), 
                            html.Div(id='datatable-plots-coach', children=[
                                html.Div(id='datatable-plot-bar', style={'display':'inline-block', 'width': '59%'}), 
                                html.Div(id='datatable-plot-trend', style={'display':'inline-block', 'width': '39%'}),        
                            ])    
                        ]),
                        
                        dcc.Tab(label='Training/Match', children=[
                            html.Div([
                            dash_table.DataTable(
                                            id='dummy-table',
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
                        ]),
                        dcc.Tab(label='In Depth Player', children=[

                        ]),


                    ])
                ]),
                dcc.Tab(label='Tactical Analysis', id='tactical-analysis-coach', value='tactical-coach', children=[
                    # wrap this in html details container
                    html.Details(children=[
                    html.Summary("Match and Parameter Selection"),

                    # parameter selection
                    html.Div(id='parameter-selection-coach', children=[
                        html.Div([
                        html.H6('Internal Parameters', style={'textAlign':'center'}),
                        dcc.Dropdown(
                                    id='internal-select-coach',
                                    options=[{'label': i, 'value': i} for i in internal_parameters],
                                    value=internal_parameters[0],
                                    multi=True,
                        ),
                        ], style={'display': 'inline-block', 'width': '49%',}),
                        html.Div([
                        html.H6('External Parameters', style={'textAlign':'center'}),
                        dcc.Dropdown(
                            id='external-select-coach',
                            options=[{'label': i, 'value': i} for i in external_parameters],
                            value=external_parameters[0],
                            multi=True,
                        ),
                        ], style={'display': 'inline-block', 'width': '49%',}),
                    ], style={'padding-top': '10px', 'margin-bottom': '10px'}),

                    html.Div(id='match-selections-coach', children=[
                        html.Div(children=[
                        html.H5("Select Match", style={'textAlign': 'center'}),
                            dcc.Dropdown(
                                id='match-select-tactical-coach-left',
                                options=[{'label': i, 'value': i} for i in possible_team_matches],
                                value=possible_team_matches[0],
                                multi=False,
                        ),
                        ], style={'display': 'inline-block', 'width': '49%'}),
                        
                        html.Div(children=[
                        html.H5("Select Match", style={'textAlign': 'center'}),
                            dcc.Dropdown(
                                id='match-select-tactical-coach-right',
                                options=[{'label': i, 'value': i} for i in possible_team_matches],
                                value=possible_team_matches[0],
                                multi=False,
                                ),
                        ], style={'display': 'inline-block', 'width': '49%'}),
                    ]),
                        # html.Div([
                        # html.H6('Ball Parameters', style={'textAlign':'center'}),
                        # dcc.Dropdown(
                        #     id='ball-select-coach',
                        #     options=[{'label': i, 'value': i} for i in ball_parameters],
                        #     value=ball_parameters[0],
                        #     multi=True,
                        # ),
                        # ], style={'display': 'inline-block', 'width': '33%',})
                    ]),
                    html.Details(children=[
                        html.Summary("Match Modifications"),
                        html.Div([
                            html.Div([
                                html.Button('First Half', id='first-half-left', n_clicks=0, style={'display': 'inline-block'}),
                                html.Button('Second Half', id='second-half-left', n_clicks=0, style={'display': 'inline-block'}),
                            ], style={'textAlign': 'center', 'margin-top': '5px', 'margin-bottom': '5px'}),

                            dcc.RangeSlider(
                                            id='time-slider-pitch-left-coach',
                                            min=0,
                                            max=45,
                                            step=None,
                                            marks={
                                                0: "0'",
                                                5: "5'",
                                                10:"10'",
                                                15:"15'",
                                                20:"20'",
                                                25:"25'",
                                                30:"30'",
                                                35:"35'",
                                                40:"40'",
                                                45:"45'"
                                            },
                                            pushable=5,
                                            value=[0,45],
                            ),

                            dcc.Dropdown(
                                            id='player-select-left-pitch-coach',
                                            #options=[{'label': i, 'value': i} for i in xy_players],
                                            options=[{'label': i, 'value': i} for i in possible_match_players],
                                            value=[possible_match_players[0]],
                                            multi=True
                            ),
                        ], style={'display': 'inline-block', 'width': '49%'},),

                        html.Div([
                            html.Div([
                                html.Button('First Half', id='first-half-right', n_clicks=0, style={'display': 'inline-block'}),
                                html.Button('Second Half', id='second-half-right', n_clicks=0, style={'display': 'inline-block'}),
                                ], style={'textAlign': 'center', 'margin-top': '5px', 'margin-bottom': '5px'}),

                                dcc.RangeSlider(
                                        id='time-slider-pitch-right-coach',
                                        min=0,
                                        max=45,
                                        step=None,
                                        marks={
                                            0: "0'",
                                            5: "5'",
                                            10:"10'",
                                            15:"15'",
                                            20:"20'",
                                            25:"25'",
                                            30:"30'",
                                            35:"35'",
                                            40:"40'",
                                            45:"45'"
                                        },
                                        pushable=5,
                                        value=[0,45],
                                ),

                                dcc.Dropdown(
                                            id='player-select-right-pitch-coach',
                                            # options=[{'label': i, 'value': i} for i in xy_players],
                                            # value=[xy_players[0]],
                                            options=[{'label': i, 'value': i} for i in possible_match_players],
                                            value=[possible_match_players[0]],
                                            multi=True,
                                ),
                        ], style={'display': 'inline-block', 'width': '49%'},)
                    ]),
                    ####
                    html.Div([
                        html.Div([
                                    
                        html.Div(
                            dash_table.DataTable(
                                id='datatable-left-pitch-coach',
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                ],
                                sort_action="native",
                                style_cell={'textAlign': 'center'},
                                style_header={
                                    'fontWeight': 'bold'
                                },
                                style_table={
                                    'table-layout': 'fixed',
                                    'width': '90%',
                                },
                            ),
                        ),

                        dcc.Graph(
                            id="football-pitch-left-coach"
                        ),
                    
                        ], style={'display':'inline-block', 'width': '45%', 'margin-right':'5px', 'margin-top':'10px', 'vertical-align': 'top'}),

                                        # to select first or seconds half
                        html.Div([

                            html.Div(
                                dash_table.DataTable(
                                    id='datatable-right-pitch-coach',
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                                    ],
                                    sort_action="native",
                                    style_cell={'textAlign': 'center'},
                                    style_header={
                                        'fontWeight': 'bold'
                                    },
                                    style_table={
                                        'table-layout': 'fixed',
                                        'width': '90%',
                                    }
                                ),
                            ),

                            dcc.Graph(
                                id="football-pitch-right-coach",
                                config={
                                    'displayModeBar': False
                                },
                            ),
                

                        ], style={'display':'inline-block', 'width': '49%','margin-left':'5px', 'margin-top':'10px', 'vertical-align': 'top'}),  

                    ], style={'display':'flex', 'justify-content': 'center', 'align-items': 'center'}),                  
                ]),
            ]),
            ]),
        ]),

            ######## end of top bar ##########
            ###################################

            ######## side bar mode ############
            ####################################
        #     dbc.Row(
        #     [
        #     dbc.Col(dbc.Card(
        #         [
        #             dbc.CardBody(
        #                 [
        #                     #html.H3("Sidebar"),
        #                     html.H6('Your Team'),
        #                     html.H6(my_team_name),

        #                     # html.H6('Select Time Period Start'),
        #                     # dcc.Dropdown(
        #                     #     id='select-start-time-coach',
        #                     #     options=[{'label': i, 'value': i} for i in available_dates],
        #                     #     value=available_dates[0]
        #                     # ),

        #                     # html.H6('Select Time Period End'),
        #                     # dcc.Dropdown(
        #                     #     id='select-end-time-coach',
        #                     #     options=[{'label': i, 'value': i} for i in available_dates],
        #                     #     value=available_dates[-1]
        #                     # ),

        #                     dcc.Tabs(children=[
        #                         dcc.Tab(label='Match', children=[
        #                             # html.H6('Select Match'),
        #                             # dcc.Dropdown(
        #                             #     id='match-select-coach',
        #                             #     options=[{'label': i, 'value': i} for i in possible_team_matches],
        #                             #     value='61614647-8504-4983-8976-143056946FF0',
        #                             #     clearable=False
        #                             # ),
        #                             ]),

        #                             dcc.Tab(label='Train', children=[
        #                                 html.H6('Select Training'),
        #                                 dcc.Dropdown(
        #                                     id='training-select-coach',
        #                                     clearable=False
        #                                 ),
        #                             ])
        #                         ]),
                            
        #                     # html.H6('Internal Parameters'),
        #                     # dcc.Dropdown(
        #                     #     id='internal-select-coach-1',
        #                     #     options=[{'label': i, 'value': i} for i in internal_parameters],
        #                     #     value=internal_parameters[0],
        #                     #     multi=True
        #                     # ),

        #                     # html.H6('External Parameters'),
        #                     # dcc.Dropdown(
        #                     #     id='external-select-coach-1',
        #                     #     options=[{'label': i, 'value': i} for i in external_parameters],
        #                     #     value=external_parameters[0],
        #                     #     multi=True
        #                     # ),

        #                     # html.H6('Ball Parameters'),
        #                     # dcc.Dropdown(
        #                     #     id='ball-select-coach-1',
        #                     #     options=[{'label': i, 'value': i} for i in ball_parameters],
        #                     #     value=ball_parameters[0],
        #                     #     multi=True
        #                     # ),

        #                 ]
        #             )
        #         ]), width=3),
        
        #     dbc.Col(dbc.Card(
        #         [
        #             dbc.CardBody(
        #                 [
        #                     html.H3("Plots"),
        #                     dcc.Tabs(id='tabs', children=[
        #                             dcc.Tab(label='Player Analysis', children=[
        #                                 dcc.Tabs([
        #                                     dcc.Tab(label='Match Performance', children=[
        #                                         # dash_table.DataTable(
        #                                         #     id='datatable-coach',
        #                                         #     # columns=[
        #                                         #     #     {"name": i, "id": i, "selectable": True} for i in match_df.columns
        #                                         #     # ],
        #                                         #     # data=dummy_df.to_dict('records'),
        #                                         #     sort_action="native",
        #                                         #     sort_mode="multi",
        #                                         #     style_table={
        #                                         #         #'overflowX': 'auto',
        #                                         #         'minWidth': '100%',
        #                                         #         'height': '300px',
        #                                         #         'overflowY': 'auto'
        #                                         #     },
        #                                         #     page_action='none',
        #                                         #     selected_columns=[],
        #                                         #     selected_rows=[],
        #                                         #     row_selectable="multi",
        #                                         #     #fixed_columns={'headers': True, 'data':1},
        #                                         #     fixed_rows={'headers': True},
        #                                         #     # style_table={'minWidth': '100%'},
        #                                         #     column_selectable="multi",
        #                                         #     style_cell={
        #                                         #         'textAlign': 'center',
        #                                         #         'minWidth': '80px', 'width': '100px', 'maxWidth': '180px',
        #                                         #     },
        #                                         #     # style_cell_conditional=[
        #                                         #     #     {
        #                                         #     #         'if': {'column_id': c},
        #                                         #     #         'textAlign': ''
        #                                         #     #     } for c in ['Date', 'Region']
        #                                         #     # ],
        #                                         #     style_data_conditional=[
        #                                         #         {
        #                                         #             'if': {'row_index': 'odd'},
        #                                         #             'backgroundColor': 'rgb(248, 248, 248)'
        #                                         #         }
        #                                         #     ],
        #                                         #     style_header={
        #                                         #         'backgroundColor': 'rgb(230, 230, 230)',
        #                                         #         'fontWeight': 'bold'
        #                                         #     }
        #                                         # ),
        #                                         # html.Div(id='datatable-plot-coach'),

        #                                         html.H3("Correlation Analysis"),
        #                                         html.H6("Select one parameter"),
        #                                         dcc.Dropdown(
        #                                             id='player-metric-1-coach',
        #                                             options=[{'label': i, 'value':i} for i in available_metrics],
        #                                             value=available_metrics[0],
        #                                             clearable=False
        #                                         ),
        #                                         html.H6("Select another parameter"),
        #                                         dcc.Dropdown(
        #                                             id='player-metric-2-coach',
        #                                             options=[{'label': i, 'value':i} for i in available_metrics],
        #                                             value=available_metrics[1],
        #                                             clearable=False
        #                                         ),
        #                                         html.Div([
        #                                             dcc.Graph(
        #                                                 id='quadrant-plot-coach',
        #                                             )
        #                                         ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        #                                         html.Div([
        #                                             dcc.Graph(id='y-time-series'),
        #                                             dcc.Graph(id='x-time-series'),
        #                                         ], style={'display': 'inline-block', 'width': '49%'}),
                                                
        #                                     ]),# closes overview table tab
        #                                     dcc.Tab(label='Correlation Analysis', children=[
                                                
                                            
        #                                     ]), # closes charts tab
        #                                     dcc.Tab(label='In Depth Player', children=[

        #                                     ]), # closes in depth player analysis
        #                                 ])
        #                             ]), # closes player analysis tab
        #                             # compare team tabs for later analysis
        #                             # dcc.Tab(label='Compare Teams', children=[
        #                             #     dcc.Dropdown(
        #                             #         id='team-metric-select-coach'
        #                             #     ),
        #                             #     dcc.Graph(id='player-metric'),
        #                             # ]), # closes team-comparion tab
        #                             dcc.Tab(label='Tactical Analysis', children=[
        #                             # html.Div([
        #                             #     dcc.RangeSlider(
        #                             #         id='time-slider-pitch-left-coach',
        #                             #         min=0,
        #                             #         max=45,
        #                             #         step=None,
        #                             #         marks={
        #                             #             0: "0'",
        #                             #             5: "5'",
        #                             #             10:"10'",
        #                             #             15:"15'",
        #                             #             20:"20'",
        #                             #             25:"25'",
        #                             #             30:"30'",
        #                             #             35:"35'",
        #                             #             40:"40'",
        #                             #             45:"45'"
        #                             #         },
        #                             #         pushable=5,
        #                             #         value=[0,45],
        #                             #     ),
        #                             #     dcc.Dropdown(
        #                             #         id='player-select-left-pitch-coach',
        #                             #         #options=[{'label': i, 'value': i} for i in xy_players],
        #                             #         options=[{'label': i, 'value': i} for i in possible_match_players],
        #                             #         value=[possible_match_players[0]],
        #                             #         multi=True
        #                             #     ),
        #                             #     dcc.Graph(
        #                             #         id="football-pitch-left-coach"
        #                             #     ),
        #                             #     html.Div(
        #                             #         dash_table.DataTable(
        #                             #             id='datatable-left-pitch-coach',
        #                             #             style_data_conditional=[
        #                             #                 {
        #                             #                     'if': {'row_index': 'odd'},
        #                             #                     'backgroundColor': 'rgb(248, 248, 248)'
        #                             #                 }
        #                             #             ],
        #                             #             style_cell={'textAlign': 'center'},
        #                             #             style_header={
        #                             #                 'fontWeight': 'bold'
        #                             #             },
        #                             #         ), style={'margin-right': '50px'},
        #                             #     ),
        #                             # ], style={'display':'inline-block'}),

        #                             # html.Div([
        #                             #     dcc.RangeSlider(
        #                             #     id='time-slider-pitch-right-coach',
        #                             #     min=0,
        #                             #     max=45,
        #                             #     step=None,
        #                             #     marks={
        #                             #         0: "0'",
        #                             #         5: "5'",
        #                             #         10:"10'",
        #                             #         15:"15'",
        #                             #         20:"20'",
        #                             #         25:"25'",
        #                             #         30:"30'",
        #                             #         35:"35'",
        #                             #         40:"40'",
        #                             #         45:"45'"
        #                             #     },
        #                             #     pushable=5,
        #                             #     value=[0,45],
        #                             # ),
        #                             # dcc.Dropdown(
        #                             #         id='player-select-right-pitch-coach',
        #                             #         # options=[{'label': i, 'value': i} for i in xy_players],
        #                             #         # value=[xy_players[0]],
        #                             #         options=[{'label': i, 'value': i} for i in possible_match_players],
        #                             #         value=[possible_match_players[0]],
        #                             #         multi=True,
        #                             #     ),
        #                             # dcc.Graph(
        #                             #     id="football-pitch-right-coach"
        #                             # ),
        #                             # html.Div(
        #                             #     dash_table.DataTable(
        #                             #         id='datatable-right-pitch-coach',
        #                             #         style_data_conditional=[
        #                             #             {
        #                             #                 'if': {'row_index': 'odd'},
        #                             #                 'backgroundColor': 'rgb(248, 248, 248)'
        #                             #             }
        #                             #         ],
        #                             #         style_cell={'textAlign': 'center'},
        #                             #         style_header={
        #                             #                 'fontWeight': 'bold'
        #                             #         },
        #                             #     ),style={'margin-left': '50px'},
        #                             # ),

        #                             # ], style={'display':'inline-block'})

                                    
        #                         ]),
        #                         ]), # closes dcc.Tabs
        #                 ]
        #             ),
        #         ]), width=9),

        # ]),# closes row
        # ]) # closes Analysis Tab

    ]) # closes big Tabs Menu

])

## show and hide internal parameter selectoins ###
@app.callback(
    [Output('parameter-selection-coach', 'style'),
     Output('time-selection-dropdown', 'style')],
    [Input('analysis-tabs-coach', 'value')]
)
def update_sidebar(value):
    if value == 'player-coach':
        return {'display': 'none'}, {'display': 'block', 'padding-top': '10px'}
    else:
        return {'display': 'block'}, {'display': 'none'}



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


# Callback to update the player comparison plot quadrant plot
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

    max_x = filtered_df[x_axis_value].max() * 1.1
    max_y = filtered_df[y_axis_value].max() * 1.1

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
            height=500,
            transition = {'duration': 500},
    ))

    # make sure the axis have the correct range, for some reason they are off sometimes
    fig.update_xaxes(range=[-0.5, max_x])
    fig.update_yaxes(range=[-0.5, max_y])

    fig.add_shape(
        dict(
            type= 'line',
            x0= 0,#filtered_df[x_axis_value].min(),
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
            y0= 0,#filtered_df[y_axis_value].min(),
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

@app.callback(
    Output('y-time-series', 'figure'),
    [Input('player-metric-1-coach', 'value'), 
     Input('quadrant-plot-coach', 'hoverData')]
)
def update_y_times_series(y_axis_value, hoverData):
    # get player id from hoverData
    if hoverData is not None:
        # get playerId from hover
        player_id = str(hoverData['points'][0]['text'])
        # filter data
        df = db.all_match_data_per_player(player_id, y_axis_value)
    
    else:
        df = db.all_match_data_per_player('72288', y_axis_value)

    # get x values
    xs = list(range(len(df)))
    fig = go.Figure(go.Scatter(
        x = xs,
        y = df[y_axis_value],
        mode='lines+markers'
    ))

    fig.update_layout(
        title=y_axis_value,
        showlegend=False,
        template='seaborn',
        height=250,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=30,
            pad=4
        ),
    )

    return fig

@app.callback(
    Output('x-time-series', 'figure'),
    [Input('player-metric-2-coach', 'value'), 
     Input('quadrant-plot-coach', 'hoverData')]
)
def update_x_times_series(x_axis_value, hoverData):
    # get player id from hoverData
    if hoverData is not None:
        # get playerId from hover
        player_id = str(hoverData['points'][0]['text'])
        # filter data
        df = db.all_match_data_per_player(player_id, x_axis_value)
    
    else:
        df = db.all_match_data_per_player('72288', x_axis_value)

    # get x values
    xs = list(range(len(df)))
    fig = go.Figure(go.Scatter(
        x = xs,
        y = df[x_axis_value],
        mode='lines+markers'
    ))

    fig.update_layout(
        title=x_axis_value,
        showlegend=False,
        template='seaborn',
        height=250,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=30,
            pad=4
        ),
    )

    return fig


### callback to update table with game data ###
@app.callback(
    [Output('datatable-coach', 'columns'),
     Output('datatable-coach', 'data')],
    [Input('match-select-coach', 'value')]
)
def update_datatable(match):
    match_df = db.select_match_data(match)
    columns=[
        {"name": i, "id": i, "selectable": True} for i in match_df.columns.tolist()
    ]
    data=match_df.to_dict('records')
    return columns, data


# callback to update chart yielded from table selection
@app.callback(
    [Output('datatable-plot-bar', 'children'),
     Output('datatable-plot-trend', 'children')],
    [Input('match-select-coach', 'value'),
     Input('datatable-coach', 'derived_virtual_data'),
     Input('datatable-coach', 'derived_virtual_selected_rows'),
     Input('datatable-coach', 'selected_columns'),
     Input('datatable-coach', 'active_cell')]
)
def update_data_table(match, rows, derived_virtual_selected_rows, cols, active_cell):
    # when no rows are selected

    if derived_virtual_selected_rows and derived_virtual_selected_rows is not None and cols:

        # always append playerId columns so you can filter by it
        cols.append("playerId")
        
        # collect playerIds
        player_ids = []
        for i in derived_virtual_selected_rows:
            player_ids.append(rows[i]['playerId'])

        # select match data
        dff = db.select_match_data(match)

        # filter by selected columns
        dff = dff[cols]

        # append an average column
        dff.loc['Team Average'] = dff.mean()
        dff.at['Team Average', 'playerId'] = 'Team Average'

        # append "average" to player_ids
        player_ids.append('Team Average')

        # add color condition so there is distinction between metrics like average and player data
        avg_color = '#ff944d' # light orange
        normal_color = '#66b3ff' # light blue
        selected_color = '#0059b3'# darker blue

        # if active cell is in the list of players 
        if active_cell is not None:
            
            # get the corresponding player id
            selected_value = str(rows[active_cell['row']]['playerId'])
        else:
            selected_value = 'nothing'

        condlist = [dff['playerId']=='Team Average', dff['playerId']==selected_value, dff['playerId']!='Team Average']
        choicelist = [avg_color, selected_color, normal_color]
        dff['color'] = np.select(condlist, choicelist)

        # filter by selected players
        dff = dff[dff['playerId'].isin(player_ids)]

        # take out player Id out of cols so it is not plotted
        cols.remove('playerId')

        # create fig by having sorted displays of selected columns comparing players
        children_bar = []

        
        for column in cols:
            # filter by respective column
            plot_df = dff[['playerId', 'color', column]]

            # order in descending 
            plot_df.sort_values(by=column, ascending=False, inplace=True)

            chart_bar = dcc.Graph(
                id={
                    'type': 'column-table-select',
                    'index': column
                },
                figure={
                    "data": [
                        {
                            "x": plot_df['playerId'],
                            "y": plot_df[column],
                            "type": "bar",
                            "marker": {
                                "color": plot_df['color']
                            },
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True, "type": 'category'},
                        "yaxis": {
                            "automargin": True,
                            "title": {"text": column}
                        },
                        "height": 300,
                        "margin": {"t": 10, "l":10, "r": 10},
                    },
                },
            )

            # append chart to fig list
            children_bar.append(chart_bar)

        #### line chart ####

        ### get match data for the selected player_ids ###
        player_matches_df = db.match_data_list_players(player_ids)

        # add colors to data
        # condlist = [player_matches_df['playerId']=='Team Average', player_matches_df['playerId']==selected_value, player_matches_df['playerId']!='Team Average']
        # choicelist = [avg_color, selected_color, normal_color]
        # player_matches_df['color'] = np.select(condlist, choicelist)

        # sort by match_id
        player_matches_df.sort_values(by='matchId', inplace=True)
        # get list of player_ids
        players_and_mean = player_matches_df['playerId'].unique().tolist()
    
        children_line = []

        # per selected variable create one line chart over all games  
        for column in cols:
            plot_df = player_matches_df[['playerId', 'matchId', column]]
            
            # create a figure
            fig = go.Figure()

            # use traces to append trace per player
            for p in players_and_mean:
                line_df = plot_df[plot_df['playerId']==p]

                # get the correct color
                if p == 'Team Average':
                    color = avg_color
                elif p == selected_value:
                    color = selected_color
                else:
                    color = normal_color

                fig.add_trace(
                    go.Scatter(
                        x=line_df['matchId'],
                        y=line_df[column],
                        mode='lines+markers',
                        marker_color=color,
                        name=p
                    )
                )

                # add vertical line for the current selected match
                fig.add_shape(
                # Line Vertical
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=match,
                    y0=0,
                    x1=match,
                    y1=line_df[column].max(),
                    line=dict(
                        color="Black",
                        width=3,
                        dash="dot",
                    )
                ))

            
            # updata fig layout
            fig.update_layout(
                xaxis={
                    'automargin': True,
                    'type': 'category'
                },
                yaxis={
                    #'automargin': True,
                    'title': {'text': column}
                },
                height=300,
                width=700,
                margin={"t": 10, "l":10, "r": 5},
                hovermode='x unified',
                template='plotly_white',
                showlegend=False
            )
            
            # append as dcc.Graph element
            chart_line = dcc.Graph(
                id={
                    #'type': 'column-table-select',
                    'index': column
                },
                figure=fig
            )

            children_line.append(chart_line)
               

    else:
        children_bar = []  
        children_line = []



    return children_bar, children_line

### callback to be able to click on the match performance trend chart and select game
# @app.callback(
#     Output('match-select-coach', 'value'),
#     [Input('datatable-plot-trend', 'children')]
# )
# def update_match_selection(clickData):
#     print("Inside match selection update")
#     print(clickData)
#     if clickData is not None:
#         print(clickData)

#     return possible_team_matches[0]

### callback for left pitch ###
@app.callback(
    Output('football-pitch-left-coach', 'figure'),
    [Input('time-slider-pitch-left-coach', 'value'),
     Input('player-select-left-pitch-coach', 'value'),
     Input('football-pitch-left-coach', 'clickData'),
     Input('match-select-tactical-coach-left', 'value')]
)
def update_pitch_left_coach(time, players, clickData, matchId):
    fig = update_pitch_coach(time, players, clickData, matchId)
    return fig
    
# callback for left table underneath the pitch
@app.callback(
    [Output('datatable-left-pitch-coach', 'columns'),
     Output('datatable-left-pitch-coach', 'data')],
    [Input('football-pitch-left-coach', 'clickData'),
     Input('internal-select-coach', 'value'),
     Input('external-select-coach', 'value'),
     #Input('ball-select-coach', 'value'),
     Input('time-slider-pitch-left-coach', 'value'),
     Input('player-select-left-pitch-coach', 'value'),
     Input('match-select-tactical-coach-left', 'value')]
)
def update_left_pitch_table(clickData, internal_param, external_param, time, players, matchId):
    columns, data = update_pitch_table(clickData, internal_param, external_param, time, players, matchId)
    return columns, data

### callback for right pitch
@app.callback(
    Output('football-pitch-right-coach', 'figure'),
    [Input('time-slider-pitch-right-coach', 'value'),
     Input('player-select-right-pitch-coach', 'value'),
     Input('football-pitch-right-coach', 'clickData'),
     Input('match-select-tactical-coach-right', 'value')]
)
def update_pitch_right_coach(time, players, clickData, matchId):
    fig = update_pitch_coach(time, players, clickData, matchId)
    return fig


# callback for right table underneath the pitch
@app.callback(
    [Output('datatable-right-pitch-coach', 'columns'),
     Output('datatable-right-pitch-coach', 'data')],
    [Input('football-pitch-right-coach', 'clickData'),
     Input('internal-select-coach', 'value'),
     Input('external-select-coach', 'value'),
     #Input('ball-select-coach', 'value'),
     Input('time-slider-pitch-right-coach', 'value'),
     Input('player-select-right-pitch-coach', 'value'),
     Input('match-select-tactical-coach-right', 'value')]
)

def update_right_pitch_table(clickData, internal_param, external_param, time, players, matchId):
    columns, data = update_pitch_table(clickData, internal_param, external_param, time, players, matchId)
    return columns, data


########### ###################

###### functions to update the pitch and the datatable, only parameters as input are changing

############ ####################
def update_pitch_table(clickData, internal_param, external_param, time, players, matchId):
    # if only one is selected, put it in list format
    if isinstance(internal_param, str):
        internal = [internal_param]
    elif isinstance(internal_param, list) and not internal_param:
        internal = []
    else:
        internal = internal_param

    if isinstance(external_param, str):
        external = [external_param]
    elif isinstance(external_param, list) and not external_param:
        external = []
    else:
        external = external_param


    # get list to check types in database
    ima, intensity = ima_and_intensity(external)
    
    # put players, ima and intensity in correct format
    set_of_players = ["'" + m for m in players]
    set_of_players = [m + "'" for m in set_of_players]
    set_of_players_str = ','.join(set_of_players) 

    set_of_ima = ["'" + m for m in ima]
    set_of_ima = [m + "'" for m in set_of_ima]
    set_of_ima_str = ','.join(set_of_ima) 

    set_of_intensity = ["'" + m for m in intensity]
    set_of_intensity = [m + "'" for m in set_of_intensity]
    set_of_intensity_str = ','.join(set_of_intensity)

    # database call
    ima_event_df = db.combine_ima_events(matchId, set_of_players_str, time, set_of_ima_str, set_of_intensity_str)

    interval_df = db.combine_interval_events(matchId, set_of_players_str, time, internal)

    # merge the two dataframes by player id
    full_event_df = pd.merge(ima_event_df, interval_df, how='left', left_on='playerId', right_on='playerId')

    # get ball events
    time_df, pitch_size = db.combine_ball_event_data(matchId, set_of_players_str, time)
    ball_df = time_df.groupby(['playerId', 'Type']).size().reset_index()
    ball_df.columns = ['playerId', 'Type', 'count']
    ball_df = ball_df.pivot(index='playerId', columns='Type', values='count').reset_index()

    # add ball events to full table
    full_event_df = pd.merge(full_event_df, ball_df, how='left', left_on='playerId', right_on='playerId')

    # if the df has at least 2 entries add a sum row
    if len(full_event_df) > 1:
        # add the sum row
        full_event_df.loc['Sum'] = full_event_df.sum()
        full_event_df.loc['Sum', 'playerId'] = 'Sum' 

    # round the values
    full_event_df = full_event_df.round(2)
    # return the data as a dash data table
    columns=[
        {"name": i, "id": i, "selectable": True} for i in full_event_df.columns.tolist()
    ]
    data=full_event_df.to_dict('records')
    
    return columns, data


def ima_and_intensity(param):
    ima = []
    intensity = [] 
    for p in param:
        if 'Acc' in p:
            ima.append('ACC')
        if 'Dec' in p:
            ima.append('DEC')
        if 'Righ' in p:
            ima.append('RIGH_TURN')
        if 'Left' in p:
            ima.append('LEFT_TURN')

        if 'Low' in p:
            intensity.append('LOW')
        if 'Mid' in p:
            intensity.append('MID')
        if 'High' in p:
            intensity.append('HIGH')

    return ima, intensity


def update_pitch_coach(time, players, clickData, matchId):

    # get players in correct format to query from database
    set_of_players = ["'" + m for m in players]
    set_of_players = [m + "'" for m in set_of_players]
    set_of_players_str = ','.join(set_of_players)

    # time_df = xy_df[xy_df['minute'].between(begin, end)]
    time_df, pitch_size = db.combine_ball_event_data(matchId, set_of_players_str, time)
    # print(time_df)
    pitch_size = 'SIX'
    
    # get correct field size
    # 6 V 6 #
    #if max_x_position < 45 and max_y_position < 35:
    if pitch_size == "SIX":
        pitch_x = 42.5
        pitch_y = 30
        penalty_x = 7
        penalty_y = pitch_y
        mid_circle_radius = 4
    # 8 V 8 #
    #elif max_x_position < 70 and max_y_position < 50:
    elif pitch_size == "EIGTH":
        pitch_x = 64
        pitch_y = 42.5
        penalty_x = 12
        penalty_y = pitch_y
        mid_circle_radius = 6
    # 11 V 11 #
    else:
        pitch_x = 100
        pitch_y = 64
        penalty_x = 16
        penalty_y = 23
        mid_circle_radius = 10

    # create football pitch
    fig = go.Figure()

    # Set axes properties / This is a vertical football pitch
    fig.update_xaxes(range=[0, pitch_y], zeroline=False)
    fig.update_yaxes(range=[0, pitch_x])
    
    # add pitch outline
    fig.add_shape(
        # outline pitch
        type="rect",
        x0=0,
        y0=0,
        x1=pitch_y,
        y1=pitch_x,
        line=dict(
            color="black",
        ),
    )

    # add midline
    fig.add_shape(
        type='line',
        x0=0,
        y0=pitch_x/2,
        x1=pitch_y,
        y1=pitch_x/2
    )

    # add mid circle
    fig.add_shape(
        type='circle',
        xref="x",
        yref='y',
        x0=(pitch_y/2)-mid_circle_radius,
        y0=(pitch_x/2)-mid_circle_radius,
        x1=(pitch_y/2)+mid_circle_radius,
        y1=(pitch_x/2)+mid_circle_radius
    )

    # add bottom penalty area
    fig.add_shape(
        type='rect',
        x0=(pitch_y/2)-(penalty_y/2),
        y0=0,
        x1=(pitch_y/2)+(penalty_y/2),
        y1=penalty_x
    )

    fig.add_shape(
        type='rect',
        x0=(pitch_y/2)-(penalty_y/2),
        y0=pitch_x - penalty_x,
        x1=(pitch_y/2)+(penalty_y/2),
        y1=pitch_x
    )

    # add invisible boxes that allow the hovering
    n_boxes_x = 4
    n_boxes_y = 3
    box_size_x = pitch_x / n_boxes_x
    box_size_y = pitch_y / n_boxes_y
    zone_counter = 0
    # dictionaries to keep track of the box coordinates so data can be retrieved
    box_x_dict = {}
    box_y_dict = {}

    for i in range(n_boxes_x):
        #zone_i = i
        for j in range(n_boxes_y):
            zone_counter += 1
            x_data = [0 + i * box_size_x, 0 + i * box_size_x,
                        i * box_size_x + box_size_x, i * box_size_x + box_size_x,
                        0 + i * box_size_x]
            y_data = [0 + j * box_size_y, j * box_size_y + box_size_y,
                        j * box_size_y + box_size_y, 0 + j * box_size_y,
                        0 + j * box_size_y]
            fig.add_trace(
                go.Scatter(
                    x= y_data,
                    y= x_data,
                    fill='toself',
                    name="Zone" + str(zone_counter),
                    fillcolor='rgba(255,255,255,1)',
                    line=dict(color='rgba(224,224,224,.8)', width=2,
                              dash='dash'),
                    showlegend=False
                )
            )

            # add data to dictionary
            box_x_dict[zone_counter-1] = x_data
            box_y_dict[zone_counter-1] = y_data

    event_types = time_df['Type'].unique().tolist()
    # think about taking out touches
    for e in event_types:
        if e == 'pass':
            marker_color = 'blue'
        elif e == 'shot':
            marker_color = 'red'
        elif e == 'tackle':
            marker_color = 'yellow'
        elif e == 'touch':
            marker_color = 'black'
        else:
            marker_color = 'green'

        plot_df = time_df[time_df['Type'] == e]
        fig.add_trace(
            go.Scatter(
                x=plot_df['posY'],
                y=plot_df['posX'],
                name=e,
                mode='markers',
                marker=dict(
                    color=marker_color,
                    size=10,
                ),
                #text=plot_df['playerId'],
                #hovertemplate = "%{text}",
                hoverinfo='skip'
            )
        )
    
    # add arrows on hover
    if clickData is not None:
        # print(clickData)
        area = clickData['points'][0]['curveNumber']
        # print("AREA")
        # print(area)
        x_min = box_x_dict[area][1]
        x_max = box_x_dict[area][2]

        y_min = box_y_dict[area][0]
        y_max = box_y_dict[area][2]

        # filter data to get data for only that box
        pass_df = time_df[time_df['Type'] == 'pass']
        arrow_df = pass_df[pass_df['posX'].between(x_min, x_max)]
        arrow_df = arrow_df[arrow_df['posY'].between(y_min, y_max)]
        
        x_start_df = arrow_df['posX']
        y_start_df = arrow_df['posY']
        x_end_df = arrow_df['receivedPosX']
        y_end_df = arrow_df['receivedPosY']
        success = arrow_df['isSucceeded']

        ## different colors for successfull and not successfull pass ##
        arrow_color_dict = {
            "true": 'blue',
            "false": 'skyblue'
        }

        arrows = [
            dict(
               x = y_end,
               y = x_end,
               showarrow=True,
               axref='x', ayref='y',
               ax=y_start,
               ay=x_start,
               arrowhead=3,
               arrowwidth=1.5,
               arrowcolor=arrow_color_dict[s] 
            ) for x_end, y_end, x_start, y_start, s in zip(x_end_df, y_end_df, x_start_df, y_start_df, success)]
    else:
        arrows=[]

    fig.update_layout(
        #paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(x=0.25, y=1),
        legend_orientation="h",
        plot_bgcolor='rgba(0,0,0,0)',
        width=600, height=800,
        annotations=arrows,
        showlegend=True,
        margin=dict(
            l=50,
            r=50,
            b=50,
            t=50,
            pad=4
        ),
    )
    
    fig.update_yaxes(
        autorange="reversed",
        visible=False,
    )

    fig.update_xaxes(
        autorange="reversed",
        visible=False,
    )
    # add data
    return fig