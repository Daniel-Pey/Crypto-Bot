"""
⭐️ Файл для работы с тг звездами
"""

from config import config
from utils import logger


def convert_rub_to_stars(rub_amount: int) -> int:
    """
    ⭐ Конвертация рублей в Telegram Stars
    
    Args:
        rub_amount: Сумма в рублях
        
    Returns:
        int: Количество Stars
    """
    # 📝 Цена одной звезды в рублях (примерно 1.5-2 рубля)
    # 🔥 Telegram берет комиссию ~30%, поэтому нужно закладывать это
    stars = int(rub_amount / config.ONE_STAR_PRICE)
    
    # 🔥 Минимальное количество звезд для покупки
    if stars < 1:
        stars = 1
    
    logger.debug(f"💰 {rub_amount}₽ = ⭐{stars} (курс: {config.ONE_STAR_PRICE}₽/⭐)")
    return stars