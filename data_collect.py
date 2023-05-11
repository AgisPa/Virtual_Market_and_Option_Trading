import pandas as pd
from pymongo import MongoClient
import numpy as np
from numba import njit,jit
import matplotlib.pyplot as plt
import datetime
import certifi

#Link to your MongoDB database
link=...

#Connects and gets collection
ca = certifi.where()
cluster=MongoClient(link, tlsCAFile=ca)
database=cluster["MarketData"]
collection=database["ask-bid"]
coll=collection.find({})


@jit()
def date_time(date_element):
    quote_time = date_element.replace("-", "")
    quote_time_days = int(quote_time) % 100
    quote_time_months = (int(quote_time) % 10000 - quote_time_days) / 100
    quote_time_years=(int(quote_time)-quote_time_months*100-quote_time_days)/10000
    return {"years":quote_time_years,"months":quote_time_months,"days": quote_time_days}

@jit()
def time_back_to_reference(time_element):
    end_time_years = str(int(time_element/365+2022))
    time_element=time_element-(int(end_time_years)-2022)*365
    end_time_months = int(time_element/ 30 + 1)
    if end_time_months < 10:
        end_time_months = "0" + str(end_time_months)
    else:
        end_time_months = str(end_time_months)
    time_element=time_element-30*(int(end_time_months)-1)
    end_time_days = int(time_element+3)
    if end_time_days<10:
        end_time_days="0"+str(end_time_days)
    else:
        end_time_days =str(end_time_days)
    date=end_time_years+"-"+end_time_months+"-"+end_time_days
    return date


@jit()
def option_data():


    #Turns visuals on
    vis=True

    #Ask-Bid values
    stocks=[]
    for exchange in coll:
        if stocks.count(exchange["underlying"])==0:
            stocks.append(exchange["underlying"])

    stocks_options_quote_times=[]
    stocks_options_expiration_times=[]
    stocks_options_call_bid_prices=[]
    stocks_options_put_bid_prices=[]
    stocks_options_call_sizes=[]
    stocks_options_call_ask_prices=[]
    stocks_options_put_ask_prices=[]
    stocks_options_put_sizes=[]
    stocks_options_strike=[]


    for exchange in stocks:
        stocks_coll=collection.find({"underlying": exchange})
        option_expiration_times=[]
        option_call_bid_prices=[]
        option_call_ask_prices=[]
        option_put_bid_prices = []
        option_put_ask_prices = []
        option_call_size=[]
        option_put_size=[]
        option_strike=[]
        option_time=[]
        for posts in stocks_coll:
            quote_date_days=date_time(posts["quote_date"])["days"]
            quote_date_months = date_time(posts["quote_date"])["months"]
            quote_date_years=date_time(posts["quote_date"])["years"]
            expiration_date_days=date_time(posts["expiration"])["days"]
            expiration_date_months = date_time(posts["expiration"])["months"]
            expiration_date_years = date_time(posts["expiration"])["years"]
            expiration_days=(expiration_date_years-quote_date_years)*365+(expiration_date_months-quote_date_months)*30+expiration_date_days-quote_date_days+1
            option_expiration_times.append(expiration_days)
            option_call_bid_prices.append(posts["call_bid"])
            option_call_ask_prices.append(posts["call_ask"])
            option_put_bid_prices.append(posts["put_bid"])
            option_put_ask_prices.append(posts["put_ask"])

            q_time=posts["quote_date"]
            q_time=date_time(q_time)["days"]+30*date_time(q_time)["months"]+365*date_time(q_time)["years"]-738063
            option_time.append(q_time)

            call_size=int(posts["call_size"])
            call_multiplier=int(posts["call_size_multiplier"])
            call_shares=call_size*call_multiplier
            put_size=int(posts["put_size"])
            put_size_multiplier = int(posts["put_size_multiplier"])
            put_shares=put_size * put_size_multiplier

            option_call_size.append(call_shares)
            option_put_size.append(put_shares)
            option_strike.append(posts["strike"])
        stocks_options_quote_times.append(option_time)
        stocks_options_expiration_times.append(option_expiration_times)
        stocks_options_call_bid_prices.append(option_call_bid_prices)
        stocks_options_call_ask_prices.append(option_call_ask_prices)
        stocks_options_put_bid_prices.append(option_put_bid_prices)
        stocks_options_put_ask_prices.append(option_put_ask_prices)
        stocks_options_call_sizes.append(option_call_size)
        stocks_options_put_sizes.append(option_put_size)
        stocks_options_strike.append(option_strike)
    df= pd.DataFrame({
        "expiration_times": stocks_options_expiration_times[0],
        "quote_time":stocks_options_quote_times[0],
        "strike":stocks_options_strike[0],
        "call_bid":stocks_options_call_bid_prices[0],
        "call_ask":stocks_options_call_ask_prices[0],
        "put_bid":stocks_options_put_bid_prices[0],
        "put_ask":stocks_options_put_ask_prices[0],
        "call_size":stocks_options_call_sizes[0],
        "put_size":stocks_options_put_sizes[0]
    })
    df.to_csv(r'folder/subfolder/data.csv',index=False)
