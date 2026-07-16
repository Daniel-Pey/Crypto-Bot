import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL')
    CRYPTO_API_KEY = os.getenv('CRYPTO_API_KEY')
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Цены на подписки
    SUBSCRIPTION_PRICES = {
        5: 500,   # 5 монет - 500 руб/мес
        10: 1000, # 10 монет - 1000 руб/мес
        15: 1500, # 15 монет - 1500 руб/мес
        20: 2000  # 20 монет - 2000 руб/мес
    }
    
    # Бесплатный лимит
    FREE_LIMIT = 1
    
    # Интервал проверки цен (в секундах)
    PRICE_CHECK_INTERVAL = 60

config = Config()