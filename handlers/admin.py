"""
👑 Административные команды бота
"""

from bot import bot
from config import config
from utils.logger import logger
from utils.admin import (
    admin_required,
    admin_callback_required,
    is_admin
)
from database import create_session
from models import User, Coin, Alert
from datetime import datetime
from keyboards.admin import (
    get_admin_keyboard, get_admin_menu_keyboard,
    get_admin_cancel_keyboard,
    get_admin_back_keyboard,
    get_admin_confirm_broadcast_keyboard
)


# ============================================================
# 📋 КОМАНДА /ADMIN
# ============================================================

@admin_required
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """
    👑 Административная панель
    Доступна только для администраторов
    """
    logger.info(f"👑 Администратор @{message.from_user.username} открыл панель")
    
    # 📝 Текст панели
    text = """
👑 <b>Административная панель</b>

📊 <b>Статистика:</b>
• Всего пользователей: {users_count}
• Всего монет: {coins_count}
• Активных подписок: {active_subscriptions}

📋 <b>Доступные действия:</b>
• 👥 Просмотр пользователей
• 📊 Статистика системы
• 📨 Рассылка сообщений
• 📝 Логи админа
• ℹ️ Информация о системе
    """
    
    # 📊 Получаем статистику
    db = create_session()
    
    try:
        users_count = db.query(User).count()
        coins_count = db.query(Coin).count()
        active_subscriptions = db.query(User).filter(User.subscription_type > 1).count()
        
        text = text.format(
            users_count=users_count,
            coins_count=coins_count,
            active_subscriptions=active_subscriptions
        )
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=get_admin_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"💥 Ошибка в admin_panel: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при загрузке панели"
        )
    finally:
        db.close()


# ============================================================
# 👥 ПРОСМОТР ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data == "admin_users")
def admin_users(call):
    """
    👥 Просмотр пользователей (админ-функция)
    """
    db = create_session()
    
    try:
        # 📊 Получаем всех пользователей
        users = db.query(User).order_by(User.created_at.desc()).limit(50).all()
        
        if not users:
            text = "📭 Нет пользователей"
        else:
            text = "👥 <b>Последние 50 пользователей:</b>\n\n"
            
            for i, user in enumerate(users, 1):
                username = f"@{user.username}" if user.username else "Не указан"
                status = "✅" if user.has_valid_subscription() else "❌"
                coins_count = len(user.coins)
                max_coins = user.get_max_coins()
                
                text += (
                    f"{i}. {status} <b>{user.first_name}</b> "
                    f"({username})\n"
                    f"   📊 ID: <code>{user.telegram_id}</code>\n"
                    f"   🪙 Монет: {coins_count}/{max_coins}\n"
                    f"   📅 Зарегистрирован: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                )
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_admin_back_keyboard()
        )
        
        bot.answer_callback_query(call.id, "👥 Список пользователей")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в admin_users: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
    finally:
        db.close()


# ============================================================
# 📨 РАССЫЛКА СООБЩЕНИЙ
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def admin_broadcast_prompt(call):
    """
    📨 Запрос текста для рассылки
    """
    text = """
📨 <b>Рассылка сообщений</b>

✏️ Введите текст сообщения для рассылки всем пользователям.

📌 <b>Внимание:</b>
• Поддерживается HTML-разметка
• Сообщение будет отправлено ВСЕМ пользователям
• Отменить рассылку нельзя

⌨️ <b>Введите текст:</b>
    """
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=get_admin_cancel_keyboard()
    )
    
    # 🔄 Регистрируем следующий шаг
    bot.register_next_step_handler(call.message, process_broadcast)
    
    bot.answer_callback_query(call.id, "📨 Напишите текст")


