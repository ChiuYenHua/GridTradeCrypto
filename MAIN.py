import TRADE
from binance.client import Client

if __name__ == '__main__':
    # argument
    interval_time = Client.KLINE_INTERVAL_30MINUTE
    start_time = "1 days ago UTC"
    grid_type1 = 'arithmetic'
    grid_type2 = 'geometric'
    account_money = 100

    # outer class 1.make plot 2.grid trading
    ETHUSDT = TRADE.Crypto('ETHUSDT', interval_time, start_time)
    ETHUSDT.plot_maker()
    ETHUSDT.grid_trading(2100,1900,30,grid_type1,100)
    
    # inner class do statics
    #crypto_statics = ETHUSDT.statics
    #crypto_statics.z_score()