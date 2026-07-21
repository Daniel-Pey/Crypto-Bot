"""
🎯 Обработчики для управления акциями (только для админов)
"""

from bot import bot
from utils.logger import logger
from utils.admin import admin_required, admin_callback_required, admin_log
from database import create_session
from models import User, Sale
from config import config
from datetime import datetime, timedelta
from keyboards.sales import (
    get_sales_admin_keyboard,
    get_sale_detail_keyboard,
    get_sale_edit_keyboard,
    get_sales_list_keyboard,
    get_sale_confirm_keyboard,
    get_sale_cancel_keyboard
)
from keyboards.inline import get_back_keyboard
import re


# ============================================================
# 📋 КОМАНДА /SALE (ДЛЯ ПОЛЬЗОВАТЕЛЕЙ)
# ============================================================

@bot.message_handler(commands=['sale'])
def show_active_sales(message):
    """
    🎯 Показать активные акции для пользователей
    """
    logger.info(f"👤 Пользователь @{message.from_user.username} запросил акции")
    
    db = create_session()
    
    try:
        # 🔍 Получаем все активные акции
        now = datetime.utcnow()
        sales = db.query(Sale).filter(
            Sale.is_active == True,
            Sale.end_date > now,
            Sale.max_uses > Sale.used_count
        ).order_by(Sale.is_featured.desc(), Sale.created_at.desc()).all()
        
        if not sales:
            text = """
🎯 <b>Акции</b>

📭 На данный момент активных акций нет.

💡 <b>Совет:</b>
• Подпишитесь на обновления, чтобы не пропустить новые акции
• Акции появляются регулярно
• Следите за новостями в боте
            """
            
            bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=get_back_keyboard()
            )
            return
        
        # 📝 Формируем список акций
        text = "🎯 <b>Доступные акции!</b>\n\n"
        
        for sale in sales:
            # 🏷️ Добавляем эмодзи для фичеринг-акций
            emoji = "🌟 " if sale.is_featured else "🎯 "
            
            # 📝 Формируем информацию об акции
            text += f"{emoji}<b>{sale.name}</b>\n"
            text += f"📊 {sale.get_coins_display()} - {sale.get_price_display()}\n"
            
            if sale.description:
                text += f"📝 {sale.description}\n"
            
            # 📅 Оставшееся время
            if sale.end_date:
                days_left = (sale.end_date - now).days
                if days_left > 0:
                    text += f"⏳ Осталось {days_left} дн.\n"
            
            # 📊 Осталось использований
            if sale.max_uses:
                left = sale.max_uses - sale.used_count
                text += f"🎫 Осталось {left} шт.\n"
            
            text += f"➡️ /buy_{sale.id} - Купить\n"
            text += "\n" + "─" * 30 + "\n\n"
        
        text += "💡 Для покупки используйте /buy_<id>"
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=get_sales_list_keyboard(sales)
        )
        
        logger.info(f"✅ Отправлены акции @{message.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в show_active_sales: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при загрузке акций"
        )
    finally:
        db.close()


