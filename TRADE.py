from binance.client import Client
from datetime import datetime
import json
import pandas as pd
#%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import os.path
import math
import statistics
from scipy import stats

api_key = '3HTHfYgqcxA8NS5TjFQIYNq2xQzGt7wq5Dg6vysAokBpkX75c98mmGisbbySYek2'
api_secret = '2Sxle9W0mlHuC2999zdou0UMnEgm2GgOWaKQuZni9I9PLzeRGcw7QJmrdVoozPYi'
client = Client(api_key, api_secret)

class Crypto:
    def __init__(self,symbol, interval_time, start_time):
        now = datetime.now()
        self.file_name =  str(symbol) + '_' + interval_time + '_' + start_time + '_' + str(now.year) + str(now.month) + str(now.day)
        self.interval_time = interval_time
        self.start_time = start_time
        self.symbol = symbol
        self.df = [] # Fill DataFrame Later
        self.log = {} # Dict For Every Record in Grid Trading
        self.read_data()
        self.statics = self.Statics(self.df,self.symbol)

    class Statics:
        # Initial get datatframe from outer class
        def __init__(self, df, symbol):
            self.price = list(df['open'])
            self.symbol = symbol
            self.basic_info()

        def basic_info(self):
            print('\n********** Statistics **********')
            print(f"Mean: {statistics.mean(self.price)}")
            print("Standard deviation: " + str(statistics.pstdev(self.price)))
            print(f"Z-score: {stats.zscore(self.price)[-1]}")
            print('********** ********** **********\n')

        def z_score(self):
            plt.figure(2)
            plt.figure(figsize=(12,6))
            plt.rcParams.update({'font.size': 20,'text.color' : "grey"})
            plt.rc('xtick', labelsize=20, color='grey')
            plt.rc('ytick', labelsize=20, color='grey')
            plt.title(f'{self.symbol}"s normal distribution',fontweight ="bold")
            plt.hist(self.price, bins=40)
            plt.show()


    # Read data on pc, if not exist, download it then read on pc
    def read_data(self):
        # CHECK CSV already on local, if not then Download first
        if not os.path.exists(self.file_name+'.csv'):
            self.download_csv()

        # Then Read CSV Locally
        self.df = pd.read_csv(self.file_name+'.csv')
        print(f'DataFrame of {self.symbol} is {self.df.shape}')

    # Check CSV FIle Already Saved, if yes then Read CSV Locally
    def download_csv(self):
        # fetch klines
        klines = client.get_historical_klines(self.symbol, self.interval_time, self.start_time)

        # into dataframe
        download_df = pd.DataFrame(klines, columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'quoteAssetVolume', 'numberOfTrades', 'takerBuyBaseVol', 'takerBuyQuoteVol', 'ignore'])

        # data cleaning
        download_df['dateTime'] = pd.to_datetime(download_df['dateTime'],unit='ms')

        # Set index
        download_df = download_df.reset_index()
        download_df.set_index('index', inplace=True)

        # store csv file in correct format
        download_df.to_csv(self.file_name+'.csv')

    # Make Plot
    def plot_maker(self):
        # Get Open & X-axis in Dataframe
        symbol_open = list(map(float,self.df['open'].tolist()))
        symbol_x = [*range(0, len(symbol_open))]

        # Plot
        plt.figure(1)
        plt.style.use('seaborn-deep')
        plt.figure(figsize=(12,6))
        plt.rcParams.update({'font.size': 20,'text.color' : "grey"})
        plt.rc('xtick', labelsize=20, color='grey')
        plt.rc('ytick', labelsize=20, color='grey')
        plt.title(f'{self.symbol}"s price lineplot',fontweight ="bold")
        plt.plot(symbol_x, symbol_open)
        plt.show()

    # Calculate All Grid Price
    def calculate_grid_price(self, max_price, min_price, grid_count, grid_type):
        # Make list of Grid Price, then turn to tuple later (faster)
        temp_grid_price = []

        # Make grid price distributed by which
        # 等差網格
        if grid_type == 'arithmetic':
            # Calculate price gap
            price_gap = (max_price - min_price) / grid_count

            # Append all price in list of grid price
            for i in range(grid_count):
                temp_grid_price.append(min_price + price_gap * i)

        # 等比網格
        elif grid_type == 'geometric':
            # Calculate price gap
            price_gap = math.pow((max_price / min_price), 1 / grid_count)

            # Append all price in list of grid price
            for i in range(grid_count):
                temp_grid_price.append(min_price * math.pow(price_gap,i))

        # list to tuple (grid price) then return
        return tuple(temp_grid_price)

    # draw grid line
    def draw_grid(self, grid_price):
        # Plot All trade price
        for price in grid_price:
            plt.axhline(price, color='r', linewidth = 1)

    # Grid Trading
    def grid_trading(self, max_price, min_price, grid_count, grid_type, account_money):
        #******************************************************************
        # INITIAL ALL VARIABLE
        # Get Grid Price (in tuple)
        grid_price =  self.calculate_grid_price(max_price, min_price, grid_count, grid_type)

        # Get Real Price (in tuple)
        real_price = tuple(self.df['open'])

        # Get Trade percent of total_money (every trade)
        trade_percent = 1/grid_count

        # list of buy or sell on every grid price (in list)
        buy_sell_grid = []

        # Remember real_price in which grid of buy_sell_grid
        real_price_between_buy_sell_grid = [0,0]

        # Initial buy_sell_grid & real_price_between_buy_sell_grid
        previous_grid_price = 999999999999999999

        for every_grid_price in range(len(grid_price)):
            if real_price[0] > grid_price[every_grid_price]:
                buy_sell_grid.append('BUY')
            else:
                buy_sell_grid.append('NULL')

            if real_price[0] < grid_price[every_grid_price] and real_price[0] > previous_grid_price:
                real_price_between_buy_sell_grid[0] = every_grid_price-1
                real_price_between_buy_sell_grid[1] = every_grid_price
            elif real_price[0] == grid_price[every_grid_price]:
                real_price_between_buy_sell_grid[0] = every_grid_price
                real_price_between_buy_sell_grid[1] = every_grid_price

            previous_grid_price = grid_price[every_grid_price]
        #******************************************************************

        # Draw grid line
        self.draw_grid(grid_price)

        print(buy_sell_grid)
        print(real_price_between_buy_sell_grid)
        print(f'real_price_between: {grid_price[real_price_between_buy_sell_grid[0]]}')
        print(f'real_price_between: {grid_price[real_price_between_buy_sell_grid[1]]}')
        print(f'Now REAL PRICE: {real_price[0]}')
        print(f'Now REAL PRICE: {real_price[1]}')
        #**************************************************************************
        # Main function to BUY & SELL
        # Iterate through every REAL Price (except first one, beacause already initial)
#         for every_real_price in range(1,len(real_price)):
#             print('****************BEFORE****************')
#             print(f'buy_sell_grid: {buy_sell_grid}')
#             print(f'real_price_between: {real_price_between_buy_sell_grid}')
#             print(f'real_price_between: {grid_price[real_price_between_buy_sell_grid[0]]}')
#             print(f'real_price_between: {grid_price[real_price_between_buy_sell_grid[1]]}')
#             print(f'Now REAL PRICE: {real_price[every_real_price]}')

#             # Update 'real_price_between_buy_sell_grid'

#             # Upadate 'buy_sell_grid'

#             # Decide to BUY or SELL in 'trade percent'

#             # Record info in log
#             print('****************AFTER****************')
#             print(f'buy_sell_grid: {buy_sell_grid}')
#             print(f'real_price_between: {real_price_between_buy_sell_grid}')
#             print(f'************** {every_real_price} ROUND OVER **************')
