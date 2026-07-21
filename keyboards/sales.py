"""
🎯 Клавиатуры для управления акциями
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ============================================================
# 👑 АДМИН-КЛАВИАТУРЫ ДЛЯ АКЦИЙ
# ============================================================

def get_sales_admin_keyboard():
    """
    👑 Главная админ-клавиатура для акций
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("➕ Создать акцию", callback_data="sale_create"),
        InlineKeyboardButton("📋 Список акций", callback_data="sales_list")
    )
    
    keyboard.add(
        InlineKeyboardButton("📊 Статистика", callback_data="sales_stats"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


def get_sale_detail_keyboard(sale_id: int):
    """
    🔍 Клавиатура для деталей акции
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Вкл/Выкл", callback_data=f"sale_toggle_{sale_id}"),
        InlineKeyboardButton("🗑️ Удалить", callback_data=f"sale_delete_{sale_id}")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад к списку", callback_data="sales_list")
    )
    
    return keyboard


def get_sale_edit_keyboard(sale_id: int):
    """
    ✏️ Клавиатура для редактирования акции
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Вкл/Выкл", callback_data=f"sale_toggle_{sale_id}"),
        InlineKeyboardButton("🗑️ Удалить", callback_data=f"sale_delete_{sale_id}")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


# ============================================================
# 🛒 КЛАВИАТУРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

def get_sales_list_keyboard(sales):
    """
    📋 Клавиатура со списком акций для пользователей
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 📝 Добавляем кнопки для каждой акции
    for sale in sales:
        if hasattr(sale, 'id'):
            keyboard.add(
                InlineKeyboardButton(
                    f"🎯 {sale.name}",
                    callback_data=f"sale_buy_{sale.id}"
                )
            )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


def get_sale_confirm_keyboard(sale_id: int):
    """
    ✅ Клавиатура подтверждения покупки
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("✅ Купить", callback_data=f"sale_confirm_{sale_id}"),
        InlineKeyboardButton("❌ Отмена", callback_data="sale_cancel")
    )
    
    return keyboard


def get_sale_cancel_keyboard():
    """
    ❌ Клавиатура отмены
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("❌ Отмена", callback_data="sale_cancel")
    )
    return keyboard


def get_sale_buy_keyboard(sale_id: int):
    """
    🛒 Клавиатура покупки акции
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🛒 Купить", callback_data=f"sale_confirm_{sale_id}"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard