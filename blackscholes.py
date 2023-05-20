import datetime
from numba import njit,jit
from pymongo import MongoClient
import numpy as np
import certifi
import pandas as pd
import math

ca = certifi.where()
cluster = MongoClient('mongodb+srv://Agis:IyuQpSizXj2IVoIz@firstcluster.wmeiivv.mongodb.net/test', tlsCAFile=ca)
database = cluster["MarketData"]
collection = database["ask-bid"]
spot_collection=database["Spot"]


@njit()
def normal_cdf(x):
    q = math.erf(x / math.sqrt(2.0))
    return (1.0 + q) / 2.0


@jit()
def black_scholes(strike, expiration_time):
    curr_spot=spot_collection.find().sort("Time", -1).limit(1)
    spot=list(curr_spot)[0]
    prev_spot=spot_collection.find({"Time": int(spot["Time"]-1)})

    previous=list(prev_spot)[0]
    historical=list(spot_collection.find({}))[0]["Spot"]

    sigma=np.std(historical)/np.mean(historical)
    spot=spot["Spot"]
    previous=previous["Spot"]
    ret = np.log(spot / previous)
    div = (strike - spot)/spot


    div_1=(np.log(spot*np.exp(-div*expiration_time)/(strike*np.exp(-ret*expiration_time)))+1/2*sigma**2*expiration_time)/(sigma*np.sqrt(expiration_time))
    div_2=div_1-sigma*np.sqrt(expiration_time)
    call=spot*np.exp(-ret*expiration_time)*normal_cdf(div_1)-strike*np.exp(-ret*expiration_time)*normal_cdf(div_2)
    put=strike*np.exp(-ret*expiration_time)*normal_cdf(-div_2)-spot*np.exp(-div*expiration_time)*normal_cdf(-div_1)
    return {"call":call,"put":put}

@jit()
def evaluation():
    data = pd.read_csv(r'C:\Users\cooki\Desktop\Virtual Market Project\data.csv')
    strikes=data["strike"]
    call_bid=data["call_bid"]
    call_ask=data["call_ask"]
    put_bid=data["put_bid"]
    put_ask=data["put_ask"]
    expiration_times=data["expiration_times"]
    quote_time=list(data["quote_time"])
    spot_collection = database["Spot"]
    curr_spot = spot_collection.find().sort("Time", -1).limit(1)
    time=list(curr_spot)[0]["Time"]
    call_buy=[]
    call_sell=[]
    put_buy=[]
    put_sell=[]
    ids=[]
    report = ""
    the_range=abs(quote_time.index(time)-quote_time.index(time+1))
    for times in range(len(quote_time)):
        if quote_time[times]==time:
            strike=strikes[times]
            if str(int(round(round(abs(times-quote_time.index(time)),1)/(the_range)*100,0)))+"% complete" !=report:
                report=str(int(round(round(abs(times-quote_time.index(time)),1)/(the_range)*100,0)))+"% complete"
                print("Black-Scholes analysis: ",report,"  ", datetime.datetime.now())
            expiration=expiration_times[times]
            call_put=black_scholes(strike,expiration)
            call=call_put["call"]
            put=call_put["put"]
            item=collection.find_one({"call_bid": call_bid[times], "call_ask":call_ask[times], "put_bid":put_bid[times],"put_ask": put_ask[times], "strike": int(strike) })
            call_buy.append(call-call_ask[times])
            call_sell.append(call_bid[times]-call)
            put_buy.append(put-put_ask[times])
            put_sell.append(put_bid[times]-put)
            ids.append(item["_id"])
    return {"call_buy":call_buy,"call_sell":call_sell,"put_buy":put_buy,"put_sell":put_sell,"_id":ids}

@jit()
def report():
    df=pd.DataFrame(evaluation())
    df.to_csv(r'C:\Users\cooki\Desktop\Virtual Market Project\evaluation.csv',index=False)
