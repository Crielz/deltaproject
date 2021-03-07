from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import sys
#----------------------------------------------------------------------------------------
# set up client and retrieve database + collection
uri = "mongodb://root:deltaproject01@localhost:27017"
client = MongoClient(uri)

mydb = client.prices
priceCollection = mydb["priceCollection"]


#----------------------------------------------------------------------------------------
# method definition 
def get_recent_price(collection, baseCurrency, quoteCurrency, exchange):
    query = {
        "priceEvent.exchange":  exchange, 
        "priceEvent.baseCurrency": baseCurrency, 
        "priceEvent.quoteCurrency": quoteCurrency
        }

    # query is comparable with a where clause
    #decending sorting on timestamp to retrieve the most recent price
    
    return collection.find(query).limit(1).sort("timestampInMs",-1)


def get_all_recent_prices_from_base_currency(collection, baseCurrency):
    all_prices = collection.aggregate([
    {
        "$match": { "priceEvent.baseCurrency": baseCurrency }
    },
    {
        "$group" : { 
            "_id" : { 
                "baseCurrency" : "$priceEvent.baseCurrency",
                "quoteCurrency" : "$priceEvent.quoteCurrency",
                #"price" : "$priceEvent.price",
            },
            "most_recent_timestamp" : {"$max" : "$timestampInMs"},
            "price" : {"$first":"$priceEvent.price"} # $first shows matching entries
        } 
    },
    {
         "$sort": {"_id.baseCurrency":1}
    }

])
    return all_prices




def get_all_recent_prices_with_pairs_all_exchanges(collection):
    all_prices = collection.aggregate([
    {
        "$group" : { 
            "_id" : { 
                "baseCurrency" : "$priceEvent.baseCurrency",
                "quoteCurrency" : "$priceEvent.quoteCurrency",
                "exchange" : "$priceEvent.exchange"
            },
            "most_recent_timestamp" : {"$max" : "$timestampInMs"},
            "price" : {"$first":"$priceEvent.price"} # $first shows matching entries
        } 
    },
    {
         "$sort": {"_id.exchange":1, "_id.baseCurrency":1}
    }

])
    return all_prices



# 1. The most recent price must be retrievable, given a certain `(baseCurrency, quoteCurrency, exchange)` tuple (or an array of them).
#----------------------------------------------------------------------------------------
# input baseCurrency, quoteCurrency and exchange in the input list.

"""
price_request_list = [
    {
        "baseCurrency":"ETH",
        "quoteCurrency":"USDT",
        "exchange": "coinbase"
    },
       {
        "baseCurrency":"ADA",
        "quoteCurrency":"USDC",
        "exchange": "kucoin"
    },
    {
        "baseCurrency":"BTC",
        "quoteCurrency":"EUR",
        "exchange": "kraken"
    }
]

for request in price_request_list:
    recent_price = get_recent_price(priceCollection, request['baseCurrency'], request['quoteCurrency'], request['exchange'])
    for res in recent_price:
        print(res) 
        print("most recent price: " + str(res['priceEvent']['price']))

sys.exit()
"""

# 2. Historical data must be retrievable, but the granularity can be more coarse the older the data is (generally only [OHLC]
# (https://en.wikipedia.org/wiki/Open-high-low-close_chart) is kept, make a proposal). This will be queried again in a key-value 
# (same primary key as above) fashion, but time-based range queries are possible as well.
#----------------------------------------------------------------------------------------

"""
last_hour_date_time = datetime.now() - timedelta(hours = 1)
print(last_hour_date_time)
last_hour_date_time_ts = last_hour_date_time.timestamp()
print(last_hour_date_time_ts)
query = {"timestampInMs":  {"$gt": last_hour_date_time_ts} }

res = priceCollection.find(query)#.sort("timestampInMs",-1).limit(10)
for r in res:
    print(r)


sys.exit()
"""
# 3. A list of all possible exchanges, their pairs (`(baseCurrency, quoteCurrency)`) and the last time a price point has been 
#observed should be retrievable.
#----------------------------------------------------------------------------------------

"""
all_prices_all_exchanges = get_all_recent_prices_with_pairs_all_exchanges(priceCollection)

for prices in all_prices_all_exchanges:
    print(prices) 
sys.exit()
"""

# 4. Optional: a list of the most recent prices grouped by `baseCurrency` (you can assume a mapping of 
#`baseCurrency` -> `(quoteCurrency, exchange)` is available) should be retrievable.
#----------------------------------------------------------------------------------------

# input baseCurrency
baseCurrency = "ETH"

all_prices_from_base_currency = get_all_recent_prices_from_base_currency(priceCollection, baseCurrency)
for element in all_prices_from_base_currency:
    print(element) 
