import numpy as np
import requests
import json
import pandas as pd
import time
import sys
from tzlocal import get_localzone
import threading
import csv
from pathlib import Path
from email.mime.text import MIMEText
import pytz
import datetime
from polygon import RESTClient
import dateutil.relativedelta

import db
import mongo
import quandl
import smtplib, ssl
from email.mime.text import MIMEText
import CONSTANTS as c

rescan_periodicity_minutes = 60
rescan_alerts_periodicity_minutes = 60
last_day_from_alphavantage_only = True
rescan_stocks_or_no = False
rescan_crypto_or_no = True
alphavantage_rescan_during_trading_hours = True
check_alerts_after_rescan = True
polygon_minutes_intraday = 30
polygon_default_res = 'minute'

cryptocompare_API_key = c.cryptocompare_API_key
#polygon_API_key = c.polygon_API_key
starttime = time.time()

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    print("utc now: ", datetime.datetime.utcnow().time())
    check_time = check_time or datetime.datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def download_full_crypto_data(ticker):
    newest_timestamp_available = mongo.retrieve_newest_date(ticker)
    download_data_from_cryptocompare_cycled(ticker, newest_timestamp_available, datetime.datetime.now(), 'hourly',None, None)
    return

def download_data_from_cryptocompare_cycled(ticker, oldest,newest,data_resolution,proof = None,asset_launch = None,fullname=None):
    oldest_date_received = datetime.datetime.now().timestamp()

    if newest == None or type(newest) is None or type(newest) is not datetime.datetime:
        oldest_date_received = datetime.datetime.now().timestamp()
    else:
        oldest_date_received = newest.timestamp()

    start_date = (datetime.date.today() - dateutil.relativedelta.relativedelta(months=72))
    start_date_t = datetime.datetime.combine(start_date, datetime.datetime.min.time()).timestamp()

    if oldest > datetime.datetime.min:
        if type(oldest) is datetime.datetime:
            start_date_t = oldest.timestamp()
    first_cycle = 0
    local_tz = get_localzone()

    print("Cryptocompare load start date t: ", start_date_t, " until: ", oldest_date_received , " for: ", ticker, " oldest in db: ",datetime.datetime.utcfromtimestamp(oldest_date_received))

    dt_nonzero = []
    px_nonzero = []

    while oldest_date_received > start_date_t:
        data = download_hist_data_from_cryptocompare(ticker, data_resolution, oldest_date_received)
        if data.empty: break
        oldest_date_received = min(data['time']).timestamp()
        dt = data['time']
        px = data['close']

        tz = list(filter(lambda s: s[1] > 0.0, zip(dt,px)))
        dt_nonzero_temp, px_nonzero_temp = zip(*tz)
        dt_nonzero_temp = list(dt_nonzero_temp)
        px_nonzero_temp = list(px_nonzero_temp)
        dt_nonzero.extend(dt_nonzero_temp)
        px_nonzero.extend(px_nonzero_temp)

        print("     Cryptocompare downloaded data: ", min(dt_nonzero_temp), " ", max(dt_nonzero_temp))
        if len(dt_nonzero_temp) != len(dt) and len(px_nonzero_temp) != len(px): break #return

        if first_cycle == 0:
            mongo.update_record_with_single_attribute(ticker, db.db_data_source_key, "cryptocompare")
            mongo.update_record_with_single_attribute(ticker, db.db_asset_class_record_key, "cryptocurrency")
            if type(proof) is str:
                mongo.update_record_with_single_attribute(ticker, db.db_proof_record_key, proof)
            if type(fullname) is str:
                mongo.update_record_with_single_attribute(ticker, 'name', fullname)
            format_str = '%Y-%m-%d'  # The format

            if type(asset_launch) is str:
                try:
                    date_of_launch = datetime.datetime.strptime(asset_launch, format_str)
                except:
                    try:
                        date_of_launch = datetime.datetime.strptime(asset_launch, '%d-%m-%Y')
                    except:
                        date_of_launch = datetime.datetime.strptime(asset_launch, '%d/%m/%Y')
                mongo.update_record_with_single_attribute(ticker, db.db_coin_launched_record_key, date_of_launch)
            first_cycle += 1

    #sort by date
    print("len dt nonzero: ", len(dt_nonzero), " len px nonzero: " , len(px_nonzero))
    if len(dt_nonzero) == 0: return
    res = zip(dt_nonzero,px_nonzero)
    res = sorted(res, key=lambda x: x[0])
    dt_nonzero, px_nonzero = zip(*res)
    dt_nonzero = list(dt_nonzero)
    px_nonzero = list(px_nonzero)
    #print(min(dt_nonzero))
    #print(max(dt_nonzero))
    if type(dt_nonzero) == tuple: sys.exit("xx")
    print("     Cryptocompare adding to MONGO: ", min(dt_nonzero), " ", max(dt_nonzero))
    mongo.update_record_with_series_attribute(ticker, dt_nonzero, db.db_price_record_key, px_nonzero)

    return



