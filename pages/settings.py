import streamlit as st

from modules.web_core import WebCore
from modules.config import api_write, read_config, change_config
from modules.telegram import Telegram

web_core=WebCore()


st.set_page_config(layout='wide')

st.title('Настройки')
col1, col2 = st.columns(2)

if col1.button('Закрыть все позиции'):
    web_core.close_all_positions()

if col1.button('Отключить все стратегии'):
    web_core.deact_all_strats()

if col1.button('Очистить логер'):
    web_core.clear_logger()

data = web_core.logger_data()
col1.download_button(label="Скачать логер", data=data, file_name="debug.log")

if col1.button('Настроить биржу'):
    web_core.set_default_trade_settings()


col2.header('Блок API')
with col2.form('API_form'):
    # Функция сохранения АПИ ключей в конфиг
    TELE_API = st.text_input('Введите АПИ Телеграмм бота')
    CHAT_ID = st.text_input('Введите Ваш айди Телеграмм')
    REAL_OKX_API_KEY = st.text_input('Введите основной OKX API KEY')
    REAL_OKX_SECRET = st.text_input('Введите основной OKX Secret')
    REAL_OKX_PASSPHRAZE = st.text_input('Введите основной OKX Passphraze')
    DEMO_OKX_API_KEY = st.text_input('Введите демо OKX API KEY', help='Если демо торговля не нужна можно не вводить')
    DEMO_OKX_SECRET = st.text_input('Введите демо OKX Secret', help='Если демо торговля не нужна можно не вводить')
    DEMO_OKX_PASSPHRAZE = st.text_input('Введите демо OKX Passphraze', help='Если демо торговля не нужна можно не вводить')
    NGROK_TOKEN =st.text_input('Введите NGROK Token')
    if st.form_submit_button('Сохранить'):
        try:
            api_write(NGROK_TOKEN=NGROK_TOKEN,TELE_API=TELE_API,CHAT_ID=CHAT_ID,REAL_OKX_API_KEY=REAL_OKX_API_KEY,REAL_OKX_SECRET=REAL_OKX_SECRET,REAL_OKX_PASSPHRAZE=REAL_OKX_PASSPHRAZE,DEMO_OKX_API_KEY=DEMO_OKX_API_KEY,DEMO_OKX_SECRET=DEMO_OKX_SECRET,DEMO_OKX_PASSPHRAZE=DEMO_OKX_PASSPHRAZE)
            st.toast('АПИ Сохранены!', icon='✅')
        except Exception as e:
            st.toast('Ошибка сохранения', icon='❌')



col1.header('Блок конфигуратора')
cfg = read_config()
with col1.form('cfg_form'):
    DEMO_MODE = int(st.checkbox("Демо", value=cfg['DEMO_MODE']))
    START_BALANCE = st.number_input('Стартовый баланс', value=cfg['START_BALANCE'])
    TOKEN_LIST = st.text_area('Список возможных токенов', value=str(cfg['TOKEN_LIST'])[1:-1].replace("'", '')).split(", ")
    FEES = st.number_input('Процент комисии', max_value=1.0, value=cfg['FEES']*100)/100
    TASKS = st.text_input('Времена для оповещения', value=str(cfg['TASKS'])[1:-1].replace("'", '')).split(", ")
    if st.form_submit_button('Сохранить'):
        change_config(DEMO_MODE=DEMO_MODE, START_BALANCE=START_BALANCE, TOKEN_LIST=TOKEN_LIST, FEES=FEES, TASKS=TASKS)
        tele = Telegram()
        tele.telegram_notification()