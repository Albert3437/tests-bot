import streamlit as st

from modules.web_core import WebCore
from modules.metrics import Metrics
from modules.config import *

st.set_page_config(layout='wide')

web_core = WebCore()
metric = Metrics()
st.title('Главная')

col1, col2, col3 = st.columns(3)

total_balance, profit_percent = web_core.get_total_balance()
col1.metric("Полный баланс", f'{total_balance}$', f'{profit_percent}%')
col2.metric("Количество стратегий", web_core.number_of_strat())
col3.metric("Всего комиссий", f'{web_core.get_all_fees()}$')

st.subheader('Список активных стратегий')
st.dataframe(web_core.strategy_list_active())


col1, col2 = st.columns(2)

col1.subheader('График общего баланса')
col1.line_chart(web_core.get_balance_list())

col2.subheader('Активные сделки')
col2.dataframe(web_core.get_active_deals())

st.subheader('Люгер')
st.dataframe(web_core.logger_df())

st.subheader('Котировки')
token = str(st.selectbox('Выбор токена', TOKEN_LIST))

html_code = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
    <div id="tradingview_83424"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget(
    {{
    "autosize": true,
    "symbol": "BINANCE:{token}USDT",
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "ru",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_legend": true,
    "allow_symbol_change": true,
    "save_image": false,
    "container_id": "tradingview_83424"
    }}
    );
    </script>
    </div>
    <!-- TradingView Widget END -->
    """

st.components.v1.html(html_code.format(token=token))
