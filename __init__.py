import dash
import dash_bootstrap_components as dbc
import os
from flask_login import LoginManager, UserMixin
import random
from auth import pwdb, User as base
from config import config, engine
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash
from app import app
from app import server
import warnings
import configparser
import os
import flask
import dash_auth
import shutil
import pandas as pd
import plotly.express as px
from flask import redirect, url_for
import sqlite3
from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
import login,register,forgot_password,change_password
from werkzeug.security import generate_password_hash, check_password_hash
import pg_home,profile, pg_about,pg_front,pg_contact
import master_yield_class
import STYLE_CONSTANTS as c
from user import User
import smtplib, ssl
import CONSTANTS
import db
from pathlib import Path
import time
import datetime
from datetime import timedelta
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

format_str = CONSTANTS.date_str   # The format

print('pg init py')

# config
server.config.update(
    SECRET_KEY='make this key random or hard to guess',
    SQLALCHEMY_DATABASE_URI=config.get('database', 'con'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

pwdb.init_app(server)

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


###USER WAS HERE
app.validation_layout = html.Div([
    pg_home.layout(),
    profile.layout(),
    pg_about.layout(),
    pg_front.layout(),
])

computing = [False]

# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

header = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("fondue.finance", href="/"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink('user-name',id='user-name',href='/profile',external_link=True)),
                    dbc.NavItem(dbc.NavLink('login', id='user-action', href='Login')),
                    dbc.NavItem(dbc.NavLink('home', id='user-action2')),
                    dbc.NavItem(dbc.NavLink("about", href="/about",external_link=True)),
                    dbc.NavItem(dbc.NavLink("contact us", href="/contact", external_link=True)),
                ]
            )
        ],style={'color':'dark',}
    ),
    style={'margin-bottom':'10px'}
)

app.layout = html.Div(
    [
        header,
        html.Div(
            [
                dbc.Container(
                    id='page-content'
                )
            ]
        ),
        dcc.Location(id='base-url', refresh=True)
    ],
    #style={'font-family': 'Roboto, sans-serif'}
    style = {'font-family': CONSTANTS.font_style}
)


@app.callback(
    Output('page-content', 'children'),
    [Input('base-url', 'pathname')])
def router(pathname):
    if pathname == '/':
        return login.layout()
    elif pathname == '/login':
        if not current_user.is_authenticated:
            return login.layout()
    elif pathname == '/register':
        if not current_user.is_authenticated:
            return register.layout()
    elif pathname == '/change':
        if not current_user.is_authenticated:
            return change_password.layout()
    elif pathname == '/forgot':
        if not current_user.is_authenticated:
            return forgot_password.layout()
    elif pathname == '/logout':
        if current_user.is_authenticated: logout_user()
    elif pathname == '/profile':
        if current_user.is_authenticated: return profile.layout()
    elif pathname == '/home':
        if current_user.is_authenticated: return pg_home.layout()
    elif pathname == '/about':
        return pg_about.layout()
    elif pathname == '/contact':
        return pg_contact.layout()
    # DEFAULT LOGGED IN: /home
    if current_user.is_authenticated:
        return pg_home.layout()
    # DEFAULT NOT LOGGED IN: /login
    return login.layout()


@app.callback(
    [Output('user-name', 'children'),
     Output('user-name', 'href')
     ],
    [Input('page-content', 'children')])
def profile_link(content):
    if current_user.is_authenticated:
        return current_user.first,'/profile'
    else:
        return '',''


@app.callback(
    [Output('user-action', 'children'),
     Output('user-action', 'href'),

     Output('user-action2', 'children'),
     Output('user-action2', 'href')

     ],
    [Input('page-content', 'children')])
def user_logout(input1):
    '''returns a navbar link to /logout or /login, respectively, if the user is authenticated or not'''
    if current_user.is_authenticated:
        return 'logout', '/logout', 'home','/home'
    else:
        return 'login', '/login', 'home','/'

#######################
@app.callback(
    Output('table-own-portfolio', 'figure'),

    [Input('add-asset-button', 'n_clicks'),
     Input('delete-asset-button', 'n_clicks'),],
    [
        State('inp-ticker', 'value'),
        State("inp-value", "value"),
     ],
    prevent_initial_call=True
             )
