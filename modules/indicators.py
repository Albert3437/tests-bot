import talib
import pandas as pd 
from modules.logger import logging



class TechnicalIndicators:
    def __init__(self, df):
        self.df = df
        self.df['close'] = pd.to_numeric(self.df['close'], errors='coerce')
        self.df['high'] = pd.to_numeric(self.df['high'], errors='coerce')
    
    @logging
    def moving_average(self, window=20):      
        self.df['SMA'] = talib.SMA(self.df['close'], timeperiod=window)
        self.df['SMA_50'] = talib.SMA(self.df['close'], timeperiod=50)
        self.df['SMA_200'] = talib.SMA(self.df['close'], timeperiod=200)
        self.df['SMA signal'] = 0
        self.df.loc[(self.df['close'] > self.df['SMA_50']) & (self.df['close'] > self.df['SMA_200']), 'SMA signal'] = 1
        self.df.loc[(self.df['close'] < self.df['SMA_50']) & (self.df['close'] < self.df['SMA_200']), 'SMA signal'] = -1
        return self.df
    
    @logging
    def relative_strength_index(self, window=14):
        self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=window)
        self.df['RSI signal'] = 0
        self.df.loc[self.df['RSI'] > 70, 'RSI signal'] = -1
        self.df.loc[self.df['RSI'] < 30, 'RSI signal'] = 1
        return self.df
    
    @logging
    def macd(self, short_window=12, long_window=26, signal_window=9):
        macd, signal, _ = talib.MACD(self.df['close'], fastperiod=short_window, slowperiod=long_window, signalperiod=signal_window)
        self.df['MACD'] = macd
        self.df['Signal'] = signal
        self.df['MACD signal'] = 0
        self.df.loc[(self.df['MACD'] > self.df['Signal']) & (self.df['MACD'].shift(1) < self.df['Signal'].shift(1)), 'MACD signal'] = 1
        self.df.loc[(self.df['MACD'] < self.df['Signal']) & (self.df['MACD'].shift(1) > self.df['Signal'].shift(1)), 'MACD signal'] = -1
        return self.df
    
    @logging
    def bollinger_bands(self, window=20, num_std=2):
        upper_band, middle_band, lower_band = talib.BBANDS(self.df['close'], timeperiod=window, nbdevup=num_std, nbdevdn=num_std)
        self.df['Upper Band'] = upper_band
        self.df['Middle Band'] = middle_band
        self.df['Lower Band'] = lower_band
        self.df['Bollinger signal'] = 0
        self.df.loc[self.df['close'] > self.df['Upper Band'], 'Bollinger signal'] = -1
        self.df.loc[self.df['close'] < self.df['Lower Band'], 'Bollinger signal'] = 1
        return self.df
    
    @logging
    def stochastic_oscillator(self, window=14):
        slowk, slowd = talib.STOCH(self.df['high'], self.df['low'], self.df['close'], fastk_period=window, slowk_period=window, slowd_period=window)
        self.df['SlowK'] = slowk
        self.df['SlowD'] = slowd
        self.df['Stochastic signal'] = 0
        self.df.loc[(self.df['SlowK'] < 20) & (self.df['SlowD'] < 20), 'Stochastic signal'] = 1
        self.df.loc[(self.df['SlowK'] > 80) & (self.df['SlowD'] > 80), 'Stochastic signal'] = -1
        return self.df
    
    @logging
    def average_directional_index(self, window=14):
        self.df['ADX'] = talib.ADX(self.df['high'], self.df['low'], self.df['close'], timeperiod=window)
        self.df['ADX signal'] = 0
        self.df.loc[self.df['ADX'] > 25, 'ADX signal'] = 1
        self.df.loc[self.df['ADX'] < 20, 'ADX signal'] = -1
        return self.df
    
    @logging
    def calculate_ichimoku_cloud(self, conversion_period=9, base_period=26, leading_span_period=52, lagging_span_period=26):
        
        # Вычисление линий Облака Ишимоку
        high_prices = self.df["high"]
        low_prices = self.df["low"]
        
        self.df["Conversion Line"] = (high_prices.rolling(window=conversion_period).max() + low_prices.rolling(window=conversion_period).min()) / 2
        self.df["Base Line"] = (high_prices.rolling(window=base_period).max() + low_prices.rolling(window=base_period).min()) / 2
        self.df["Leading Span A"] = ((self.df["Conversion Line"] + self.df["Base Line"]) / 2).shift(leading_span_period)
        self.df["Leading Span B"] = ((high_prices.rolling(window=leading_span_period).max() + low_prices.rolling(window=leading_span_period).min()) / 2).shift(leading_span_period)
        self.df["Lagging Span"] = high_prices.shift(-lagging_span_period)
        self.df['Ichimoku signal'] = 0
        self.df.loc[(self.df['close'] > self.df['Leading Span A']) & (self.df['close'] > self.df['Leading Span B']), 'Ichimoku signal'] = 1
        self.df.loc[(self.df['close'] < self.df['Leading Span A']) & (self.df['close'] < self.df['Leading Span B']), 'Ichimoku signal'] = -1
        return self.df
    
    @logging
    def fibonacci_strategy(self):
        # Вычисление чисел Фибоначчи
        def fibonacci(n):
            fib = [0, 1]
            for i in range(2, n):
                fib.append(fib[i-1] + fib[i-2])
            return fib

        # Создание столбцов для хранения сигналов покупки/продажи
        self.df['Buy_Signal'] = 0
        self.df['Sell_Signal'] = 0

        self.df['close'] = self.df['close'].astype(float)

        # Определение точек входа и выхода на основе чисел Фибоначчи
        fib_levels = fibonacci(10)  # Выберите количество уровней Фибоначчи, которые хотите использовать
        for i in range(len(self.df)):
            buy_signal = False
            sell_signal = False

            for level in fib_levels:
                if self.df['close'][i] <= level:
                    buy_signal = True
                    break
                elif self.df['close'][i] >= level:
                    sell_signal = True
                    break

            if buy_signal:
                self.df.at[i, 'Buy_Signal'] = 1
                self.df.at[i, 'Sell_Signal'] = 0
            elif sell_signal:
                self.df.at[i, 'Buy_Signal'] = 0
                self.df.at[i, 'Sell_Signal'] = 1

        return self.df
    
    @logging
    def parabolic_sar(self):
        self.df['SAR'] = talib.SAR(self.df['high'], self.df['low'])
        self.df['SAR signal'] = 0
        self.df.loc[self.df['close'] > self.df['SAR'], 'SAR signal'] = 1
        self.df.loc[self.df['close'] < self.df['SAR'], 'SAR signal'] = -1
        return self.df
    
    @logging
    def on_balance_volume(self):
        self.df['OBV'] = talib.OBV(self.df['close'], self.df['volume'])
        self.df['OBV signal'] = 0
        self.df.loc[self.df['OBV'] > 0, 'OBV signal'] = 1
        self.df.loc[self.df['OBV'] < 0, 'OBV signal'] = -1
        return self.df
    
    @logging
    def calculate_momentum_system(self, window=14, threshold=0):
        momentum = talib.MOM(self.df['close'], timeperiod=window)
        self.df['Momentum'] = momentum
        self.df['Momentum signal'] = 0  # Инициализируем столбец 'Signal' нулями

        # Генерация сигналов на основе моментума и порогового значения
        self.df.loc[momentum > threshold, 'Momentum signal'] = 1  # Длинная позиция при положительном моментуме
        self.df.loc[momentum < -threshold, 'Momentum signal'] = -1  # Короткая позиция при отрицательном моментуме

        return self.df

    @logging
    def chaikin_money_flow(self, window=20):
        self.df['CMF'] = talib.ADOSC(self.df['high'], self.df['low'], self.df['close'], self.df['volume'], fastperiod=3, slowperiod=10)
        self.df['CMF signal'] = 0
        self.df.loc[self.df['CMF'] > 0, 'CMF signal'] = 1
        self.df.loc[self.df['CMF'] < 0, 'CMF signal'] = -1
        return self.df
    
    @logging
    def williams_percent_range(self, window=14):
        wpr = talib.WILLR(self.df['high'], self.df['low'], self.df['close'], timeperiod=window)
        self.df['WPR'] = wpr
        self.df['WPR signal'] = 0
        self.df.loc[self.df['WPR'] < -20, 'WPR signal'] = -1
        self.df.loc[self.df['WPR'] > -80, 'WPR signal'] = 1
        return self.df
    
    @logging
    def commodity_channel_index(self, window=20):
        self.df['CCI'] = talib.CCI(self.df['high'], self.df['low'], self.df['close'], timeperiod=window)
        self.df['CCI signal'] = 0
        self.df.loc[self.df['CCI'] > 100, 'CCI signal'] = -1
        self.df.loc[self.df['CCI'] < -100, 'CCI signal'] = 1
        return self.df
    
    @logging
    def rate_of_change(self, window=12):
        self.df['ROC'] = talib.ROC(self.df['close'], timeperiod=window)
        self.df['ROC signal'] = 0
        self.df.loc[self.df['ROC'] > 5, 'ROC signal'] = 1
        self.df.loc[self.df['ROC'] < -5, 'ROC signal'] = -1
        return self.df
