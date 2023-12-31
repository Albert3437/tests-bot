import streamlit as st

from modules.config import add_new_strat
from modules.db import DealsDataBase
from modules.config import *


st.set_page_config(layout='centered')


st.header("Добавление новой стратегии")

with st.form("add_form"):

    name = st.text_input("Название")
    indicator_list = st.multiselect(
        'Выберите индикаторы',
        INDICATOR_LIST)
    arch = st.selectbox("Архитектура", ARCH_LIST)
    strat_type = st.selectbox("Тип стратегии", ARCH_TYPE, help="classic это закрытие сделок при смене тренда, all signal это закрытие сделок по всем сигналам")
    stop_loss = st.number_input("Стоп лосс", help='0.98 это 2% для стоп лосса, если не нужен тогда не надо указывать')
    take_profit = st.number_input("Тейк профит", help='1.02 это 2% для тейк профита, если не нужен тогда не надо указывать')
    leverage = st.number_input("Левередж", help='Указать кредитное плече')
    balance = st.number_input("Стартовый баланс")
    interval = st.selectbox("Интервал", INTERVALS) 
    token = st.selectbox("Токен", TOKEN_LIST ,help='Пример токена: BTC')
    demo_mode = st.checkbox('Демо режим', value=True, help='Если отмечено то торговля будет идти через демо счет')

    if st.form_submit_button("Добавить"):
        try:
            db = DealsDataBase(name)
            add_new_strat(name=name, indicator_list=indicator_list, demo_mode=demo_mode, status='off', arch=arch, strat_type=strat_type, balance=balance, interval=interval, token=token, stop_loss=stop_loss, take_profit=take_profit, leverage=leverage)
            st.success("Стратегия успешно добавлена")
        except Exception:
            st.error("Ошибка при добавлении стратегии")
