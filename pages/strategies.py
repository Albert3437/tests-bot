import streamlit as st

from modules.web_core import WebCore
from modules.config import *
from configs.config import *



st.set_page_config(layout='wide')


def strategy_list():
    strat_names = []
    strats = read_strategies()
    for strat in strats:
        strat_names.append(strat['name'])
    return strat_names


strat_name = st.selectbox(
    'Выберите стратегию',
    strategy_list())
web_core = WebCore(strat_name)


col1, col2 = st.columns(2)
strat = read_some_strat(strat_name)

if strat['status'] == 'on':
    col1.success('Запущенa')
else:
    col1.error('Выключенa')

if web_core.work_status():
    col2.success('В порядке')
elif strat['status'] == 'off':
    col2.error('Выключенa')
else:
    col2.error('Ошибка')


balance_amount, profit_percent = web_core.balance(strat_name)
deals_number, profit_deals_percent = web_core.number_of_deals()
total_fee = web_core.get_total_fees()

col1, col2, col3 = st.columns(3)
col1.metric('Balance', f'{balance_amount} $', f'{profit_percent} %')
col2.metric('Deals', deals_number, f'{profit_deals_percent} %')
col3.metric('Fee`s', f'{total_fee} $')

st.subheader('Список сделок')
st.dataframe(web_core.deals_df())

col1, col2 = st.columns(2)

col1.subheader('Управление')
if col1.button('ON/OFF'):
    result = web_core.activate_button()
    st.toast(result)

csv_data = web_core.convert_df(web_core.deals_df())
col1.download_button(label="Скачать бд сделок", data=csv_data, file_name=f'{strat_name}.csv', mime='text/csv',)

if col1.button('Очистить базу данных'):
    result = web_core.clear_db()
    st.toast(result)

if col1.button('Удалить стратегию'):
    result = web_core.remove_strategy()
    st.toast(result)

col2.subheader("Изменение стратегии")

with col2.form("add_form"):
# НАСТРОИТЬ ОТОБРАЖЕНИЕ ВСЕХ СТАРТОВЫХ ПОЗИЦИЙ
    
    name = st.text_input("Название", value=strat['name'])
    indicator_list = st.multiselect('Выберите индикаторы',INDICATOR_LIST, default=strat['indicator_list'])
    arch = st.selectbox("Архитектура", ARCH_LIST, index=ARCH_LIST.index(strat['arch']))
    strat_type = st.selectbox("Тип стратегии", ARCH_TYPE, help="classic это закрытие сделок при смене тренда, all signal это закрытие сделок по всем сигналам", index=ARCH_TYPE.index(strat['strat_type']))
    stop_loss = st.number_input("Стоп лосс", help='0.98 это 2% для стоп лосса, если не нужен тогда не надо указывать', value=strat['stop_loss'])
    take_profit = st.number_input("Тейк профит", help='1.02 это 2% для тейк профита, если не нужен тогда не надо указывать', value=0)
    balance_ = st.number_input("Стартовый баланс", value=strat['balance'])
    interval = st.selectbox("Интервал", INTERVALS, index=INTERVALS.index(strat['interval'])) 
    token = st.selectbox("Токен", TOKEN_LIST ,help='Пример токена: BTC', index=TOKEN_LIST.index(strat['token']))
    demo_mode = st.checkbox('Демо режим', value=bool(strat['demo_mode']), help='Если отмечено то торговля будет идти через демо счет')

    if st.form_submit_button("Изменить"):
        try:
            change_strat(strat_name=strat_name, name=name, indicator_list=indicator_list, demo_mode=demo_mode, arch=arch, strat_type=strat_type, balance=balance_, interval=interval, token=token, stop_loss=stop_loss, take_profit=take_profit)
            st.success("Стратегия успешно измененна", icon="✅")
        except Exception:
            st.error("Ошибка при изменении стратегии", icon="❌")