def read_stock_data_from_csv(ticker):
    converters_ = {
        "Date": lambda value: datetime.strptime(value, "%Y-%m-%d").date(),
        "Time": lambda value: datetime.strptime(value, "%H:%M").time()
    }

    file = "C:/Users/User/Downloads/" + ticker + ".csv"
    data = pd.read_csv(file, sep=',', header = 0, converters=converters_)

    dates = []

    if type(data["Date"][0]) != datetime:
        dates = [datetime(dt.year, dt.month, dt.day) for dt in data["Date"]]
    else:
        dates = data["Date"]

    px = data[db.price_key]

    d = pd.DataFrame({
        'Date': dates,
        db.price_key: px
        }
    )

    d['Date'] = [datetime(dt.year, dt.month, dt.day) for dt in dates] #d.info()
    #dd = data[["Date",db.price_key]]    #dd.info()
    return d


def download_hist_data_from_coinapi(crypto_ticker,data_resolution,next_page_or_no,timestamp_to_pull_until):
    coinapi_key = "8FA2F62D-4323-4163-8FCF-4039BA7D2667"
    url = 'https://rest.coinapi.io/v1/ohlcv/'+ crypto_ticker + '/USD/history?period_id=1MIN&time_start=2016-01-01T00:00:00'
    headers = {'X-CoinAPI-Key' : coinapi_key}
    response = requests.get(url, headers=headers)
    datadict = json.loads(response.text)
    df = pd.DataFrame(datadict)
    return df


def download_top_coin_list_from_cryptocompare(number_of_coins):
    if number_of_coins < 10:
        numstr = str(10)
    else:
        numstr = str(number_of_coins)

    query_str = "https://min-api.cryptocompare.com/data/top/mktcapfull?limit="+numstr+"&tsym=USD"
    #query_str = "https://min-api.cryptocompare.com/data/top/mktcapfull?limit=10&tsym=USD"
    cryptocompare_REST_query = query_str + "&api_key=" + cryptocompare_API_key
    response = requests.get(cryptocompare_REST_query)
    datadict = json.loads(response.text)
    df = pd.DataFrame(datadict['Data'])
    print("TOP COIN LIST DATA: ",df)

    return df


def download_full_coin_list_from_cryptocompare():
    query_str = "https://min-api.cryptocompare.com/data/all/coinlist"
    cryptocompare_REST_query = query_str + "?api_key=" + "&limit=25" + cryptocompare_API_key
    response = requests.get(cryptocompare_REST_query)
    datadict = json.loads(response.text)
    df = pd.DataFrame(datadict['Data'])

    for col in df.columns:
        c0 = 'tokenized stock' in df[col]['Description']
        c1 = 'stock' in df[col]['Description']
        c2 = '3X' in df[col]['Description']
        c3 = '2X' in df[col]['Description']
        c4 = '0.5X' in df[col]['Description']
        c5 = '1X Short' in df[col]['Description']
        c6 = 'tokenized version of the traditional financial market' in df[col]['Description']
        c7 = 'USDC'
        c8 = 'USDT'

    if not c0 or not c1 or not c2 or not c3 or not c4 or not c5 or not c6 or not c7 or not c8:
        del df[col]

    return df


