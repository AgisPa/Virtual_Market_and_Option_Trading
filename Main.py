import MovingMarket
import localorderbook
import blackscholes
import portfolio
from pymongo import MongoClient
import certifi
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning, NumbaWarning
import warnings
from numba import jit

#ignore by message
warnings.filterwarnings("ignore", message="divide by zero encountered in divide")

##part of the message is also okay
warnings.filterwarnings("ignore", message="divide by zero encountered")
warnings.filterwarnings("ignore", message="invalid value encountered")

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaWarning)
warnings.simplefilter('ignore', category=RuntimeWarning)

duration=100
market_step=10
max_orders=20
order_increment=1

@jit()
def start_sim(duration, market_step,order_increment,max_orders):
    ca = certifi.where()
    cluster = MongoClient('', tlsCAFile=ca)
    database = cluster["MarketData"]
    order_collection = database["OrderBook"]
    order_collection.delete_many({})
    port_collection = database["Portfolio"]
    port_collection.delete_many({})
    importance_collection=database["ImportanceFactor"]
    importance_collection.delete_many({})
    MovingMarket.market_initialization()
    portfolio.wallet_initialize()
    MovingMarket.market_move(True, 0)
    t=1
    while t<=duration:
        MovingMarket.market_move(True,t)
        blackscholes.report()
        localorderbook.importance_factor()
        for i in range(int(market_step/order_increment)):
            localorderbook.send_orders(order_increment,max_orders)
            portfolio.pull_through()
        t+=1

start_sim(duration,market_step, order_increment, max_orders)
