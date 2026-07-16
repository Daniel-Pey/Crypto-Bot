import logging
import sys
from datetime import datetime
from config import config

# 🎨 Цвета для терминала
class Colors:
    """Класс с цветами для красивого вывода в терминале"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class EmojiFormatter(logging.Formatter):
    """Форматтер с эмодзи для разных уровней логирования"""
    
    # 🎯 Эмодзи для разных уровней
    LEVEL_EMOJIS = {
        'DEBUG': '🐛',      # DEBUG
        'INFO': 'ℹ️',       # INFO
        'WARNING': '⚠️',    # WARNING
        'ERROR': '❌',      # ERROR
        'CRITICAL': '🔥',   # CRITICAL
    }
    
    # 🎨 Цвета для разных уровней
    LEVEL_COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    def __init__(self):
        """Инициализация форматтера с кастомным форматом"""
        super().__init__()
        # 📅 Формат: [2024-01-15 14:30:45] ℹ️  INFO - Сообщение
        self.base_format = f"{Colors.BLUE}%(asctime)s{Colors.END} %(emoji)s %(levelname)s - %(message)s"
        self.date_format = '%Y-%m-%d %H:%M:%S'
    
    def format(self, record):
        """Форматирование записи лога с эмодзи и цветами"""
        # 📝 Добавляем эмодзи в зависимости от уровня
        record.emoji = self.LEVEL_EMOJIS.get(record.levelname, '📌')
        
        # 🎨 Добавляем цвет для уровня
        level_color = self.LEVEL_COLORS.get(record.levelname, '')
        record.levelname = f"{level_color}{record.levelname}{Colors.END}"
        
        # 📅 Форматируем время
        record.asctime = self.formatTime(record, self.date_format)
        
        # 🏗️ Собираем финальное сообщение
        return self.base_format % record.__dict__

class EmojiHandler(logging.StreamHandler):
    """Кастомный хендлер с эмодзи для красивого вывода"""
    
    def __init__(self, stream=None):
        super().__init__(stream)
        self.setFormatter(EmojiFormatter())

def setup_logger(name='crypto_bot'):
    """
    🚀 Настройка красивого логирования с эмодзи и цветами
    
    Returns:
        logging.Logger: Настроенный логгер с красивым выводом
    """
    # 📋 Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # 🧹 Очищаем существующие хендлеры
    if logger.handlers:
        logger.handlers.clear()
    
    # 🎨 Добавляем кастомный хендлер с эмодзи
    emoji_handler = EmojiHandler()
    logger.addHandler(emoji_handler)
    
    # 📁 Добавляем файловый хендлер (без цветов и эмодзи для читаемости в файле)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler = logging.FileHandler('crypto_bot.log', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 🎉 Логируем успешную инициализацию
    logger.info(f"🚀 Logger initialized successfully!")
    
    return logger

# 📦 Создаем глобальный экземпляр логгера
logger = setup_logger()

# 🎯 Декоратор для логирования ошибок в функциях
def log_error(func):
    """
    📝 Декоратор для автоматического логирования ошибок в функциях
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"💥 Error in {func.__name__}: {str(e)}")
            raise
    return wrapper