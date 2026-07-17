"""
🚀 Точка входа в приложение
Запуск бота и фоновых сервисов
"""

import signal
import sys
from datetime import datetime

# 📦 Импорты
from bot import bot
from config import config
from utils.logger import logger
from database import create_session, global_init
from services.price_checker import PriceChecker

# 📦 Импортируем все хендлеры для автоматической регистрации
from handlers import start, menu, coins, subscription, alerts

from utils import admin

# 🎨 ASCII-арт для красивого запуска
BOT_ASCII_ART = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 CRYPTO PRICE TRACKER BOT v1.0                        ║
║   📊 Мониторинг криптовалют с умными алертами             ║
║                                                           ║
║   👨‍💻 Developed by: Daniel Pey                             ║
║   📅 Started at: 16.07.2026                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

# 🔄 Глобальные переменные для сервисов
price_checker = None


def stop_working_handler(sig, frame):
    """
    🔄 Обработчик сигналов для корректного завершения бота
    """
    logger.info("🛑 Получен сигнал завершения...")
    
    global price_checker
    if price_checker:
        logger.info("🔄 Остановка PriceChecker...")
        price_checker.stop()
    
    logger.info("🧹 Закрываю соединение с базой данных...")
    logger.info("👋 Бот успешно остановлен.")
    admin.admin_log(f"🛑 Бот остановлен\nВремя: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nПричина: Штатное прекращение работы")
    sys.exit(0)


def signal_handler(sig, frame):
    """
    🔄 Обработчик сигналов для корректного завершения бота
    """
    logger.info("🛑 Получен сигнал завершения...")
    
    global price_checker
    if price_checker:
        logger.info("🔄 Остановка PriceChecker...")
        price_checker.stop()
    
    logger.info("🧹 Закрываю соединение с базой данных...")
    logger.info("👋 Бот успешно остановлен.")
    admin.admin_log(f"🛑 Бот остановлен\nВремя: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nПричина: Ошибка на сервере {sig} {frame}")
    sys.exit(1)

if __name__ == '__main__':
    # 📝 Выводим красивый ASCII-арт при запуске
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(BOT_ASCII_ART.format(timestamp=current_time))
    
    # 🎯 Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, stop_working_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 🗄️ Инициализируем базу данных
    logger.info("🗄️ Инициализация базы данных...")
    global_init(config.DATABASE_FILE)
    logger.info("✅ База данных успешно инициализирована")
    
    # 🤖 Выводим информацию о боте
    logger.info(f"🤖 Бот запущен . . .")
    logger.info(f"📊 Режим логирования: {config.LOG_LEVEL}")
    logger.info(f"🔄 Интервал проверки цен: {config.PRICE_CHECK_INTERVAL} сек")
    
    # 📊 Выводим информацию о тарифах
    logger.info("💰 Доступные тарифы:")
    for coins, price in config.SUBSCRIPTION_PRICES.items():
        logger.info(f"   • {coins} монет - {price} ₽/мес")
    logger.info(f"   • 1 монета - БЕСПЛАТНО 🎁")
    
    # 🔄 Запускаем PriceChecker в фоновом режиме
    logger.info("🔄 Запуск PriceChecker...")
    price_checker = PriceChecker(bot, check_interval=config.PRICE_CHECK_INTERVAL)
    price_checker.start()
    logger.info("✅ PriceChecker запущен")
    
    # 🚀 Запускаем бота
    logger.info("🚀 Запуск бота...")
    
    # 🔄 Запускаем бесконечный поллинг
    logger.info("✅ Бот готов к работе . . .")
    admin.admin_log(f'✅ Бот запущен\nВремя: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    try:
        bot.polling(non_stop=True, timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        logger.error(f"🛑 Не получилось запустить бота: {e}")
        admin.admin_log(f"🛑 Не получилось запустить бота в {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {e}")
        sys.exit(1)