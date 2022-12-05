import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import mongo
from datetime import date
import datetime

label_width = '70%'
input_width = '25%'
input_width_halved = '12%'
opt_width = '8.33%'
desc_width = '1%'
br = html.Br()
hr = html.Hr(style={'clear':'both','margin-top':'5px','margin-bottom':'5px','float':'center'})
hr80 = html.Hr(style={'clear':'both','margin-top':'5px','margin-bottom':'5px','float':'center','width':'80%'})

var_desc_style = {"width": desc_width,'display': 'inline-block','padding-left':'10px','color':'#808080','font-size':'13px'}

#'float':'left'
label_style = {'width': label_width,'display': 'inline-block', 'text-align':'left','padding-right':'10px','height':'35px'}

label_style_RHS = {'width': label_width,'display': 'inline-block', 'text-align':'right','padding-right':'10px','height':'35px'}

inp_style = {"width": "25%",'float':'left','margin-right':'0px','height':'35px'} #,'margin-right':'10px'
dd_style = {"width": "25%",'height':'35px','display': 'inline-block'} #'display': 'inline-block','float':'left',
input_style = {"width": input_width,'display': 'inline-block','height':'35px'}

input_style_with_padding = {"width": "25%",'display': 'inline-block','float':'left','height':'35px','margin-bottom':'5px'}

dt_input_style = {"width": '12.5%','display': 'inline-block','height':'35px'}

optionlist = [
            {'label': 'Move in price of fixed size and time', 'value': 'MOVE'},
        ]

optionlist_full = optionlist

chart_style = {'width': '100%', 'display': 'inline-block','font-weight': 'bold','height':'35px','padding-bottom':'0.05rem','padding-top':'0.05rem'}
txt_style = {'width': '100%', 'display': 'inline-block','font-weight': 'bold','background-color':'#BEBEBE','border-style':'none','border-radius':'0px'}

link_to_event_library = dbc.NavItem(dbc.NavLink("view event database", active=True, href="/event_library",external_link=True),style={'width': '17.5%', 'display': 'inline-block','float':'left'})

link_to_result = dbc.NavItem(dbc.NavLink("download xls summary", id ='link-to-query-result', active=True, href='',external_link=True),style={'width': '17.5%', 'display': 'inline-block','float':'left'})

detailed_event_description = html.Div([dbc.Label(children="please choose event", id='detailed-event-desc',size="md")], style={'width': '52.5%', 'display': 'inline-block','font-weight': 'bold','text-align':'right','padding-right':'10px','float':'left'})

detailed_event_description_opt = html.Div([dbc.Label(children="detailed desc goes here", id='detailed-event-desc-opt',size="md")], style={'width': '52.5%', 'display': 'inline-block','font-weight': 'bold','text-align':'right','padding-right':'10px','float':'left'})

labl2style ={'width': label_width, 'display': 'inline-block','font-weight': 'bold','text-align':'right','padding-right':'10px','float':'left'}

event_selection_label = html.Div([dbc.Label("Event: ", size="md")], style={'width': label_width, 'display': 'inline-block','text-align':'right','padding-right':'10px'})
empty_box = html.Div([dbc.Label(" ", size="md")], style={'width': label_width, 'display': 'inline-block'})
event_selection_menu = html.Div(
    [dcc.Dropdown(id='EVENT_ID_state',options=optionlist_full,value='')],
        style={"width": input_width,'display': 'inline-block'}
)

event_selection_menu_opt_try = html.Div(
    dbc.FormFloating(
         [
            dcc.Dropdown(id='EVENT_ID_state_opt',options=[
                        {'label': 'Move in price of fixed size and time', 'value': 'MOVE'},
                        {'label': 'Parabolic price move', 'value': 'MOVE_PARABOLIC'},
                        {'label': 'Periodic High Low', 'value': 'PERIODIC_HIGH_LOW'},
                        {'label': 'Sigma', 'value': 'MOVE_INVARIANT_SIGMA'},
                        {'label': 'please choose event', 'value': ''},
                    ],
                      value=''),
             dbc.Label("event"),
         ],style={'height':'40px'}
     ),
        style={"width": input_width,'display': 'inline-block'}
)

event_selection_menu_opt = html.Div(
    [dcc.Dropdown(id='EVENT_ID_state_opt', options=[
        {'label': 'Move in price of fixed size and time', 'value': 'MOVE'},
        {'label': 'Parabolic price move', 'value': 'MOVE_PARABOLIC'},
        {'label': 'Periodic High Low', 'value': 'PERIODIC_HIGH_LOW'},
        {'label': 'Sigma', 'value': 'MOVE_INVARIANT_SIGMA'},
        {'label': 'please choose event', 'value': ''},
    ],
                  value='')],
    style={"width": input_width, 'display': 'inline-block'}
)

