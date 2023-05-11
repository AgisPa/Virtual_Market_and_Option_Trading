# Virtual_Market_and_Option_Trading
This code was built to simulate an option market by comparing its financial elements to historical values and predict the pricing of options using the Black-Scholes equation. The code has been build in such a way as to include a NoSql Mongo Db database.

-In order to run this code and get/manipulate the required data you need:
1)A Mongo Db database
2)Option trading data that must be saved in a collection with the name "ask-bid" containing the fields ({"quote_date", "underlying", "expiration", "call_size", "call_size_multiplier", "put_size", "put_size_multiplier", "call_bid", "call-ask", "put_bid", "put_ask"}).
3)A reference database with stocks of variable value named "SampleStocks" having the fields {"underlying", "open", "close"}.
4)Five empty collections named {"ImportanceFactor", "Spot", "Wallet", "Portfolio", "OrderBook"}.

-Run data_collection once. Approximate run time estimate of 20 mins. In this time the algorithms takes the "ask-bid" data from the database and stores the ones most frequently used in local files.
-Run Main. Approximate run time per "day" circle 1.5 hours. Runs virtual market simulation incremented by days, calculates option pricing using the Black-Scholes model, creates a list of increasingly important trades, exucutes them and checks for possible cash outs of already owned contracts.

