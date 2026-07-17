"""
🔔 Обработчики управления алертами
Настройка и управление уведомлениями
"""

from bot import bot
from utils.logger import logger
from database import create_session
from models import User, Coin, UserCoin, Alert
from utils.validators import validate_price, validate_percent
from keyboards.inline import get_back_keyboard, get_cancel_keyboard, get_alert_keyboard
from handlers.menu import back_to_menu
import telebot
from datetime import datetime

@bot.callback_query_handler(func=lambda call: call.data == "my_alerts")
def my_alerts(call):
    """
    🔔 Показать список алертов пользователя
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} запросил список алертов")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🔔 Получаем алерты пользователя
        alerts = user.alerts
        
        if not alerts:
            # 📭 Если алертов нет
            text = """
🔔 <b>У вас пока нет настроенных алертов</b>

📌 <b>Как создать алерт:</b>
1️⃣ Добавьте монету в список
2️⃣ Выберите монету из списка
3️⃣ Нажмите "🔔 Настроить алерт"
4️⃣ Выберите тип алерта:
   • По достижении цены
   • По изменению процента

💡 <b>Примеры:</b>
• Алерт на BTC при достижении $100,000
• Алерт на ETH при изменении на +5%
            """
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
        else:
            # 📊 Формируем список алертов
            text = "🔔 <b>Ваши алерты:</b>\n\n"
            alert_count = 0
            
            for alert in alerts:
                if not alert.is_triggered:
                    # 🔍 Получаем монету
                    user_coin = alert.user_coin
                    if user_coin:
                        coin = user_coin.coin
                        symbol = coin.symbol if coin else "Неизвестно"
                        
                        text += f"• 🪙 {symbol} - "
                        if alert.alert_type == "price_reached":
                            text += f"💰 Цена ${alert.trigger_value}\n"
                        else:
                            text += f"📊 Изменение {alert.trigger_value}%\n"
                        alert_count += 1
            
            if alert_count == 0:
                text += "❌ Нет активных алертов\n"
            
            text += "\n💡 Чтобы создать новый алерт, выберите монету в списке"
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "🔔 Список алертов")
        
        logger.info(f"✅ Отправлен список алертов @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в my_alerts для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("alert_price_"))
def setup_price_alert(call):
    """
    💰 Настройка алерта по цене
    """
    # 📝 Извлекаем символ монеты
    symbol = call.data.replace("alert_price_", "")
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} настраивает ценовой алерт для {symbol}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Получаем монету
        coin = db.query(Coin).filter_by(symbol=symbol).first()
        
        if not coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена")
            return
        
        # 🔍 Получаем связь пользователь-монета
        user_coin = db.query(UserCoin).filter_by(
            user_id=user.id,
            coin_id=coin.id
        ).first()
        
        if not user_coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена в вашем списке")
            return
        
        # 📝 Формируем запрос
        text = f"""
🎯 <b>Настройка алерта по цене для {symbol}</b>

💰 <b>Текущая цена:</b> ${coin.current_price if coin.current_price else "Неизвестно"}

✏️ <b>Введите целевую цену:</b>
• Когда цена достигнет указанного значения - вы получите уведомление
• Используйте формат: 100000.00

⌨️ <b>Введите цену (или нажмите "Отмена"):</b>
        """
        
        # 📤 Отправляем сообщение с запросом ввода
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        
        # 🔄 Регистрируем обработчик ввода цены
        bot.register_next_step_handler(call.message, process_price_alert, user.id, coin.id, user_coin.id)
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, f"🎯 Настройка ценового алерта для {symbol}")
        
        logger.info(f"✅ Запрошен ввод цены для алерта {symbol} у @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в setup_price_alert для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("alert_percent_"))
def setup_percent_alert(call):
    """
    📊 Настройка алерта по проценту
    """
    # 📝 Извлекаем символ монеты
    symbol = call.data.replace("alert_percent_", "")
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} настраивает процентный алерт для {symbol}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Получаем монету
        coin = db.query(Coin).filter_by(symbol=symbol).first()
        
        if not coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена")
            return
        
        # 🔍 Получаем связь пользователь-монета
        user_coin = db.query(UserCoin).filter_by(
            user_id=user.id,
            coin_id=coin.id
        ).first()
        
        if not user_coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена в вашем списке")
            return
        
        # 📝 Формируем запрос
        text = f"""
📊 <b>Настройка алерта по проценту для {symbol}</b>

📈 <b>Текущее изменение:</b> {coin.price_change_24h if coin.price_change_24h else "Неизвестно"}%

✏️ <b>Введите процент изменения:</b>
• При изменении цены на указанный % вы получите уведомление
• Используйте формат: 5 (для 5%)
• Значение от 0 до 100 (не обязательно целое)

