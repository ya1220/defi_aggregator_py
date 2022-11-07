import download
import mongo
import datetime
import pandas as pd
import numpy as np
import sys
import cython
import time
import CONSTANTS
#import master_yield_class

data_db = {}
other_attr_db = {}

date_key = "Dates"
in_memory_db_date_key = 'Date'

price_key = "Close"

#for mongo
db_asset_class_record_key = 'asset_class'
db_price_record_key = CONSTANTS.price_record_key
db_volume_record_key = 'volumes'
db_data_source_key = 'data_source'
db_exchange_key = 'exchange'
db_proof_record_key = 'proof_type'
db_coin_launched_record_key = 'coin_launched_date'
db_name_key = 'name'

print("db.py")

all_tickers_keyword = "-"

print_or_no = CONSTANTS.print_or_no

def fetch_necessary_data_from_local_drive(tickers):
    for ticker in tickers:
        data = download.read_stock_data_from_csv(ticker)
        data_db[ticker] = data


def append_recently_downloaded_data_to_db():
    for ticker in mongo.all_available_tickers:
        if ticker == all_tickers_keyword: continue

        if ticker not in list(data_db.keys()): fetch_necessary_data_from_db(ticker)
        if len(data_db[ticker][in_memory_db_date_key]) == 0:
            newest_in_memory_db = datetime.datetime.min
        else:
            newest_in_memory_db = max(data_db[ticker][in_memory_db_date_key])

        dt = []
        px = []
        compressed = []
        #print("newest now: ", mongo.retrieve_newest_date(ticker), " vs max in memory dB: ", oldest)
        if mongo.retrieve_newest_date(ticker) > newest_in_memory_db:
            dt, px = mongo.retrieve_record_series_attribute_recent(ticker, db_price_record_key, newest_in_memory_db)
            print("extending newly downloaded data for: ", ticker, " with data after: ", newest_in_memory_db, " to ", max(dt))

        if len(dt) > 0:
            dto = []
            dto.extend(data_db[ticker][in_memory_db_date_key])
            pxo = np.array(data_db[ticker][price_key])
            dto.extend(dt) #, axis=0)
            pxo = np.concatenate((pxo, px), axis=0) #print("pxo: ", pxo, "dto: ", dto)

            newx = pd.DataFrame({
                in_memory_db_date_key: dto,
                price_key: pxo,
                #CONSTANTS.compressed_flag_key: [data_db[ticker][CONSTANTS.compressed_flag_key].tolist()[0]] * len(pxo),
            })

            data_db[ticker] = newx
    return

def fetch_necessary_data_from_db(tickers,recent_only = True,days_to_fetch=365*5):
    if type(tickers) is not list:
        tickers_list = []
        tickers_list.append(tickers)
    else:
        tickers_list = tickers

    #print("405: ", tickers_list)

    for ticker in tickers_list:
        if recent_only == False:
            dt,px = mongo.retrieve_record_series_attribute(ticker,db_price_record_key)
            if dt is not None: print("406 - fetched all for: ", ticker, " min: ", min(dt))
        else:
            start_time = time.time()
            print("     407 - fetching recent data for: ", ticker, " over: ", days_to_fetch, " days")
            oldest = datetime.datetime.now() - datetime.timedelta(days=days_to_fetch)
            dt,px = mongo.retrieve_record_series_attribute_recent(ticker, db_price_record_key, oldest)
            if print_or_no == 1: print("    ---FETCHING DATA took %s seconds ---" % (time.time() - start_time))

        asset_class = mongo.retrieve_record_single_attribute(ticker,db_asset_class_record_key)

        if dt is not None:
            #compress here
            d = pd.DataFrame({
                in_memory_db_date_key: dt,
                price_key: px,
                #CONSTANTS.compressed_flag_key: pd.Series([0]*len(dt)),
                }
            )
            data_db[ticker] = d
        else:
            print("714..")
        other_attr_db[db_asset_class_record_key] =  asset_class

    return

#print("rescanning")
#download.rescan()
print("ABOUT TO FETCH DATA FOR IN MEMORY DB")
if CONSTANTS.USE_IN_MEMORY_DB_OR_NO: fetch_necessary_data_from_db(mongo.all_available_tickers,True,10)
print("FETCHED!")