import re
from typing import Tuple, Optional
from utils.logger import logger

def validate_crypto_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    🪙 Валидация символа криптовалюты
    
    Args:
        symbol: Символ криптовалюты (например, "BTC")
        
    Returns:
        Tuple[bool, Optional[str]]: (валидность, сообщение об ошибке)
    """
    # 🔍 Проверяем, что символ не пустой
    if not symbol:
        return False, "❌ Символ не может быть пустым"
    
    # 📝 Очищаем и приводим к верхнему регистру
    symbol = symbol.strip().upper()
    
    # 📏 Проверяем длину
    if len(symbol) < 2 or len(symbol) > 10:
        return False, "❌ Символ должен содержать от 2 до 10 символов"
    
    # 🔤 Проверяем, что только буквы
    if not re.match(r'^[A-Z]+$', symbol):
        return False, "❌ Символ может содержать только латинские буквы"
    
    # 📝 Логируем успешную валидацию
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
            return False, "❌ Цена должна быть положительной"
        
        # 📝 Логируем успешную валидацию
        logger.debug(f"✅ Цена {price_float} прошел валидацию")
        
        return True, price_float
        
    except ValueError:
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
            return False, "❌ Процент должен быть от 0 до 100"
        
        # 📝 Логируем успешную валидацию
        logger.debug(f"✅ Процент {percent_float} прошел валидацию")
        
        return True, percent_float
        
    except ValueError:
        return False, "❌ Некорректный формат процента. Используйте числа"