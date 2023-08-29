import threading
import pandas as pd

from modules.logger import logging, logger
from modules.metrics import Metrics
from modules.config import *
from modules.db import DealsDataBase
from modules.market_connector import okxTrade
from arch.classic import Strategy

class WebCore:
    def __init__(self, strat_name = 'classic'):
        # Грубо говоря это бекенд для веб приложения
        self.strat_name = strat_name
        flag = '1'
        strats = read_strategies()
        for strat in strats:
            if strat_name == strat['name']:
                flag = str(strat['demo_mode'])
        self.metric = Metrics(flag, strat_name)
        self.deals_db = DealsDataBase(strat_name)
        self.trade = okxTrade(flag)
        self.threads = {}


    @logging
    def get_total_balance(self):
        # Получение полного баланса
        total_balance = 0
        total_balance = self.metric.total_balance()
        return self.metric.total_balance()



    @logging
    def number_of_strat(self):
        # Получение количества существующих стратегий
        try:
            number_of_strategies = 0
            number_of_strategies += len(read_strategies())
            return number_of_strategies
        except Exception as e:
            logger.error(e)


    @logging
    def balance(self, strat_name = None):
        # Функция получения баланса и процента доходности
        if strat_name == None:
            strat_name = self.strat_name
        profit_percent, balance = 0, 0
        strats = read_strategies()
        for strat in strats:
            if strat['name'] == strat_name:
                balance = strat['balance']
        profit_percent += self.metric.profit_percent_per_day()
        return round(balance, 2), round(profit_percent, 2) 


    @logging
    def number_of_deals(self, strat_name=None):
        # Функция получения количества сделок и процента их доходности
        if strat_name == None:
            strat_name = self.strat_name
        deals_number, profit_deals_percent = 0, 0
        deals = self.deals_db.read_deals(strat_name)
        deals_number += len(deals)
        profit_deals_percent += self.metric.total_percent_of_success(strat_name) or 0
        if profit_deals_percent < 50:
            profit_deals_percent = -profit_deals_percent
        return deals_number, round(profit_deals_percent, 2)


    @logging
    def get_total_fees(self, strat_name = None):
        # Функция для получения общего числа комисий
        if strat_name == None:
            strat_name = self.strat_name
        total_fee = 0
        total_fee = self.metric.total_fees(strat_name)
        return round(total_fee, 2) # Функция получения комисий


    @logging
    def start_strategy(self):
        # Запуск потока для стратегии
        strat = Strategy(self.strat_name)
        thread = threading.Thread(target=strat.run)
        self.threads[self.strat_name] = (strat, thread)
        thread.start()


    @logging
    def stop_strategy(self):
        # Отключение потока для стратегии
        if self.strat_name in self.threads:
            strat, thread = self.threads[self.strat_name]
            strat.stop()
            thread.join()
            del self.threads[self.strat_name]


    @logging
    def activate_button(self, strat_name = None):
        # Функция включени и выключения бота
        if strat_name == None:
            strat_name = self.strat_name
        strats = read_strategies()
        for strat in strats:
            if strat['status'] == 'on' and strat['name'] == strat_name:
                change_strat(strat_name, status = 'off')
                self.stop_strategy()
                return 'Выключено'
            elif strat['status'] == 'off' and strat['name'] == strat_name:
                change_strat(strat_name, status = 'on')
                self.start_strategy()
                return 'Включено'



    @logging
    def remove_strategy(self, strat_name = None):
        # Функция удаления стратегии
        if strat_name == None:
            strat_name = self.strat_name
        strat = read_some_strat(strat_name)
        if strat['status'] == 'on' and strat['name'] == strat_name:
            change_strat(strat_name, status = 'off')
            self.stop_strategy()
        remove_strat(strat_name)
        return 'Стратегия удалена'



    @logging
    def close_all_positions(self):
        # Функция для принудительного закрытия всех сделок
        # Переписать под правильное закрытие позиций
        strats = read_strategies()
        for strat in strats:
            self.trade.close_position(strat['token'], 'long')
            self.trade.close_position(strat['token'], 'short')


    @logging
    def clear_db(self):
        # Очистка базы данных
        self.deals_db.clear_deals()
        return 'Очищено'


    @logging
    def deact_all_strats(self):
        # Отключение всех запущеных стратегий
        # Нужно переписать
        strats = read_strategies()
        for strat in strats:
            if strat['status'] == 'on':
                change_strat(strat['name'], status = 'off')


    @logging
    def strategy_list_active(self) -> pd.DataFrame:
        # Получение датафрейма со всеми активными стратегиями и их доходностью
        strats = read_strategies()
        for strat in strats:
            balance_amount, profit_percent = self.balance(strat['name'])
            deals_number, profit_deals_number = self.number_of_deals(strat['name'])
            total_fee = self.get_total_fees()
            strat['balance_amount'] = balance_amount
            strat['profit_percent'] = profit_percent
            strat['deals_number'] = deals_number
            strat['profit_deals_number'] = profit_deals_number
            strat['total_fee'] = total_fee
        return pd.DataFrame(strats)


    def write_api(self, NGROK_TOKEN, TELE_API, CHAT_ID, OKX_API_KEY, OKX_SECRET, OKX_PASSPHRAZE):
        # Функция записи АПИ
        api_write(NGROK_TOKEN=NGROK_TOKEN,TELE_API=TELE_API,CHAT_ID=CHAT_ID,OKX_API_KEY=OKX_API_KEY,OKX_SECRET=OKX_SECRET,OKX_PASSPHRAZE=OKX_PASSPHRAZE)


    def deals_df(self) -> pd.DataFrame:
        # Получение датафрейма со всеми сделками
        deals = self.deals_db.read_deals(self.strat_name)
        df = pd.DataFrame(data = deals)
        return df


    @logging
    def logger_data(self) -> pd.DataFrame:
        # Получение датафрейма с записями логера
        with open('debug.log', 'r') as f:
            data = f.readlines()
        new_data = []
        for i in data:
            new_data.append(i.split('|'))
        df = pd.DataFrame(data=new_data, columns=['timestamp', 'type', 'message'])
        return df
    

    @logging
    def clear_logger(self):
        # Очищение логера
        with open('debug.log', 'w') as f:
            f.write('')


    @logging
    def strategy_list():
        # Список стратегий
        strat_names = []
        strats = read_strategies()
        for strat in strats:
            strat_names.append(strat['name'])
        return strat_names