"""
🎨 Пакет клавиатур для бота
"""

# Inline-клавиатуры
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
    get_settings_keyboard
)

# Reply-клавиатуры
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
    get_admin_keyboard as get_admin_reply_keyboard
)

# Административные клавиатуры
from .admin import (
    get_admin_keyboard,                    # 🔥 ОСНОВНАЯ АДМИН-КЛАВИАТУРА
    get_admin_menu_keyboard,
    get_admin_back_keyboard,
    get_admin_cancel_keyboard,
    get_admin_confirm_broadcast_keyboard,
    get_admin_logs_keyboard,
    get_admin_users_keyboard,
    get_admin_stats_keyboard,
    get_admin_broadcast_keyboard,
    get_admin_info_keyboard
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
    
    # Reply-клавиатуры
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
    
    # Админ-клавиатуры
    'get_admin_keyboard',
    'get_admin_menu_keyboard',
    'get_admin_back_keyboard',
    'get_admin_cancel_keyboard',
    'get_admin_confirm_broadcast_keyboard',
    'get_admin_logs_keyboard',
    'get_admin_users_keyboard',
    'get_admin_stats_keyboard',
    'get_admin_broadcast_keyboard',
    'get_admin_info_keyboard'
]