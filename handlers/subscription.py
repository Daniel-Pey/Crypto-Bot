"""
💎 Обработчики управления подпиской
Тарифы, платежи и обновление подписки
"""

from bot import bot
from utils.logger import logger
from database import create_session
from models import User
from datetime import datetime, timedelta
from config import config
from keyboards.inline import (
    get_subscription_keyboard, 
    get_back_keyboard, 
    get_confirm_payment_keyboard,
    get_confirm_keyboard,
    get_payments_keyboard
)
from .payments import confirm_payment


@bot.callback_query_handler(func=lambda call: call.data == "subscription")
def subscription_menu(call):
    """
    💎 Показать меню подписки
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} открыл меню подписки")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 📊 Получаем информацию о текущей подписке
        is_valid = user.has_valid_subscription()
        subscription_status = "✅ Активна" if is_valid else "❌ Неактивна"
        
        if user.subscription_type == 1:
            subscription_status = "🎁 Бесплатный"
            end_date = "Бессрочно"
        else:
            end_date = user.subscription_end_date.strftime('%d.%m.%Y') if user.subscription_end_date else "Не установлена"
        
        # 📝 Формируем текст
        text = f"""
💎 <b>Управление подпиской</b>

📊 <b>Текущий тариф:</b> {user.subscription_type} монет
📊 <b>Статус:</b> {subscription_status}
📅 <b>Действует до:</b> {end_date}

🪙 <b>Используется:</b> {len(user.coins)}/{user.get_max_coins()} монет

📋 <b>Доступные тарифы:</b>
"""
        
        # 📋 Добавляем информацию о тарифах
        for coins, price in config.SUBSCRIPTION_PRICES.items():
            is_current = coins == user.subscription_type
            marker = "✅" if is_current else "  "
            text += f"\n{marker} • {coins} монет - {price} ₽/мес"
        
        text += "\n\n🎁 • 1 монета - БЕСПЛАТНО\n"
        
        if user.subscription_type == 1:
            text += "\n💡 Хотите больше монет? Выберите платный тариф!"
        else:
            text += "\n💡 Хотите изменить тариф? Выберите другой!"
        
        # 📤 Отправляем сообщение
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_subscription_keyboard()
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "💎 Меню подписки")
        
        logger.info(f"✅ Отправлено меню подписки @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в subscription_menu для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("subscribe_"))
def subscribe(call):
    """
    💰 Обработка выбора тарифа
    """
    # 📝 Извлекаем количество монет
    coins = int(call.data.replace("subscribe_", ""))
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} выбрал тариф {coins} монет")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🎁 Обработка бесплатного тарифа
        if coins == 1:
            # 🔄 Обновляем тариф
            user.subscription_type = 1
            user.subscription_end_date = None
            db.commit()
            
            text = """
🎁 <b>Вы переключены на бесплатный тариф!</b>

📊 <b>Новые возможности:</b>
• 1 монета для отслеживания
• Бессрочный доступ
• Базовые алерты

💡 Хотите больше возможностей? 
Вернитесь в меню подписки и выберите платный тариф!
            """
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
            
            bot.answer_callback_query(call.id, "🎁 Переключено на бесплатный тариф")
            
            logger.info(f"✅ Пользователь @{call.from_user.username} переключен на бесплатный тариф")
            return
        
        # 💰 Обработка платных тарифов
        price = config.SUBSCRIPTION_PRICES.get(coins)
        if not price:
            bot.answer_callback_query(call.id, "❌ Тариф не найден")
            return
        
        # 📝 Формируем информацию о платеже
        text = f"""
💳 <b>Подтверждение подписки</b>

📊 <b>Вы выбрали тариф:</b> {coins} монет
💰 <b>Стоимость:</b> {price} ₽/мес
📅 <b>Период:</b> 30 дней

👤 <b>Пользователь:</b> @{call.from_user.username}

Выберите способ оплаты 👇
"""
        # 📤 Отправляем информацию о платеже
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_payments_keyboard(coins, price)
        )
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в subscribe для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        db.rollback()
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_payment_"))
def confirm_payment_rub(call):
    """
    ✅ Подтверждение платежа
    """
    # 📝 Извлекаем данные
    parts = call.data.split("_")
    if len(parts) < 3:
        bot.answer_callback_query(call.id, "❌ Ошибка в данных")
        return
    
    coins = int(parts[2])
    price = int(parts[3]) if len(parts) > 3 else 0
    
    try:
        # 🎉 Успешное обновление
        text = confirm_payment(coins, price, call.from_user.id)
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, f"✅ Подписка на {coins} монет активирована")
        
        logger.info(f"✅ Подписка активирована для @{call.from_user.username}: {coins} монет")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в confirm_payment для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")