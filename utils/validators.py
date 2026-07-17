"""
✅ Валидаторы для пользовательского ввода
"""

import re
from typing import Tuple, Optional
from .logger import logger


def validate_crypto_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    🪙 Валидация символа криптовалюты
    
    Args:
        symbol: Символ криптовалюты (например, "BTC")
        
    Returns:
        Tuple[bool, Optional[str]]: (валидность, сообщение об ошибке или символ)
    """
    # 🔍 Проверяем, что символ не пустой
    if not symbol:
        logger.debug("❌ Пустой символ")
        return False, "❌ Символ не может быть пустым"
    
    # 📝 Очищаем и приводим к верхнему регистру
    symbol = symbol.strip().upper()
    
    # 📏 Проверяем длину
    if len(symbol) < 2 or len(symbol) > 10:
        logger.debug(f"❌ Неверная длина: {symbol}")
        return False, "❌ Символ должен содержать от 2 до 10 символов"
    
    # 🔤 Проверяем, что только буквы
    if not re.match(r'^[A-Z]+$', symbol):
        logger.debug(f"❌ Недопустимые символы: {symbol}")
        return False, "❌ Символ может содержать только латинские буквы"
    
    # ✅ Логируем успешную валидацию
    logger.debug(f"✅ Символ {symbol} прошел валидацию")
    
    return True, symbol


def validate_price(price: str) -> Tuple[bool, Optional[float]]:
    """
    💰 Валидация цены
    
    Args:
        price: Строка с ценой
        
    Returns:
        Tuple[bool, Optional[float]]: (валидность, цена)
    """
    try:
        # 🔄 Преобразуем в число
        price_float = float(price.replace(',', '.'))
        
        # ✅ Проверяем, что цена положительная
        if price_float <= 0:
            logger.debug(f"❌ Отрицательная цена: {price_float}")
            return False, "❌ Цена должна быть положительной"
        
        # ✅ Проверяем, что цена не слишком большая
        if price_float > 1_000_000_000:
            logger.debug(f"❌ Слишком большая цена: {price_float}")
            return False, "❌ Цена слишком большая (макс: 1,000,000,000)"
        
        # 📝 Логируем успешную валидацию
        logger.debug(f"✅ Цена {price_float} прошла валидацию")
        
        return True, price_float
        
    except ValueError as e:
        logger.debug(f"❌ Ошибка парсинга цены: {e}")
        return False, "❌ Некорректный формат цены. Используйте числа и точку"
    

def validate_percent(percent: str) -> Tuple[bool, Optional[float]]:
    """
    📊 Валидация процента изменения
    
    Args:
        percent: Строка с процентом
        
    Returns:
        Tuple[bool, Optional[float]]: (валидность, процент)
    """
    try:
        # 🔄 Преобразуем в число
        percent_float = float(percent.replace(',', '.'))
        
        # ✅ Проверяем диапазон
        if percent_float < 0 or percent_float > 100:
            logger.debug(f"❌ Процент вне диапазона: {percent_float}")
            return False, "❌ Процент должен быть от 0 до 100"
        
        # 📝 Логируем успешную валидацию
        logger.debug(f"✅ Процент {percent_float} прошел валидацию")
        
        return True, percent_float
        
    except ValueError as e:
        logger.debug(f"❌ Ошибка парсинга процента: {e}")
        return False, "❌ Некорректный формат процента. Используйте числа"


def validate_amount(amount: str) -> Tuple[bool, Optional[float]]:
    """
    💰 Валидация количества
    
    Args:
        amount: Строка с количеством
        
    Returns:
        Tuple[bool, Optional[float]]: (валидность, количество)
    """
    try:
        amount_float = float(amount.replace(',', '.'))
        
        if amount_float <= 0:
            return False, "❌ Количество должно быть положительным"
        
        if amount_float > 1_000_000:
            return False, "❌ Слишком большое количество"
        
        return True, amount_float
        
    except ValueError:
        return False, "❌ Некорректный формат. Используйте числа"