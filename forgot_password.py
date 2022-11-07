import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State
from dash import no_update

from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
import time
from sqlalchemy.sql import select

from config import engine
from app import app
from user import User


from auth import (
    send_password_key,
    user_table,
)

success_alert = dbc.Alert(
    'Reset successful. Taking you to change password.',
    color='success',
)
failure_alert = dbc.Alert(
    'Reset unsuccessful. Are you sure that email was correct?',
    color='danger',
)
already_login_alert = dbc.Alert(
    'User already logged in. Taking you to your profile.',
    color='warning'
)

def layout():
    return dbc.Row(
        dbc.Col(
            [
                html.H3('Forgot Password'),
                dcc.Location(id='forgot-url',refresh=True),
                dbc.Container(
                    [
                        html.Div(id='forgot-alert'),
                        html.Div(id='forgot-trigger',style=dict(display='none')),
                        html.Br(),

                        dbc.Input(id='forgot-email',autoFocus=True),
                        dbc.FormText('Email'),
                        html.Br(),

                        dbc.Button('Submit email to receive code',id='forgot-button',color='primary'),

                    ]
                )
            ],
            width=6
        )
    )



@app.callback(
    [Output('forgot-alert','children'),
     Output('forgot-url','pathname')],
    [Input('forgot-button','n_clicks')],
    [State('forgot-email','value')]
)
def forgot_submit(submit,email):
    # get first name
    #email lowercase
    table = user_table()
    statement = select([table.c.first]).\
                where(table.c.email==email)
    conn = engine.connect()
    resp = list(conn.execute(statement))
    #print("len of resp: ", len(resp))

    if len(resp)==0:
        return failure_alert, no_update    
    else:
        firstname = resp[0].first
    conn.close()

    #print("connection closed")
    #sent_reset_code_or_no = send_password_key(email, firstname, engine)
    #print(sent_reset_code_or_no,type(sent_reset_code_or_no))

    # if it does, send password reset and save info
    if send_password_key(email, firstname, engine):
        #print("success in sending reset")
        return success_alert, '/change'
    else:
        #print("sending reset code failed")
        return failure_alert, no_update