import time

import pandas as pd

from binance.client import Client
from modules.logger import logging



class BinanceData:
    def __init__(self, api_key='API_KEY', api_secret='API_SECRET'):
        self.client = Client(api_key, api_secret)
        
    @logging
    def get_historical_candles(self, start_date:str, end_date:str, symbol:str='BTC', interval=Client.KLINE_INTERVAL_5MINUTE):
        # Получение исторических данных для тестов стратегии
        for _ in range(5):
            try:
                candles = self.client.get_historical_klines(f'{symbol}USDT', interval, start_date, end_date)
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']  # список нужных столбцов
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                df = df[columns]
                return df
            except:
                time.sleep(5)

        

    @logging
    def get_last_candles(self, limit:int=200, symbol:str="BTC", interval=Client.KLINE_INTERVAL_5MINUTE):
        # Получение актуальных свечей
        for _ in range(5):
            try:
                candles = self.client.get_klines(symbol=f'{symbol}USDT', interval=interval, limit=limit)
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
                df = df[columns]
                return df
            except:
                time.sleep(5)
