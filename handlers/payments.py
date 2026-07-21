"""
💳 Обработчики действий с оплатой
"""

from bot import bot
from utils.logger import logger
from telebot import types
from config import config
from database import create_session
from models import User
import datetime
from datetime import timedelta
from keyboards.inline import get_back_keyboard, get_confirm_payment_keyboard
from utils.stars import convert_rub_to_stars


# ============================================================
# 💰 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================


def activate_subscription(user_id: int, coins: int, price: int) -> str:
    """
    ✅ Активация подписки для пользователя
    
    Args:
        user_id: ID пользователя в Telegram
        coins: Количество монет в тарифе
        price: Стоимость в рублях
        
    Returns:
        str: Текст результата
    """
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=user_id).first()
        
        if not user:
            return "❌ Пользователь не найден"
        
        # 🔄 Обновляем подписку
        user.subscription_type = coins
        user.subscription_end_date = datetime.datetime.utcnow() + timedelta(days=30)
        db.commit()
        
        # 📝 Логируем действие
        logger.info(f"👤 Пользователь @{user.username} активировал подписку {coins} монет за {price}₽")
        
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
        logger.error(f"💥 Ошибка активации подписки: {e}")
        return f"❌ Произошла ошибка: {e}"
    finally:
        db.close()


# ============================================================
# 💳 ОБРАБОТЧИКИ ОПЛАТЫ
# ============================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment_type_stars"))
def stars_payment_handler(call):
    """
    ⭐ Обработка оплаты через Telegram Stars
    """
    # 📝 Извлекаем данные
    parts = call.data.split('_')
    if len(parts) < 4:
        bot.answer_callback_query(call.id, "❌ Ошибка в данных")
        return
    
    coins = int(parts[2])
    price = int(parts[3])
    
    # 📝 Логируем
    logger.info(f"👤 Пользователь @{call.from_user.username} выбрал оплату Stars для {coins} монет")
    
    try:
        # ⭐ Конвертируем рубли в Stars
        star_price = convert_rub_to_stars(price)
        
        # 📝 Создаем счет для оплаты
        prices = [types.LabeledPrice(label=f"⭐{star_price} Stars", amount=star_price)]
        
        # 📤 Отправляем инвойс
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title="💰 Оплата подписки через Telegram Stars",
            description=f"📊 {coins} монет для отслеживания\n💰 {price} ₽ = ⭐{star_price}",
            invoice_payload=f"subscription_payment_{coins}_{price}",
            provider_token="",  # ⚠️ Для Stars обязательно оставляем пустым
            currency="XTR",     # 💰 Валюта Telegram Stars
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "⭐ Отправлен счет на оплату Stars")
        
        logger.info(f"✅ Отправлен счет на ⭐{star_price} для @{call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в stars_payment_handler: {e}")
        bot.answer_callback_query(call.id, f"❌ Ошибка: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("payment_type_card"))
def card_payment_handler(call):
    """
    💳 Обработка оплаты через карту/СБП
    """
    # 📝 Извлекаем данные
    parts = call.data.split('_')
    if len(parts) < 4:
        bot.answer_callback_query(call.id, "❌ Ошибка в данных")
        return
    
    coins = int(parts[2])
    price = int(parts[3])
    
    # 📝 Логируем
    logger.info(f"👤 Пользователь @{call.from_user.username} выбрал оплату картой для {coins} монет")
    
    try:
        # 📝 Формируем информацию для оплаты картой
        card_number = config.CARD_NUMBER
        
        text = f"""
💳 <b>Оплата картой/СБП</b>

📊 <b>Тариф:</b> {coins} монет
💰 <b>Сумма:</b> {price} ₽

📌 <b>Реквизиты для оплаты:</b>
• Карта: <code>{card_number}</code>
• Получатель: Crypto Tracker Bot

📝 <b>Инструкция:</b>
1️⃣ Переведите {price} ₽ на указанную карту
2️⃣ Нажмите кнопку "✅ Я оплатил" ниже
3️⃣ Подписка будет активирована автоматически

⚠️ <b>Внимание:</b>
• Укажите в комментарии ваш ID: <code>{call.from_user.id}</code>
• Подписка активируется после проверки платежа
        """
        
        # 📤 Отправляем информацию
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_confirm_payment_keyboard(coins, price)
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "💳 Информация для оплаты отправлена")
        
        logger.info(f"✅ Отправлена информация для оплаты картой @{call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в card_payment_handler: {e}")
        bot.answer_callback_query(call.id, f"❌ Ошибка: {e}")


# ============================================================
# ✅ ОБРАБОТЧИКИ ПОДТВЕРЖДЕНИЯ ПЛАТЕЖЕЙ
# ============================================================

# 🔄 Обработчик для подтверждения платежа перед списанием (для Stars)
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    """
    ✅ Подтверждение платежа перед списанием Stars
    """
    try:
        # ✅ Подтверждаем оплату
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        logger.info(f"✅ Pre-checkout подтвержден для {pre_checkout_query.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в pre_checkout: {e}")
        bot.answer_pre_checkout_query(
            pre_checkout_query.id, 
            ok=False, 
            error_message="❌ Произошла ошибка при обработке платежа"
        )


# 📨 Обработчик успешной оплаты (для Stars)
@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    """
    ✅ Обработка успешной оплаты Stars
    """
    try:
        # 📝 Получаем информацию о платеже
        payment_info = message.successful_payment
        payload = payment_info.invoice_payload
        
        # 📝 Извлекаем данные из payload
        parts = payload.split('_')
        if len(parts) >= 3:
            coins = int(parts[2])
            price = int(parts[3]) if len(parts) > 3 else 0
        else:
            coins = 5
            price = 300
        
        # ✅ Активируем подписку
        text = activate_subscription(message.from_user.id, coins, price)
        
        # 📤 Отправляем подтверждение
        bot.send_message(
            message.chat.id,
            f"✅ Платеж прошел успешно!\n⭐ Оплачено: {payment_info.total_amount} Stars\n\n{text}",
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
        logger.info(f"✅ Успешная оплата Stars от @{message.from_user.username}: {payment_info.total_amount}⭐")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в handle_successful_payment: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при обработке платежа. Пожалуйста, свяжитесь с поддержкой."
        )


# ============================================================
# ✅ ПОДТВЕРЖДЕНИЕ ОПЛАТЫ ПО КАРТЕ (ВРУЧНУЮ)
# ============================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_payment_"))
def confirm_payment_rub(call):
    """
    ✅ Подтверждение оплаты по карте (вручную пользователем)
    """
    # 📝 Извлекаем данные
    parts = call.data.split("_")
    if len(parts) < 3:
        bot.answer_callback_query(call.id, "❌ Ошибка в данных")
        return
    
    coins = int(parts[2])
    price = int(parts[3]) if len(parts) > 3 else 0
    
    # 📝 Логируем
    logger.info(f"👤 Пользователь @{call.from_user.username} подтвердил оплату {price}₽ за {coins} монет")
    
    try:
        # ✅ Активируем подписку
        text = activate_subscription(call.from_user.id, coins, price)
        
        # 📤 Отправляем результат
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
        logger.error(f"💥 Ошибка в confirm_payment_rub: {e}")
        bot.answer_callback_query(call.id, f"❌ Произошла ошибка: {e}")