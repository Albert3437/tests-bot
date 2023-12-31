from modules.db import *
from modules.market_connector import okxTrade
from modules.logger import logging
from modules.db import DealsDataBase



class Metrics:
    def __init__(self, db_name='test'):
        # Класс для просчета метрик работы бота
        self.trade = okxTrade()
        self.deals_db = DealsDataBase(db_name)


    @logging
    def total_balance(self):
        # Получение и просчет баланса по всем торговым инструментам(вместе с позициями)
        all = 0
        bal = self.trade.balance('USDT')
        deals = self.trade.position_list_active()
        for deal in deals:
            pos_size = deal['notionalUsd']
            all += float(pos_size)
        all += float(bal)
        return round(all, 2)


    @logging
    def profit_percent_per_day(self):
        # Процент прибыли за день по токену
        deals = self.deals_db.read_deals()
        profit_percent = 0
        for deal in deals:
            percent = deal['percent']
            if percent != 0:
                profit_percent += (percent or 1) - 1
        return round((profit_percent * 100), 2)


    @logging
    def total_percent_of_success(self, db_name):
        # Процент Прибыли за все время, по токену
        deals = self.deals_db.read_deals(db_name)
        deal_len = len(deals)
        success = deal_len
        for deal in deals:
            profit_percent = deal['percent']
            if profit_percent == None:
                deal_len -= 1
                success -= 1
            elif profit_percent < 1:
                success -= 1
                if profit_percent == 0:
                    deal_len -= 1
        if deal_len == 0:
            deal_len = 1
        return success / deal_len * 100



    @logging
    def get_fee(self, symbol):
        try:
            # Получение комисии по последней сделке, по токену
            r = self.trade.order_history()['data']
            for i in r:
                if i['instId'][:3] == symbol:
                    return i['fee']
        except Exception as e:
            return 0


    @logging
    def total_fees(self, db_name):
        # Общая уплаченая комисия
        fee = 0
        deals = self.deals_db.read_deals(db_name)
        for deal in deals:
            fee+=deal['commision'] or 0
        return fee