#https://github.com/CryptoCompareLTD/api-guides/tree/master/python
def download_hist_data_from_cryptocompare(crypto_ticker,data_resolution,timestamp_to_pull_until):
    query_str = ""
    if data_resolution == "day" or data_resolution == "daily" or data_resolution == "D":
        query_str = "https://min-api.cryptocompare.com/data/v2/histoday?fsym="
    elif data_resolution == "hour" or data_resolution == "hourly" or data_resolution == "H":
        query_str = "https://min-api.cryptocompare.com/data/v2/histohour?fsym="
    elif data_resolution == "minute" or data_resolution == "minutes" or data_resolution == "M":
        #print("459 - minutes!!!")
        query_str = "https://min-api.cryptocompare.com/data/v2/histominute?fsym="

    to_time = ""

    if type(timestamp_to_pull_until) is int or type(timestamp_to_pull_until) is float:
        if timestamp_to_pull_until == 0:
            to_time = ""
        else: #print(" in cryptocompare - 277 - TO T: ", str(round(timestamp_to_pull_until)))
            to_time = "&toTs=" + str(round(timestamp_to_pull_until))
    if type(timestamp_to_pull_until) is datetime.datetime:
        to_time = "&toTs=" + str(round(timestamp_to_pull_until.timestamp()))


    if data_resolution == "minute" or data_resolution == "minutes" or data_resolution == "M":
        cryptocompare_REST_query = query_str + crypto_ticker + "&aggregate=1&tryConversion=false&tsym=USD&limit=300" + to_time + "&api_key=" + cryptocompare_API_key
    else:
        cryptocompare_REST_query = query_str + crypto_ticker + "&aggregate=1&tryConversion=false&tsym=USD&limit=2000" + to_time + "&api_key=" + cryptocompare_API_key

    response = requests.get(cryptocompare_REST_query)
    datadict = json.loads(response.text)
    if datadict['Response'] != 'Error':
        df = pd.DataFrame(datadict['Data']['Data'],columns = ['time', 'close'])
        df['time'] = [datetime.datetime.utcfromtimestamp(tt) for tt in df['time']]
        df['time'] = [pytz.utc.localize(tt) for tt in df['time']]
        #df['time'] = [datetime.datetime.fromtimestamp(tt) for tt in df['time']]
    else:
        df = pd.DataFrame({})
    return df



def rescan_all_cryptocompare():
    for tkr in mongo.all_available_tickers:
        if tkr == db.all_tickers_keyword: continue
        data_source = mongo.retrieve_record_single_attribute(tkr,db.db_data_source_key)
        if data_source != "cryptocompare": continue
        if tkr == 'DOGE'\
            or tkr == 'BTC' \
               or tkr == 'A' \
               or tkr == 'AA' \
               or tkr == 'AAAU' \
               or tkr == 'ETH' \
               or tkr == 'XRP' \
               or tkr == 'BNB' \
               or tkr == 'ADA' \
               or tkr == 'DOGE' \
               or tkr == 'LINK' \
               or tkr == 'ICP' \
               or tkr == 'UNI' \
               or tkr == 'DOT' \
               or tkr == 'SOL' \
               or tkr == 'XLM' \
               or tkr == 'FLOW' \
               or tkr == 'MATIC' \
               or tkr == 'BCH' \
               or tkr == 'LTC' \
               or tkr == 'FTT' \
               or tkr == 'VET' \
               or tkr == 'ETC' \
               or tkr == 'TRX' \
               or tkr == 'THETA' \
               or tkr == 'AMP' \
               or tkr == 'GRT' \
               or tkr == 'SHIB' \
               or tkr == 'FIL' \
               or tkr == 'ALGO' \
               or tkr == 'CRO' \
               or tkr == 'AVAX' \
               or tkr == 'CEL' \
               or tkr == 'EOS' \
               or tkr == 'AAVE'\
                : continue

        mongo.date_price_collection.update({'ticker':tkr}, {'$unset': {'dates': 1}})
        mongo.date_price_collection.update({'ticker':tkr}, {'$unset': {db.db_price_record_key: 1}})

        newest_timestamp_available = mongo.retrieve_newest_date(tkr)
        print("newest date is now: ", newest_timestamp_available)

        if type(newest_timestamp_available) is str:
            newest_timestamp_available = (datetime.date.today() - dateutil.relativedelta.relativedelta(months=72))
        if newest_timestamp_available == None or newest_timestamp_available == datetime.datetime.min.replace(tzinfo=pytz.UTC):
            newest_timestamp_available = datetime.datetime.min

        print("rescanning data for: ", tkr, " T since last addition: ", datetime.datetime.utcnow() - newest_timestamp_available, "since: ", newest_timestamp_available)
        print("\nrescanning from CRYPTOCOMPARE for: ", tkr, " from: ", newest_timestamp_available, " to: ", datetime.datetime.now())

        data_resolution = "hourly"
        download_data_from_cryptocompare_cycled(tkr,newest_timestamp_available,datetime.datetime.now(),data_resolution,None,None)

    return


