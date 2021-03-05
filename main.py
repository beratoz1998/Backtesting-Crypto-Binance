import pandas as pd
from binance.client import Client
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import talib

coin = 'BTCUSDT'
client = Client()
btc_data = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1HOUR, "6 year ago UTC")
df = pd.DataFrame(btc_data)
df[0] = pd.to_datetime(df[0],unit='ms')
df[6] = pd.to_datetime(df[6],unit='ms')
df.rename(columns={0:'DateTime', 1:'open', 2:'high', 3:'low', 4:'close',5:'volume',6:'CloseTime',7:'QuoteAssetVolume',8:'NumberTrades',9:'TakerBuyBaseAssetVolume',10:'TakerBuyQuoteAssetVolume',11:'Ignore'}, inplace=True)
df[['open','high','low','close','volume','TakerBuyBaseAssetVolume','TakerBuyQuoteAssetVolume']] = df[['open','high','low','close','volume','TakerBuyBaseAssetVolume','TakerBuyQuoteAssetVolume']].astype(float)
df['NumberTrades'] = df['NumberTrades'].astype(int)
df.set_index('DateTime', inplace=True)
df['adj close'] = df['close']
btc_data_df = pd.DataFrame()
btc_data_df[['Open','High','Low','Close','Volume']] = df[['open','high','low','close','volume']]
btc_data_df.to_csv("btc.csv")


class Indicator(Strategy):
    slow_ma = 20
    fast_ma = 10
    rsi_period = 14
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(talib.SMA, price, self.fast_ma)
        self.ma2 = self.I(talib.SMA, price, self.slow_ma)
        self.rsi = self.I(talib.RSI, price, timeperiod=self.rsi_period)

    def next(self):
        if crossover(self.ma1, self.ma2) :
            self.buy()
        elif crossover(self.ma2, self.ma1) :
            self.sell()


bt = Backtest(btc_data_df, Indicator, commission=.002,
              exclusive_orders=True,cash=100000,hedging=True)
stats = bt.run()
bt.plot()
print(stats)