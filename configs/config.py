# Это файл с перечеслением в нем всех возможных параметров, используется для конфигуратора в веб приложении

TOKEN_LIST = ['DOGE', 'SOL', 'DOT', 'AVAX', 'MATIC', 'ADA', 'BTC', 'LTC', 'ETH', 'TRX']
COEF = {'DOGE':1, 'SOL':10, 'DOT':10, 'AVAX':10, 'ADA':1, 'BTC':1000, 'LTC':1000, 'ETH':100, 'TRX':0.001}
INDICATOR_LIST = ['ADX', 'Bollinger', 'CCI', 'CMF', 'Ichimoku', 'MACD', 'Momentum', 'OBV', 'SAR', 'ROC', 'RSI', 'SMA', 'Stochastic', 'WPR', 'TR', 'ATR', 'AD', 'AA', 'TS', 'DM', 'PPO', 'PPOP', 'TSI', 'RS', 'ADO', 'MFI']
INTERVALS = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h']
ARCH_LIST = ['classic', "classic reverse"]
ARCH_TYPE = ['classic', 'all signals']
INTERVALS_DICT = {'1m':60, '5m':300, '15m':900, '30m':1800, '1h':3600, '2h':7200, '4h':14400, '6h':21600, '12h':43200}
INDICATOR_DICT = {'ADX':'ta.average_directional_index()',
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
                    'WPR':'ta.williams_percent_range()',
                    'TR':'ta.TR()',
                    'ATR':'ta.ATR()',
                    'AD':'ta.AD()',
                    'AA':'ta.AA()',
                    'TS':'ta.TS()',
                    'DM':'ta.DM()',
                    'PPO':'ta.PPO()',
                    'PPOP':'ta.PPOP()',
                    'TSI':'ta.TSI()',
                    'RS':'ta.RS()',
                    'ADO':'ta.ADO()',
                    'MFI':'ta.MFI()'}
FEES = 0.0005