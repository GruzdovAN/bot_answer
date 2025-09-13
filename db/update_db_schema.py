#!/usr/bin/env python3
"""
Скрипт для обновления схемы базы данных
Изменяет тип telegram_id с Integer на BigInteger
"""
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import db_manager
from src.config.logging_config import setup_logging, get_logger
from sqlalchemy import text

# Настраиваем логирование
setup_logging(level="INFO", log_to_file=False)
logger = get_logger("update_db")

def update_database_schema():
    """Обновляет схему базы данных"""
    try:
        logger.info("Начинаем обновление схемы базы данных...")
        
        # Проверяем подключение к базе данных
        if not db_manager.health_check():
            logger.error("Не удается подключиться к базе данных")
            return False
        
        # SQL команды для обновления схемы
        update_commands = [
            # Обновляем таблицу chats
            "ALTER TABLE chats ALTER COLUMN telegram_id TYPE BIGINT;",
            
            # Обновляем таблицу users  
            "ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT;",
            
            # Обновляем таблицу messages
            "ALTER TABLE messages ALTER COLUMN telegram_id TYPE BIGINT;",
        ]
        
        # Выполняем команды
        session = db_manager.get_session()
        try:
            for command in update_commands:
                logger.info(f"Выполняем: {command}")
                session.execute(text(command))
                session.commit()
            
            logger.info("Схема базы данных обновлена успешно!")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при выполнении SQL команд: {e}")
            return False
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Ошибка обновления схемы базы данных: {e}")
        return False

if __name__ == "__main__":
    success = update_database_schema()
    sys.exit(0 if success else 1)
