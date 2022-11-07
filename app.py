import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output

## Diskcache
import diskcache
import CONSTANTS as c

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

#<link rel="preconnect" href="https://fonts.googleapis.com">
#<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
#<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap" rel="stylesheet">

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inconsolata:wght@300&family=Spartan:wght@300;400&display=swap'
        #'https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap',
        #'https://fonts.googleapis.com/css2?family=Spartan:wght@300;400&display=swap'
                          ],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions = True,
    long_callback_manager=long_callback_manager,
)

app.css.config.serve_locally = True

server = app.server
app._favicon = ("favicon.ico")
app.title = c.WEBSITE_NAME