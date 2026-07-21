"""
🪙 Обработчики управления криптовалютами
Добавление, удаление и просмотр монет
"""

from bot import bot
from utils.logger import logger
from database import create_session
from database.models import User, Coin, UserCoin
from utils.validators import validate_crypto_symbol
from keyboards.inline import (
    get_coins_keyboard, 
    get_back_keyboard, 
    get_confirm_keyboard,
    get_start_keyboard,
    get_cancel_keyboard,
    get_coin_detail_keyboard
)
from handlers.menu import back_to_menu
import telebot
from datetime import datetime

@bot.callback_query_handler(func=lambda call: call.data == "my_coins")
def my_coins(call):
    """
    📊 Показать список монет пользователя
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} запросил список монет")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🪙 Получаем монеты пользователя
        user_coins = user.coins
        
        if not user_coins:
            # 📭 Если монет нет
            text = """
📭 <b>У вас пока нет добавленных монет</b>

🪙 Чтобы добавить монету:
1️⃣ Нажмите "➕ Добавить монету"
2️⃣ Введите символ монеты (например, BTC)
3️⃣ Монета будет добавлена в ваш список

💡 <b>Совет:</b> Начните с популярных монет:
• BTC - Bitcoin
• ETH - Ethereum
• SOL - Solana
• ADA - Cardano
            """
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=get_coins_keyboard([])
            )
        else:
            # 📊 Формируем список монет
            coins_text = "🪙 <b>Ваши монеты:</b>\n\n"
            
            for user_coin in user_coins:
                coin = user_coin.coin
                price = coin.current_price if coin.current_price else "❓ Неизвестно"
                
                coins_text += f"• {coin.symbol} - {coin.name or coin.symbol}\n"
                coins_text += f"  💰 Цена: ${price}\n"
                
                if user_coin.target_price:
                    coins_text += f"  🎯 Цель: ${user_coin.target_price}\n"
                
                coins_text += "\n"
            
            # 📊 Добавляем информацию о лимитах
            max_coins = user.get_max_coins()
            coins_count = len(user_coins)
            coins_text += f"\n📊 <b>Использовано:</b> {coins_count}/{max_coins} монет"
            
            if coins_count >= max_coins:
                coins_text += "\n⚠️ <b>Достигнут лимит!</b> Обновите тариф для добавления новых монет"
            
            bot.edit_message_text(
                coins_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=get_coins_keyboard(user_coins)
            )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "📊 Список монет")
        
        logger.info(f"✅ Отправлен список монет пользователю @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в my_coins для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data == "add_coin")
def add_coin_prompt(call):
    """
    ➕ Запрос на добавление новой монеты
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} начал добавление монеты")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # ✅ Проверяем лимит монет
        max_coins = user.get_max_coins()
        coins_count = len(user.coins)
        
        if coins_count >= max_coins:
            # 🚫 Если достигнут лимит
            text = f"""
⚠️ <b>Достигнут лимит монет!</b>

📊 <b>Ваш тариф:</b> {user.subscription_type} монет
🪙 <b>Использовано:</b> {coins_count}/{max_coins}

💎 Чтобы добавить больше монет:
1️⃣ Обновите тариф до следующего уровня
2️⃣ Или удалите ненужные монеты

🔽 <b>Доступные тарифы:</b>
• 5 монет - 500 ₽/мес
• 10 монет - 1000 ₽/мес
• 15 монет - 1500 ₽/мес
• 20 монет - 2000 ₽/мес
            """
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
            
            bot.answer_callback_query(call.id, "⚠️ Достигнут лимит")
            return
        
        # ✏️ Запрашиваем ввод символа монеты
        text = """
✏️ <b>Введите символ криптовалюты</b>

📝 <b>Примеры:</b>
• BTC - Bitcoin
• ETH - Ethereum
• SOL - Solana
• ADA - Cardano

📌 <b>Внимание:</b>
• Используйте латинские буквы
• Символ должен быть от 2 до 10 символов
• Нажмите "Отмена" для возврата в меню

⌨️ <b>Введите символ:</b>
        """
        
        # 📤 Отправляем сообщение с запросом ввода
        msg = bot.send_message(
            call.message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=get_cancel_keyboard()
        )
        
        # 🔄 Сохраняем состояние ожидания ввода
        bot.register_next_step_handler(msg, process_add_coin, call.from_user.id)
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "✏️ Введите символ монеты")
        
        logger.info(f"✅ Запрошен ввод монеты у @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в add_coin_prompt для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

def process_add_coin(message, user_id):
    """
    📝 Обработка введенного символа монеты
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{message.from_user.username} ввел: {message.text}")
    
    # 📊 Если пользователь отменил
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
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Проверяем валидность символа
        is_valid, result = validate_crypto_symbol(message.text)
        
        if not is_valid:
            # ❌ Если символ невалидный
            bot.send_message(
                message.chat.id,
                f"{result}\n\nПопробуйте снова или нажмите 'Отмена'",
                parse_mode='HTML',
                reply_markup=get_cancel_keyboard()
            )
            
            # 🔄 Регистрируем обработчик снова
            bot.register_next_step_handler(message, process_add_coin, user_id)
            return
        
        # ✅ Получаем символ в верхнем регистре
        symbol = result.upper()
        
        # 🔍 Проверяем, существует ли пользователь
        user = db.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            bot.send_message(message.chat.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Проверяем, не добавлена ли уже эта монета
        existing = db.query(Coin).filter_by(symbol=symbol).first()
        
        if existing:
            # ✅ Проверяем, не отслеживает ли пользователь уже эту монету
            existing_user_coin = db.query(UserCoin).filter_by(
                user_id=user.id,
                coin_id=existing.id
            ).first()
            
            if existing_user_coin:
                bot.send_message(
                    message.chat.id,
                    f"⚠️ Монета {symbol} уже добавлена в ваш список!",
                    parse_mode='HTML'
                )
                return
        
        # 🆕 Создаем или получаем монету
        if not existing:
            # 📝 Создаем новую монету
            coin = Coin(
                symbol=symbol,
                name=symbol  # Временно, потом обновим через API
            )
            db.add(coin)
            db.flush()  # Получаем ID без коммита
            logger.info(f"🆕 Создана новая монета: {symbol}")
        else:
            coin = existing
        
        # ➕ Добавляем монету пользователю
        user_coin = UserCoin(
            user_id=user.id,
            coin_id=coin.id
        )
        db.add(user_coin)
        db.commit()
        
        # 🎉 Успешное добавление
        success_text = f"""
✅ <b>Монета успешно добавлена!</b>

🪙 <b>Добавлено:</b> {symbol}
📊 <b>Всего монет:</b> {len(user.coins) + 1}/{user.get_max_coins()}

💡 <b>Что дальше?</b>
• Настройте алерт для этой монеты
• Или добавьте еще монет
• Используйте меню для навигации
        """
        
        bot.send_message(
            message.chat.id,
            success_text,
            parse_mode='HTML',
            reply_markup=get_start_keyboard()
        )
        
        logger.info(f"✅ Добавлена монета {symbol} пользователю @{message.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в process_add_coin для @{message.from_user.username}: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при добавлении монеты. Попробуйте позже."
        )
        db.rollback()
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("coin_"))
def coin_detail(call):
    """
    🪙 Детальная информация о монете
    """
    # 📝 Извлекаем символ монеты
    symbol = call.data.replace("coin_", "")
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} запросил информацию о {symbol}")
    
    # 📊 Получаем сессию БД
    db = create_session()
    
    try:
        # 🔍 Получаем монету
        coin = db.query(Coin).filter_by(symbol=symbol).first()
        
        if not coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена")
            return
        
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🔍 Получаем связь пользователь-монета
        user_coin = db.query(UserCoin).filter_by(
            user_id=user.id,
            coin_id=coin.id
        ).first()
        
        if not user_coin:
            bot.answer_callback_query(call.id, "❌ Монета не найдена в вашем списке")
            return
        
        # 📊 Формируем информацию о монете
        price = coin.current_price if coin.current_price else "❓ Неизвестно"
        change = coin.price_change_24h if coin.price_change_24h else "❓"
        
        # 📈 Определяем эмодзи для изменения цены
        change_emoji = "📈" if change != "❓" and float(change) >= 0 else "📉"
        
        text = f"""
🪙 <b>{coin.symbol}</b> - {coin.name or coin.symbol}

💰 <b>Текущая цена:</b> ${price}
📊 <b>Изменение за 24ч:</b> {change_emoji} {change}%

🎯 <b>Целевая цена:</b> {user_coin.target_price if user_coin.target_price else "Не установлена"}

📊 <b>Дата добавления:</b> {user_coin.created_at.strftime('%d.%m.%Y')}

💡 <b>Доступные действия:</b>
• 🔔 Настроить алерт для {symbol}
• 🎯 Установить целевую цену
• 🗑️ Удалить монету из списка
        """
        
        # 📤 Отправляем или редактируем сообщение
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_coin_detail_keyboard(symbol)
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, f"🪙 {symbol}")
        
        logger.info(f"✅ Отправлена информация о {symbol} пользователю @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в coin_detail для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_coin_"))
def delete_coin(call):
    """
    🗑️ Удаление монеты из списка пользователя
    """
    # 📝 Извлекаем символ монеты
    symbol = call.data.replace("delete_coin_", "")
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} удаляет монету {symbol}")
    
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
        
        # 🗑️ Удаляем связь
        db.delete(user_coin)
        db.commit()
        
        # 🎉 Успешное удаление
        text = f"""
✅ <b>Монета {symbol} удалена из вашего списка!</b>

📊 <b>Теперь у вас:</b> {len(user.coins)}/{user.get_max_coins()} монет

💡 Чтобы добавить новую монету, нажмите "➕ Добавить монету"
        """
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, f"🗑️ {symbol} удалена")
        
        logger.info(f"✅ Удалена монета {symbol} у @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в delete_coin для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        db.rollback()
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("setup_alert_"))
def setup_alert_prompt(call):
    """
    🔔 Настройка алерта для монеты
    """
    # 📝 Извлекаем символ монеты
    symbol = call.data.replace("setup_alert_", "")
    
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} настраивает алерт для {symbol}")
    
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
        
        # 🔍 Проверяем, есть ли монета у пользователя
        user_coin = db.query(UserCoin).filter_by(
            user_id=user.id,
            coin_id=coin.id
        ).first()
        
        if not user_coin:
            bot.answer_callback_query(call.id, "❌ У вас нет этой монеты")
            return
        
        # 📤 Отправляем меню выбора типа алерта
        text = f"""
🔔 <b>Настройка алерта для {symbol}</b>

💰 <b>Текущая цена:</b> ${coin.current_price if coin.current_price else "Неизвестно"}

📌 <b>Выберите тип алерта:</b>
• По достижении цены - уведомление при достижении указанной цены
• По изменению процента - уведомление при изменении на указанный %

💡 <b>Совет:</b> Вы можете создать несколько алертов для одной монеты
        """
        
        # 📤 Импортируем get_alert_keyboard из keyboards
        from keyboards.inline import get_alert_keyboard
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_alert_keyboard(symbol)
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, f"🔔 Настройка алерта для {symbol}")
        
        logger.info(f"✅ Отправлено меню алерта для {symbol} @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в setup_alert_prompt для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()