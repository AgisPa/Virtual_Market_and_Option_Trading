from pymongo import MongoClient
import MovingMarket
import certifi
from bson.objectid import ObjectId
from numba import jit
import data_collect

#Link to your MongoDB database
link=...

ca = certifi.where()
cluster = MongoClient(link, tlsCAFile=ca)
database = cluster["MarketData"]
port_collection = database["Portfolio"]
reference = database["ask-bid"]
wallet = database["Wallet"]
spot_collection=database["Spot"]
order_collection = database["OrderBook"]

@jit()
def owned():
    port=port_collection.find({})
    ids=[]
    call_put=[]
    for elements in port:
        ids.append(elements["id"])
        call_put.append(elements["option_type"])
    return {"_id":ids}

@jit()
def ordering(new_order):
    if new_order["move"]=="buy":
        MovingMarket.market_buy_option(new_order["id"],new_order["option_type"],10)
    if new_order["move"]=="sell":
        MovingMarket.market_sell_option(new_order["id"],new_order["option_type"],10)

@jit()
def trades():

    trade=order_collection.find({}).sort("rank",1).limit(5)
    for elements in trade:
        ordering(elements)

@jit()
def pull_through():
    curr_spot_time = list(spot_collection.find().sort("Time", -1).limit(1))[0]["Time"]
    curr_spot = list(spot_collection.find().sort("Time", -1).limit(1))[0]["Spot"]
    for elements in port_collection.find({}):
        strike=list(reference.find({"_id":ObjectId(elements["id"])}))[0]["strike"]
        ident_y=data_collect.date_time(list(reference.find({"_id":ObjectId(elements["id"])}))[0]["expiration"])["years"]-data_collect.date_time(data_collect.time_back_to_reference(curr_spot_time))["years"]
        ident_m=data_collect.date_time(list(reference.find({"_id":ObjectId(elements["id"])}))[0]["expiration"])["months"]-data_collect.date_time(data_collect.time_back_to_reference(curr_spot_time))["months"]
        ident_d=data_collect.date_time(list(reference.find({"_id":ObjectId(elements["id"])}))[0]["expiration"])["days"]-data_collect.date_time(data_collect.time_back_to_reference(curr_spot_time))["days"]
        prev = list(wallet.find({}, {"_id": False}))[0]["Cash"]
        if ident_y>=0 and ident_m>=0 and ident_d>=0:
            if elements["option_type"]=="call":
                diff=curr_spot-strike
                if diff>=0.6*elements["importance"]:
                    port_collection.delete_one({"id":elements["id"]})
                    wallet.update_one({"Cash":prev},{"$set": {"Cash": prev + diff}})
                    print("Option with id:",elements["id"], "was exercised")
            if elements["option_type"]=="put":
                diff=strike-curr_spot
                if diff>=0.6*elements["importance"]:
                    port_collection.delete_one({"id": elements["id"]})
                    wallet.update_one({"Cash": prev}, {"$set": {"Cash": prev + diff}})
                    print("Option with id:", elements["id"], "was exercised")

@jit()
def wallet_initialize():
    capital = 1000000
    prev = list(wallet.find({}, {"_id": False}))[0]["Cash"]
    wallet.update_one({"Cash": prev}, {"$set": {"Cash": capital}})
