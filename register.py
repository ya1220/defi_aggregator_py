import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State
from dash import no_update

from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
import time
from validate_email import validate_email

#from __init__ import app, User, engine
from config import engine
from app import app
from user import User

from auth import (
    add_user,
    user_exists,
    pwdb,
)


success_alert = dbc.Alert(
    'registered successfully. redirecting to login page',
    color='success',
    dismissable=True
)
failure_alert = dbc.Alert(
    'could not register - invalid inputs.',
    color='danger',
    dismissable=True
)

failure_alert_db = dbc.Alert(
    'could not register - database error',
    color='danger',
    dismissable=True
)


already_registered_alert = dbc.Alert(
    "you are already registered. taking you home.",
    color='success',
    dismissable=True
)

def layout():
    return dbc.Row(
        dbc.Col(
            [
                dcc.Location(id='register-url',refresh=True,),
                html.Div(id='register-trigger',style=dict(display='none')),
                html.Div(id='register-alert'),
                dbc.Container(
                    [
                        dbc.FormText('first name'),
                        dbc.Input(id='register-first',autoFocus=True),
                        html.Br(),

                        dbc.FormText('last name'),
                        dbc.Input(id='register-last'),
                        html.Br(),

                        dbc.FormText('email', id='register-email-formtext', color='secondary'),
                        dbc.Input(id='register-email'),
                        html.Br(),

                        dbc.FormText('password'),
                        dbc.Input(id='register-password',type='password'),
                        html.Br(),

                        dbc.FormText('confirm password'),
                        dbc.Input(id='register-confirm',type='password'),
                        html.Br(),

                        dbc.FormText('registration code'),
                        dbc.Input(id='register-code', type='text'),
                        #dbc.(id='contact us a registration code if you do not have one'),
    html.Div([dbc.NavLink('contact us for a registration code - registration is only by code for now',href='mailto:xxx')],style={'display': 'inline-block'}),
                        html.Br(),

                        dbc.Button('submit',color='primary',id='register-button'),
                    ]
                )
            ],
            width=6
        )
    )




@app.callback(
    [Output('register-'+x,'valid') for x in ['first','last','email','password','confirm']]+\
    [Output('register-'+x,'invalid') for x in ['first','last','email','password','confirm']]+\
    [Output('register-button','disabled'),
     Output('register-email-formtext','children'),
     Output('register-email-formtext','color')],
    [Input('register-'+x,'value') for x in ['first','last','email','password','confirm']]
)
def register_validate_inputs(first,last,email,password,confirm):
    '''validate all inputs'''

    #print("email before: ", email)
    email = email.lower()
    #print("email after: ", email)

    email_formtext = 'email'
    email_formcolor = 'secondary'
    disabled = True
    bad = [None,'']
    
    v = {k:f for k,f in zip(['first','last','email','password','confirm'],[first,last,email,password,confirm])}
    # if all the values are empty, leave everything blank and disable button
    if sum([x in bad for x in v.values()])==5:
        return [False for x in range(10)]+[disabled,email_formtext,email_formcolor]

    d = {}
    d['valid'] = {x:False for x in ['first','last','email','password','confirm']}
    d['invalid'] = {x:False for x in ['first','last','email','password','confirm']}

    def validate(x, inst):
        if x == 'password' and v[x] is not None:
            if len(v[x]) < 6:
                d['valid'][x], d['invalid'][x] = False,True
                return
        if v[x] in bad:
            pass
        elif not isinstance(v[x],inst):
            d['valid'][x], d['invalid'][x] = False,True
        else:
            d['valid'][x], d['invalid'][x] = True, False

    for k in ['first','last','password']:
        validate(k,str)

    x = 'confirm'
    if v[x] in bad:
        pass
    d['valid'][x] = not v[x]in bad and v['password']==v[x]
    d['invalid'][x] = not v['confirm']

    #print("bad: ", bad, type(bad))
    # if it's a valid email, check if it already exists
    # if it exists, invalidate it and let the user know
    x = 'email'
    if v[x] in bad:
        pass
    else: 
        d['valid'][x] = validate_email(v[x])
        d['invalid'][x] = not d['valid'][x]
    if user_exists(v[x],engine):
        d['valid'][x] = False
        d['invalid'][x] = True
        email_formcolor = 'danger'
        email_formtext = 'Email already exists.'
    
    # if all are valid, enable the button
    if sum(d['valid'].values())==5:
        disabled = False

    #if code != 'ANAGAMI68':
    #    d['invalid']['code'] = True
    #    print("code: ", code)
    #if code ==  or 'DJIHAD95':
    #print(d['valid'],d['invalid'])

    return [
        *list(d['valid'].values()),
        *list(d['invalid'].values()),
        disabled,
        email_formtext,
        email_formcolor
    ]





@app.callback(
    [Output('register-url', 'pathname'),
     Output('register-alert', 'children')],
    [Input('register-button', 'n_clicks')],
    [State('register-'+x, 'value') for x in ['first','last','email','password','confirm','code']],
)
def register_success(n_clicks,first,last,email,password,confirm,code):
    if n_clicks == 0:
        time.sleep(.25)
        if current_user.is_authenticated:
            return '/home',already_registered_alert
        else:
            return no_update,no_update

    #if len(password) < 6:
    #    return '/register', failure_alert

    if code == 'DJIHAD95' or code == '2THEMOON':
        if add_user(first,last,password,email.lower(),engine):
                return '/login',success_alert
        else:
            return '/register',failure_alert_db
    else:
        return '/register',failure_alert
