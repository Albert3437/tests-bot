import streamlit as st
from modules.web_core import WebCore
from modules.config import api_write


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


col2.header('Блок API')
with col2.form('db_form'):
    # Функция сохранения АПИ ключей в конфиг
    TELE_API = st.text_input('Введите АПИ Телеграмм бота')
    CHAT_ID = st.text_input('Введите Ваш айди Телеграмм')
    OKX_API_KEY = st.text_input('Введите OKX API KEY')
    OKX_SECRET = st.text_input('Введите OKX Secret')
    OKX_PASSPHRAZE = st.text_input('Введите OKX Passphraze')
    NGROK_TOKEN =st.text_input('Введите NGROK Token')
    if st.form_submit_button('Сохранить'):
        try:
            api_write(NGROK_TOKEN=NGROK_TOKEN,TELE_API=TELE_API,CHAT_ID=CHAT_ID,OKX_API_KEY=OKX_API_KEY,OKX_SECRET=OKX_SECRET,OKX_PASSPHRAZE=OKX_PASSPHRAZE)
            st.toast('АПИ Сохранены!', icon='✅')
        except Exception as e:
            st.toast('Ошибка сохранения', icon='❌')



