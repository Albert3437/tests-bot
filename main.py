from threading import Thread
from pyngrok import ngrok

from modules.config import read_API
from modules.telegram import Telegram
from modules.config import init_settings
from modules.web_core import WebCore


web_core = WebCore()

web_core.set_default_trade_settings()
init_settings()
tele = Telegram()


def grok():
    # Запуск ngrok для работы веб сервера на открытом порте(Ссылка оправляется в телеграмм)
        ngrok.set_auth_token(read_API()['NGROK_TOKEN'])
        url = ngrok.connect(5001)
        tele.send_link(url)
        print(url)
        while True:
            pass


# Телеграмм канал
telegram_chanel_thread = Thread(target=tele.main)
telegram_chanel_thread.start()
# Телеграмм оповещения
telegram_thread = Thread(target=tele.telegram_notification)
telegram_thread.start()
# ngrok поток
ngrok_thread = Thread(target=grok)
ngrok_thread.start()