"""
🎨 Inline-клавиатуры для бота
Все клавиатуры используют InlineKeyboardMarkup для интерактивного взаимодействия
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config


# ============================================================
# 🏠 ГЛАВНЫЕ КЛАВИАТУРЫ
# ============================================================

def get_start_keyboard():
    """
    🎨 Главная клавиатура для приветствия
    
    Используется при первом запуске бота или после команды /start
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с основными действиями
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 📊 Первая строка - управление монетами
    keyboard.add(
        InlineKeyboardButton("📊 Мои монеты", callback_data="my_coins"),
        InlineKeyboardButton("➕ Добавить монету", callback_data="add_coin")
    )
    
    # 🔔 Вторая строка - алерты и подписка
    keyboard.add(
        InlineKeyboardButton("🔔 Мои алерты", callback_data="my_alerts"),
        InlineKeyboardButton("💎 Тарифы", callback_data="subscription")
    )
    
    # ℹ️ Третья строка - помощь
    keyboard.add(
        InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
    )
    
    return keyboard


def get_main_menu_keyboard():
    """
    🎨 Клавиатура главного меню
    
    Используется для навигации по основным разделам бота
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с полным набором действий
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 📊 Первая строка - управление монетами
    keyboard.add(
        InlineKeyboardButton("📊 Мои монеты", callback_data="my_coins"),
        InlineKeyboardButton("➕ Добавить монету", callback_data="add_coin")
    )
    
    # 🔔 Вторая строка - алерты и подписка
    keyboard.add(
        InlineKeyboardButton("🔔 Мои алерты", callback_data="my_alerts"),
        InlineKeyboardButton("💎 Тарифы", callback_data="subscription")
    )
    
    # 🔄 Третья строка - дополнительные функции
    keyboard.add(
        InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
        InlineKeyboardButton("🔄 Обновить", callback_data="refresh")
    )
    
    return keyboard


# ============================================================
# 🪙 КЛАВИАТУРЫ ДЛЯ МОНЕТ
# ============================================================

def get_coins_keyboard(coins_list):
    """
    🪙 Клавиатура со списком монет пользователя
    
    Args:
        coins_list (list): Список монет пользователя (объекты UserCoin или строки)
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками для каждой монеты
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 🔄 Если список не пустой, создаем кнопки для каждой монеты
    if coins_list:
        for user_coin in coins_list:
            # 🔍 Определяем символ монеты
            if hasattr(user_coin, 'coin'):
                symbol = user_coin.coin.symbol
            else:
                symbol = user_coin
            
            # ➕ Добавляем кнопку с символом монеты
            keyboard.add(
                InlineKeyboardButton(f"🪙 {symbol}", callback_data=f"coin_{symbol}")
            )
    
    # ➕ Если монет нет, предлагаем добавить первую
    if not coins_list:
        keyboard.add(
            InlineKeyboardButton("➕ Добавить первую монету", callback_data="add_coin")
        )
    
    # 🔙 Всегда добавляем кнопку "Назад"
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


def get_coin_detail_keyboard(symbol):
    """
    🪙 Клавиатура для детальной информации о монете
    
    Args:
        symbol (str): Символ монеты (например, "BTC")
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с действиями для монеты
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 🔔 Первая строка - настройка алерта
    keyboard.add(
        InlineKeyboardButton("🔔 Настроить алерт", callback_data=f"setup_alert_{symbol}")
    )
    
    # 🗑️ Вторая строка - удаление монеты
    keyboard.add(
        InlineKeyboardButton("🗑️ Удалить монету", callback_data=f"delete_coin_{symbol}")
    )
    
    # 🔙 Третья строка - возврат к списку
    keyboard.add(
        InlineKeyboardButton("🔙 Назад к списку", callback_data="my_coins")
    )
    
    return keyboard


# ============================================================
# 💎 КЛАВИАТУРЫ ДЛЯ ПОДПИСКИ
# ============================================================

def get_subscription_keyboard():
    """
    💎 Клавиатура с тарифами подписки
    
    Отображает все доступные тарифы из конфигурации
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками тарифов
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # 💰 Добавляем кнопки для каждого платного тарифа
    for coins, price in config.SUBSCRIPTION_PRICES.items():
        keyboard.add(
            InlineKeyboardButton(
                f"💎 {coins} монет - {price} ₽/мес",
                callback_data=f"subscribe_{coins}"
            )
        )
    
    # 🎁 Добавляем бесплатный тариф
    keyboard.add(
        InlineKeyboardButton(
            "🎁 Бесплатно (1 монета)",
            callback_data="subscribe_1"
        )
    )
    
    # 🔙 Навигация назад
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


