import talib
import pandas as pd 
from modules.logger import logging



class TechnicalIndicators:
    def __init__(self, df):
        # Класс для вычисления всех индикаторов и записи сразу сигналов в Датафрейм
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


    @logging
    def TR(self):
        self.df['TrueRange'] = talib.TRANGE(self.df['high'], self.df['low'], self.df['close'])

        # Добавляем столбец для сигналов на основе True Range
        self.df['TR signal'] = 0
        self.df.loc[self.df['TrueRange'] > 25, 'TR signal'] = 1
        self.df.loc[self.df['TrueRange'] < 20, 'TR signal'] = -1

        return self.df


    @logging
    def ATR(self, window = 12):
        self.df['ATR'] = talib.ATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=window)

        # Добавляем столбец для сигналов на основе ATR
        self.df['ATR signal'] = 0
        self.df.loc[self.df['ATR'] > 25, 'ATR signal'] = 1
        self.df.loc[self.df['ATR'] < 20, 'ATR signal'] = -1

        return self.df


    @logging
    def AD(self):
        self.df['AD'] = talib.AD(self.df['high'], self.df['low'], self.df['close'], self.df['volume'])

        # Добавляем столбец для сигналов на основе A/D
        self.df['AD signal'] = 0
        self.df.loc[self.df['AD'] > self.df['AD'].shift(1), 'AD signal'] = 1
        self.df.loc[self.df['AD'] < self.df['AD'].shift(1), 'AD signal'] = -1

        return self.df


    @logging
    def AA(self):
        # Рассчитываем индекс средней амплитуды (AA) с помощью библиотеки talib
        self.df['AA'] = talib.AVGPRICE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

        # Добавляем столбец для сигналов на основе AA
        self.df['AA signal'] = 0
        self.df.loc[self.df['AA'] > self.df['AA'].shift(1), 'AA signal'] = 1
        self.df.loc[self.df['AA'] < self.df['AA'].shift(1), 'AA signal'] = -1

        return self.df


    @logging
    def TS(self):
        self.df['EMA20'] = talib.EMA(self.df['close'], timeperiod=20)  

        # Преобразуем 'close' к float
        self.df['close'] = self.df['close'].astype(float)

        # Теперь вычитаем  
        self.df['TS'] = self.df['EMA20'] - self.df['close']

        # Добавляем столбец с сигналами 
        self.df['TS signal'] = 0

        # Присваиваем значения сигналов
        self.df.loc[self.df['TS'] > 0, 'TS signal'] = 1  # EMA выше Close - сила тренда есть 
        self.df.loc[self.df['TS'] < 0, 'TS signal'] = -1 # EMA ниже Close - сила тренда слабая

        return self.df


    @logging
    def DM(self):
        self.df['TR'] = talib.TRANGE(self.df['high'], self.df['low'], self.df['close'])

        self.df['high'] = self.df['high'].astype(float)
        self.df['low'] = self.df['low'].astype(float)

        # Находим положительное и отрицательное направленное движение  
        self.df['PDM'] = self.df['high'] - self.df['high'].shift(1)
        self.df['NDM'] = self.df['low'].shift(1) - self.df['low']

        # Обнуляем отрицательные значения
        self.df.loc[self.df['PDM'] < 0, 'PDM'] = 0  
        self.df.loc[self.df['NDM'] < 0, 'NDM'] = 0

        # Добавляем сигналы
        self.df['DM signal'] = 0
        self.df.loc[self.df['PDM'] > self.df['NDM'], 'DM signal'] = 1
        self.df.loc[self.df['PDM'] < self.df['NDM'], 'DM signal'] = -1 

        return self.df


    @logging
    def PPO(self):
        self.df['EMA_12'] = talib.EMA(self.df['close'], timeperiod=12)
        self.df['EMA_26'] = talib.EMA(self.df['close'], timeperiod=26)

        # Находим PPO как разницу между EMA
        self.df['PPO'] = (self.df['EMA_12'] - self.df['EMA_26']) / self.df['EMA_26'] * 100

        # Добавляем сигнал
        self.df['PPO_signal'] = 0
        self.df.loc[self.df['PPO'] > 0, 'PPO signal'] = 1  
        self.df.loc[self.df['PPO'] < 0, 'PPO signal'] = -1

        return self.df


    @logging
    def PPOP(self):
        # Рассчитаем EMA с периодами 12 и 26
        self.df['EMA_12'] = talib.EMA(self.df['close'], timeperiod=12)  
        self.df['EMA_26'] = talib.EMA(self.df['close'], timeperiod=26)

        # Находим разницу между EMA
        self.df['Diff'] = self.df['EMA_12'] - self.df['EMA_26'] 

        # Рассчитываем PPO%
        self.df['PPOP'] = self.df['Diff'] / self.df['EMA_26']

        # Добавляем сигналы
        self.df['PPOP signal'] = 0
        self.df.loc[self.df['PPOP'] > 0, 'PPOP signal'] = 1
        self.df.loc[self.df['PPOP'] < 0, 'PPOP signal'] = -1

        return self.df


    @logging
    def TSI(self):
        # Рассчитываем два EMA с периодами 25 и 13
        self.df['EMA_25'] = talib.EMA(self.df['close'], timeperiod=25)
        self.df['EMA_13'] = talib.EMA(self.df['close'], timeperiod=13)

        # Находим разницу между EMA
        self.df['Diff'] = self.df['EMA_25'] - self.df['EMA_13']

        # Рассчитываем EMA разницы с периодом 13  
        self.df['DEA'] = talib.EMA(self.df['Diff'], timeperiod=13)

        # Находим TSI
        self.df['TSI'] = self.df['Diff'] / self.df['DEA'] * 100

        # Добавляем сигнал
        self.df['TSI signal'] = 0
        self.df.loc[self.df['TSI'] > 0, 'TSI signal'] = 1
        self.df.loc[self.df['TSI'] < 0, 'TSI signal'] = -1

        return self.df


    @logging
    def RS(self):
        # Рассчитываем простую скользящую среднюю за 14 периодов 
        self.df['SMA_14'] = talib.SMA(self.df['close'], timeperiod=14)

        # Находим отношение Close/SMA_14
        self.df['RS'] = self.df['close'] / self.df['SMA_14'] 

        # Добавляем сигналы
        self.df['RS signal'] = 0
        self.df.loc[self.df['RS'] > 1, 'RS signal'] = 1 # Close выше SMA_14 
        self.df.loc[self.df['RS'] < 1, 'RS signal'] = -1 # Close ниже SMA_14

        return self.df


    @logging    
    def ADO(self):
        # Рассчитываем ADO
        self.df['ADO'] = talib.AD(high=self.df['high'], low=self.df['low'], close=self.df['close'], volume=self.df['volume'])

        # Добавляем сигнальную колонку
        self.df['ADO signal'] = 0

        # Сигнал на покупку, если ADO растет
        self.df.loc[self.df['ADO'] > self.df['ADO'].shift(1), 'ADO signal'] = 1  

        # Сигнал на продажу, если ADO падает
        self.df.loc[self.df['ADO'] < self.df['ADO'].shift(1), 'ADO signal'] = -1

        return self.df


    @logging
    def MFI(self):
        # Рассчитываем MFI через talib
        self.df['MFI'] = talib.MFI(self.df['high'], self.df['low'], self.df['close'], self.df['volume'], timeperiod=14)

        # Добавляем сигнал
        self.df['MFI signal'] = 0
        self.df.loc[self.df['MFI'] > 80, 'MFI signal'] = -1  
        self.df.loc[self.df['MFI'] < 20, 'MFI signal'] = 1

        return self.df