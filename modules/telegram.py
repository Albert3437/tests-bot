import telebot
from modules.logger import logging
from modules.config import read_API, read_strategies
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from modules.metrics import Metrics
import schedule
import time

class Telegram:
    def __init__(self):
        # Инициация класса для работы с телеграмм, данные берутся из конфига
        self.bot = telebot.TeleBot(read_API()['TELE_API'])
        self.chat_id = read_API()['CHAT_ID']
        self.settings_db = read_strategies()


    @logging
    def message(self, message):
        # Отправка сообщения в чат
            self.bot.send_message(self.chat_id, message)


    @logging
    def send_link(self, link):
        # Отправка ссылки в чат
            self.link = link
            self.bot.send_message(self.chat_id, self.link)


    @logging
    def send_notification(self):
        # Отправка уведомления в чат
        metric = Metrics()
        message = f'Баланс: {round(metric.total_balance(),2)}$\nПроцент дохода за день: {metric.profit_percent_per_day()}%'
        self.message(message)
            

    @logging
    def handle_messages(self, message):
        text = message.text

        if text == '/start':
            # Создаем клавиатуру с двумя кнопками
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = KeyboardButton(text="Ссылка на сайт")
            button2 = KeyboardButton(text="Отобразить показатели")
            keyboard.add(button1, button2)

            # Отправляем сообщение с клавиатурой
            self.bot.send_message(self.chat_id, "Доброго времени суток!\nЭто бот для отслеживания результатов работы торгового алгоритма.", reply_markup=keyboard)
        if text == 'Ссылка на сайт':
            self.bot.send_message(self.chat_id, self.link)
        if text == 'Отобразить показатели':
            self.send_notification()


    @logging
    def main(self):
        # Запуск основной функции работы телеграмм
            self.bot.message_handler()(self.handle_messages)
            while True:
                try:
                    self.bot.polling()
                except Exception:
                    time.sleep(5)
    

    @logging
    def telegram_notification(self):
    # Запуск телеграмм оповещений, при надобности можно добавить любое количество
            schedule.every().day.at("11:00").do(self.send_notification)
            schedule.every().day.at("20:00").do(self.send_notification)
            while True:
                    schedule.run_pending()
                    time.sleep(1)

    