def process_broadcast(message):
    """
    📨 Обработка текста для рассылки
    """
    # ✅ Проверяем, что пользователь админ
    if not is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🚫 Доступ запрещен!"
        )
        return
    
    broadcast_text = message.text
    
    if broadcast_text == "❌ Отмена":
        bot.send_message(
            message.chat.id,
            "❌ Рассылка отменена",
            reply_markup=get_admin_menu_keyboard()
        )
        return
    
    # 📊 Получаем всех пользователей
    db = create_session()
    
    try:
        users = db.query(User).all()
        total = len(users)
        
        if total == 0:
            bot.send_message(
                message.chat.id,
                "📭 Нет пользователей для рассылки"
            )
            return
        
        # 📨 Отправляем подтверждение
        confirm_text = f"""
📨 <b>Подтверждение рассылки</b>

📊 <b>Получателей:</b> {total} пользователей
📝 <b>Текст сообщения:</b>

{broadcast_text}

✅ Отправить рассылку?
        """
        
        bot.send_message(
            message.chat.id,
            confirm_text,
            parse_mode='HTML',
            reply_markup=get_admin_confirm_broadcast_keyboard(broadcast_text)
        )
        
    except Exception as e:
        logger.error(f"💥 Ошибка в process_broadcast: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка: {e}"
        )
    finally:
        db.close()


@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_broadcast_confirm_"))
def admin_broadcast_confirm(call):
    """
    📨 Подтверждение и отправка рассылки
    """
    # Извлекаем текст
    broadcast_text = call.data.replace("admin_broadcast_confirm_", "")
    
    db = create_session()
    
    try:
        users = db.query(User).all()
        total = len(users)
        
        success = 0
        failed = 0
        
        # 📨 Отправляем сообщение каждому пользователю
        for user in users:
            try:
                bot.send_message(
                    user.telegram_id,
                    f"📨 <b>Рассылка от администратора</b>\n\n{broadcast_text}",
                    parse_mode='HTML'
                )
                success += 1
            except Exception as e:
                failed += 1
                logger.error(f"❌ Ошибка отправки пользователю {user.telegram_id}: {e}")
        
        # 📊 Результат
        result_text = f"""
✅ <b>Рассылка завершена!</b>

📊 <b>Статистика:</b>
• ✅ Успешно: {success}
• ❌ Ошибок: {failed}
• 📊 Всего: {total}
        """
        
        bot.edit_message_text(
            result_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_admin_menu_keyboard()
        )
        
        bot.answer_callback_query(call.id, "✅ Рассылка выполнена")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в admin_broadcast_confirm: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
    finally:
        db.close()


# ============================================================
# 📊 СТАТИСТИКА
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    """
    📊 Статистика системы
    """
    db = create_session()
    
    try:
        # 📊 Собираем статистику
        users_total = db.query(User).count()
        users_active = db.query(User).filter(User.is_active == True).count()
        users_paid = db.query(User).filter(User.subscription_type > 1).count()
        
        coins_total = db.query(Coin).count()
        alerts_total = db.query(Alert).count()
        
        # 📝 Формируем текст
        text = f"""
📊 <b>Статистика системы</b>

👥 <b>Пользователи:</b>
• Всего: {users_total}
• Активных: {users_active}
• С подпиской: {users_paid}

🪙 <b>Монеты:</b>
• Всего монет: {coins_total}
• Активных алертов: {alerts_total}

📈 <b>Подписки:</b>
"""
        
        # 📊 Подсчет по тарифам
        for coins, price in config.SUBSCRIPTION_PRICES.items():
            count = db.query(User).filter(User.subscription_type == coins).count()
            text += f"• {coins} монет: {count} пользователей\n"
        
        text += f"• Бесплатно: {db.query(User).filter(User.subscription_type == 1).count()} пользователей\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_admin_back_keyboard()
        )
        
        bot.answer_callback_query(call.id, "📊 Статистика")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в admin_stats: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
    finally:
        db.close()


# ============================================================
# ℹ️ ИНФОРМАЦИЯ О СИСТЕМЕ
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data == "admin_info")
def admin_info(call):
    """
    ℹ️ Информация о системе
    """
    import sys
    import platform
    
    text = f"""
ℹ️ <b>Информация о системе</b>

🤖 <b>Бот:</b>
• Версия: {config.VERSION}
• Python: {sys.version.split()[0]}
• ОС: {platform.system()} {platform.release()}

📊 <b>База данных:</b>
• Тип: SQLite
• Файл: {config.DATABASE_FILE}

🔄 <b>Сервисы:</b>
• PriceChecker: Активен
• Интервал проверки: {config.PRICE_CHECK_INTERVAL}с
"""

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=get_admin_back_keyboard()
    )
    
    bot.answer_callback_query(call.id, "ℹ️ Информация")