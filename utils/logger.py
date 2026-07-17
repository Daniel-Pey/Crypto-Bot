"""
📝 Красивое и удобное логирование для бота
"""

import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ============================================================
# 🎨 ЦВЕТА ДЛЯ ТЕРМИНАЛА
# ============================================================

class Colors:
    """🎨 Цвета для красивого вывода в терминале"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'
    MAGENTA = '\033[95m'

# ============================================================
# 📝 ФОРМАТТЕРЫ ДЛЯ ЛОГОВ
# ============================================================

class EmojiFormatter(logging.Formatter):
    """📝 Форматтер с эмодзи и цветами для разных уровней"""
    
    # 🎯 Эмодзи для разных уровней
    LEVEL_EMOJIS = {
        'DEBUG': '🐛',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }
    
    # 🎨 Цвета для разных уровней
    LEVEL_COLORS = {
        'DEBUG': Colors.GRAY,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    def __init__(self, use_colors=True):
        """
        Инициализация форматтера
        
        Args:
            use_colors: Использовать ли цвета в выводе
        """
        super().__init__()
        self.use_colors = use_colors
        self.date_format = '%Y-%m-%d %H:%M:%S'
    
    def format(self, record):
        """
        Форматирование записи лога с эмодзи и цветами
        """
        # 📝 Добавляем эмодзи в зависимости от уровня
        record.emoji = self.LEVEL_EMOJIS.get(record.levelname, '📌')
        
        # 📅 Форматируем время
        record.asctime = self.formatTime(record, self.date_format)
        
        # 📝 Получаем имя файла и номер строки
        record.filename_short = os.path.basename(record.filename)
        
        # 🎨 Добавляем цвет для уровня
        if self.use_colors:
            level_color = self.LEVEL_COLORS.get(record.levelname, '')
            record.levelname_colored = f"{level_color}{record.levelname}{Colors.END}"
            record.filename_colored = f"{Colors.CYAN}{record.filename_short}{Colors.END}"
            record.lineno_colored = f"{Colors.GRAY}{record.lineno}{Colors.END}"
            
            # 📝 Формируем сообщение с цветами
            message = (
                f"{Colors.BLUE}{record.asctime}{Colors.END} "
                f"{record.emoji} "
                f"{record.levelname_colored} "
                f"[{record.filename_colored}:{record.lineno_colored}] "
                f"{record.getMessage()}"
            )
        else:
            # 📝 Формируем сообщение без цветов
            message = (
                f"{record.asctime} "
                f"{record.emoji} "
                f"{record.levelname} "
                f"[{record.filename_short}:{record.lineno}] "
                f"{record.getMessage()}"
            )
        
        return message


# ============================================================
# 🛠️ НАСТРОЙКА ЛОГГЕРОВ
# ============================================================

class LoggerSetup:
    """🛠️ Настройка логгеров для всего приложения"""
    
    def __init__(self):
        """Инициализация настроек логгеров"""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 🎯 Уровни логирования
        self.console_level = logging.INFO
        self.file_level = logging.DEBUG
        
        # 🎯 Создаем логгеры
        self._setup_root_logger()
        self._setup_handlers()
        
        # 📊 Логируем запуск
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Система логирования инициализирована")
    
    def _setup_root_logger(self):
        """Настройка корневого логгера"""
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)
        
        # 🧹 Очищаем существующие хендлеры
        if self.root_logger.handlers:
            self.root_logger.handlers.clear()
    
    def _setup_handlers(self):
        """Создание и настройка хендлеров"""
        
        # 📱 Консольный хендлер (с цветами)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)
        console_formatter = EmojiFormatter(use_colors=True)
        console_handler.setFormatter(console_formatter)
        self.root_logger.addHandler(console_handler)
        
        # 📁 Файловый хендлер (с ротацией)
        log_file = self.log_dir / f"crypto_bot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_485_760,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.file_level)
        file_formatter = EmojiFormatter(use_colors=False)
        file_handler.setFormatter(file_formatter)
        self.root_logger.addHandler(file_handler)
        
        # ⚠️ Хендлер для ошибок (отдельный файл)
        error_log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5_242_880,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        self.root_logger.addHandler(error_handler)

# ============================================================
# 📊 ФУНКЦИИ ДЛЯ РАБОТЫ С ЛОГГЕРОМ
# ============================================================

# 🎯 Инициализация системы логирования
_logger_setup = LoggerSetup()

def get_logger(name: str = None) -> logging.Logger:
    """
    📊 Получение логгера с именем
    
    Args:
        name: Имя логгера (обычно __name__)
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    if name is None:
        return logging.getLogger()
    return logging.getLogger(name)


def get_logger_for_file(filename: str) -> logging.Logger:
    """
    📊 Получение логгера для конкретного файла
    
    Args:
        filename: Имя файла (например, "main.py")
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    name = os.path.splitext(os.path.basename(filename))[0]
    return get_logger(name)


# ============================================================
# 🎯 ДЕКОРАТОРЫ ДЛЯ ЛОГИРОВАНИЯ
# ============================================================

def log_function_call(func):
    """
    🎯 Декоратор для логирования вызовов функций
    
    Использование:
        @log_function_call
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"🔄 Вызов {func.__name__}()")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅ {func.__name__}() выполнен успешно")
            return result
        except Exception as e:
            logger.error(f"💥 {func.__name__}() ошибка: {e}", exc_info=True)
            raise
    
    return wrapper


def log_error(func):
    """
    🎯 Декоратор для логирования ошибок
    
    Использование:
        @log_error
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"💥 Ошибка в {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


# ============================================================
# 📝 БЫСТРЫЙ ДОСТУП К ЛОГГЕРУ
# ============================================================

# 🎯 Создаем основной логгер для всего приложения
logger = get_logger('crypto_bot')


# ============================================================
# 🔧 ФУНКЦИИ ДЛЯ ОТЛАДКИ
# ============================================================

def set_debug_mode(enabled: bool = True):
    """
    🔧 Включение/выключение режима отладки
    
    Args:
        enabled: Включить режим отладки
    """
    level = logging.DEBUG if enabled else logging.INFO
    
    # 📱 Меняем уровень консольного хендлера
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(level)
    
    logger.info(f"🔧 Режим отладки: {'ВКЛЮЧЕН' if enabled else 'ВЫКЛЮЧЕН'}")


def get_log_files() -> list:
    """
    📁 Получение списка файлов логов
    
    Returns:
        list: Список файлов логов
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        return []
    
    return sorted(log_dir.glob("*.log"), key=os.path.getmtime, reverse=True)


def print_log_summary():
    """
    📊 Вывод краткой информации о логах
    """
    log_files = get_log_files()
    
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА ЛОГОВ")
    print("=" * 60)
    
    if not log_files:
        print("📭 Нет файлов логов")
        return
    
    print(f"📁 Всего файлов логов: {len(log_files)}")
    print("\n📄 Последние файлы:")
    
    for log_file in log_files[:5]:
        size = log_file.stat().st_size
        size_mb = size / (1024 * 1024)
        modified = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"  • {log_file.name} ({size_mb:.1f} MB) - {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("=" * 60 + "\n")


# ============================================================
# 🚀 ИНИЦИАЛИЗАЦИЯ
# ============================================================

# 📊 Выводим информацию о логах при импорте
logger.info("=" * 60)
logger.info("🚀 Система логирования загружена")
logger.info(f"📁 Логи сохраняются в: {Path('logs').absolute()}")
logger.info("=" * 60)