from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import CONSTANTS
import mongo

import STYLE_CONSTANTS as c

def layout():
    return html.Div([
    html.Div([dbc.NavLink('contact us',href='mailto:xxx')],style={'display': 'inline-block','padding-right':'0px','margin-right':'0px'}),
    html.Div([html.P(' enquire about access, functionality, features, suggest additions, or report bugs')],style={'display': 'inline-block','padding-left':'0px','margin-left':'0px'})
],style={'display': 'inline-block'})


full_email_layout = html.Div([
    html.H3('contact us: enquire about functionality, report bugs etc'),


        dbc.Label("your email"),
        dbc.Input(id="email-input", type="email", value=""),
        #dbc.FormText("We only accept gmail..."),
        #dbc.FormFeedback("That looks like a gmail address :-)", type="valid"),
        dbc.FormFeedback(
            "your email is not valid",
            type="invalid",
        ),
        dbc.Label("your message"),
        dbc.Input(id="message", type="text", value=""),
        c.br,

        dbc.Button(
            "send",
            id='send_button',
        ),
        dbc.FormFeedback(
            "",id='send_status'
            #type="valid",
        ),
])





