# Virtual_Market_and_Option_Trading

## Overview
This code was built to simulate an option market by comparing its financial elements to historical values and predict the pricing of options using the Black-Scholes equation. The code has been build in such a way as to include a NoSql Mongo Db database.

## Requirements

-In order to run this code and get/manipulate the required data you need:
1)A Mongo Db database
2)Option trading data that must be saved in a collection with the name "ask-bid" containing the fields ({"quote_date", "underlying", "expiration", "call_size", "call_size_multiplier", "put_size", "put_size_multiplier", "call_bid", "call-ask", "put_bid", "put_ask"}).
3)A reference database with stocks of variable value named "SampleStocks" having the fields {"underlying", "open", "close"}.
4)Five empty collections named {"ImportanceFactor", "Spot", "Wallet", "Portfolio", "OrderBook"}.

-Run data_collection once. Approximate run time estimate of 20 mins. In this time the algorithms takes the "ask-bid" data from the database and stores the ones most frequently used in local files.
-Run Main. Approximate run time per "day" circle 1.5 hours. Runs virtual market simulation incremented by days, calculates option pricing using the Black-Scholes model, creates a list of increasingly important trades, exucutes them and checks for possible cash outs of already owned contracts.


## Technologies and Packages Used

- **MongoDB:** NoSQL database for storing market data, portfolio details, and order book information.
- **Pandas:** Data manipulation and analysis library for handling data structures.
- **Numpy:** Numerical computing library for efficient array operations.
- **Certifi:** Certificate authority package for secure connections.
- **Matplotlib:** Plotting library for data visualization.
- **NumPy:** Efficient numerical operations for mathematical calculations.
- **Numba:** Just-In-Time (JIT) compiler for accelerating code execution.

## Mathematical Concepts

### Black-Scholes Equation

The Black-Scholes equation is utilized for option pricing in the market simulation. The key formulae for call and put options are employed in the project.

### Asynchronous Programming

The code incorporates asynchronous programming techniques, enabling concurrent execution of tasks for improved performance.

## Code Structure

### Part 1: Initialization and Simulation

This section initializes the MongoDB connection, sets up the initial market conditions, and starts the simulation loop.

### Part 2: Order Book and Portfolio Management

This part handles the management of the order book, portfolio, and importance factors.

### Part 3: Data Collection and Processing

This section focuses on collecting and processing market data, including option details and spot prices.

### Part 4: Market Movement and Statistics

This part contains functions for simulating market movement, updating statistics, and executing buy/sell orders.

## Requirements

To run this code, you need the following:

- Python interpreter (3.6 or higher)
- MongoDB server installed and running
- Required Python packages: pymongo, pandas, numpy, numba, matplotlib

## Running the Simulation

1. Install the required packages using:

2. Ensure MongoDB is running.

3. Execute the main script:


The simulation will run for the specified duration, with market steps and order increments as defined in the script. Adjust parameters as needed for your simulation.

