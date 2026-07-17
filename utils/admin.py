from bot import bot
from config import config


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

        for id in self.admins_id:
            bot.send_message(id, message)


admin = Admin(config.ADMINS_ID)