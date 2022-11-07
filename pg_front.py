import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State
from dash import no_update
from flask_login import current_user
import time
import datetime
from datetime import datetime
from datetime import date
from datetime import timedelta

import STYLE_CONSTANTS as c

ac = {'text-align': 'center'}
event_header = "HOW IT WORKS: a calendar of economic events with an analysis of their impact - " + datetime.now().strftime('%b-%Y')

def layout():
    return dbc.Row(
        dbc.Col(
            [
                dbc.CardHeader(html.Div([dbc.Label("YIELD TABLE", size="md")], ), style=c.chart_style),
            ],
            width=12,
        )
    )