# ============================================================
# 🛒 ПОКУПКА АКЦИИ
# ============================================================

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/buy_'))
def buy_sale(message):
    """
    🛒 Обработка покупки акции
    """
    try:
        # 📝 Извлекаем ID акции
        sale_id = int(message.text.replace('/buy_', ''))
        
        logger.info(f"👤 Пользователь @{message.from_user.username} покупает акцию {sale_id}")
        
        db = create_session()
        
        try:
            # 🔍 Получаем акцию
            sale = db.query(Sale).filter_by(id=sale_id).first()
            
            if not sale:
                bot.send_message(
                    message.chat.id,
                    "❌ Акция не найдена"
                )
                return
            
            # ✅ Проверяем, активна ли акция
            if not sale.is_valid():
                bot.send_message(
                    message.chat.id,
                    "❌ Эта акция уже недоступна"
                )
                return
            
            # 🔍 Получаем пользователя
            user = db.query(User).filter_by(telegram_id=message.from_user.id).first()
            
            if not user:
                bot.send_message(
                    message.chat.id,
                    "❌ Пользователь не найден. Используйте /start"
                )
                return
            
            # 📝 Формируем информацию о покупке
            text = f"""
🛒 <b>Покупка акции</b>

🎯 <b>Акция:</b> {sale.name}
📊 <b>Вы получаете:</b> {sale.get_coins_display()}
💰 <b>Цена:</b> {sale.get_price_display()}

📝 <b>Описание:</b>
{sale.description or 'Нет описания'}

✅ Подтвердите покупку
"""
            
            # 📤 Отправляем подтверждение
            bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=get_sale_confirm_keyboard(sale.id)
            )
            
            logger.info(f"✅ Отправлено подтверждение покупки @{message.from_user.username}")
            
        finally:
            db.close()
            
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Неверный формат команды. Используйте /buy_<id>"
        )
    except Exception as e:
        logger.error(f"💥 Ошибка в buy_sale: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка"
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("sale_confirm_"))
def confirm_sale_purchase(call):
    """
    ✅ Подтверждение покупки акции
    """
    # 📝 Извлекаем ID акции
    sale_id = int(call.data.replace("sale_confirm_", ""))
    
    logger.info(f"👤 Пользователь @{call.from_user.username} подтвердил покупку акции {sale_id}")
    
    db = create_session()
    
    try:
        # 🔍 Получаем акцию
        sale = db.query(Sale).filter_by(id=sale_id).first()
        
        if not sale:
            bot.answer_callback_query(call.id, "❌ Акция не найдена")
            return
        
        # ✅ Проверяем, активна ли акция
        if not sale.is_valid():
            bot.answer_callback_query(call.id, "❌ Акция уже недоступна")
            return
        
        # 🔍 Получаем пользователя
        user = db.query(User).filter_by(telegram_id=call.from_user.id).first()
        
        if not user:
            bot.answer_callback_query(call.id, "❌ Пользователь не найден")
            return
        
        # 🔄 Применяем акцию (обновляем подписку)
        old_coins = user.subscription_type
        user.subscription_type = sale.coins
        user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
        
        # 📊 Увеличиваем счетчик использований
        sale.used_count += 1
        
        db.commit()
        
        # 🎉 Успешная покупка
        text = f"""
✅ <b>Акция успешно применена!</b>

🎉 Поздравляем! Вы купили акцию "{sale.name}"

📊 <b>Ваш тариф обновлен:</b>
• Было: {old_coins} монет
• Стало: {sale.coins} монет
• Действует до: {user.subscription_end_date.strftime('%d.%m.%Y')}

💰 <b>Стоимость:</b> {sale.get_price_display()}
🎯 <b>Акция:</b> {sale.name}

💡 Теперь вы можете отслеживать больше монет!
        """
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
        bot.answer_callback_query(call.id, "✅ Акция применена!")
        
        logger.info(f"✅ Акция {sale.id} применена для @{call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в confirm_sale_purchase: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")
        db.rollback()
    finally:
        db.close()


@bot.callback_query_handler(func=lambda call: call.data == "sale_cancel")
def cancel_sale_purchase(call):
    """
    ❌ Отмена покупки акции
    """
    bot.edit_message_text(
        "❌ Покупка отменена",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=get_back_keyboard()
    )
    
    bot.answer_callback_query(call.id, "❌ Отменено")


# ============================================================
# 👑 АДМИНИСТРАТИВНЫЕ КОМАНДЫ ДЛЯ АКЦИЙ
# ============================================================

@admin_required
@bot.message_handler(commands=['sales_admin'])
def sales_admin_panel(message):
    """
    👑 Административная панель для управления акциями
    """
    logger.info(f"👑 Админ @{message.from_user.username} открыл панель акций")
    
    db = create_session()
    
    try:
        # 📊 Получаем статистику
        total_sales = db.query(Sale).count()
        active_sales = db.query(Sale).filter(Sale.is_active == True).count()
        
        text = f"""
👑 <b>Управление акциями</b>

📊 <b>Статистика:</b>
• Всего акций: {total_sales}
• Активных: {active_sales}

📋 <b>Доступные действия:</b>
• ➕ Создать новую акцию
• 📋 Список всех акций
• 📊 Статистика использования
        """
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=get_sales_admin_keyboard()
        )
        
        admin_log(f"Админ {message.from_user.username} открыл панель акций")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в sales_admin_panel: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка"
        )
    finally:
        db.close()


# ============================================================
# 📋 СПИСОК АКЦИЙ (ДЛЯ АДМИНА)
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data == "sales_list")
def sales_list_admin(call):
    """
    📋 Список всех акций для администратора
    """
    logger.info(f"👑 Админ @{call.from_user.username} запросил список акций")
    
    db = create_session()
    
    try:
        sales = db.query(Sale).order_by(Sale.created_at.desc()).all()
        
        if not sales:
            text = "📭 Нет созданных акций"
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=get_back_keyboard()
            )
            return
        
        text = "📋 <b>Список акций:</b>\n\n"
        
        for sale in sales:
            status = "✅" if sale.is_valid() else "❌"
            uses = f"{sale.used_count}/{sale.max_uses or '∞'}"
            
            text += f"{status} <b>{sale.name}</b>\n"
            text += f"   🪙 {sale.get_coins_display()} - {sale.get_price_display()}\n"
            text += f"   📊 Использований: {uses}\n"
            text += f"   🆔 ID: <code>{sale.id}</code>\n\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_sales_list_keyboard(sales)
        )
        
        bot.answer_callback_query(call.id, "📋 Список акций")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в sales_list_admin: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
    finally:
        db.close()


