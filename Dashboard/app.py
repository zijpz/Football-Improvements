import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

print(dcc.__version__) # 0.6.0 or above is required

external_stylesheet = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheet)

server = app.server
app.config.suppress_callback_exceptions = True

#if __name__ == '__main__':
#    app.run_server(debug=True)
