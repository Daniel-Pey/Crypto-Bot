"""
⌨️ Reply-клавиатуры для бота
Используются для быстрого ввода данных
"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_reply_keyboard():
    """
    ⌨️ Основная reply-клавиатура
    
    Используется для быстрого доступа к основным функциям
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками-командами
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    # 📊 Первая строка - управление монетами
    keyboard.add(
        KeyboardButton("📊 Мои монеты"),
        KeyboardButton("➕ Добавить монету")
    )
    
    # 🔔 Вторая строка - алерты и подписка
    keyboard.add(
        KeyboardButton("🔔 Мои алерты"),
        KeyboardButton("💎 Тарифы")
    )
    
    # ℹ️ Третья строка - помощь
    keyboard.add(
        KeyboardButton("ℹ️ Помощь"),
        KeyboardButton("🔄 Обновить")
    )
    
    return keyboard


def get_cancel_reply_keyboard():
    """
    ⌨️ Reply-клавиатура с кнопкой отмены
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопкой отмены
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    keyboard.add(
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


def get_confirm_reply_keyboard():
    """
    ⌨️ Reply-клавиатура с кнопками подтверждения
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками "Да" и "Нет"
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    keyboard.add(
        KeyboardButton("✅ Да"),
        KeyboardButton("❌ Нет")
    )
    
    return keyboard


def get_remove_keyboard():
    """
    ⌨️ Клавиатура для удаления предыдущей reply-клавиатуры
    
    Returns:
        ReplyKeyboardMarkup: Пустая клавиатура для удаления
    """
    return ReplyKeyboardMarkup(remove_keyboard=True)