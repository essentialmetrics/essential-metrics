import dash
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title='Essential Metrics Dashboard', update_title='Loading page...')
server = app.server

app.config.suppress_callback_exceptions = True