# ============================================================
# ➕ СОЗДАНИЕ АКЦИИ
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data == "sale_create")
def sale_create_prompt(call):
    """
    ➕ Запрос на создание новой акции
    """
    logger.info(f"👑 Админ @{call.from_user.username} начал создание акции")
    
    text = """
➕ <b>Создание новой акции</b>

📝 Введите данные акции в формате:
<code>Название | Описание | Количество_монет | Цена_руб | Цена_Stars | Дней_действия</code>

📌 <b>Пример:</b>
<code>Спецпредложение | 3 монеты за 5 Stars | 3 | 0 | 5 | 7</code>

⚠️ <b>Примечания:</b>
• Если цена в рублях не нужна, поставьте 0
• Если цена в Stars не нужна, поставьте 0
• Дней действия: 0 = бессрочно
• Максимальное количество использований: 0 = без ограничений

⌨️ <b>Введите данные:</b>
    """
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=get_sale_cancel_keyboard()
    )
    
    # 🔄 Регистрируем следующий шаг
    bot.register_next_step_handler(call.message, process_sale_create)
    
    bot.answer_callback_query(call.id, "➕ Создание акции")


def process_sale_create(message):
    """
    📝 Обработка ввода данных для создания акции
    """
    # ✅ Проверяем, что пользователь админ
    if message.from_user.id not in config.ADMINS_ID:
        bot.send_message(
            message.chat.id,
            "🚫 Доступ запрещен!"
        )
        return
    
    # ❌ Проверяем отмену
    if message.text == "❌ Отмена":
        bot.send_message(
            message.chat.id,
            "❌ Создание акции отменено",
            reply_markup=get_back_keyboard()
        )
        return
    
    try:
        # 📝 Парсим введенные данные
        parts = message.text.split('|')
        parts = [p.strip() for p in parts]
        
        if len(parts) < 6:
            bot.send_message(
                message.chat.id,
                "❌ Неверный формат. Введите все 6 полей через |"
            )
            return
        
        name = parts[0]
        description = parts[1]
        coins = int(parts[2])
        price_rub = int(parts[3])
        price_stars = int(parts[4])
        days = int(parts[5])
        
        # ✅ Валидация
        if coins < 1:
            bot.send_message(message.chat.id, "❌ Количество монет должно быть >= 1")
            return
        
        if price_rub < 0 or price_stars < 0:
            bot.send_message(message.chat.id, "❌ Цена не может быть отрицательной")
            return
        
        if price_rub == 0 and price_stars == 0:
            bot.send_message(message.chat.id, "❌ Укажите хотя бы одну цену")
            return
        
        # 📅 Вычисляем дату окончания
        end_date = None
        if days > 0:
            end_date = datetime.utcnow() + timedelta(days=days)
        
        # 📊 Сохраняем в БД
        db = create_session()
        
        try:
            sale = Sale(
                name=name,
                description=description,
                coins=coins,
                price_rub=price_rub if price_rub > 0 else None,
                price_stars=price_stars if price_stars > 0 else None,
                start_date=datetime.utcnow(),
                end_date=end_date,
                is_active=True,
                created_by=message.from_user.id
            )
            
            db.add(sale)
            db.commit()
            
            # 🎉 Успешное создание
            text = f"""
✅ <b>Акция успешно создана!</b>

📊 <b>Данные акции:</b>
• Название: {sale.name}
• Описание: {sale.description or 'Нет'}
• Монет: {sale.coins}
• Цена: {sale.get_price_display()}
• Действует: {'Бессрочно' if not sale.end_date else f'до {sale.end_date.strftime("%d.%m.%Y")}'}
• ID: <code>{sale.id}</code>

💡 Пользователи могут купить акцию по команде /buy_{sale.id}
            """
            
            bot.send_message(
                message.chat.id,
                text,
                parse_mode='HTML',
                reply_markup=get_sale_detail_keyboard(sale.id)
            )
            
            admin_log(f"Создана акция {sale.id}: {sale.name} ({sale.coins} монет)")
            
        except Exception as e:
            logger.error(f"💥 Ошибка сохранения акции: {e}")
            db.rollback()
            bot.send_message(
                message.chat.id,
                f"❌ Ошибка при создании акции: {e}"
            )
        finally:
            db.close()
            
    except ValueError as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка в данных: {e}"
        )
    except Exception as e:
        logger.error(f"💥 Ошибка в process_sale_create: {e}")
        bot.send_message(
            message.chat.id,
            f"❌ Произошла ошибка: {e}"
        )


