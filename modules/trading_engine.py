from modules.market_connector import okxTrade
from modules.db import *
from pandas import DataFrame
from modules.logger import logging, logger
from modules.metrics import Metrics
import time
from modules.config import *
# надо розобраться с ошибкой при закрытии позиций
# Сделать правильное указание цены
# Сделать проверку на закрытую сделку



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
    def wait_time(self):
        strat = read_some_strat(self.strat_name)
        interval = strat['interval']
        intervals = {'1m':60, '5m':300, '15m':900, '30m':1800, '1h':3600, '2h':7200, '4h':14400, '6h':21600, '12h':43200}
        return int(intervals[interval] * 0.6)


    @logging
    def close_data(self):
        r = self.trade.position_list_history()['data'][0]
        percent = 1 + float(r['pnlRatio'])
        close_price = float(r['closeAvgPx'])
        open_price = float(r['openAvgPx'])
        fee = float(r['closeTotalPos']) * float(r['closeAvgPx']) * 0.0005
        return percent, close_price, open_price, fee


    @logging
    def create_order(self, price, token, side, act_type = 'open'):
        trade = okxTrade()
        if act_type == 'close':
            deal_result = self.trade.long(token, self.summ(), price, side='sell') if side == 'long' else self.trade.short(token, self.summ(), price, side='buy')
        else:
            deal_result = self.trade.long(token, self.summ(), price) if side == 'long' else self.trade.short(token, self.summ(), price)
        if deal_result['data'][0]['sMsg'] == 'Order placed':
            order_id = deal_result['data'][0]['ordId']
            for _ in range(self.wait_time()):
                status = trade.last_order('ADA', order_id)['data'][0]['state']
                if status == 'filled':
                    return deal_result, status
                time.sleep(1)
            else:
                if act_type == 'close':
                    #trade.cancel_order(token, order_id) вроду бы работает без этого
                    deal_result = self.trade.long(token, self.summ(), '', side='sell', ordType='market') if side == 'long' else self.trade.short(token, self.summ(), '', side='buy', ordType='market')
                else:
                    trade.cancel_order(token, order_id)
                status = trade.last_order('ADA', order_id)['data'][0]['state']
                return deal_result, status


    @logging
    def close_deal(self, df, side):
        strat = read_some_strat(self.strat_name)
        token, balance = strat['token'], strat['balance']
        price, timestamp = float(df['close'].iloc[-2]), int(df['timestamp'].iloc[-1])
        close_result = self.create_order(price, token, side, 'close')
        last_deal = self.deals_db.read_deals()[-1]
        side, status = last_deal['deal_type'], last_deal['status']
        if status == 'canceled':
            self.deals_db.close_deal()
        else:
            percent, close_price, _, fee = self.close_data()
            self.deals_db.close_deal(timestamp, close_price, percent, fee)
        change_strat(self.strat_name, balance = balance*percent)
        logger.info(close_result)
        return close_result


    def open_deal(self, df:DataFrame, side:str):
        deals = self.deals_db.read_deals()
        strat = read_some_strat(self.strat_name)
        token, strat_type = strat['token'], strat['strat_type']
        price, timestamp = float(df['close'].iloc[-2]), int(df['timestamp'].iloc[-1])
        if len(deals) == 0 or deals[-1]['deal_type'] != side or strat_type == 'all signals':
            if len(deals) != 0 and deals[-1]['commision'] == None:
                self.close_deal(df, side)
            deal_result, status = self.create_order(price, token, side)
            order_id = deal_result['data'][0]['ordId']
            _, _, open_price, _ = self.close_data()
            self.deals_db.open_deal(order_id, timestamp, open_price, side, status)
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