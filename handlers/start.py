"""
🚀 Обработчик команды /start
Регистрация и приветствие пользователей
"""

from bot import bot
from utils.logger import logger
from database import get_db
from models import User
from datetime import datetime
import telebot

# 🎨 Импортируем клавиатуры
from keyboards.inline import get_start_keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    """
    🚀 Обработчик команды /start
    
    Регистрирует нового пользователя или приветствует существующего
    """
    # 📝 Логируем начало обработки
    logger.info(f"👤 Пользователь @{message.from_user.username} вызвал /start")
    
    # 📊 Получаем сессию БД
    db = get_db()
    
    try:
        # 🔍 Проверяем, существует ли пользователь
        user = db.query(User).filter_by(telegram_id=message.from_user.id).first()
        
        if not user:
            # 🆕 Регистрируем нового пользователя
            logger.info(f"🆕 Создаю нового пользователя: @{message.from_user.username}")
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            logger.info(f"✅ Пользователь @{message.from_user.username} успешно зарегистрирован")
            
            # 🎉 Приветственное сообщение для нового пользователя
            welcome_text = f"""
🎉 <b>Добро пожаловать в Crypto Price Tracker!</b>

👋 Привет, {message.from_user.first_name}!

📊 Я помогу тебе отслеживать цены криптовалют и получать уведомления об изменениях.

🎁 <b>Бесплатный тариф:</b>
• 1 криптовалюта для отслеживания

💎 <b>Платные тарифы:</b>
• 5 монет - 500 ₽/мес
• 10 монет - 1000 ₽/мес
• 15 монет - 1500 ₽/мес
• 20 монет - 2000 ₽/мес

🚀 <b>Что ты можешь делать:</b>
• 📈 Отслеживать цены криптовалют
• 🔔 Настраивать умные алерты
• 📊 Получать уведомления о изменениях

👉 Нажми кнопку "Меню", чтобы начать!
            """
        else:
            # 👋 Приветствие для существующего пользователя
            logger.info(f"👋 Возвращаюсь к пользователю @{message.from_user.username}")
            
            # 📊 Получаем информацию о подписке
            max_coins = user.get_max_coins()
            is_valid = user.has_valid_subscription()
            
            subscription_status = "✅ Активна" if is_valid else "❌ Неактивна"
            if user.subscription_type == 1:
                subscription_status = "🎁 Бесплатный"
            
            welcome_text = f"""
👋 <b>С возвращением, {message.from_user.first_name}!</b>

📊 <b>Твой статус:</b>
• Тариф: {user.subscription_type} монет
• Статус: {subscription_status}
• Максимум монет: {max_coins}

💡 Используй кнопки ниже для навигации!
            """
        
        # 📤 Отправляем приветственное сообщение
        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode='HTML',
            reply_markup=get_start_keyboard()
        )
        
        logger.info(f"✅ Приветствие отправлено пользователю @{message.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в start_command для @{message.from_user.username}: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
        )
        db.rollback()
    finally:
        # 🧹 Закрываем сессию
        db.close()