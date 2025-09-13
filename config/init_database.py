"""
Скрипт для инициализации базы данных
"""
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import db_manager
from src.config.logging_config import setup_logging, get_logger

# Настраиваем логирование
setup_logging(level="INFO", log_to_file=False)
logger = get_logger("init_db")


def init_database():
    """Инициализирует базу данных"""
    try:
        logger.info("Начинаем инициализацию базы данных...")
        
        # Проверяем подключение к базе данных
        if not db_manager.health_check():
            logger.error("Не удается подключиться к базе данных")
            return False
        
        # Создаем таблицы
        db_manager.create_tables()
        
        logger.info("База данных инициализирована успешно!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
