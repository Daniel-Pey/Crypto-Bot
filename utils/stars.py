"""
⭐️ Файл для работы с тг звездами
"""

from config import config


def convert_rub_to_stars(price):
    """ Функция для превращения рублей в звезды

    Args:
        price (int | str): цена в рублях
    """
    
    return int(int(price) * config.ONE_STAR_PRICE)