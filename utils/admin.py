"""
👑 Административные функции и декораторы
"""

from bot import bot
from config import config
from .logger import logger

import os
from datetime import datetime
from functools import wraps
from typing import List, Optional


class Admin:
    """Класс админа"""

    def __init__(self, admins_id: list[int]):
        """ Инициализизация Админа

        Args:
            admins_id (list[int]): список id админов
        """
        self.admins_id = admins_id
    
    def admin_log(self, message: str):
        """ Отправление сообщения админам

        Args:
            message (str): сообщение (лог) для админа
        """

        try:
            for id in self.admins_id:
                bot.send_message(id, message)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"💥 Ошибка типа {error_type} при попытке отправки сообщения админу: {e}")


admin = Admin(config.ADMINS_ID)


def is_admin(user_id: int) -> bool:
    """
    ✅ Проверка, является ли пользователь администратором
    
    Args:
        user_id: ID пользователя в Telegram
        
    Returns:
        bool: True если пользователь админ
    """
    
    return user_id in config.ADMINS_ID


def admin_required(func):
    """
    🎯 Декоратор для проверки прав администратора
    
    Использование:
        @admin_required
        @bot.message_handler(commands=['admin'])
        def admin_command(message):
            # Только для админов
            pass
    
    Args:
        func: Функция-обработчик
        
    Returns:
        function: Обернутая функция с проверкой прав
    """
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        from bot import bot
        
        user_id = message.from_user.id
        
        if is_admin(user_id):
            # ✅ Пользователь админ - выполняем функцию
            logger.info(f"👑 Администратор {message.from_user.username} вызвал {func.__name__}")
            return func(message, *args, **kwargs)
        else:
            # ❌ Не админ - отправляем сообщение
            logger.warning(f"⚠️ Пользователь {message.from_user.username} пытался вызвать {func.__name__}")
            bot.send_message(
                message.chat.id,
                "🚫 <b>Доступ запрещен!</b>\n\n"
                "Эта команда доступна только для администраторов.\n"
                "Если вы администратор, проверьте настройки.",
                parse_mode='HTML'
            )
            return None
    
    return wrapper


def admin_callback_required(func):
    """
    🎯 Декоратор для callback-запросов от администраторов
    
    Использование:
        @admin_callback_required
        @bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
        def admin_callback(call):
            # Только для админов
            pass
    
    Args:
        func: Функция-обработчик callback
        
    Returns:
        function: Обернутая функция с проверкой прав
    """
    @wraps(func)
    def wrapper(call, *args, **kwargs):
        from bot import bot
        
        user_id = call.from_user.id
        
        if is_admin(user_id):
            logger.info(f"👑 Админ {call.from_user.username} вызвал callback {call.data}")
            return func(call, *args, **kwargs)
        else:
            logger.warning(f"⚠️ Пользователь {call.from_user.username} пытался вызвать {call.data}")
            bot.answer_callback_query(
                call.id,
                "🚫 Доступ запрещен! Только для администраторов.",
                show_alert=True
            )
            return None
    
    return wrapper
