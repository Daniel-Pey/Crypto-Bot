"""
⌨️ Основные Reply-клавиатуры для бота

Этот файл содержит клавиатуры, которые отображаются в виде кнопок
в поле ввода сообщения (ReplyKeyboardMarkup).
Используются для упрощения взаимодействия с пользователем.
"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


# ============================================================
# 🏠 ГЛАВНЫЕ КЛАВИАТУРЫ
# ============================================================

def get_main_keyboard():
    """
    ⌨️ Главная Reply-клавиатура
    
    Отображается в поле ввода сообщения и содержит основные команды.
    Используется после регистрации пользователя.
    
    Returns:
        ReplyKeyboardMarkup: Главная клавиатура с основными действиями
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,           # 🔢 Количество кнопок в строке
        resize_keyboard=True,   # 📏 Автоматическое изменение размера
        one_time_keyboard=False # 🔄 Постоянная клавиатура (не скрывается после нажатия)
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
    
    # ℹ️ Третья строка - помощь и обновление
    keyboard.add(
        KeyboardButton("ℹ️ Помощь"),
        KeyboardButton("🔄 Обновить")
    )
    
    return keyboard


def get_simple_main_keyboard():
    """
    ⌨️ Упрощенная главная Reply-клавиатура
    
    Используется для пользователей, которые только начали работу.
    Содержит только базовые функции.
    
    Returns:
        ReplyKeyboardMarkup: Упрощенная клавиатура
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    keyboard.add(
        KeyboardButton("📊 Мои монеты"),
        KeyboardButton("➕ Добавить монету")
    )
    
    keyboard.add(
        KeyboardButton("ℹ️ Помощь")
    )
    
    return keyboard


# ============================================================
# 📝 КЛАВИАТУРЫ ДЛЯ ВВОДА ДАННЫХ
# ============================================================

def get_cancel_keyboard():
    """
    ❌ Reply-клавиатура с кнопкой отмены
    
    Используется когда бот ожидает ввод данных от пользователя.
    Позволяет отменить текущее действие.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопкой отмены
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=True  # 🔄 Скрывается после нажатия
    )
    
    keyboard.add(
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


def get_confirm_keyboard():
    """
    ✅ Reply-клавиатура с кнопками подтверждения
    
    Используется для критических действий (удаление, оплата и т.д.)
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками "Да" и "Нет"
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=True  # 🔄 Скрывается после нажатия
    )
    
    keyboard.add(
        KeyboardButton("✅ Да"),
        KeyboardButton("❌ Нет")
    )
    
    return keyboard


def get_price_input_keyboard():
    """
    💰 Reply-клавиатура для ввода цены
    
    Содержит примеры цен для быстрого ввода.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с примерами цен
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=3,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # 📊 Примеры цен для популярных криптовалют
    keyboard.add(
        KeyboardButton("50000"),
        KeyboardButton("75000"),
        KeyboardButton("100000")
    )
    
    keyboard.add(
        KeyboardButton("150000"),
        KeyboardButton("200000"),
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


def get_percent_input_keyboard():
    """
    📊 Reply-клавиатура для ввода процента
    
    Содержит примеры процентов для быстрого ввода.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с примерами процентов
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=3,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    keyboard.add(
        KeyboardButton("1"),
        KeyboardButton("2"),
        KeyboardButton("5")
    )
    
    keyboard.add(
        KeyboardButton("10"),
        KeyboardButton("15"),
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


def get_coin_symbol_keyboard():
    """
    🪙 Reply-клавиатура с популярными символами криптовалют
    
    Используется для быстрого добавления популярных монет.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с популярными символами
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=4,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # 🪙 Популярные криптовалюты
    keyboard.add(
        KeyboardButton("BTC"),
        KeyboardButton("ETH"),
        KeyboardButton("SOL"),
        KeyboardButton("ADA")
    )
    
    keyboard.add(
        KeyboardButton("XRP"),
        KeyboardButton("DOGE"),
        KeyboardButton("DOT"),
        KeyboardButton("LINK")
    )
    
    keyboard.add(
        KeyboardButton("MATIC"),
        KeyboardButton("AVAX"),
        KeyboardButton("UNI"),
        KeyboardButton("ATOM")
    )
    
    keyboard.add(
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


# ============================================================
# 🔢 КЛАВИАТУРЫ С ЧИСЛАМИ
# ============================================================

def get_number_keyboard(max_number=10):
    """
    🔢 Reply-клавиатура с числами от 1 до max_number
    
    Args:
        max_number (int): Максимальное число (по умолчанию 10)
        
    Returns:
        ReplyKeyboardMarkup: Клавиатура с числами
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=5,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # 📊 Добавляем кнопки с числами
    row = []
    for i in range(1, max_number + 1):
        row.append(KeyboardButton(str(i)))
        if len(row) == 5:
            keyboard.add(*row)
            row = []
    
    # ➕ Добавляем оставшиеся кнопки
    if row:
        keyboard.add(*row)
    
    # ❌ Кнопка отмены
    keyboard.add(
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


# ============================================================
# 🗑️ УДАЛЕНИЕ КЛАВИАТУРЫ
# ============================================================

def remove_keyboard():
    """
    🗑️ Клавиатура для удаления текущей Reply-клавиатуры
    
    Используется когда нужно убрать кнопки из поля ввода.
    
    Returns:
        ReplyKeyboardMarkup: Пустая клавиатура для удаления
    """
    return ReplyKeyboardMarkup(remove_keyboard=True)


# ============================================================
# 👑 АДМИНИСТРАТИВНЫЕ КЛАВИАТУРЫ
# ============================================================

def get_admin_keyboard():
    """
    👑 Reply-клавиатура для администратора
    
    Содержит административные функции.
    Доступна только для пользователей с правами администратора.
    
    Returns:
        ReplyKeyboardMarkup: Административная клавиатура
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    keyboard.add(
        KeyboardButton("📊 Статистика"),
        KeyboardButton("📨 Рассылка")
    )
    
    keyboard.add(
        KeyboardButton("👥 Пользователи"),
        KeyboardButton("💎 Управление тарифами")
    )
    
    keyboard.add(
        KeyboardButton("📝 Логи"),
        KeyboardButton("🔄 Перезапустить")
    )
    
    keyboard.add(
        KeyboardButton("🔙 В главное меню")
    )
    
    return keyboard


# ============================================================
# 💡 ДОПОЛНИТЕЛЬНЫЕ КЛАВИАТУРЫ
# ============================================================

def get_language_keyboard():
    """
    🌐 Reply-клавиатура для выбора языка
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с выбором языка
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    keyboard.add(
        KeyboardButton("🇷🇺 Русский"),
        KeyboardButton("🇬🇧 English")
    )
    
    keyboard.add(
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


def get_feedback_keyboard():
    """
    💬 Reply-клавиатура для обратной связи
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с вариантами обратной связи
    """
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    keyboard.add(
        KeyboardButton("🐛 Сообщить об ошибке"),
        KeyboardButton("💡 Предложение")
    )
    
    keyboard.add(
        KeyboardButton("📧 Связаться с поддержкой"),
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard