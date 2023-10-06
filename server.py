import threading
import sys
import signal

from flask import Flask, request

from arch.classic import Strategy
from modules.logger import *
from modules.config import *


app = Flask(__name__)

threads = {}


@logging
def start_strategy(strat_name):
    # Запуск потока для стратегии
    strat = Strategy(strat_name)
    thread = threading.Thread(target=strat.run)
    threads[strat_name] = (strat, thread)
    thread.start()
    logger.info(threads)


@logging
def stop_strategy(strat_name):
    # Отключение потока для стратегии
    if strat_name in threads:
        strat, thread = threads[strat_name]
        strat.stop()
        thread.join()
        del threads[strat_name]
        logger.info(threads)


@app.route('/start_strat', methods=['POST'])
def start_strat():
    try:
        params = dict(request.form)
        start_strategy(params['strat_name'])
        return 'Started'
    except Exception as e:
        return e
    

@app.route('/stop_strat', methods=['POST'])
def stop_strat():
    try:
        params = dict(request.form)
        stop_strategy(params['strat_name'])
        return 'Stoped'
    except Exception as e:
        return e


def handle_interrupt(signum, frame):
    strats = read_strategies()
    for strat in strats:
        change_strat(strat['name'], status = 'off')
    print("Программа завершена пользователем.")
    sys.exit(1)


def start_handler():
    for strat_name in STRATS:
        strat = read_some_strat(strat_name)
        if strat['status'] == 'on':
            start_strategy(strat_name)


if __name__ == '__main__':
    start_handler()
    signal.signal(signal.SIGINT, handle_interrupt)
    app.run(debug=True, port=5002)