⌨️ <b>Введите процент (или нажмите "Отмена"):</b>
        """
        
        # 📤 Отправляем сообщение с запросом ввода
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        
        # 🔄 Регистрируем обработчик ввода процента
        bot.register_next_step_handler(call.message, process_percent_alert, user.id, coin.id, user_coin.id)
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, f"🎯 Настройка процентного алерта для {symbol}")
        
        logger.info(f"✅ Запрошен ввод процента для алерта {symbol} у @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в setup_percent_alert для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

def process_price_alert(message, user_id, coin_id, user_coin_id):
    """
    💰 Обработка ввода цены для алерта
    """
    # 📝 Проверяем, не отмена ли это
    if message.text == "❌ Отмена":
        # Создаем объект callback для back_to_menu
        class CallbackMock:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user
                self.id = "cancel"
                self.data = "back_to_menu"
        
        mock_call = CallbackMock(message)
        back_to_menu(mock_call)
        return
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{message.from_user.username} ввел цену: {message.text}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # ✅ Валидируем цену
        is_valid, result = validate_price(message.text)
        
        if not is_valid:
            # ❌ Если цена невалидная
            bot.send_message(
                message.chat.id,
                f"{result}\n\nПопробуйте снова или нажмите 'Отмена'",
                parse_mode='HTML',
                reply_markup=get_cancel_keyboard()
            )
            
            # 🔄 Регистрируем обработчик снова
            bot.register_next_step_handler(message, process_price_alert, user_id, coin_id, user_coin_id)
            return
        
        # ✅ Получаем цену
        price = result
        
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Получаем монету
        coin = db.query(Coin).filter_by(id=coin_id).first()
        if not coin:
            bot.send_message(message.chat.id, "❌ Монета не найдена")
            return
        
        # 🔍 Получаем связь пользователь-монета
        user_coin = db.query(UserCoin).filter_by(id=user_coin_id).first()
        if not user_coin:
            bot.send_message(message.chat.id, "❌ Связь не найдена")
            return
        
        # 📝 Создаем алерт
        alert = Alert(
            user_id=user_id,
            user_coin_id=user_coin_id,
            alert_type="price_reached",
            trigger_value=price,
            created_at=datetime.utcnow()
        )
        db.add(alert)
        
        # 🆕 Обновляем целевую цену в UserCoin
        user_coin.target_price = price
        
        db.commit()
        
        # 🎉 Успешное создание
        success_text = f"""
✅ <b>Алерт успешно создан!</b>

🪙 <b>Монета:</b> {coin.symbol}
💰 <b>Тип:</b> По достижении цены
🎯 <b>Цена:</b> ${price}

📊 <b>Текущая цена:</b> ${coin.current_price if coin.current_price else "Неизвестно"}

🔔 Вы получите уведомление, когда цена {coin.symbol} достигнет ${price}!

💡 <b>Совет:</b>
• Следите за уведомлениями в этом чате
• При необходимости можно создать несколько алертов
        """
        
        bot.send_message(
            message.chat.id,
            success_text,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
        logger.info(f"✅ Создан алерт по цене для @{message.from_user.username}: {coin.symbol} - ${price}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в process_price_alert для @{message.from_user.username}: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при создании алерта. Попробуйте позже."
        )
        db.rollback()
    finally:
        # 🧹 Закрываем сессию
        db.close()

def process_percent_alert(message, user_id, coin_id, user_coin_id):
    """
    📊 Обработка ввода процента для алерта
    """
    # 📝 Проверяем, не отмена ли это
    if message.text == "❌ Отмена":
        # Создаем объект callback для back_to_menu
        class CallbackMock:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user
                self.id = "cancel"
                self.data = "back_to_menu"
        
        mock_call = CallbackMock(message)
        back_to_menu(mock_call)
        return
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{message.from_user.username} ввел процент: {message.text}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # ✅ Валидируем процент
        is_valid, result = validate_percent(message.text)
        
        if not is_valid:
            # ❌ Если процент невалидный
            bot.send_message(
                message.chat.id,
                f"{result}\n\nПопробуйте снова или нажмите 'Отмена'",
                parse_mode='HTML',
                reply_markup=get_cancel_keyboard()
            )
            
            # 🔄 Регистрируем обработчик снова
            bot.register_next_step_handler(message, process_percent_alert, user_id, coin_id, user_coin_id)
            return
        
        # ✅ Получаем процент
        percent = result
        
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Получаем монету
        coin = db.query(Coin).filter_by(id=coin_id).first()
        if not coin:
            bot.send_message(message.chat.id, "❌ Монета не найдена")
            return
        
        # 🔍 Получаем связь пользователь-монета
        user_coin = db.query(UserCoin).filter_by(id=user_coin_id).first()
        if not user_coin:
            bot.send_message(message.chat.id, "❌ Связь не найдена")
            return
        
        # 📝 Создаем алерт
        alert = Alert(
            user_id=user_id,
            user_coin_id=user_coin_id,
            alert_type="price_change",
            trigger_value=percent,
            created_at=datetime.utcnow()
        )
        db.add(alert)
        
        # 🆕 Обновляем порог в UserCoin
        user_coin.alert_threshold = percent
        
        db.commit()
        
        # 🎉 Успешное создание
        success_text = f"""
