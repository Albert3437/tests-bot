from time import sleep, time
from modules.kline_collector import BinanceData
from modules.indicators import TechnicalIndicators
from modules.config import read_some_strat
from modules.logger import logging, logger
from modules.trading_engine import TradingEngine

class Strategy:
    def __init__(self, strat_name):
        self.trade_data = BinanceData()
        self.strategy = read_some_strat(strat_name)
        self.runing = True


    @logging
    def stop(self):
        self.runing = False


    @logging
    def timing_handler(self, timestamp, interval_in_seconds):
        # Работа с таймингами для свечей
        interval_in_seconds += .5
        sleep_time = interval_in_seconds - (time() - timestamp / 1000)
        if sleep_time<=0:
            sleep_time = interval_in_seconds - sleep_time
        sleep(sleep_time)


    @logging
    def calculate(self, df, signal_list):
        # Вычисление необходимых индикаторов
        ta = TechnicalIndicators(df)
        indicator_dict = {'ADX':'ta.average_directional_index()',
                    'Bollinger':'ta.bollinger_bands()',
                    'CCI':'ta.commodity_channel_index()',
                    'CMF':'ta.chaikin_money_flow()',
                    'Ichimoku':'ta.calculate_ichimoku_cloud()',
                    'MACD':'ta.macd()',
                    'Momentum':'ta.calculate_momentum_system()',
                    'OBV':'ta.on_balance_volume()',
                    'SAR':'ta.parabolic_sar()',
                    'ROC':'ta.rate_of_change()',
                    'RSI':'ta.relative_strength_index()',
                    'SMA':'ta.moving_average()',
                    'Stochastic':'ta.stochastic_oscillator()',
                    'WPR':'ta.williams_percent_range()'}
        for signal in signal_list:
            eval(indicator_dict[signal])
        return df


    @logging
    def core(self, df, indicator_list):
        pos_side = 0
        signals = set()
        logger.info('test')
        for sign in indicator_list:
            signals.add(df[f'{sign} signal'].iloc[-2])

        if len(signals) == 1:
            pos_side = signals.pop()
        
        return  pos_side


    @logging
    def run(self):
        logger.info(self.strategy['name'])
        # Main функция для работы запуска определения сигналов
        # signal:
        # 1 == long
        # -1 == short
        while self.runing:
            indicator_list = self.strategy['indicator_list']
            token = self.strategy['token']
            strat_name = self.strategy['name']
            trading_engine = TradingEngine(strat_name)
            interval = self.strategy['interval']
            df = self.trade_data.get_last_candles(symbol=f'{token}USDT', interval=interval)
            timestamp = df['timestamp'].iloc[-1]
            if self.strategy['status'] == 'on' and self.strategy['arch'] == "classic":
                df = self.calculate(df, indicator_list)
                side = self.core(df, indicator_list)
                if side == 1:
                    trading_engine.open_deal(df, 'long')
                if side == -1:
                    trading_engine.open_deal(df, 'short')
            elif self.strategy['status'] == 'on' and self.strategy['arch'] == "classic reverse":
                df = self.calculate(df, indicator_list)
                side = self.core(df, indicator_list)
                if side == 1:
                    trading_engine.open_deal(df, 'short')
                if side == -1:
                    trading_engine.open_deal(df, 'long')
            self.timing_handler(timestamp, 300)