import sys
import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import pytz
import certifi

import CONSTANTS
import CONSTANTS as c
#import db

ca = certifi.where()
all_available_tickers = []

def retrieve_newest_date(ticker):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    z = datetime.min #.replace(tzinfo=pytz.UTC)

    if date_price_collection.count_documents({ 'ticker': ticker }, limit = 1) != 0:
        max_date = date_price_collection.find({"ticker": ticker}, {"_id": False, "dates": {"$max": "$dates"}})
        for m in max_date:
            if m['dates'] == None: return z
            return m['dates'] #print("m2: ", m)
    client.close()
    return z


def retrieve_records_single_attribute_by_val(attr_name0, attr_val0):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]

    cursor = date_price_collection.find({attr_name0:attr_val0},{'ticker': 1, attr_name0: 1})
    list_of_tickers = []
    for document in cursor: list_of_tickers.append(document['ticker'])

    client.close()
    return list_of_tickers


def retrieve_all_records_single_attribute_range(attribute_name):
    print("retrieving records from mongo")
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    try:
        cursor = date_price_collection.find({},{attribute_name: 1})
        #print("cursor:", cursor)
        list_of_tickers = []
        for document in cursor:
            #print("attr: ", document[attribute_name])
            list_of_tickers.append(document[attribute_name])
        client.close()
        return list_of_tickers
    except Exception as e:
        print("Error: could not retrieve from Mongo")
        client.close()
        return ""

    client.close()
    return


def retrieve_record_single_attribute(ticker, attribute_name):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    try:
        if date_price_collection.count_documents({'ticker': ticker }, limit = 1) != 0:
            x = date_price_collection.find( {'ticker': ticker }, {attribute_name: 1, '_id': 0 } )

            client.close()

            for el in x:
                return el[attribute_name]
    except Exception as e:
        print("Error: could not retrieve from Mongo: ", ticker + " " + attribute_name)
        client.close()
        return None
    return


def delete_record_series_attribute_recent(ticker, attribute_name, since):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    if retrieve_newest_date(ticker) < since: return
    if date_price_collection.count_documents({ 'ticker': ticker }, limit = 1) != 0:
        print("retrieving all")
        dates,prices = retrieve_record_series_attribute(ticker,'prices')
        print("deleting")
        x = date_price_collection.update(
            {'ticker': ticker},
            { '$unset': {'dates':"",'prices':""}},
        )

        tz = list(filter(lambda s: s[0] < since, zip(dates,prices)))
        dates_truncated, prices_truncated = zip(*tz)
        tz = list(filter(lambda s: s[1] > 0.0, zip(dates_truncated,prices_truncated)))
        dates_truncated, prices_truncated = zip(*tz)

        print("len dates truncated: ", len(dates_truncated)," min = ", min(dates_truncated), " max = ", max(dates_truncated))
        print("len prices truncated: ", len(prices_truncated))
        print("adding again")
        #add chopped
        update_record_with_series_attribute(ticker, dates_truncated, 'prices', prices_truncated)


    client.close()
    return


def retrieve_record_series_attribute_recent(ticker,attribute_name,oldest): #,oldest = 100
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]

    dt = []
    vals = []

    timezone = pytz.timezone("UTC")

    if retrieve_newest_date(ticker) < oldest: return dt, vals

    if date_price_collection.count_documents({ 'ticker': ticker }, limit = 1) != 0:

        x = date_price_collection.aggregate([
            {'$match': {'ticker': ticker}},

            {
                "$addFields": {
                    "dates": {
                        '$filter': {
                            'input': "$dates",
        'as': "date",
            'cond': {
            '$gte':  ["$$date",oldest]
        }
        }
        }
        }
        },
        {
            '$project': {
                'dates': 1,
                attribute_name: {
                    '$slice': [
                        "$prices",
                        {
                            "$multiply": [-1,{'$size': "$dates"}]
                        },
                        900000
                    ]
                }
            }
        }
        ])



        for el in x:
            dt = np.array(el['dates'])
            vals = np.array(el['prices'])

        if len(dt) != len(vals):
            print("len dt: ", len(dt))
            print("len vals: ", len(vals))
            kk = list(zip(dt,vals))
            print("trying using the classic method..")
            dt,vals = retrieve_record_series_attribute(ticker,attribute_name)
            print("len dt = ",len(dt))
            print("vals = ",len(vals))

            if len(dt) == len(vals): return np.array(dt),np.array(vals)

            print("oldest: ", retrieve_oldest_date(ticker))
            print("newest: ", retrieve_newest_date(ticker))
            print("input oldest var: ", oldest)

            if len(dt) > 0: print("len dt = ", type(dt[0]))
            if len(vals) > 0: print("len dt = ", type(vals[0]))
            sys.exit("Unequal dates and prices fetched from db")

    client.close()
    return np.array(dt),np.array(vals)