#mongo.all_available_tickers
ticker_options = []

for el in mongo.all_available_tickers:
    ticker_options.append({'label':el,'value':el})

#'display': 'inline-block',,'float':'left'
ticker_selection_label_style = {'width': label_width, 'text-align':'left','padding-right':'10px'}

ticker_selection_label = html.Div([dbc.Label("Ticker(s): ", size="md")], style=ticker_selection_label_style)
#ticker_selection_menu = dcc.Input(id='MASTER_TICKER_STR_state', type='text', value='QQQ', style={"width": input_width},)

ticker_selection_menu = html.Div([
    dcc.Dropdown(id='MASTER_TICKER_STR_state', options=ticker_options, value='QQQ',
                 )],
                 style={"width": input_width,'display': 'inline-block'})

ticker_selection_menu_opt = html.Div([dcc.Input(id='MASTER_TICKER_STR_state_opt', type='text', value='QQQ',style={"width": '100%'})],
                                     style={"width": input_width,'display': 'inline-block'})




ticker_tooltip = dbc.Tooltip(
    "instrument selection currently supports major US stocks and the top 100 cryptocurrencies.\n\n"
    "please let us know if the ticker you would like to analyse is not in our database",
    target="MASTER_TICKER_STR_state",
    placement='right',
    style={'width': input_width},
)

ticker_tooltip_opt = dbc.Tooltip(
    "instrument selection currently supports major US stocks and the top 100 cryptocurrencies.\n\n"
    "please let us know if the ticker you would like to analyse is not in our database",
    target="MASTER_TICKER_STR_state_opt",
    placement='right',
    style={'width': input_width},
)

show_inputs_tooltip = dbc.Tooltip(
    "click to show inputs specific to the chosen Event",
    target="submit-button-choose-event",
    placement='right',
    style={'width': input_width},
)

#show_inputs_tooltip_opt = dbc.Tooltip(
#    "click to show inputs specific to the chosen Event",
#    target="submit-button-choose-event_opt",
#    placement='right',
#    style={'width': input_width},
#)

go_tooltip = dbc.Tooltip(
    "click Go! to run query and wait a few seconds for it to calculate",
    target="submit-button-state-go-run-query",
    placement='right',
    style={'width': input_width},
)

go_tooltip_opt = dbc.Tooltip(
    "click Go! to run query and wait a few seconds for it to calculate",
    target="submit-button-state-go-run-opt",
    placement='right',
    style={'width': input_width},
)

ticker_input_explanation_label = html.Div([dbc.Label("type in any US ticker or crypto", size="md")],
                                          style={'width': desc_width, 'display': 'inline-block','margin-left':'10px','top': '25%'})
event_input_explanation_label = html.Div([dbc.Label("choose event from dropdown menu. learn more about events on link", size="md")],
                                         style={'width': desc_width, 'display': 'inline-block','margin-left':'10px','top': '50%'})

event_selection_tooltip = dbc.Tooltip("choose event from dropdown menu.\n" 
                                      "full list of event descriptions is available on the event_library page",
                                      target='EVENT_ID_state',
                                      placement='right',
                                      style={'width': input_width},
                                      )

event_selection_tooltip_opt = dbc.Tooltip("choose event from dropdown menu.\n" 
                                      "full list of event descriptions is available on the event_library page",
                                      target='EVENT_ID_state_opt',
                                      placement='right',
                                      style={'width': input_width},
                                      )

calendar_month_selection_menu = html.Div(
    [dcc.Dropdown(id='calendar_month',value=date(datetime.datetime.now().year,datetime.datetime.now().month,1),options=[
            {'label': 'Nov-2021', 'value': date(2021,11,1)},
            {'label': 'Dec-2021', 'value': date(2021,12,1)},
            {'label': 'Jan-2022', 'value': date(2022,1, 1)},
        ],)],
        style={"width": input_width,'display': 'inline-block'}
)

############################################################################
newsletter_subscribe_form = dbc.FormFloating(
    [
        dbc.Input(id='newsletter-signup-input',type="email", placeholder="example@internet.com"),
        dbc.Label("email"),
    ]
    )

subscribe_to_newsletter_button = dbc.Button("subscribe to our newsletter",
                   id="submit-newsletter-subscription",
                   n_clicks=0,
                   outline=True,
                   size='lg',
                   href='xxx@x',
                   color="dark",
                   className="d-grid gap-2 col-6 mx-auto",style={'width':'100%'},
                   #style={'width': input_width,'margin-bottom': '10px'},
)
