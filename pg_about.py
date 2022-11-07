import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State
from dash import no_update
import random
from flask_login import current_user
import time
from functools import wraps

from STYLE_CONSTANTS import hr, br

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='about-url',refresh=True)
ac = {'text-align': 'center'}

def layout():
    return dbc.Row(
        dbc.Col(
        [
            location,
            html.Div(id='about-login-trigger'),
            html.H3('about fondue.finance', style=ac),br,

            html.Div([dbc.Label(
                'premise'
            )], style={'font-weight': 'bold', 'text-align': 'center'}), br,

            html.P('''find some yield''',style=ac),

            html.Div([dbc.Label(
                'history and founding team:'
            )], style={'font-weight': 'bold','text-align': 'center'}), br,
            html.P('''xxx''', style={'text-align': 'center'}),
            html.Div([dbc.NavLink('Founding team',href='https://www.linkedin.com/in/iaroslavafonin/',external_link=True)],style={'text-align': 'center'}),
            br,

            html.Div([dbc.Label('functionality: yield optimisation')], style={'font-weight': 'bold','text-align': 'center'}),br,
            html.P('''''', style={'text-align': 'center'}),

        ],
        width=14
        )

        )



a = html.Div([dbc.Label(
    'answering questions'
)], style={'font-weight': 'bold', 'text-align': 'center'})


print("pg_about.py")