def retrieve_record_series_attribute(ticker,attribute_name):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    if date_price_collection.count_documents({ 'ticker': ticker }, limit = 1) != 0:
        x = date_price_collection.find( { 'ticker': ticker }, { 'dates': 1, attribute_name: 1, '_id': 0 } )
        dt = []
        vals = []

        for el in x:
            #print(el)
            k, v = list(el.values())[:2]
            dt.append(k)
            vals.append(v)

        dt = dt[0]
        vals = vals[0]

        client.close()
        return np.array(dt),np.array(vals)
    else:
        print("Error - does not exist in mongo - ", ticker)
        client.close()
        return None,None

    client.close()
    return

def update_record_with_single_attribute(ticker, attribute_name, attribute_val):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    if date_price_collection.count_documents({ 'ticker': ticker }, limit = 1) != 0:
        date_price_collection.update_one({"ticker": ticker},{'$set': {attribute_name: attribute_val}})
        client.close()
    else:  # create new record
        record = {
            "ticker": ticker,
            attribute_name: attribute_val,
        }
        _ = date_price_collection.insert_one(record)
    client.close()
    return

def update_record_with_series_attribute_older(ticker, dates, attribute_name, attribute_vals):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    print("UPDATING WITH OLDER DATA")
    zipped_lists = zip(list(dates), list(attribute_vals))
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    dates_truncated, prices_truncated = [list(tuple) for tuple in tuples]

    date_price_collection.update_one({"ticker": ticker}, {
        '$push': {"dates": {'$each': dates_truncated,'$position':0}, attribute_name: {'$each': prices_truncated,'$position': 0}}})

    client.close()
    return


def update_record_with_series_attribute(ticker, dates, attribute_name, attribute_vals):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    timezone = pytz.timezone("UTC")
    print("\nAdding PX DT data for: ", ticker, " from: ", min(dates), " to: ", max(dates))

    if type(attribute_vals) == tuple:
        print("converting prices from tuple to list")
        attribute_vals = list(attribute_vals)
        attribute_vals = np.array(attribute_vals)

    if type(dates[0]) == datetime.date:
        dates = np.asarray([datetime(dt.year, dt.month, dt.day, tzinfo=pytz.UTC) for dt in dates])

    if type(dates[0]) is np.datetime64:
        dates = np.asarray([datetime.utcfromtimestamp(dt.tolist() / 1e9) for dt in dates]) #dt.astype(datetime)
        dates = np.asarray([timezone.localize(dt) for dt in dates])

    if type(dates[0]) is pd.Timestamp:
        dates = np.asarray([dt.to_pydatetime() for dt in dates])

    if dates[0].tzinfo == None:
        dates = np.asarray([timezone.localize(dt) for dt in dates])

    if date_price_collection.count_documents({ 'ticker': ticker }, limit = 1) != 0:
        #print("record exists..layering on..")
        y = date_price_collection.find( { 'ticker': ticker }).sort("dates", -1).limit(1)
        contents = dict(y[0])

        max_date_existing = contents.get('dates')

        if max_date_existing != None:
            max_date_existing = [timezone.localize(dt) for dt in max_date_existing]
            min_date_existing = min(max_date_existing)
            max_date_existing = max(max_date_existing)
        else:
            max_date_existing = datetime.min.replace(tzinfo=pytz.UTC)
            min_date_existing = datetime.min.replace(tzinfo=pytz.UTC)

        if type(max_date_existing) == list:
            max_date_existing = max_date_existing[0]

        if type(max_date_existing) == list:
            min_date_existing = min_date_existing[0]

        print("     MAX DATE EXISTING: ", max_date_existing, " TZ: ", max_date_existing.tzinfo)
        #print("     MIN DATE EXISTING: ", min_date_existing, " TZ: ", min_date_existing.tzinfo)
        print("     new dates 0 tz info: ", dates[0].tzinfo, " added min: ", min(dates), " max: ", max(dates), " for: ", ticker)

        t_min = datetime.min
        if max_date_existing.tzinfo != None: t_min = t_min.replace(tzinfo=pytz.UTC)

        if max_date_existing > t_min:
            mde = list([dates > max_date_existing][0])
            dates_truncated = [i for (i, v) in zip(dates, mde) if v]
            prices_truncated = [i for (i, v) in zip(attribute_vals, mde) if v]
        else:
            dates_truncated = dates
            prices_truncated = attribute_vals

        dates_truncated_older = dates[dates < min_date_existing]

        if len(dates_truncated) == 0 and len(dates_truncated_older) == 0:
            print("nothing to append..")
            return
        if len(dates_truncated) > 0:
            print("     DATES (TRUNCATED) FROM: ", dates_truncated[0], " TO: ", dates_truncated[len(dates_truncated) - 1])

        if len(dates_truncated_older) > 0 and len(dates_truncated) == 0:
            print("..inserting older with len: ", len(dates_truncated_older))
            update_record_with_series_attribute_older(ticker, dates_truncated_older, attribute_name, attribute_vals[dates < min_date_existing])
            return

        if len(dates_truncated) > 0:
            zipped_lists = zip(list(dates_truncated), list(prices_truncated))
            sorted_pairs = sorted(zipped_lists)
            tuples = zip(*sorted_pairs)
            dates_truncated, prices_truncated = [list(tuple) for tuple in tuples]

            if max_date_existing > datetime.min.replace(tzinfo=pytz.UTC):
                date_price_collection.update_one({"ticker": ticker},{'$push': {"dates": {'$each': dates_truncated}, attribute_name: {'$each': prices_truncated}}})
            elif max_date_existing == datetime.min.replace(tzinfo=pytz.UTC):
                date_price_collection.update_one({"ticker": ticker},{'$set': {"dates": dates_truncated, attribute_name: prices_truncated}})

    else:
        print("Creating new record!!")
        record = {"ticker": ticker}
        x = date_price_collection.insert_one(record)
        if len(dates) == 0 or len(attribute_vals) == 0: sys.exit("ERROR of zero len on ticker: ", ticker)
        zipped_lists = zip(list(dates), list(np.asarray(attribute_vals)))
        sorted_pairs = sorted(zipped_lists)
        tuples = zip(*sorted_pairs)
        dates, attribute_vals = [list(tuple) for tuple in tuples]
        date_price_collection.update_one({"ticker": ticker}, {'$set': {"dates": dates, attribute_name: attribute_vals}})

    print("     adding data complete for: ", ticker)

    client.close()
    return


