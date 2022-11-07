import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State
from dash import no_update

from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
import time

import STYLE_CONSTANTS

from app import app
from user import User

success_alert = dbc.Alert(
    'logged in successfully. taking you home!',
    color='success',
    dismissable=True
)
failure_alert = dbc.Alert(
    'login unsuccessful. please try again.',
    color='danger',
    dismissable=True
)
already_login_alert = dbc.Alert(
    'you are already logged in. taking you home!',
    color='warning',
    dismissable=True
)


def layout():
    return dbc.Row(
        dbc.Col(
            [
                dcc.Location(id='login-url',refresh=True,pathname='/login'),
                html.Div(id='login-trigger',style=dict(display='none')),
                html.Div(id='login-alert'),
                dbc.Container(
                    [
                        #dbc.Alert('Try test@test.com / test', color='info',dismissable=True),
                        #html.Br(),

                        dbc.FormText('Email'),
                        STYLE_CONSTANTS.empty_box, dbc.Input(id='login-email',autoFocus=True,
                                                             style={
                                                                 'border-top-left-radius': '0px',
                                                                 'border-top-right-radius': '0px',
                                                                 'border-bottom-right-radius': '0px',
                                                                 'border-bottom-left-radius': '0px',
                                                             }

                                                             ),


                        html.Br(),
                        dbc.FormText('Password'),
                        html.Div(dbc.Input(id='login-password',type='password',debounce=True), style={'float':'center',
                                  'border-top-left-radius': '0px',
                                'border-top-right-radius': '0px',
                                'border-bottom-right-radius': '0px',
                                    'border-bottom-left-radius': '0px',
                                                                                                      }),
                        #dbc.Input(id='login-password',type='password',debounce=True),

                        html.Br(),
                        dbc.Button('Submit',color='primary',id='login-button',
                                   style={
                                       'border-top-left-radius': '0px',
                                       'border-top-right-radius': '0px',
                                       'border-bottom-right-radius': '0px',
                                       'border-bottom-left-radius': '0px',
                                   }
                                   ),
                        #dbc.FormText(id='output-state')

                        html.Br(),
                        html.Br(),
                        dcc.Link('Register',href='/register'),
                        html.Br(),
                        dcc.Link('Forgot Password',href='/forgot')
                    ]
                )
            ],
            width=6
        )
    )

@app.callback(
    [Output('login-url', 'pathname'),
     Output('login-alert', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('login-password', 'value')],
    [State('login-email', 'value')]
)
def login_success(n_clicks, password, email):
    '''logs in the user'''

    if password is not None or n_clicks > 0:
        user = User.query.filter_by(email=email).first()
        if not user: email = email.lower()
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user)

                return '/home',success_alert
            else:
                return no_update,failure_alert
        else:
            return no_update,failure_alert
    else:
        return no_update,''