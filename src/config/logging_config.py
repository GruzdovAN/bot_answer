"""
Конфигурация логирования для Telegram бота
"""
import logging
import logging.handlers
import os
from datetime import datetime


class BotLogger:
    """Класс для настройки логирования бота"""
    
    def __init__(self, name: str = "telegram_bot", log_level: str = "INFO"):
        """
        Инициализация логгера
        
        Args:
            name: Имя логгера
            log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Настраивает логгер с консольным и файловым выводом"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Очищаем существующие обработчики
        logger.handlers.clear()
        
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Создаем директорию для логов
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Файловый обработчик с ротацией
        log_file = os.path.join(log_dir, f"{self.name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Обработчик для ошибок
        error_log_file = os.path.join(log_dir, f"{self.name}_errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Возвращает настроенный логгер"""
        return self.logger
    
    def set_level(self, level: str):
        """Изменяет уровень логирования"""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)


# Глобальный логгер
bot_logger = BotLogger()
logger = bot_logger.get_logger()


def get_logger(name: str = None) -> logging.Logger:
    """
    Возвращает логгер для указанного модуля
    
    Args:
        name: Имя модуля (если None, возвращает основной логгер)
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    if name:
        return logging.getLogger(f"telegram_bot.{name}")
    return logger


def setup_logging(level: str = "INFO", log_to_file: bool = True):
    """
    Настраивает логирование для всего приложения
    
    Args:
        level: Уровень логирования
        log_to_file: Логировать ли в файл
    """
    global bot_logger, logger
    
    bot_logger = BotLogger(log_level=level)
    logger = bot_logger.get_logger()
    
    if not log_to_file:
        # Удаляем файловые обработчики
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                logger.removeHandler(handler)
    
    logger.info(f"Логирование настроено. Уровень: {level}")
