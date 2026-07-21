import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DATABASE_FILE = os.getenv('DATABASE_FILE')
    CRYPTO_API_KEY = os.getenv('CRYPTO_API_KEY')
    ADMINS_ID = list(map(int, str(os.getenv('ADMIN_ID')).split(', ')))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    CARD_NUMBER = os.getenv('CARD_NUMBER')
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")
    VERSION = os.getenv("VERSION")
    
    # Цены на подписки
    SUBSCRIPTION_PRICES = {
        5: 300,
        10: 600,
        15: 900,
        20: 1200
    }
    
    # Способы оплаты
    PAYMENT_TYPES = {
        'stars': "⭐️ STARS",
        'card': " 💳 СБП"
    }
    
    # Цена одной тг звезды в рублях (примерно)
    ONE_STAR_PRICE = 2
    
    # Бесплатный лимит
    FREE_LIMIT = 1
    
    # Интервал проверки цен (в секундах)
    PRICE_CHECK_INTERVAL = 60
    
    
    def get_prices(self):
        """ Функция для получения цен

        Returns:
            str: цены на подписки
        """
        
        prices = f"• 🎁 {self.FREE_LIMIT} монета - БЕСПЛАТНО"
        for coins, price in self.SUBSCRIPTION_PRICES:
            prices += f"\n• {coins} монет - {price} ₽/мес"
        
        return prices

config = Config()