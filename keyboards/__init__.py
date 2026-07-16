"""
🎨 Пакет клавиатур для бота
"""

# 📦 Inline-клавиатуры (для callback-запросов)
from .inline import (
    get_start_keyboard,
    get_main_menu_keyboard,
    get_coins_keyboard,
    get_coin_detail_keyboard,
    get_subscription_keyboard,
    get_confirm_payment_keyboard,
    get_alert_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_settings_keyboard,
    get_admin_keyboard
)

# ⌨️ Reply-клавиатуры (для быстрого ввода)
from .main import (
    get_main_keyboard,
    get_simple_main_keyboard,
    get_cancel_keyboard as get_cancel_reply_keyboard,
    get_confirm_keyboard as get_confirm_reply_keyboard,
    get_price_input_keyboard,
    get_percent_input_keyboard,
    get_coin_symbol_keyboard,
    get_number_keyboard,
    remove_keyboard,
    get_admin_keyboard as get_admin_reply_keyboard,
    get_language_keyboard,
    get_feedback_keyboard
)

# ⌨️ Reply-клавиатуры (альтернативный файл)
from .reply import (
    get_main_reply_keyboard,
    get_cancel_reply_keyboard as get_cancel_reply_alt,
    get_confirm_reply_keyboard,
    get_remove_keyboard
)

__all__ = [
    # Inline-клавиатуры
    'get_start_keyboard',
    'get_main_menu_keyboard',
    'get_coins_keyboard',
    'get_coin_detail_keyboard',
    'get_subscription_keyboard',
    'get_confirm_payment_keyboard',
    'get_alert_keyboard',
    'get_back_keyboard',
    'get_cancel_keyboard',
    'get_confirm_keyboard',
    'get_settings_keyboard',
    'get_admin_keyboard',
    
    # Reply-клавиатуры из main.py
    'get_main_keyboard',
    'get_simple_main_keyboard',
    'get_cancel_reply_keyboard',
    'get_confirm_reply_keyboard',
    'get_price_input_keyboard',
    'get_percent_input_keyboard',
    'get_coin_symbol_keyboard',
    'get_number_keyboard',
    'remove_keyboard',
    'get_admin_reply_keyboard',
    'get_language_keyboard',
    'get_feedback_keyboard',
    
    # Reply-клавиатуры из reply.py
    'get_main_reply_keyboard',
    'get_cancel_reply_alt',
    'get_confirm_reply_keyboard',
    'get_remove_keyboard'
]