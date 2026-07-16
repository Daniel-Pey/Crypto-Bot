import telebot
from config import config

# Создаем экземпляр бота
bot = telebot.TeleBot(config.BOT_TOKEN)

# В этом файле больше ничего нет - только переменная bot