import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from auth import success, login, login_fd, logout
from apps import home, club, player, coach
from dash.dependencies import Input, Output
from flask_login import logout_user, current_user
from server import app, server

print(dcc.__version__) # 0.6.0 or above is required

external_stylesheet = [dbc.themes.BOOTSTRAP]

#app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

#server = app.server
#app.config.suppress_callback_exceptions = True

#if __name__ == '__main__':
#    app.run_server(debug=True)

header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%'},
        children=[
            html.Img(
                src='assets/dash-logo-stripe.svg',
                className='logo'
            ),
            html.Div(className='links', children=[
                html.Div(id='user-name', className='link'),
                html.Div(id='logout', className='link')
            ])
        ]
    )
)

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container-width'),
        dcc.Location(id='url', refresh=False),
    ]
)

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if not current_user.is_authenticated:
        return login.layout
    
    if pathname == '/':
        return home.layout
    elif pathname == '/club':
        return club.layout
    elif pathname == '/player':
        return player.layout
    elif pathname == '/coach':
        return coach.layout
    elif pathname == '/login':
        return login.layout
    elif pathname == '/login':
        return login.layout
    #elif pathname == '/success':
    #    if current_user.is_authenticated:
    #        return success.layout
    #    else:
    #        return login_fd.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return '404'


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        return html.Div('Current user: ' + current_user.username)
        # 'User authenticated' return username in get_id()
    else:
        return '*'


@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated:
        return html.A('Logout', href='/logout')
    else:
        return ''


if __name__ == '__main__':
    app.run_server(debug=True)