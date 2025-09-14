#!/usr/bin/env python3
"""
Скрипт для запуска группового автоответчика
"""
import asyncio
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.bots.group_responder import GroupResponder
from src.config.logging_config import get_logger

logger = get_logger("group_responder_main")


async def main():
    """Основная функция запуска группового автоответчика"""
    try:
        # Проверяем наличие переменной GROUP_NAME
        if not os.getenv('GROUP_NAME'):
            logger.error("Переменная окружения GROUP_NAME не задана!")
            logger.error("Установите переменную: export GROUP_NAME=@your_group_username")
            return
        
        logger.info("Запуск группового автоответчика...")
        logger.info(f"Группа: {os.getenv('GROUP_NAME')}")
        
        # Создаем и запускаем бота
        bot = GroupResponder()
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Остановка по запросу пользователя")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
