import datetime
from pymongo import MongoClient
import numpy as np
from random import gauss
import pandas as pd
import certifi
from numba import njit, jit
from bson.objectid import ObjectId

ca = certifi.where()
cluster = MongoClient('mongodb+srv://Agis:IyuQpSizXj2IVoIz@firstcluster.wmeiivv.mongodb.net/test', tlsCAFile=ca)
database = cluster["MarketData"]
ask_bid_collection = database["ask-bid"]
collection = database["SampleStocks"]
spot_collection = database["Spot"]
init_data=pd.read_csv(r'C:\Users\cooki\Desktop\Virtual Market Project\statistics.csv')

@njit()
def market_initial_stock_value():


    coll = ask_bid_collection.find({})
    stocks = []
    for exchange in coll:
        if stocks.count(exchange["underlying"]) == 0:
            stocks.append(exchange["underlying"])
    coll = ask_bid_collection.find({})
    stocks_strike_prices = []
    for exchange in stocks:
        strike_prices = []
        for strikes in coll:
            if strike_prices.count(strikes["strike"]) == 0:
                strike_prices.append(strikes["strike"])
        stocks_strike_prices.append(strike_prices)

    #For multiple stocks change below

    mu=np.mean(strike_prices)
    sigma=np.std(strike_prices)
    s0= gauss(mu, sigma)
    return s0, mu, sigma

@njit()
def market_statistics(s0):
    coll = collection.find({})
    stocks = []
    for posts in coll:
        if stocks.count(posts["underlying"]) == 0:
            stocks.append(posts["underlying"])
    stock_avg_prices=[]
    for stock in stocks:
        stock_avg_price=collection.aggregate([{"$match":{'underlying':stock}},{'$group': {"_id":"$underlying",'avg_val':{'$avg':'$open'}}}])
        for average in stock_avg_price:
            stock_avg_prices.append(average["avg_val"])
    par_stock_index=min(range(len(stock_avg_prices)), key=lambda i: abs(stock_avg_prices[i]-s0))
    par_coll=collection.find({"underlying":stocks[par_stock_index]})
    par_inport=[]
    for opens in par_coll:
        par_inport.append(opens["open"])
    mu=np.mean(par_inport)
    sigma=np.std(par_inport)
    df=pd.DataFrame({"s0":s0 ,"mu": mu , "sigma": sigma,"Parallel Stock" :stocks[par_stock_index] },index=[0])
    df.to_csv(r'C:\Users\cooki\Desktop\Virtual Market Project\statistics.csv')
@jit()
def market_step(s0,mu,sigma,time):
    mu=mu/s0
    sigma=sigma/s0
    st=s0*np.exp((mu - 0.5 * sigma ** 2) * (1. / 365.) + sigma *np.sqrt(1/365)*gauss(mu=0, sigma=1))
    time+=1
    spot_collection.insert_one({
        "Spot": st,
        "Time":time
    })
    return st

@jit()
def market_move(play,in_time):
    if play:
        s0=init_data["s0"][0]
        mu=init_data["mu"][0]
        sigma=init_data["sigma"][0]
        if in_time==0:
            market_step(s0, mu, sigma,in_time)
        else:
            spot=spot_collection.find().sort("Time", -1).limit(1)
            for posts in spot:
                market_step(posts["Spot"], mu, sigma, in_time)
@jit()
def market_initialization():
    #For multiple stocks change below
    start_datetime = datetime.datetime.now()
    print("Starting simulation on: ", start_datetime)
    #market_statistics(market_initial_stock_value()[0])
    spot_collection.delete_many({})

def market_buy_option(id, call_put, number):

    spot_time = spot_collection.find().sort("Time", -1).limit(1)
    _id = ObjectId(id)
    buy = ask_bid_collection.find_one({"_id": _id})
    for spot in spot_time:
        if int(buy["quote_date"].replace("-",""))-20220103==int(spot["Time"]):
            if call_put=="call":
                dim_number=number/int(buy["call_size_multiplier"])
                if dim_number<=buy["call_size"]:
                    ask_bid_collection.update_one({"_id":_id},{"$set":{"call_size": buy["call_size"]-dim_number}})
                    print(number," of ", call_put," : ",_id," options bought")
                    return True
                else:
                    print("Request to buy the ",call_put," : ",_id," option canceled due to insuffucient market size")
                    return False
            if call_put=="put":
                dim_number=number/int(buy["put_size_multiplier"])
                if dim_number<=buy["put_size"]:
                    ask_bid_collection.update_one({"_id":_id},{"$set":{"put_size":buy["put_size"]-dim_number}})
                    print(number, " of ", call_put, " : ", _id, " options bought")
                    return True
                else:
                    print("Request to buy the ",call_put," : ",_id," option canceled due to insuffucient market size")
                    return False
        else:
            print("Request to buy the ",call_put," : ",_id," option canceled due to being overdue:",int(buy["quote_date"].replace("-",""))-20220103-int(spot["Time"])," days")
            return False


def market_sell_option(id, call_put, number):

    spot_time = spot_collection.find().sort("Time", -1).limit(1)
    _id = ObjectId(id)
    buy = ask_bid_collection.find_one({"_id": _id})
    for spot in spot_time:
        if int(buy["expiration"].replace("-",""))-20220103>=int(spot["Time"]):
            if call_put=="call":
                dim_number=int(number/int(buy["call_size_multiplier"]))
                if dim_number!=0:
                    ask_bid_collection.update_one({"_id":_id},{"$set":{"call_size": buy["call_size"]+dim_number}})
                    print(int(dim_number*buy["call_size_multiplier"])," of ", call_put," : ",_id," options sold")
                    return True
                else:
                    print("Request to sell",number, "of ", call_put, "id: ",_id, "options failed as the minimum selling amount is",int(buy["call_size_multiplier"]))
                    return False

            if call_put=="put":
                dim_number=int(number/int(buy["put_size_multiplier"]))
                if dim_number!=0:
                    ask_bid_collection.update_one({"_id":_id},{"$set":{"put_size":buy["put_size"]+dim_number}})
                    print(int(dim_number*buy["put_size_multiplier"]), " of ", call_put, " : ", _id, " options sold")
                    return True
                else:
                    print("Request to sell", number, "of ", call_put, " id: ", _id,
                          "options failed as the minimum selling amount is", int(buy["put_size_multiplier"]))
                    return False
        else:
            print("Request to sell the ",call_put," : ",_id," option canceled due to being overdue:",int(buy["quote_date"].replace("-",""))-20220103-int(spot["Time"])," days")
            return False