def get_payments_keyboard(coins, price) -> InlineKeyboardMarkup:
    """
    💳 Клавиатура выбора способа оплаты
    
    Args:
        coins (int): Количество монет в тарифе
        price (int): Стоимость тарифа в рублях
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками подтверждения/отмены
    """
    keyboard = InlineKeyboardMarkup(row_width=len(config.PAYMENT_TYPES))
    
    for callback_type, title in config.PAYMENT_TYPES:
        keyboard.add(
            InlineKeyboardButton(
                title,
                callback_data=f"payment_type_{callback_type}_{coins}_{price}"
            )
        )
    
    # ❌ Кнопка отмены (возврат к тарифам)
    keyboard.add(
        InlineKeyboardButton("❌ Отмена", callback_data="subscription")
    )
        
    return keyboard


def get_confirm_payment_keyboard(coins, price) -> InlineKeyboardMarkup:
    """
    💳 Клавиатура подтверждения платежа
    
    Args:
        coins (int): Количество монет в тарифе
        price (int): Стоимость тарифа в рублях
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками подтверждения/отмены
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # ✅ Кнопка подтверждения оплаты
    keyboard.add(
        InlineKeyboardButton(
            f"✅ Подтвердить оплату {price}₽",
            callback_data=f"confirm_payment_{coins}_{price}"
        )
    )
    
    # ❌ Кнопка отмены (возврат к тарифам)
    keyboard.add(
        InlineKeyboardButton("❌ Отмена", callback_data="subscription")
    )
    
    return keyboard


# ============================================================
# 🔔 КЛАВИАТУРЫ ДЛЯ АЛЕРТОВ
# ============================================================

def get_alert_keyboard(symbol):
    """
    🔔 Клавиатура для настройки алертов
    
    Args:
        symbol (str): Символ монеты (например, "BTC")
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с типами алертов
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # 💰 Алерт по достижении цены
    keyboard.add(
        InlineKeyboardButton(
            "💰 По достижении цены",
            callback_data=f"alert_price_{symbol}"
        )
    )
    
    # 📊 Алерт по изменению процента
    keyboard.add(
        InlineKeyboardButton(
            "📊 По изменению процента",
            callback_data=f"alert_percent_{symbol}"
        )
    )
    
    # 🔙 Возврат к деталям монеты
    keyboard.add(
        InlineKeyboardButton("🔙 Назад к монете", callback_data=f"coin_{symbol}")
    )
    
    return keyboard


# ============================================================
# 🧭 НАВИГАЦИОННЫЕ КЛАВИАТУРЫ
# ============================================================

def get_back_keyboard():
    """
    🔙 Клавиатура с кнопкой "Назад"
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с одной кнопкой
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    return keyboard


def get_cancel_keyboard():
    """
    ❌ Клавиатура с кнопкой "Отмена"
    
    Используется при ожидании ввода данных от пользователя
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой отмены
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu")
    )
    return keyboard


# ============================================================
# ✅ КЛАВИАТУРЫ ПОДТВЕРЖДЕНИЯ
# ============================================================

def get_confirm_keyboard():
    """
    ✅ Клавиатура подтверждения действия
    
    Используется для критических действий (удаление, оплата и т.д.)
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками подтверждения/отмены
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel")
    )
    
    return keyboard


# ============================================================
# 🎯 ДОПОЛНИТЕЛЬНЫЕ КЛАВИАТУРЫ
# ============================================================

def get_settings_keyboard():
    """
    ⚙️ Клавиатура настроек (заглушка для будущего функционала)
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с настройками
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔔 Уведомления", callback_data="settings_notifications"),
        InlineKeyboardButton("🌐 Язык", callback_data="settings_language")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


def get_admin_keyboard():
    """
    👑 Административная клавиатура (заглушка для будущего функционала)
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с админ-функциями
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast")
    )
    
    keyboard.add(
        InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        InlineKeyboardButton("💎 Тарифы", callback_data="admin_prices")
    )
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    
    return keyboard


# ============================================================
# 🔔 КЛАВИАТУРЫ ДЛЯ УПРАВЛЕНИЯ АЛЕРТАМИ
# ============================================================

def get_alert_control_keyboard(alert_id: int, symbol: str):
    """
    🔔 Клавиатура для управления алертом после получения уведомления
    
    Args:
        alert_id: ID алерта
        symbol: Символ монеты
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками управления
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton(
            "🔕 Отключить алерт",
            callback_data=f"alert_disable_{alert_id}"
        ),
        InlineKeyboardButton(
            "🔄 Сбросить алерт",
            callback_data=f"alert_reset_{alert_id}"
        )
    )
    
    keyboard.add(
        InlineKeyboardButton(
            "📊 Посмотреть монету",
            callback_data=f"coin_{symbol}"
        )
    )
    
    return keyboard


def get_alert_settings_keyboard(symbol: str):
    """
    ⚙️ Клавиатура настроек алерта
    
    Args:
        symbol: Символ монеты
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с настройками
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton(
            "🔄 Повторять алерт",
            callback_data=f"alert_repeat_{symbol}"
        ),
        InlineKeyboardButton(
            "🔕 Отключить",
            callback_data=f"alert_disable_{symbol}"
        )
    )
    
    keyboard.add(
        InlineKeyboardButton(
            "🔙 Назад к монете",
            callback_data=f"coin_{symbol}"
        )
    )
    
    return keyboard