def add_asset_to_pf(add_clicks,remove_clicks,ticker,value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(triggered_id)
    if triggered_id == 'add-asset-button':
        print("in callback - adding value: ", add_clicks, ticker,value)
        master_yield_class.global_yield_and_pf_objects[0].add_asset_to_pf(ticker,value)
    if triggered_id == 'delete-asset-button':
        print("in callback - DELETING value: ", remove_clicks, ticker,value)
        master_yield_class.global_yield_and_pf_objects[0].delete_asset_from_pf(ticker)

    return master_yield_class.global_yield_and_pf_objects[0].get_starting_portfolio_fig()

#OPTIMISATION
@app.callback(
    Output('table-optimised-portfolio', 'figure'),
    Input('submit-button-state-optimise', 'n_clicks'),
    State("inp-value-rebalancing-days", "value"),
    State('inp-fitness', 'value'),
             )
def optimise_portfolio(n_clicks,rebalancing_days,fitness_to_use): #,children
    print("311 - in opt callback",n_clicks,rebalancing_days, fitness_to_use)
    master_yield_class.global_yield_and_pf_objects[0].rebalance_frequency = rebalancing_days
    master_yield_class.global_yield_and_pf_objects[0].fitness_to_use = fitness_to_use
    return master_yield_class.global_yield_and_pf_objects[0].get_optimised_portfolio_fig()


#LOGIN FORMS
@app.callback(
    Output('url_logout', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/register'

@app.callback(
    [Output('container-button-basic', "children"),
     ],
    [Input('submit-val', 'n_clicks')],
    [
        State('email_username', 'value'),
        State('password', 'value'),
        State('registration_code', 'value')
    ]
)
def insert_users(n_clicks, email_username, pw, registration_code):
    hashed_password = ''
    if pw is not None: hashed_password = generate_password_hash(pw, method='sha256')
    if email_username is not None and pw is not None and registration_code == 'XXX': #is not None:
        ins = users.Users_tbl.insert().values(username=email_username, password=hashed_password)
        conn = users.engine.connect()
        conn.execute(ins)
        conn.close()
        return [html.Div([html.H2('registration successful!'),login])] #redirect(url_for('/'))
    else:
        if email_username is not None:
            if '@' not in email_username:
                return [html.Div([html.H2('error: invalid username')])]
        if pw is not None:
            if len(pw) <6:
                return [html.Div([html.H2('error: password too short')])]
        errors = False
        if errors == False: return [html.Div([html.H2('')])]

@app.callback(
    Output('url_login', 'pathname')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def successful(n_clicks, input1, input2):
    user = users.Users.query.filter_by(username=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            return '/home'
        else:
            pass
    else:
        pass

@app.callback(
    Output('output-state', 'children')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = users.Users.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                return ''
            else:
                return 'incorrect username or password'
        else:
            return 'incorrect username or password'
    else:
        return ''

@app.callback(
    Output('url_login_success', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0: return '/register'

@app.callback(
    Output('url_login_df', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0: return '/register'



@app.callback(
    [Output("email-input", "valid"), Output("email-input", "invalid")],
    [Input("email-input", "value")],
)
def check_validity(text):
    if text:
        is_email = ('@' in text)
        return is_email, not is_email
    return False, False


@app.callback(
    Output('send_status', 'children'),
    Input('send_button', 'n_clicks'),
    Input('email-input', 'value'),
    Input('message', 'value'),
             )
def update_send_status(n_clicks,sender_email,form_msg):
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)

    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(sender_email, CONSTANTS.password)
    rcv = CONSTANTS.EMAIL

    TEXT = '<html><body>' + form_msg + '</body></html>'
    msg = MIMEText(TEXT, 'html')
    msg['To'] = rcv
    msg['From'] = sender_email
    msg['Subject'] = 'EMAIL THROUGH ' + CONSTANTS.WEBSITE_NAME + 'WEBSITE'

    smtp_server.sendmail('anagamicapital@gmail.com', 'anagamicapital@gmail.com', msg.as_string())
    if n_clicks:
        if n_clicks > 0:
            return 'sent successfully'
        else:
            return ''
    else:
        return ''


###################################################
if __name__ == '__main__':
    app.run_server(debug=True,port=5000)