# ============================================================
# 🔍 ДЕТАЛИ АКЦИИ (ДЛЯ АДМИНА)
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data.startswith("sale_detail_"))
def sale_detail(call):
    """
    🔍 Детальная информация об акции (для админа)
    """
    # 📝 Извлекаем ID акции
    sale_id = int(call.data.replace("sale_detail_", ""))
    
    logger.info(f"👑 Админ @{call.from_user.username} запросил детали акции {sale_id}")
    
    db = create_session()
    
    try:
        sale = db.query(Sale).filter_by(id=sale_id).first()
        
        if not sale:
            bot.answer_callback_query(call.id, "❌ Акция не найдена")
            return
        
        # 📝 Формируем информацию
        status = "✅ Активна" if sale.is_valid() else "❌ Неактивна"
        uses = f"{sale.used_count}/{sale.max_uses or '∞'}"
        
        text = f"""
🔍 <b>Детали акции #{sale.id}</b>

📋 <b>Основная информация:</b>
• Название: <b>{sale.name}</b>
• Описание: {sale.description or 'Нет'}
• Статус: {status}

💰 <b>Цена:</b>
• Рубли: {sale.price_rub or 'Нет'} ₽
• Stars: {sale.price_stars or 'Нет'} ⭐

🪙 <b>Монет:</b> {sale.coins}

📊 <b>Использование:</b>
• Использовано: {uses}
• Создана: {sale.created_at.strftime('%d.%m.%Y %H:%M')}
• Действует: {'Бессрочно' if not sale.end_date else sale.end_date.strftime('%d.%m.%Y')}

📝 <b>Команда для пользователей:</b>
<code>/buy_{sale.id}</code>
        """
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_sale_edit_keyboard(sale.id)
        )
        
        bot.answer_callback_query(call.id, f"🔍 Акция #{sale.id}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в sale_detail: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
    finally:
        db.close()


# ============================================================
# 🔄 УПРАВЛЕНИЕ АКЦИЕЙ (ДЛЯ АДМИНА)
# ============================================================

@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data.startswith("sale_toggle_"))
def sale_toggle(call):
    """
    🔄 Включение/отключение акции
    """
    # 📝 Извлекаем ID акции
    sale_id = int(call.data.replace("sale_toggle_", ""))
    
    logger.info(f"👑 Админ @{call.from_user.username} переключает акцию {sale_id}")
    
    db = create_session()
    
    try:
        sale = db.query(Sale).filter_by(id=sale_id).first()
        
        if not sale:
            bot.answer_callback_query(call.id, "❌ Акция не найдена")
            return
        
        # 🔄 Переключаем статус
        sale.is_active = not sale.is_active
        db.commit()
        
        status = "включена" if sale.is_active else "выключена"
        
        bot.answer_callback_query(call.id, f"✅ Акция {status}")
        
        # 🔄 Обновляем детали
        sale_detail(call)
        
        admin_log(f"Акция {sale_id} {status} админом {call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в sale_toggle: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
        db.rollback()
    finally:
        db.close()


@admin_callback_required
@bot.callback_query_handler(func=lambda call: call.data.startswith("sale_delete_"))
def sale_delete(call):
    """
    🗑️ Удаление акции
    """
    # 📝 Извлекаем ID акции
    sale_id = int(call.data.replace("sale_delete_", ""))
    
    logger.info(f"👑 Админ @{call.from_user.username} удаляет акцию {sale_id}")
    
    db = create_session()
    
    try:
        sale = db.query(Sale).filter_by(id=sale_id).first()
        
        if not sale:
            bot.answer_callback_query(call.id, "❌ Акция не найдена")
            return
        
        # 🗑️ Удаляем акцию
        db.delete(sale)
        db.commit()
        
        bot.edit_message_text(
            f"🗑️ Акция #{sale_id} удалена",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_back_keyboard()
        )
        
        bot.answer_callback_query(call.id, "🗑️ Акция удалена")
        
        admin_log(f"Акция {sale_id} удалена админом {call.from_user.username}")
        
    except Exception as e:
        logger.error(f"💥 Ошибка в sale_delete: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка")
        db.rollback()
    finally:
        db.close()