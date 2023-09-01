import time

from pandas import DataFrame

from modules.config import *
from modules.db import *
from modules.market_connector import okxTrade
from modules.logger import logging, logger
from configs.config import FEES, INTERVALS_DICT, COEF
# надо розобраться с ошибкой при закрытии позиций
# Сделать правильное указание цены
# Сделать проверку на закрытую сделку



class TradingEngine:
    def __init__(self, strat_name, flag = '1'):
        # Это сердце всей программы: торговое ядро, открывает, отслеживает, закрывает, записывает сделки
        self.strat_name = strat_name
        self.trade = okxTrade(flag)
        self.deals_db = DealsDataBase(strat_name)


    @logging
    def summ(self):
        # функция которая вычисляет размер ордера, на основе цен контрактов, а так-же весов для разных типов торговых пар
        strat = read_some_strat(self.strat_name)
        amount, token = strat['balance'], strat['token']
        actual_price = self.trade.actual_price(token)
        amount = amount/actual_price * COEF[token]
        return int(amount)


    @logging
    def wait_time(self, deal_type:str):
        # Функция для получения времени ожидания открытия сделки
        strat = read_some_strat(self.strat_name)
        interval = strat['interval']
        coef_dict = {'open':0.3, 'close':0.3}
        return int(INTERVALS_DICT[interval] * coef_dict[deal_type])


    @logging
    def close_data(self):
        # Функция получения данных по закрытию сделки
        try:
            r = self.trade.position_list_history()[0]
            percent = (1 + float(r['pnlRatio']))
            close_price = float(r['closeAvgPx'])
            open_price = float(r['openAvgPx'])
            fee = (float(r['closeTotalPos']) * float(r['closeAvgPx']) * FEES)
        except:
            percent, close_price, open_price, fee = 0,0,0,0
        return percent, close_price, open_price, fee


    @logging
    def place_order(self, token:str, price:float, side:str, act_type:str, ordType:str):
        # Функция прокладка для открытия сделки
        side_types = {'long':{'open':'buy', 'close':'sell'}, 'short':{'open':'sell', 'close':'buy'}}
        deal_result = self.trade.open_pos(token, self.summ(), side, price,  side=side_types[side][act_type], ordType=ordType)
        return deal_result



    @logging
    def create_order(self, price, token, side, act_type = 'open'):
        # Функция создания и отслеживания ордера на открытие или закрытие позиции
        # Блок для создания заявки на открытие или закрытие позиции
        deal_result = self.place_order(token, price, side, act_type, 'limit')
        # Блок для отслеживания сделки
        if deal_result['data'][0]['sMsg'] == 'Order placed':
            order_id = deal_result['data'][0]['ordId']
            # Блок для проверки на статус сделки
            for _ in range(self.wait_time(act_type)):
                order_status = self.trade.last_order(token, order_id)['data'][0]['state']
                if order_status == 'filled':
                    return deal_result, order_status
                time.sleep(1)
            else:
                # Блок для незаполненой сделки
                if act_type == 'close':
                    #Блок для закрытия сделки по текущей рыночной цене
                    deal_result = self.place_order(token, '', side, act_type, 'market')
                else:
                    # Блок для отмены сделки
                    self.trade.cancel_order(token, order_id)
                order_status = self.trade.last_order(token, order_id)['data'][0]['state']
                return deal_result, order_status


    @logging
    def close_deal(self, df, side):
        # Функция закрытия сделки
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
        return close_result


    @logging
    def open_deal(self, df:DataFrame, side:str):
        # Функция открытия сделки
        deals = self.deals_db.read_deals()
        strat = read_some_strat(self.strat_name)
        token, strat_type = strat['token'], strat['strat_type']
        price, timestamp = float(df['close'].iloc[-2]), int(df['timestamp'].iloc[-1])
        if len(deals) == 0 or deals[-1]['deal_type'] != side or strat_type == 'all signals':
            if len(deals) != 0 and deals[-1]['commision'] == None:
                self.close_deal(df, deals[-1]['deal_type'])
            deal_result, status = self.create_order(price, token, side)
            order_id = deal_result['data'][0]['ordId']
            _, _, open_price, _ = self.close_data()
            self.deals_db.open_deal(order_id, timestamp, open_price, side, status)
            logger.info(deal_result)
            return deal_result


    @logging
    def manage_deals(self, token):
        # НЕ ИСПОЛЬЗУЕТСЯ
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