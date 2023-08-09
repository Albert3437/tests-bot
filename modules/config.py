import json
from modules.metrics import *



@logging
def init_settings():
    try:
        with open('configs/strategies.json', 'r') as f:
            json.load(f)
    except Exception:
            with open('configs/strategies.json', 'w') as f:
                json.dump([],f)


def read(filepath):
    with open(filepath, 'r') as f:
        file = json.load(f)
        return file


@logging
def read_strategies():
    return read('configs/strategies.json')


@logging
def read_some_strat(strat_name):
    strats = read_strategies()
    for strat in strats:
        if strat['name'] == strat_name:
            if strat['stop_loss'] == 'None':
                strat['stop_loss'] = 0
            if strat['take_profit'] == 'None':
                strat['take_profit'] = 0
            return strat


@logging
def read_API():
    return read('configs/API.json')


@logging
def save_dump(filename, data):
    with open(filename, 'w') as f:
        file = json.dump(data,f)
        return file


@logging
def add_new_strat(name:str, indicator_list:list, interval:str, arch:str, strat_type:str, balance:int, token:str, demo_mode:bool=True, status:int=None, *, leverage:int=1, stop_loss:float=None, take_profit:float=None):
    strats = read_strategies()
    strats.append({
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
            "token":token
            })
    save_dump('configs/strategies.json', strats)


@logging
def change_strat(strat_name, **kwargs):
    strats = read_strategies()
    for strat in strats:
        if strat['name'] == strat_name:
            for key, value in kwargs.items():
                if value != None:
                    strat[key] = value
    save_dump('configs/strategies.json', strats)


@logging
def remove_strat(strat_name):
    strats = read_strategies()
    for strat in strats:
        if strat['name'] == strat_name:
            strats.remove(strat)
    save_dump('configs/strategies.json', strats)


@logging
def api_write(**kwargs):
    api = read_API()
    for key, value in kwargs.items():
        if value != None:
            api[key] = value
    save_dump('configs/API.json', api)