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
    admin.admin_log(f"🛑 Бот остановлен {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nПричина: {sig}")
    sys.exit(0)

if __name__ == '__main__':
    # 📝 Выводим красивый ASCII-арт при запуске
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(BOT_ASCII_ART.format(timestamp=current_time))
    
    # 🎯 Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
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
    
    try:
        # 🔄 Запускаем бесконечный поллинг
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        logger.info("✅ Бот готов к работе . . .")
        admin.admin_log(f'✅ Бот запущен\nВремя: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прекращения работы")
        admin.admin_log("🛑 Бот остановлен\nПричина: Штатное завершение работы")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при работе бота: {e}")
        admin.admin_log(f"🛑 Бот остановлен\nПричина: 💥 Ошибка на сервере\nВывод:\n{e}")
    finally:
        # 🧹 Закрываем все соединения
        logger.info("🧹 Закрываю соединение с базой данных...")
        if price_checker:
            price_checker.stop()
        logger.info("👋 Бот остановлен")