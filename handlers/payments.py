"""
Обработчики действий с оплатой
"""

from bot import bot
from utils.logger import logger
from telebot import types
from utils.stars import convert_rub_to_stars
from database import create_session, User
import datetime
from datetime import timedelta
from .subscription import confirm_payment_rub


bot.callback_query_handler(func=lambda call: call.data.startswith("payment_type_stars"))
def stars_payment_handler(call):
    *args, coins, price = call.data.split('_')
    star_price = convert_rub_to_stars(price)
    prices = [types.LabeledPrice(label=f"⭐{star_price}", amount=star_price)]
    bot.send_invoice(
        chat_id=call.chat.id,
        title="Платеж через Telegram Stars ⭐",
        description=f"К оплате ⭐{star_price}",
        invoice_payload=f"subscription_payment_{coins}_{price}",
        provider_token="",  # Для Stars обязательно оставляем пустым
        currency="XTR",  # Валюта Telegram Stars
        prices=prices
    )


bot.callback_query_handler(func=lambda call: call.data.startswith("payment_type_stars"))
def card_payment_handler(call):
    *args, coins, price = call.data.split('_')
    call.data = f"confirm_payment_{coins}_price"
    confirm_payment_rub(call)


# Обработчик для подтверждения платежа перед списанием
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    # Пoдтверждаем оплату
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработчик успешной оплаты
@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    # Логика после оплаты: выдача товара, пополнение баланса, сохранение в БД
    payment_info = message.successful_payment
    bot.send_message(
        message.chat.id,
        f"✅ Платеж прошел успешно!\n Вы оплатили {payment_info.total_amount}⭐"
    )


def confirm_payment(coins, price, user_id):
    """Функция проведения оплаты"""
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=user_id).first()
        
        if not user:
            return "❌ Пользователь не найден"
        
        # 🔄 Обновляем подписку
        user.subscription_type = coins
        user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
        db.commit()
        
        # 📝 Логируем действие
        logger.info(f"👤 Пользователь @{user.username} подтвердил оплату {price}₽ за {coins} монет")
        
        # 🎉 Успешное обновление
        text = f"""
✅ <b>Подписка успешно активирована!</b>

🎉 Поздравляем! Ваш тариф обновлен.

📊 <b>Новый тариф:</b> {coins} монет
💰 <b>Оплачено:</b> {price} ₽
📅 <b>Действует до:</b> {user.subscription_end_date.strftime('%d.%m.%Y')}

🪙 <b>Теперь вы можете отслеживать до {coins} монет!</b>

💡 <b>Советы:</b>
• Добавьте новые монеты через меню "➕ Добавить монету"
• Настройте алерты для важных монет
• Следите за изменениями цен в реальном времени

🚀 Удачной торговли!
        """
        
        return text
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        return "❌ Произошла ошибка"
    finally:
        # 🧹 Закрываем сессию
        db.close()