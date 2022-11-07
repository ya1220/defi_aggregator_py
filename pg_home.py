import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State
from dash import no_update
from flask_login import current_user
import time
import STYLE_CONSTANTS as c
import CONSTANTS
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import master_yield_class
import mongo

home_login_alert = dbc.Alert(
    'not logged in - please log in.', #User not logged in. Taking you to login.
    color='danger'
)


#######
table_header = [html.Thead(html.Tr([html.Th("  "), html.Th("   ")]))]
lhs_style = {'width':'25%','display': 'inline-block','align':'left'}
st = {'width': '70%','display': 'inline-block','padding': '5px 0','margin-left': '10px','text-align': 'left'} # 'text-align': '',
b1 = html.Div([dbc.Button('analyse event impact', outline=True,size='lg',href='/query',external_link=True,color="dark",className="d-grid gap-2 col-6 mx-auto",style={'width':'100%'})],style=lhs_style)
d1 = html.Div([html.P('learn how events such as DeFi security incidents, Fed meetings, or N-sigma moves affect security prices')],style=st)

########
addbutton = dbc.Button("add asset",
                   id="add-asset-button",
                   n_clicks=0,
                   disabled=False,
                   style={'width': c.input_width_halved,'margin-bottom': '10px','margin-right': '2px','display': 'inline-block',
                           'border-top-left-radius':'0px',
                           'border-top-right-radius': '0px',
                           'border-bottom-right-radius': '0px',
                           'border-bottom-left-radius': '0px',
                          },
                    )

delbutton = dbc.Button("delete asset",
                   id="delete-asset-button",
                   n_clicks=0,
                   disabled=False,
                   style={'width': c.input_width_halved,'margin-bottom': '10px','margin-right': '2px',
                                    'border-top-left-radius':'0px',
                                    'border-top-right-radius': '0px',
                                    'border-bottom-right-radius': '0px',
                                    'border-bottom-left-radius': '0px',
                          },
                    )

buttonz = html.Div([c.empty_box,addbutton,delbutton],)

optimise_go_button = dbc.Button("Go!",
                   id="submit-button-state-optimise",
                   n_clicks=0,
                   disabled=False,
                   style={'width': c.input_width,'margin-bottom': '10px','display': 'inline-block',
                        'border-top-left-radius':'0px',
                        'border-top-right-radius':'0px',
                        'border-bottom-right-radius':'0px',
                        'border-bottom-left-radius':'0px',
                          },
                    )

inplabl = html.Div([dbc.Label('ticker:', size="md")], style=c.label_style_RHS)
inpamt = html.Div([dbc.Label('amount:', size="md")], style=c.label_style_RHS)
inpstyle = html.Div([dbc.Label('optimise for:', size="md")], style=c.label_style_RHS)
inprebal_dates = html.Div([dbc.Label('holding period:', size="md")], style=c.label_style_RHS)

ticker_dd = mongo.TICKER_DD
fitness_dd = CONSTANTS.FITNESS_DD

inpval_ticker = html.Div([dcc.Dropdown(id='inp-ticker', value=CONSTANTS.tkr_BTC,
                           options=ticker_dd,
                           style = {'width': '100%'}
                           )],style=c.dd_style
                )

inpval_number = html.Div([dcc.Input(id='inp-value', type='number', value=10.0, placeholder=10.0,
                             min=0,
                             max=10000000.0,
                             step=0.0001,
                             style={'width': '100%'}
                             )],
                  style=c.input_style,
                  )

inpval_holding_period = html.Div([dcc.Input(id='inp-value-rebalancing-days', type='number', value=30.0, placeholder=30.0,
                             min=0.0,
                             max=365.0,
                             step=1.0,
                             style={'width': '100%'}
                             )],
                  style=c.input_style,
                  )

inpval_fitness = html.Div(
    [    dcc.Dropdown(id='inp-fitness', value='stablecoins',
                           options=fitness_dd,
                           style = {'width':'100%'} #'margin-bottom': '10px','display': 'inline-block','float':'left'
                           )],
    style={"width": c.input_width,'height':'35px','display': 'inline-block'}
)


buttonz2 = html.Div([inpstyle,inpval_fitness],)
buttonz25 = html.Div([inprebal_dates,inpval_holding_period],)
buttonz3 = html.Div([c.empty_box,optimise_go_button],)

layout_menu = html.Div([
    #b1,d1,c.br,

    html.Div([
        dbc.CardHeader(html.Div([dbc.Label("YIELD TABLE", size="md")],), style=c.chart_style),

        dbc.CardBody(
            [dcc.Graph(id='yield-table',
                       figure=master_yield_class.global_yield_and_pf_objects[0].get_pools_data_fig()
                       ,style={'height': '200px'})],
        ),

        dbc.CardHeader(html.Div([dbc.Label("OPTIMISER", size="md")], ), style=c.chart_style),
        inplabl, inpval_ticker,
        inpamt, inpval_number,


        buttonz,
        #addbutton, delbutton, c.br,

        dbc.CardBody([dcc.Graph(id='table-own-portfolio',
                                figure=master_yield_class.global_yield_and_pf_objects[0].get_starting_portfolio_fig(),
                                style={'width': '100%','height': '150px'}
                                )]),
        #c.br,
        buttonz2,c.br,
        inprebal_dates, inpval_holding_period,c.br,
        #buttonz25,c.br,
        buttonz3,c.br,
        #inpval_fitness, optimise_go_button, c.br,
        dbc.CardBody([dcc.Graph(id='table-optimised-portfolio',
                                figure=master_yield_class.global_yield_and_pf_objects[0].get_optimised_portfolio_fig(),
                                style={'width': '100%','height': '200px'},
                                )],
                     ),

    ]),

])

#print('pg home.py')

def layout():
    return layout_menu