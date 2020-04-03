import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def get_header():
    header = html.Div([

        html.Div([
            html.H1(
                'Forward Football Dashboard')
        ], className="twelve columns padded"),       

    ])
    return header
# ,className="row gs-header gs-text-header")

def get_menu():
    menu = html.Div([

        dcc.Link('Home   ', href='/', className="p-2 text-dark"),
        dcc.Link('Club   ', href='/club', className="p-2 text-dark"),
        dcc.Link('Coach   ', href='/coach', className="p-2 text-dark"),
        dcc.Link('Player   ', href='/player', className="p-2 text-dark"),
        #dcc.Link('Management    ', href='/management', className="p-2 text-dark"),

    ], className="d-flex flex-column flex-md-row align-items-center p-3 px-md-4 mb-3 bg-white border-bottom shadow-sm") 
    return menu    

# 