import os
import json
from modules.logger import *
#from modules.metrics import *




file_path = 'configs/config.json'
folder_path = 'configs/strategies/'
if not os.path.exists(folder_path):
    os.mkdir(folder_path)
else:
    pass
if not os.path.exists(file_path):
    with open(file_path, 'w') as f:
        data = {"DEMO_MODE": 0, "START_BALANCE": 507, "TOKEN_LIST": ["DOGE", "SOL", "DOT", "AVAX", "ADA", "BTC", "LTC", "ETH", "TRX"], "COEF": {"DOGE": 0.1, "SOL": 10, "DOT": 10, "AVAX": 10, "ADA": 1, "BTC": 1000, "LTC": 1000, "ETH": 100, "TRX": 0.001}, "INDICATOR_LIST": ["ADX", "Bollinger", "CCI", "CMF", "Ichimoku", "MACD", "Momentum", "OBV", "SAR", "ROC", "RSI", "SMA", "Stochastic", "WPR", "TR", "ATR", "AD", "AA", "TS", "DM", "PPO", "PPOP", "TSI", "RS", "ADO", "MFI"], "INTERVALS": ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h"], "ARCH_LIST": ["classic", "classic reverse"], "ARCH_TYPE": ["classic", "all signals"], "INTERVALS_DICT": {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "12h": 43200}, "INDICATOR_DICT": {"ADX": "ta.ADI()", "Bollinger": "ta.bollinger()", "CCI": "ta.CCI()", "CMF": "ta.CMF()", "Ichimoku": "ta.ichimoku()", "MACD": "ta.macd()", "Momentum": "ta.momentum()", "OBV": "ta.OBV()", "SAR": "ta.PSAR()", "ROC": "ta.ROC()", "RSI": "ta.RSI()", "SMA": "ta.MA()", "Stochastic": "ta.stochastic()", "WPR": "ta.WPR()", "TR": "ta.TR()", "ATR": "ta.ATR()", "AD": "ta.AD()", "AA": "ta.AA()", "TS": "ta.TS()", "DM": "ta.DM()", "PPO": "ta.PPO()", "PPOP": "ta.PPOP()", "TSI": "ta.TSI()", "RS": "ta.RS()", "ADO": "ta.ADO()", "MFI": "ta.MFI()"}, "FEES": 0.0005, "STRATS": []}
        json.dump(data,f)



def read(filepath):
    # Чтение json файла
    with open(filepath, 'r') as f:
        file = json.load(f)
    return file


@logging
def read_config():
    return read('configs/config.json')


@logging
def read_strat_names():
    cfg = read_config()
    strat_names = cfg['STRATS']
    return strat_names


@logging
def read_strategies():
    strats = []
    strat_names = read_strat_names()
    for name in strat_names:
        strat = read(f'configs/strategies/{name}.json')
        strats.append(strat)
    return strats


@logging
def read_some_strat(strat_name):
    # Чтение определенной стратегии
    return read(f'configs/strategies/{strat_name}.json')


@logging
def read_API():
    # Чтение Файла АПИ
    return read('configs/API.json')


@logging
def save_dump(filename, data):
    # Сохранение произвольного файла json
    with open(filename, 'w') as f:
        file = json.dump(data,f)
    return file


@logging
def change_config(**kwargs):
    print(kwargs)
    cfg = read_config()
    for key, value in kwargs.items():
        cfg[key] = value
    save_dump('configs/config.json', cfg)


@logging
def add_new_strat(name:str, indicator_list:list, interval:str, arch:str, strat_type:str, balance:int, token:str, demo_mode:bool=True, status:int=None, *, leverage:int=1, stop_loss:float=None, take_profit:float=None, timing_status:float=0):
    # Добавление новой стратегии
    strat_names = read_strat_names()
    strat = {
            "name":name,
            "indicator_list":indicator_list,
            "demo_mode":demo_mode,
            "status":status,
            "arch":arch,
            "strat_type":strat_type,
            "leverage":leverage,
            "stop_loss":stop_loss,
            "take_profit":take_profit,
            "balance":balance,
            "interval":interval,
            "token":token,
            "timing_status":timing_status
            }
    save_dump(f'configs/strategies/{name}.json', strat)
    if name not in strat_names:
        strat_names.append(name)
    change_config(STRATS = strat_names)


@logging
def change_strat(strat_name, **kwargs):
    # Изменение определенной стратегии
    strat = read_some_strat(strat_name)
    for key, value in kwargs.items():
        if value:
            strat[key] = value
        if key == 'name':
            strat_names = read_strat_names()
            strat_names[strat_names.index(strat_name)] = value
            change_config(STRATS = strat_names)
            os.remove(f'configs/strategies/{strat_name}.json')
            strat_name = value
    save_dump(f'configs/strategies/{strat_name}.json', strat)


@logging
def remove_strat(strat_name):
    # Удаление определенной стратегии
    file_path = f'configs/strategies/{strat_name}.json'
    if os.path.exists(file_path):
        strat_names = read_strat_names()
        os.remove(file_path)
        strat_names.remove(strat_name)
        change_config(STRATS = strat_names)
    else:
        pass


@logging
def api_write(**kwargs):
    # Измененние АПИ файла
    api = read_API()
    for key, value in kwargs.items():
        if value != None:
            api[key] = value
    save_dump('configs/API.json', api)

cfg = read_config()
DEMO_MODE = cfg['DEMO_MODE']
START_BALANCE = cfg['START_BALANCE']
TOKEN_LIST = cfg['TOKEN_LIST']
COEF = cfg['COEF']
INDICATOR_LIST = cfg['INDICATOR_LIST']
INTERVALS = cfg['INTERVALS']
ARCH_LIST = cfg['ARCH_LIST']
ARCH_TYPE = cfg['ARCH_TYPE']
INTERVALS_DICT = cfg['INTERVALS_DICT']
INDICATOR_DICT = cfg['INDICATOR_DICT']
FEES = cfg['FEES']
STRATS = cfg['STRATS']