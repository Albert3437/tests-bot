import time
import math

from pandas import DataFrame

from modules.config import *
from modules.db import *
from modules.market_connector import okxTrade
from modules.logger import logging, logger
# Надо розобраться с ошибкой при закрытии позиций
# Сделать правильное указание цены
# Сделать проверку на закрытую сделку



class TradingEngine:
    def __init__(self, strat_name):
        # Это сердце всей программы - торговое ядро: открывает, отслеживает, закрывает, записывает сделки
        self.strat_name = strat_name
        self.strat = read_some_strat(strat_name)
        self.trade = okxTrade(int(self.strat['demo_mode']))
        self.deals_db = DealsDataBase(strat_name)


    @logging
    def summ(self):
        # функция которая вычисляет размер ордера, на основе цен контрактов, а так-же весов для разных типов торговых пар
        strat = read_some_strat(self.strat_name)
        amount, token = strat['balance'] * strat["leverage"], strat['token']
        actual_price = self.trade.actual_price(token)
        amount = amount / actual_price / self.trade.value_coef(token)
        logger.info(amount)
        return math.ceil(amount)


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
            token = f'{self.strat["token"]}-USDT-SWAP'
            for deal in self.trade.position_list_history():
                if deal['instId'] == token:
                    break
            percent = 1 + float(deal['pnlRatio'])
            close_price = float(deal['closeAvgPx'])
            open_price = float(deal['openAvgPx'])
            fee = (float(deal['closeTotalPos']) * float(deal['closeAvgPx']) * FEES)
        except:
            percent, close_price, open_price, fee = 0,0,0,0
        return percent, close_price, open_price, fee


    @logging
    def place_order(self, token:str, price:float, side:str, act_type:str, ordType:str):
        # Функция прокладка для открытия сделки
        side_types = {'long':{'open':'buy', 'close':'sell'}, 'short':{'open':'sell', 'close':'buy'}}
        strat = read_some_strat(self.strat_name)
        leverage = strat['leverage']
        stop_types = {'long':(price - strat['stop_loss'] * price), 'short':(price + strat['stop_loss'] * price)}
        stop_loss = stop_types[side] if strat['stop_loss'] != 0 else ''
        self.trade.set_leverage(token, leverage)
        deal_result = self.trade.open_pos(token, self.summ(), side, price, side=side_types[side][act_type], ordType=ordType, stop_loss=stop_loss)
        logger.info(deal_result)
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
        else:
            return deal_result


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
            try:
                change_strat(self.strat_name, balance = balance*percent-fee)
            except:
                logger.error('close_deal')
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
            return deal_result


#df = trade_data.get_last_candles()
#open_deal(df, 'long', 'ADA')
#close_deal(df, 'long', 'ADA')