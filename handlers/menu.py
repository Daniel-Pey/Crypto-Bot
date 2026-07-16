"""
📋 Обработчики главного меню и навигации
"""

from bot import bot
from utils.logger import logger
from database import get_db
from models import User
from keyboards.inline import get_start_keyboard, get_main_menu_keyboard, get_back_keyboard
from handlers.start import start_command

# ============================================================
# 🏠 КОМАНДА /MENU
# ============================================================

@bot.message_handler(commands=['menu'])  # 🔥 ДОБАВЛЕНО!
def menu_command(message):
    """
    📋 Команда /menu - показать главное меню
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{message.from_user.username} вызвал /menu")
    
    # 📊 Получаем сессию БД
    db = get_db()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=message.from_user.id).first()
        
        if not user:
            # 🚫 Если пользователь не найден, отправляем /start
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, начните с команды /start",
                reply_markup=get_start_keyboard()
            )
            return
        
        # 📊 Получаем информацию о подписке
        max_coins = user.get_max_coins()
        is_valid = user.has_valid_subscription()
        
        subscription_status = "✅ Активна" if is_valid else "❌ Неактивна"
        if user.subscription_type == 1:
            subscription_status = "🎁 Бесплатный"
        
        # 📊 Считаем количество монет пользователя
        coins_count = len(user.coins)
        
        # 📝 Формируем текст меню
        menu_text = f"""
📋 <b>Главное меню</b>

👤 <b>Профиль:</b>
• Тариф: {user.subscription_type} монет
• Статус: {subscription_status}
• Монет в трекинге: {coins_count}/{max_coins}

💡 <b>Доступные действия:</b>
• 📊 Посмотреть свои монеты
• ➕ Добавить новую монету
• 🔔 Настроить алерты
• 💎 Управлять подпиской
• ℹ️ Получить помощь
        """
        
        # 📤 Отправляем сообщение
        bot.send_message(
            message.chat.id,
            menu_text,
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard()
        )
        
        logger.info(f"✅ Отправлено меню пользователю @{message.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в menu_command для @{message.from_user.username}: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
        )
    finally:
        # 🧹 Закрываем сессию
        db.close()

# ============================================================
# 🔙 ОБРАБОТЧИКИ НАВИГАЦИИ
# ============================================================

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_to_menu(call):
    """
    🔙 Возврат в главное меню
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} вернулся в меню")
    
    # 📊 Получаем сессию БД
    db = get_db()
    
    try:
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            # 🚫 Если пользователь не найден, отправляем /start
            bot.send_message(
                call.message.chat.id,
                "❌ Пожалуйста, начните с команды /start",
                reply_markup=get_start_keyboard()
            )
            return
        
        # 📊 Получаем информацию о подписке
        max_coins = user.get_max_coins()
        is_valid = user.has_valid_subscription()
        
        subscription_status = "✅ Активна" if is_valid else "❌ Неактивна"
        if user.subscription_type == 1:
            subscription_status = "🎁 Бесплатный"
        
        # 📊 Считаем количество монет пользователя
        coins_count = len(user.coins)
        
        # 📝 Формируем текст меню
        menu_text = f"""
📋 <b>Главное меню</b>

👤 <b>Профиль:</b>
• Тариф: {user.subscription_type} монет
• Статус: {subscription_status}
• Монет в трекинге: {coins_count}/{max_coins}

💡 <b>Доступные действия:</b>
• 📊 Посмотреть свои монеты
• ➕ Добавить новую монету
• 🔔 Настроить алерты
• 💎 Управлять подпиской
• ℹ️ Получить помощь
        """
        
        # 📤 Обновляем сообщение
        bot.edit_message_text(
            menu_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_main_menu_keyboard()
        )
        
        # ✅ Отвечаем на callback
        bot.answer_callback_query(call.id, "🔙 Возврат в меню")
        
        logger.info(f"✅ Отправлено меню пользователю @{call.from_user.username}")
        
    except Exception as e:
        # ❌ Обрабатываем ошибки
        logger.error(f"💥 Ошибка в back_to_menu для @{call.from_user.username}: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    finally:
        # 🧹 Закрываем сессию
        db.close()

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_callback(call):
    """
    ℹ️ Обработчик команды помощи
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} запросил помощь")
    
    # 📝 Текст помощи
    help_text = """
ℹ️ <b>Помощь по боту</b>

📖 <b>Основные команды:</b>
• /start - Главное меню

🪙 <b>Управление монетами:</b>
• ➕ Добавить монету - введите символ (например, BTC)
• 📊 Мои монеты - просмотр добавленных монет
• 🗑️ Удалить монету - выберите из списка

🔔 <b>Алерты:</b>
• 📈 По достижении цены - уведомление при достижении указанной цены
• 📊 По изменению процента - уведомление при изменении на указанный %

💎 <b>Подписка:</b>
• 5 монет - 500 ₽/мес
• 10 монет - 1000 ₽/мес
• 15 монет - 1500 ₽/мес
• 20 монет - 2000 ₽/мес
• 🎁 1 монета - БЕСПЛАТНО

❓ <b>Частые вопросы:</b>
• Как добавить монету? Нажмите "➕ Добавить монету" и введите символ
• Как обновить подписку? Нажмите "💎 Тарифы" и выберите тариф
• Как настроить алерт? Выберите монету и нажмите "🔔 Настроить алерт"

📧 <b>Поддержка:</b>
Если у вас возникли проблемы, напишите @support_username
    """
    
    # 📤 Отправляем сообщение или редактируем существующее
    try:
        # 🔄 Пытаемся отредактировать сообщение
        bot.edit_message_text(
            help_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    except:
        # 📤 Если не удалось отредактировать, отправляем новое
        bot.send_message(
            call.message.chat.id,
            help_text,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    
    # ✅ Отвечаем на callback
    bot.answer_callback_query(call.id, "ℹ️ Помощь")
    
    logger.info(f"✅ Отправлена помощь пользователю @{call.from_user.username}")

@bot.callback_query_handler(func=lambda call: call.data == "refresh")
def refresh_callback(call):
    """
    🔄 Обновление текущего сообщения
    """
    # 📝 Логируем действие
    logger.info(f"👤 Пользователь @{call.from_user.username} обновил страницу")
    
    # 🔄 Просто возвращаем в меню
    back_to_menu(call)