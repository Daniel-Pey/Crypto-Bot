from bot import bot
from config import config
from .logger import logger


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