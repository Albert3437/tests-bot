import streamlit as st

from modules.web_core import WebCore
from modules.metrics import Metrics

st.set_page_config(layout='wide')

web_core = WebCore()
metric = Metrics()
st.title('Главная')

col1, col2 = st.columns(2)
col1.metric("Полный баланс", f'{metric.total_balance()}$')
col2.metric("Количество стратегий", web_core.number_of_strat())

st.subheader('Список активных стратегий')
st.dataframe(web_core.strategy_list_active())

st.subheader('Люгер')
st.dataframe(web_core.logger_data())