✅ <b>Алерт успешно создан!</b>

🪙 <b>Монета:</b> {coin.symbol}
📊 <b>Тип:</b> По изменению процента
🎯 <b>Изменение:</b> {percent}%

📈 <b>Текущее изменение:</b> {coin.price_change_24h if coin.price_change_24h else "Неизвестно"}%

🔔 Вы получите уведомление, когда цена {coin.symbol} изменится на {percent}%!

💡 <b>Совет:</b>
• Следите за уведомлениями в этом чате
• При необходимости можно создать несколько алертов
        """
        
        bot.send_message(
            message.chat.id,
            success_text,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
        logger.info(f"✅ Создан алерт по проценту для @{message.from_user.username}: {coin.symbol} - {percent}%")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в process_percent_alert для @{message.from_user.username}: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при создании алерта. Попробуйте позже."
        )
        db.rollback()
    finally:
        # 🧹 Закрываем сессию
        db.close()


# ============================================================
# 🎯 УПРАВЛЕНИЕ АЛЕРТАМИ (НОВЫЕ ФУНКЦИИ)
# ============================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("alert_disable_"))
def alert_disable(call):
    """
    🔕 Отключение алерта
    """
    # 📝 Извлекаем ID алерта
    alert_id = int(call.data.replace("alert_disable_", ""))
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} отключил алерт {alert_id}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем алерт
        alert = db.query(Alert).filter_by(id=alert_id).first()
        
        if not alert:
            bot.answer_callback_query(call.id, "❌ Алерт не найден")
            return
        
        # 🔍 Проверяем, что алерт принадлежит пользователю
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user or alert.user_id != user.id:
            bot.answer_callback_query(call.id, "🚫 Это не ваш алерт")
            return
        
        # 🗑️ Удаляем алерт
        db.delete(alert)
        db.commit()
        
        # ✅ Подтверждение
        bot.edit_message_text(
            "🔕 Алерт успешно отключен",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_back_keyboard()
        )
        
        bot.answer_callback_query(call.id, "🔕 Алерт отключен")
        
        logger.info(f"✅ Алерт {alert_id} отключен пользователем @{call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в alert_disable: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        db.rollback()
    finally:
        db.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith("alert_reset_"))
def alert_reset(call):
    """
    🔄 Сброс алерта
    """
    # 📝 Извлекаем ID алерта
    alert_id = int(call.data.replace("alert_reset_", ""))
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} сбросил алерт {alert_id}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем алерт
        alert = db.query(Alert).filter_by(id=alert_id).first()
        
        if not alert:
            bot.answer_callback_query(call.id, "❌ Алерт не найден")
            return
        
        # 🔍 Проверяем, что алерт принадлежит пользователю
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user or alert.user_id != user.id:
            bot.answer_callback_query(call.id, "🚫 Это не ваш алерт")
            return
        
        # 🔄 Сбрасываем алерт
        alert.is_triggered = False
        alert.triggered_at = None
        db.commit()
        
        # ✅ Подтверждение
        bot.edit_message_text(
            "🔄 Алерт сброшен. Он будет снова активен.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_back_keyboard()
        )
        
        bot.answer_callback_query(call.id, "🔄 Алерт сброшен")
        
        logger.info(f"✅ Алерт {alert_id} сброшен пользователем @{call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в alert_reset: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        db.rollback()
    finally:
        db.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith("alert_repeat_"))
def alert_repeat(call):
    """
    🔄 Настройка повторяющегося алерта
    """
    # 📝 Извлекаем символ
    symbol = call.data.replace("alert_repeat_", "")
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} настроил повторение для {symbol}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Получаем монету
        coin = db.query(Coin).filter_by(symbol=symbol).first()
        
        if not coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена")
            return
        
        # 🔍 Получаем связь пользователь-монета
        user_coin = db.query(UserCoin).filter_by(
            user_id=user.id,
            coin_id=coin.id
        ).first()
        
        if not user_coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена в вашем списке")
            return
        
        # 🔍 Проверяем, есть ли уже алерт
        existing_alert = db.query(Alert).filter_by(
            user_coin_id=user_coin.id,
            is_triggered=False
        ).first()
        
        if existing_alert:
            bot.answer_callback_query(call.id, "⚠️ Алерт уже активен")
            return
        
        # 📝 Создаем новый алерт (по умолчанию - по цене)
        alert = Alert(
            user_id=user.id,
            user_coin_id=user_coin.id,
            alert_type="price_reached",
            trigger_value=coin.current_price * 1.1 if coin.current_price else 100000,  # +10%
            created_at=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        
        # ✅ Подтверждение
        bot.answer_callback_query(call.id, "🔄 Алерт создан заново")
        
        logger.info(f"✅ Алерт создан заново для {symbol} пользователем @{call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в alert_repeat: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        db.rollback()
    finally:
        db.close()