import os
import json
from modules.logger import *
#from modules.metrics import *



@logging
def init_strats():
    folder_path = 'configs/strategies'

    # Проверяем, существует ли папка, и если нет, то создаем её
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    else:
        pass


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
def add_new_strat(name:str, indicator_list:list, interval:str, arch:str, strat_type:str, balance:int, token:str, demo_mode:bool=True, status:int=None, *, leverage:int=1, stop_loss:float=None, take_profit:float=None, timing_status:float=None):
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
    strat_names.append(name)
    change_config(STRATS = strat_names)


@logging
def change_strat(strat_name, **kwargs):
    # Изменение определенной стратегии
    strat = read_some_strat(strat_name)
    for key, value in kwargs.items():
        if value:
            strat[key] = value
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