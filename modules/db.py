import sqlite3

from modules.logger import logging

class DataBase:
    def __init__(self):
        # Наследуемый класс для работы с базой данных
        self.conn = sqlite3.connect('absolut.db')


    @logging
    def read_db(self, db_name):
        # Чтение данных с таблицы в бд
        cursor = self.conn.execute(f"SELECT * FROM {db_name}")
        return cursor.fetchall()
    

    @logging
    def read_header(self, db_name):
        # Чтение заголовков с таблицы в бд
        data = self.conn.execute(f'PRAGMA table_info({db_name})')
        column_headers = [row[1] for row in data.fetchall()]
        return column_headers


    @logging
    def read_dict_db(self, db_name):
        # Универсальная функция для чтения таблицы в бд в формате списка со словарями
        head = self.read_header(db_name)
        deals = self.read_db(db_name)
        dict_deals = []
        for deal in deals:
            dict_deal = {}
            for i, amount in enumerate(deal):
                dict_deal[head[i]] = amount
            dict_deals.append(dict_deal)
        return dict_deals


    @logging
    def remove_table(self, db_name):
        # Удаление таблицы по имени
        self.conn.execute(f'DROP TABLE {db_name}')


    @logging
    def clear_db(self, db_name):
        # Удаление всех данных из таблицы
        self.conn.execute(f"DELETE FROM {db_name}")
        self.conn.commit()


    @logging
    def close_db(self):
        # Закрытие связи с бд
        self.conn.close()



class DealsDataBase(DataBase):
    def __init__(self, db_name:str):
        # Класс для более узконапраленой работы с структурой данных в таблице
        super().__init__()
        self.db_name = db_name 
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
	            open_timestamp INTEGER,
                open_price REAL,
                deal_type TEXT,
                status TEXT,
                close_timestamp INTEGER,
                close_price REAL,
                percent REAL,
                commision REAL
                )
            '''.format(self.db_name))


    @logging
    def open_deal(self, order_id = 0, open_timestamp = 0, open_price = 0, deal_type = 0, status = 0):
        # Функция для записи данных по открытию сделки
        self.conn.execute(f'INSERT INTO {self.db_name} (order_id, open_timestamp, open_price, deal_type, status) VALUES (?,?,?,?,?)',(order_id, open_timestamp, open_price, deal_type, status))
        self.conn.commit()


    @logging
    def close_deal(self, close_timestamp=0, close_price=0, percent=0, commision=0):
        # Функция для записи данных по закрытию сделки
        deals = self.read_dict_db(self.db_name)
        id = deals[-1]['id']
        self.conn.execute(f"UPDATE {self.db_name} SET (close_timestamp, close_price, percent, commision) = (?,?,?,?) WHERE id = {id}", (close_timestamp, close_price, percent, commision))
        self.conn.commit()


    @logging
    def read_deals(self, db_name = None):
        # Чтение всех сделок в формате списка со словарями
        if db_name == None:
            db_name = self.db_name
        deals = self.read_dict_db(db_name)
        return deals
    

    @logging
    def clear_deals(self, db_name = None):
        # Очищение таблицы инициируемой в классе
        if db_name == None:
            db_name = self.db_name
        self.clear_db(self.db_name)