def download_data_from_db_to_xls(ticker):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    dt,px = retrieve_record_series_attribute(ticker,'prices')

    df = pd.DataFrame({
        'dates': dt,
        'prices': px,
    })

    df.to_excel(ticker+".xlsx")

    client.close()
    return


def check_data():
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]


    print("len: ", len(all_available_tickers))

    for ticker in all_available_tickers:
        if ticker == '-': continue
        x = retrieve_newest_date(ticker)
        y = retrieve_oldest_date(ticker)
        ac = retrieve_record_single_attribute(ticker,'asset_class')
        n = retrieve_record_single_attribute(ticker,'name')
        src = retrieve_record_single_attribute(ticker,'data_source')
        if ac == 'stock':
            sec = retrieve_record_single_attribute(ticker,'sector')
            cty = retrieve_record_single_attribute(ticker,'country')
        else:
            sec = ''
            cty = ''
        print(ticker, " - n: ", x, " o: ", y, " upd ago: ",datetime.utcnow() - x, " sector: ", sec, " c: ", cty, " n: ", n, " src = ", src)

    client.close()
    return


def update_record_with_daily_series_attribute(ticker, dates, attribute_name, attribute_vals):
    mongo_url = c.MONGO_URL
    client = MongoClient(mongo_url,tlsCAFile=ca) ##client = MongoClient(mongo_url)
    database = client["YIELD_DATA"]
    date_price_collection = database["historical_prices"]
    active_event_listener_collection = database["active_events"]
    fundamental_event_collection = database["fundamental_events"]

    print("updating non price data")

    client.close()
    return


print("mongo.py")
all_available_tickers.append('-')
all_available_tickers.extend(retrieve_all_records_single_attribute_range("ticker"))
all_available_tickers = sorted(all_available_tickers)
all_available_tickers = [CONSTANTS.tkr_ETH,CONSTANTS.tkr_BTC]
print("tickers pulled from db: ", all_available_tickers)

TICKER_DD = []
for el in all_available_tickers: TICKER_DD.append({'label': el, 'value': el},)