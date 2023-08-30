import threading

from flask import Flask, request

from arch.classic import Strategy
from modules.web_core import WebCore
from modules.logger import *


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


if __name__ == '__main__':
    app.run(debug=True, port=5002)
