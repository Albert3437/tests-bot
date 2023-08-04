from modules.market_connector import okxTrade
from modules.kline_collector import BinanceData
from modules.db import *
from pandas import DataFrame
from modules.logger import logging, logger
from modules.metrics import Metrics
import time
from modules.config import *




class TradingEngine:
    def __init__(self, strat_name, flag = '1'):
        self.strat_name = strat_name
        self.metric = Metrics()
        self.trade = okxTrade(flag)
        self.deals_db = DealsDataBase(strat_name)
        

    @logging
    def summ(self):
        # функция которая вычисляет размер ордера, на основе фьючерсного смещения цен, а так-же весов для разных типов торговых пар
        strat = read_some_strat(self.strat_name)
        amount = strat['balance']
        token = strat['token']
        actual_price = self.trade.actual_price(token)
        if token == 'ETH':
            amount = amount/actual_price * 100 # Это просчет количества контрактов для своповой торговли
        elif token == 'XRP':
            amount = amount/actual_price / 100 # И для каждой пары он свой
        elif token == 'ADA':
            amount = amount/actual_price
        elif token == 'SOL':
            amount = amount/actual_price * 10
        else:
            amount = amount/actual_price * 1000
        return int(amount)


    @logging
    def close_deal(self, df, side):
        strat = read_some_strat(self.strat_name)
        token = strat['token']
        balance = strat = strat['balance']
        close_result = (self.trade.close_position(token, 'long')['data'], self.trade.close_position(token, 'short')['data'])
        last_deal = self.deals_db.read_deals()[-1]
        actual_price = self.trade.actual_price(token)
        if side == 'long':
            percent = actual_price/last_deal[2]
        if side == 'short':
            percent = last_deal[2]/actual_price
        self.deals_db.close_deal(int(df['timestamp'].iloc[-1]), actual_price, percent, self.metric.get_fee(token))
        change_strat(self.strat_name, balance = balance*percent)
        logger.info(close_result)
        return close_result


    def open_deal(self, df:DataFrame, side:str):
        deals = self.deals_db.read_deals()
        strat = read_some_strat(self.strat_name)
        token = strat['token']
        strat_type = strat['strat_type']
        if len(deals) == 0 or deals[-1][3] != side or strat_type == 'all signals':
            if len(deals) != 0 and deals[-1][-1] == None:
                self.close_deal(df, side)
            deal_result = self.trade.long(token, self.summ()) if side == 'long' else self.trade.short(token, self.summ())
            self.deals_db.open_deal(int(df['timestamp'].iloc[-1]), self.trade.actual_price(token), side)
            logger.info(deal_result)
            return deal_result


    @logging
    def manage_deals(self, token):
        # Отслеживание сделок и закрытие по стоп лоссу
        while True:
            deal = self.deals_db.read_deals()[-1]
            if deal['close_price'] is None:
            # Ожидание завершения сделок, а так же отслеживание стопа и тейка, так как в сдк не работают функции стопов и тейков
                price = float(self.trade.actual_price(token))
                open_price = deal['open_price']
                stop_price = open_price * self.settings_db.read_settings()[-1]['stop_loss']
                pos = deal['deal_type']
                if pos == 'long':
                    if price <= stop_price:
                        self.close_deal(token,'long')
                if pos == 'short':
                    if price >= stop_price:
                        self.close_deal(token,'short')
            # Нужно для оптимизации и ограничения запросов на сервер, можно изменить значение
            time.sleep(2)


#df = trade_data.get_last_candles()
#open_deal(df, 'long', 'ADA')
#close_deal(df, 'long', 'ADA')