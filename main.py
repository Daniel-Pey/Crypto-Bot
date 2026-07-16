"""
🚀 Точка входа в приложение
Запуск бота и фоновых сервисов
"""

import signal
import sys
from datetime import datetime

# 📦 Импорты
from bot import bot
from config import config  # 🔥 ДОБАВЛЕНО!
from utils.logger import logger
from database import init_db, close_db

# 📦 Импортируем все хендлеры для автоматической регистрации
from handlers import start, menu, coins, subscription, alerts

# 📦 Импортируем сервисы
from services.price_checker import PriceChecker  # 🔥 ДОБАВЛЕНО!

# 🎨 ASCII-арт для красивого запуска
BOT_ASCII_ART = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 CRYPTO PRICE TRACKER BOT v1.0                       ║
║   📊 Мониторинг криптовалют с умными алертами            ║
║                                                           ║
║   👨‍💻 Developed by: Your Team                             ║
║   📅 Started at: {timestamp}                             ║
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
    
    # 🛑 Останавливаем price_checker
    global price_checker
    if price_checker:
        logger.info("🔄 Остановка PriceChecker...")
        price_checker.stop()
    
    logger.info("🧹 Закрываю соединение с базой данных...")
    close_db()
    logger.info("👋 Бот успешно остановлен. До свидания!")
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
    init_db()
    logger.info("✅ База данных успешно инициализирована")
    
    # 🤖 Выводим информацию о боте
    logger.info(f"🤖 Бот запущен с токеном: {config.BOT_TOKEN[:10]}...")
    logger.info(f"📊 Режим логирования: {config.LOG_LEVEL}")
    logger.info(f"🔄 Интервал проверки цен: {config.PRICE_CHECK_INTERVAL} сек")
    
    # 📊 Выводим информацию о тарифах
    logger.info("💰 Доступные тарифы:")
    for coins, price in config.SUBSCRIPTION_PRICES.items():
        logger.info(f"   • {coins} монет - {price} ₽/мес")
    logger.info(f"   • 1 монета - БЕСПЛАТНО 🎁")
    
    # 🔄 Запускаем PriceChecker в фоновом режиме
    logger.info("🔄 Запуск PriceChecker...")
    price_checker = PriceChecker(bot, check_interval=config.PRICE_CHECK_INTERVAL)  # 🔥 ДОБАВЛЕНО!
    price_checker.start()  # 🔥 ДОБАВЛЕНО!
    logger.info("✅ PriceChecker запущен")
    
    # 🚀 Запускаем бота
    logger.info("🚀 Запуск бота...")
    logger.info("✅ Бот готов к работе! Ожидаю сообщения...")
    
    try:
        # 🔄 Запускаем бесконечный поллинг
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания (Ctrl+C)")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при работе бота: {e}")
    finally:
        # 🧹 Закрываем все соединения
        logger.info("🧹 Закрываю соединение с базой данных...")
        if price_checker:
            price_checker.stop()
        close_db()
        logger.info("👋 Бот остановлен. До свидания!")