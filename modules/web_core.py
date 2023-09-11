import time

import requests
import pandas as pd

from modules.trading_engine import TradingEngine
from modules.logger import logging, logger
from modules.metrics import Metrics
from modules.config import *
from configs.config import * 
from modules.db import DealsDataBase
from modules.market_connector import okxTrade
from modules.kline_collector import BinanceData



class WebCore:
    def __init__(self, strat_name = 'classic'):
        # Грубо говоря это бекенд для веб приложения
        self.strat_name = strat_name
        flag = str(DEMO_MODE)
        self.metric = Metrics(strat_name)
        self.deals_db = DealsDataBase(strat_name)
        self.trade = okxTrade(flag)


    @logging
    def get_total_balance(self):
        # Получение полного баланса
        #total_balance = 0
        total_balance = self.metric.total_balance()
        profit_percent = (total_balance / START_BALANCE - 1) * 100
        return total_balance, round(profit_percent, 2)


    @logging
    def get_balance_list(self):
        strats = read_strategies()
        total_balance = self.metric.total_balance()
        balance_list = []
        balance = START_BALANCE
        for strat in strats:
            db = DealsDataBase(strat['name'])
            deals = db.read_deals()
            sorted_deals = sorted(deals, key=lambda x: x['open_timestamp'])
            for deal in sorted_deals:
                percent = ((deal['percent'] or 1) - 1) / (total_balance / strat['balance'])
                balance *= percent+1
                balance_list.append(balance)
        return balance_list


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
        total_fee = self.metric.total_fees(strat_name)
        return round(total_fee, 2) # Функция получения комисий


    @logging
    def get_all_fees(self):
        strats = read_strategies()
        all_fees = 0
        for strat in strats:
            all_fees += self.get_total_fees(strat['name'])
        return round(all_fees, 2)
        

    @logging
    def start_stop_response(self, status:str, strat_name:str=None):
        if strat_name == None:
            strat_name = self.strat_name
        url = f'http://127.0.0.1:5002/{status}_strat'   # status может быть start или stop
        params = {'strat_name': strat_name}
        response = requests.post(url, data=params)
        return response.text


    @logging
    def activate_button(self, strat_name = None):
        # Функция включени и выключения бота
        if strat_name == None:
            strat_name = self.strat_name
        strat = read_some_strat(strat_name)
        if strat['status'] == 'on':
            change_strat(strat_name, status = 'off')
            self.start_stop_response('stop')
            return 'Выключено'
        elif strat['status'] == 'off':
            change_strat(strat_name, status = 'on')
            self.start_stop_response('start')
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
        trade_engine = TradingEngine(self.strat_name)
        trade_data = BinanceData()
        for strat in strats:
            df = trade_data.get_last_candles(strat['token'])
            trade_engine.close_deal(df, 'long')
            trade_engine.close_deal(df, 'short')


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
                self.start_stop_response('stop', strat['name'])


    @logging
    def strategy_list_active(self) -> pd.DataFrame:
        # Получение датафрейма со всеми активными стратегиями и их доходностью
        strats = read_strategies()
        for strat in strats:
            balance_amount, profit_percent = self.balance(strat['name'])
            deals_number, profit_deals_number = self.number_of_deals(strat['name'])
            total_fee = self.get_total_fees(strat['name'])
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
    

    @logging
    def work_status(self):
        # Функция которая возвращает булевое значение состояния работы стратегии
        strat = read_some_strat(self.strat_name)
        diff = time.time() - strat['timing_status']
        interval = INTERVALS_DICT[strat['interval']] * 1.5

        return diff<interval
    

    @logging
    def set_default_trade_settings(self):
    # Функция которая позволяет провести предварительную настройку биржи
        for token in TOKEN_LIST:
            self.trade.set_leverage(token, 1)
        self.trade.account_mode()


    def logger_data(self):
        # Функция для получения данных из файла логера
        filename = "debug.log"
        with open(filename, "rb") as f:
            data = f.read().decode("utf-8")
        return data