"""
👑 Клавиатуры для административной панели
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ============================================================
# 👑 ГЛАВНАЯ АДМИН-КЛАВИАТУРА
# ============================================================

def get_admin_keyboard():
    """
    👑 Главная административная клавиатура
    
    Используется для быстрого доступа к админ-функциям
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    )
    
    keyboard.add(
        InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("📝 Логи", callback_data="admin_logs")
    )
    
    keyboard.add(
        InlineKeyboardButton("ℹ️ Информация", callback_data="admin_info"),
        InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")
    )
    
    return keyboard


def get_admin_menu_keyboard():
    """
    👑 Клавиатура для админ-меню (расширенная версия)
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
    )
    
    keyboard.add(
        InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("📝 Логи", callback_data="admin_logs")
    )
    
    keyboard.add(
        InlineKeyboardButton("ℹ️ Информация", callback_data="admin_info"),
        InlineKeyboardButton("🔄 Обновить", callback_data="admin_refresh")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")
    )
    
    return keyboard


# ============================================================
# 🔙 НАВИГАЦИОННЫЕ КЛАВИАТУРЫ
# ============================================================

def get_admin_back_keyboard():
    """
    🔙 Клавиатура с кнопкой назад в админ-панель
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🔙 Назад в админ-панель", callback_data="admin_back")
    )
    return keyboard


def get_admin_cancel_keyboard():
    """
    ❌ Клавиатура отмены
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("❌ Отмена", callback_data="admin_cancel")
    )
    return keyboard


# ============================================================
# 📨 КЛАВИАТУРЫ ДЛЯ РАССЫЛКИ
# ============================================================

def get_admin_confirm_broadcast_keyboard(text):
    """
    📨 Клавиатура подтверждения рассылки
    
    Args:
        text: Текст для рассылки
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 🔥 Текст может быть длинным, обрезаем для callback
    short_text = text[:50] if len(text) > 50 else text
    
    keyboard.add(
        InlineKeyboardButton(
            "✅ Отправить рассылку",
            callback_data=f"admin_broadcast_confirm_{short_text}"
        )
    )
    
    keyboard.add(
        InlineKeyboardButton("❌ Отмена", callback_data="admin_cancel")
    )
    
    return keyboard


# ============================================================
# 📝 КЛАВИАТУРЫ ДЛЯ ЛОГОВ
# ============================================================

def get_admin_logs_keyboard():
    """
    📝 Клавиатура для управления логами
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить", callback_data="admin_logs"),
        InlineKeyboardButton("🗑️ Очистить", callback_data="admin_clear_logs")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
    )
    
    return keyboard


# ============================================================
# 🔄 ОБРАБОТЧИКИ CALLBACK ДЛЯ АДМИН-КЛАВИАТУР
# ============================================================

def get_admin_callback_handlers():
    """
    🔄 Регистрация всех callback-обработчиков для админ-клавиатур
    
    Этот словарь используется для маршрутизации callback-запросов
    """
    return {
        'admin_users': '👥 Просмотр пользователей',
        'admin_stats': '📊 Статистика системы',
        'admin_broadcast': '📨 Рассылка сообщений',
        'admin_logs': '📝 Просмотр логов',
        'admin_info': 'ℹ️ Информация о системе',
        'admin_refresh': '🔄 Обновление',
        'admin_back': '🔙 Назад в админ-панель',
        'admin_cancel': '❌ Отмена',
        'admin_clear_logs': '🗑️ Очистка логов'
    }


# ============================================================
# 👑 ДОПОЛНИТЕЛЬНЫЕ КЛАВИАТУРЫ
# ============================================================

def get_admin_users_keyboard(page: int = 1, total_pages: int = 1):
    """
    👥 Клавиатура для навигации по списку пользователей
    
    Args:
        page: Текущая страница
        total_pages: Всего страниц
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # ⬅️➡️ Кнопки навигации
    nav_buttons = []
    
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅️", callback_data=f"admin_users_page_{page-1}")
        )
    
    nav_buttons.append(
        InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="admin_users_current")
    )
    
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("➡️", callback_data=f"admin_users_page_{page+1}")
        )
    
    if nav_buttons:
        keyboard.add(*nav_buttons)
    
    # 🔙 Кнопка назад
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
    )
    
    return keyboard


def get_admin_stats_keyboard():
    """
    📊 Клавиатура для статистики
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить", callback_data="admin_stats"),
        InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_stats_detailed")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
    )
    
    return keyboard


def get_admin_broadcast_keyboard():
    """
    📨 Клавиатура для рассылки
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📨 Написать сообщение", callback_data="admin_broadcast_new"),
        InlineKeyboardButton("📋 Шаблоны", callback_data="admin_broadcast_templates")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
    )
    
    return keyboard


def get_admin_info_keyboard():
    """
    ℹ️ Клавиатура для информации о системе
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить", callback_data="admin_info"),
        InlineKeyboardButton("📊 Логи", callback_data="admin_logs")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="admin_back")
    )
    
    return keyboard