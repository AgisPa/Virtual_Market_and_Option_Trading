from pymongo import MongoClient
import numpy as np
from numba import jit
import certifi
import pandas as pd
import portfolio
import time
import MovingMarket
from bson.objectid import ObjectId

order_book_size=200


ca = certifi.where()
cluster = MongoClient('', tlsCAFile=ca)
database = cluster["MarketData"]
order_collection = database["OrderBook"]
port_collection = database["Portfolio"]
importance_collection=database["ImportanceFactor"]
reference=database["ask-bid"]
wallet = database["Wallet"]

@jit()
def importance_factor():
    element = pd.read_csv(r'',
                     usecols=["_id", "call_buy", "call_sell", "put_buy", "put_sell"])
    factor_collection = database["ImportanceFactor"]
    call_buy=list(element["call_buy"])
    call_sell=list(element["call_sell"])
    put_buy=list(element["put_buy"])
    put_sell=list(element["put_sell"])
    ids=list(element["_id"])
    port=portfolio.owned()["_id"]
    bet=[]
    for i in range(len(ids)):
        max_call_buy=np.amax(call_buy)
        max_call_buy_index = np.argmax(call_buy)
        max_call_sell= np.amax(call_sell)
        max_call_sell_index = np.argmax(call_sell)
        max_put_buy=np.amax(put_buy)
        max_put_buy_index=np.argmax(put_buy)
        max_put_sell=np.amax(put_sell)
        max_put_sell_index=np.argmax(put_sell)
        re_max=max(max_call_sell,max_call_buy,max_put_sell,max_put_buy)
        if re_max==max_call_buy or re_max==max_call_sell:
            option_type="call"
            if max_call_buy>max_call_sell:
                index = max_call_buy_index
                if list(reference.find({"_id": ObjectId(ids[index])}))[0]["call_size"]>0:
                    move="buy"
                else:
                    move="none"
                    re_max=0
            else:
                move="sell"
                index=max_call_sell_index
                if port.count(ids[index])==0:
                    move="none"
                    re_max=0
        else:
            option_type="put"
            if max_put_buy>max_put_sell:
                index = max_put_buy_index
                if list(reference.find({"_id": ObjectId(ids[index])}))[0]["put_size"]>0:
                    move="buy"
                else:
                    move="none"
                    re_max=0
            else:
                move="sell"
                index=max_put_sell_index
                if port.count(ids[index])==0:
                    move="none"
                    re_max=0
        if index<=len(ids):
            bet.append({"id":ids[index], "option_type":option_type,"move":move,"rank":0,"importance": re_max})
            call_buy.pop(index)
            call_sell.pop(index)
            put_buy.pop(index)
            put_sell.pop(index)
            ids.pop(index)
    factor_collection.delete_many({})
    factor_collection.insert_many(bet)

@jit()
def orderbook(orders,order_book_size):
    order_collection.insert_many(orders)
    collection=order_collection.find().sort("importance", -1).limit(order_book_size)
    new_order=[]
    i=0
    for posts in collection:
        posts["rank"]=i+1
        i+=1
        new_order.append(posts)
    order_collection.delete_many({})
    order_collection.insert_many(new_order)

@jit()
def updating_orders(refresh_rate):
    importance = list(importance_collection.find({},{"_id":False}))
    orderbook(importance,order_book_size)
    time.sleep(refresh_rate)

@jit()
def send_orders(refresh_rate,num_orders):
    new_order=order_collection.find({"rank":{"$lte":num_orders}})
    for elements in new_order:
        ident = list(reference.find({"_id": ObjectId(elements["id"])}))[0]
        prev = list(wallet.find({}, {"_id": False}))[0]["Cash"]
        if elements["move"]=="buy":
            if elements["option_type"]=="call":
                ask = ident["call_ask"]
                if ask<=prev:
                    mrk=MovingMarket.market_buy_option(elements["id"],elements["option_type"],1)
                    if mrk:
                        wallet.update_one({"Cash": float(prev)}, {"$set": {"Cash": prev - ask}})
                        port_collection.insert_one(elements)
                else:
                    print("Insufficient funds for purchasing option with id:", elements["id"])
            elif elements["option_type"]=="put":
                ask=ident["put_ask"]
                if ask<=prev:
                    mrk=MovingMarket.market_buy_option(elements["id"],elements["option_type"],1)
                    if mrk:
                        port_collection.insert_one(elements)
                        wallet.update_one({"Cash": float(prev)}, {"$set": {"Cash": prev - ask}})
                else:
                    print("Insufficient funds for purchasing option with id:", elements["id"])
            importance_collection.delete_one({"id":elements["id"]})
        if elements["move"]=="sell":
            mrk=MovingMarket.market_sell_option(elements["id"],elements["option_type"],1)
            if mrk:
                port_collection.delete_one(elements)
                wallet.update_one({"Cash": float(prev)}, {"$set": {"Cash": prev + ask}})
            importance_collection.delete_one({"id":elements["id"]})
    for elements in order_collection.find({}):
        importance_collection.delete_one({"id": elements["id"]})
    order_collection.delete_many({"rank":{"$lte":num_orders}})
    updating_orders(refresh_rate)
