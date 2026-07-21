import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DATABASE_FILE = os.getenv('DATABASE_FILE')
    CRYPTO_API_KEY = os.getenv('CRYPTO_API_KEY')
    
    # 🔥 Исправляем получение ADMINS_ID
    admin_ids_str = os.getenv('ADMIN_ID', '')
    ADMINS_ID = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()] if admin_ids_str else []
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    CARD_NUMBER = os.getenv('CARD_NUMBER', '')
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", 'support')
    VERSION = os.getenv("VERSION", '1.0.0')
    
    # Цены на подписки
    SUBSCRIPTION_PRICES = {
        5: 300,
        10: 600,
        15: 900,
        20: 1200
    }
    
    # 🔥 Способы оплаты (исправляем формат)
    PAYMENT_TYPES = {
        'stars': "⭐️ STARS",
        'card': "💳 СБП"
    }
    
    # Цена одной тг звезды в рублях (примерно)
    ONE_STAR_PRICE = 2
    
    # Бесплатный лимит
    FREE_LIMIT = 1
    
    # Интервал проверки цен (в секундах)
    PRICE_CHECK_INTERVAL = 60
    
    def get_prices(self):
        """ Функция для получения цен """
        prices = f"• 🎁 {self.FREE_LIMIT} монета - БЕСПЛАТНО"
        for coins, price in self.SUBSCRIPTION_PRICES.items():  # 🔥 Исправлено: добавляем .items()
            prices += f"\n• {coins} монет - {price} ₽/мес"
        return prices

config = Config()