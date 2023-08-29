import json
import time

import okx.MarketData as Market
import okx.Account as Account
import okx.Trade as Trade

from modules.logger import logging



# У всех функция прописан функционал повторных запросов на сервер при ошибке через бесконечный цикл
class okxTrade:
    def __init__(self, flag='1'):
        # Класс для работы с АПИ биржи ОКХ
        with open('configs/API.json', 'r') as f:
            keys = json.load(f)
        API_KEY = keys['OKX_API_KEY']
        SECRET = keys['OKX_SECRET']
        PASSPHRAZE = keys['OKX_PASSPHRAZE']
        self.tradeAPI = Trade.TradeAPI(API_KEY, SECRET, PASSPHRAZE, False, flag)
        self.accountAPI = Account.AccountAPI(API_KEY, SECRET, PASSPHRAZE, False, flag)
        self.marketAPI = Market.MarketAPI(API_KEY, SECRET, PASSPHRAZE, False, flag)


    @logging
    def cancel_order(self, token, ordId):
        # Ликвидация ордера
        result = self.tradeAPI.cancel_order(instId=f'{token}-USDT-SWAP', ordId=ordId)
        return result


    @logging
    def balance(self, token:str):
        # Получение баланса
        for _ in range(5):
            try:
                r = self.accountAPI.get_account_balance()
                r = r['data'][0]['details']
                for i in r:
                    if i['ccy'] == token:
                        balance = i['availBal']
                return balance
            except Exception as e:
                time.sleep(5)
        return 'eror'
    

    @logging
    def long(self, token, amount, price, side="buy", ordType='limit'):
        # Открытие лонговой сделки по маркет цене
        for _ in range(5):
            try:
                result = self.tradeAPI.place_order(
                    instId=f"{token}-USDT-SWAP",
                    tdMode="cross",
                    side=side,
                    posSide="long",
                    ordType=ordType,
                    px=price,
                    sz=amount # 1 == 0.001 BTC , i dont know why it is so
                )
                return result
            except Exception as e:
                time.sleep(5)
        return 'failure'


    @logging
    def short(self, token, amount, price, side="sell", ordType='limit'):
        # Открытие шортовой сделки по маркет цене
        for _ in range(5):
            try:
                result = self.tradeAPI.place_order(
                    instId=f"{token}-USDT-SWAP",
                    tdMode="cross",
                    side=side,
                    posSide="short",
                    ordType=ordType,
                    px=price,
                    sz=amount # 1 == 0.001 BTC , i dont know why it is so
                )
                return result
            except Exception as e:
                time.sleep(5)
        return 'failure'
    

    @logging
    def set_leverage(self, symbol, leverage):
        # Установка плечей, в okx она находится отдельно
        result = self.accountAPI.set_leverage(
            instId = symbol, # Set symbol Example: "ETH-USDT-SWAP"
            lever = leverage, # Set leverage Example: "1"
            mgnMode = "cross", # margin mode 
        )
        return result


    @logging
    def close_position(self,token,side):
        # Закрытие позиций по нужному напрвлению и паре
        for _ in range(5):
            try:
                result = self.tradeAPI.close_positions(
                    instId=f"{token}-USDT-SWAP", # Example "ETH"
                    posSide=side,
                    mgnMode="cross"
                )
                return result
            except Exception as e:
                time.sleep(5)
        return 'failure'
    

    @logging
    def position_list_history(self):
        # История по позициям
        for _ in range(5):
            try:
                return self.accountAPI.get_positions_history()['data']
            except:
                time.sleep(5)
        return 'failure'


    @logging
    def order_history(self):
        # История по ордерам
        for _ in range(5):
            try:
                r = self.tradeAPI.get_orders_history('SWAP')
                return r
            except Exception as e:
                time.sleep(5)
        return 'failure'


    @logging
    def last_order(self, token, order_id):
        # История по ордерам
        for _ in range(5):
            try:
                r = self.tradeAPI.get_order(f'{token}-USDT-SWAP', ordId=order_id)
                return r
            except Exception as e:
                time.sleep(5)
        return 'failure'


    @logging
    def position_list_active(self):
        # Активные позиции
        for _ in range(5):
            try:
                r = self.accountAPI.get_positions()
                return r['data']
            except Exception as e:
                time.sleep(5)
        return 'failure'    


    @logging
    def actual_price(self, token):
        # Получение актуальной цены
        for _ in range(5):
            try:
                r = self.marketAPI.get_ticker(f'{token}-USDT')
                return float(r['data'][0]['last'])
            except Exception as e:
                time.sleep(5)
        return 1