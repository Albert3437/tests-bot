from time import sleep, time

from modules.kline_collector import BinanceData
from modules.indicators import TechnicalIndicators
from modules.config import read_some_strat
from modules.logger import logging, logger
from modules.trading_engine import TradingEngine
from configs.config import INDICATOR_DICT, INTERVALS_DICT

class Strategy:
    def __init__(self, strat_name):
        # Этот класс является одной из структур для алготорговли 
        # Вычисляет индикаторы и генерирует сигналы на покупку
        self.trade_data = BinanceData()
        self.strategy = read_some_strat(strat_name)
        self.runing = True


    @logging
    def stop(self):
        # Переключатель для работы экземпляра класса
        self.runing = False


    @logging
    def timing_handler(self, timestamp, interval):
        # Работа с таймингами для свечей
        interval_in_seconds = INTERVALS_DICT[interval]
        interval_in_seconds += .5
        sleep_time = interval_in_seconds - (time() - timestamp / 1000)
        if sleep_time<=0:
            sleep_time = interval_in_seconds - sleep_time
        sleep(sleep_time)


    @logging
    def calculate(self, df, signal_list):
        # Вычисление необходимых индикаторов
        ta = TechnicalIndicators(df)

        for signal in signal_list:
            eval(INDICATOR_DICT[signal])
        return df


    @logging
    def core(self, df, indicator_list):
        # Определение текущего сигнала
        pos_side = 0
        signals = set()
        for sign in indicator_list:
            signals.add(df[f'{sign} signal'].iloc[-2])

        if len(signals) == 1:
            pos_side = signals.pop()
        
        return  pos_side


    @logging
    def run(self):
        logger.info(self.strategy['name'])
        # Main loop для работы запуска определения сигналов
        while self.runing:
            indicator_list, token, strat_name, interval = self.strategy['indicator_list'], self.strategy['token'],self.strategy['name'], self.strategy['interval']
            trading_engine = TradingEngine(strat_name)
            df = self.trade_data.get_last_candles(symbol=token, interval=interval)
            timestamp = df['timestamp'].iloc[-1]
            if self.strategy['status'] == 'on' and self.strategy['arch'] == "classic":
                # Работа с первым подтипом  стратегии
                df = self.calculate(df, indicator_list)
                side = self.core(df, indicator_list)
                if side == 1:
                    trading_engine.open_deal(df, 'long')
                if side == -1:
                    trading_engine.open_deal(df, 'short')
            elif self.strategy['status'] == 'on' and self.strategy['arch'] == "classic reverse":
                # Работа с вторым подтипом  стратегии
                df = self.calculate(df, indicator_list)
                side = self.core(df, indicator_list)
                if side == 1:
                    trading_engine.open_deal(df, 'short')
                if side == -1:
                    trading_engine.open_deal(df, 'long')
            self.timing_handler(timestamp, interval)