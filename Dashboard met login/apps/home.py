import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from apps import player, club, coach, commonmodules

from server import app


layout = html.Div([
    commonmodules.get_header(),
    # dbc.Row(dbc.Col(html.Div('Forward Football Dashboard'))),
    commonmodules.get_menu(),
    html.Br(),
    html.H3('This is home screen'),
])