def rescan():
    last_rescan_time = 0

    while True:
        print("DATA RESCAN NEW: ", datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), "sec since last update: ", \
        int(time.time() - last_rescan_time),\
        " seconds vs: ", 60 * rescan_periodicity_minutes, " rescan period")

        if round((time.time() - last_rescan_time)) >= 60 * rescan_periodicity_minutes:
            print("..TIME ELAPSED!! rescanning APIs for new data..")

            if rescan_crypto_or_no == True:
                thread0 = threading.Thread(target=rescan_hourly_cryptocompare)
                thread0.start()

            if rescan_stocks_or_no:
                thread2 = threading.Thread(target=rescan_data_from_polygon(False))
                thread2.start()

            if rescan_crypto_or_no == True: thread0.join()
            last_rescan_time = time.time()

            #if check_alerts_after_rescan == True:
            #    check_alerts.check_for_alerts()

        else:
            print("....DATA RESCAN NEW GOING TO SLEEP: ", datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep((60.0 - ((time.time() - starttime) % 60.0)))

    return



def rescan_hourly_cryptocompare():
    for i in range(len(mongo.all_available_tickers)):
        tkr = mongo.all_available_tickers[i]
        print("rescanning ", tkr)
        if tkr == db.all_tickers_keyword: continue
        newest_timestamp_available = mongo.retrieve_newest_date(tkr)
        data_source = mongo.retrieve_record_single_attribute(tkr,'data_source')
        print(newest_timestamp_available,data_source)
        if type(newest_timestamp_available) is str:
            newest_timestamp_available = (datetime.date.today() - dateutil.relativedelta.relativedelta(months=72))
        if newest_timestamp_available == None or newest_timestamp_available == datetime.datetime.min.replace(tzinfo=pytz.UTC):
            newest_timestamp_available = datetime.datetime.min
        if data_source == 'cryptocompare' and datetime.datetime.utcnow() - newest_timestamp_available >= datetime.timedelta(minutes=30):
            #print("\nrescanning from CRYPTOCOMPARE for: ", tkr, " from: ", newest_timestamp_available)
            data_resolution = 'minute' #"hourly" #
            download_data_from_cryptocompare_cycled(tkr,newest_timestamp_available,datetime.datetime.now(),data_resolution,None,None)
    print("------RESCAN FROM CRYPTOCOMPARE COMPLETE------")
    return




def rescan_data_and_alerts():
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(check_alerts.sender_email, check_alerts.password)

    TEXT = ' '
    msg = MIMEText(TEXT, 'html')
    msg['From'] = check_alerts.sender_email
    msg['Subject'] = 'NOTIFICATION: starting continuous operation: ' + datetime.datetime.now().strftime("%d-%b-%y %H:%M")
    msg['To'] = check_alerts.receiver_email
    smtp_server.sendmail(check_alerts.sender_email, check_alerts.receiver_email, msg.as_string())

    thread0 = threading.Thread(target=rescan)
    thread0.start()

    thread1 = threading.Thread(target=rescan_alerts_in_a_loop)
    thread1.start()

    thread0.join()
    thread1.join()

    return




def rescan_alerts_in_a_loop():
    last_rescan_time = 0

    while True:
        print("RESCAN ALERTS: ", datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), " sec since last update: ", \
        int(time.time() - last_rescan_time),\
        " seconds vs: ", 60 * rescan_alerts_periodicity_minutes, " rescan period")

        if check_alerts.rescan_stock_alerts == True and not is_time_between(datetime.time(0, 1), datetime.time(  4, 0)) or check_alerts.rescan_crypto_alerts == True:
            if round((time.time() - last_rescan_time)) >= 60 * rescan_alerts_periodicity_minutes:
                check_alerts.check_for_alerts()
                last_rescan_time = time.time()
                print("----------------------COMPLETED A CYCLE OF CHECKING ALERTS--------------------")
            else:
                print("...RESCAN ALERTS going to sleep: ", datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
                time.sleep((60.0 - ((time.time() - starttime) % 60.0)))
        else:
                print("...RESCAN ALERTS going to sleep..rescan time not yet: ", datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
                time.sleep((6.0 - ((time.time() - starttime) % 5.0)))
    return


def load_fundamental_event_data_from_xls_to_db(filepath):
    #if filepath does not contain a slash
    if 'C:/' not in filepath:
        base = Path('Fundamental_Events')

        print("p: ",Path().resolve())

        fullpath = Path().resolve() / base / filepath
        xls = fullpath  
        print("xls = ", xls)

    df = pd.read_excel(xls)
    LD = df.to_dict(orient="records")
    print("Adding event: ", LD)
    for el in LD:
        for k in list(el.keys()):
            if ' ' in k:
                el[k.strip()] = el[k]
                del el[k]

    X = {k: [dic[k] for dic in LD] for k in LD[0]}
    mongo.add_fundamental_event_to_db(X)
    return

def add_pd_alerts_to_db(df):
    LD = df.to_dict(orient="records")
    for el in LD:
        for k in list(el.keys()):
            if ' ' in k:
                el[k.strip()] = el[k]
                del el[k]

    X = {k: [dic[k] for dic in LD] for k in LD[0]}
    mongo.add_fundamental_event_to_db(X)
    return



def update_fundamental_data_from_xls(xls_addr=''):
    timezone = pytz.timezone("UTC")
    xls = xls_addr

    if xls_addr == '':
        base = Path('Fundamental_Events')
        fullpath = ''
        filename = 'FILE_TO_ADD_TICKERS_TO_DB.xlsm'
        fullpath = base / (filename)
        xls = fullpath
        
        print("xls = ", xls)

    df1 = pd.read_excel(xls, 'Stocks_to_load')

    tickers = df1['TICKER']
    names = df1['IQ_COMPANY_NAME']
    sectors = df1['IQ_INDUSTRY_SECTOR']
    countries = df1['IQ_COUNTRY_OF_INC']
    exchanges = df1['Exchange']
    commodities = df1['COMMODITY']
    asset_class = 'stock'

    for i in range(len(tickers)):
        ticker = tickers[i]
        if type(ticker) is float: break
        mongo.update_record_with_single_attribute(ticker, "country", countries[i])
        mongo.update_record_with_single_attribute(ticker, "sector", sectors[i])

        mongo.update_record_with_single_attribute(ticker, db.db_name_key, names[i])
        mongo.update_record_with_single_attribute(ticker, db.db_asset_class_record_key, asset_class)
    return



def download_stock_px_data_from_xls(ticker,excel):
    #ticker = "EUA"
    df = pd.read_excel(excel)
    #print(df)
    mongo.update_record_with_series_attribute(ticker, df['Date'].values, db.db_price_record_key, df['Close'].values)
    #mongo.update_record_with_series_attribute(ticker, df['Date'].values, 'open', df['Open'].values)
    return
