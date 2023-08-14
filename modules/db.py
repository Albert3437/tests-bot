import sqlite3
from modules.logger import logging

class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect('absolut.db')


    @logging
    def read_db(self, db_name):
        cursor = self.conn.execute(f"SELECT * FROM {db_name}")
        return cursor.fetchall()
    

    @logging
    def read_header(self, db_name):
        data = self.conn.execute(f'PRAGMA table_info({db_name})')
        column_headers = [row[1] for row in data.fetchall()]
        return column_headers


    @logging
    def read_dict_db(self, db_name):
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
        self.conn.execute(f'DROP TABLE {db_name}')


    @logging
    def clear_db(self, db_name):
        self.conn.execute(f"DELETE FROM {db_name}")
        self.conn.commit()


    @logging
    def close_db(self):
        self.conn.close()



class DealsDataBase(DataBase):
    def __init__(self, db_name:str):
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
        self.conn.execute(f'INSERT INTO {self.db_name} (order_id, open_timestamp, open_price, deal_type, status) VALUES (?,?,?,?,?)',(order_id, open_timestamp, open_price, deal_type, status))
        self.conn.commit()


    @logging
    def close_deal(self, close_timestamp=0, close_price=0, percent=0, commision=0):
        deals = self.read_dict_db(self.db_name)
        id = deals[-1]['id']
        self.conn.execute(f"UPDATE {self.db_name} SET (close_timestamp, close_price, percent, commision) = (?,?,?,?) WHERE id = {id}", (close_timestamp, close_price, percent, commision))
        self.conn.commit()


    @logging
    def read_deals(self, db_name = None):
        if db_name == None:
            db_name = self.db_name
        deals = self.read_dict_db(db_name)
        return deals
    

    @logging
    def clear_deals(self):
        self.clear_db(self.db_name)