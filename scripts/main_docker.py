#!/usr/bin/env python3
"""
Telegram Bot Auto-Responder - Docker версия
Автоматически запускает SimpleResponder без интерактивного ввода
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.logging_config import setup_logging, get_logger
from src.bot_manager import BotManager
from src.config.settings import config

# Настройка логирования
setup_logging()
logger = get_logger(__name__)

async def main():
    """Основная функция для Docker"""
    try:
        logger.info("Запуск Telegram бота-автоответчика (Docker версия)")
        
        # Создаем менеджер ботов
        bot_manager = BotManager()
        
        # Автоматически запускаем SimpleResponder
        logger.info("Автоматический запуск SimpleResponder...")
        await bot_manager.run_bot('simple')
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        logger.info("Завершение работы бота")

if __name__ == "__main__":
    try:
        # Проверяем, есть ли уже запущенный event loop
        loop = asyncio.get_running_loop()
        logger.warning("Event loop уже запущен, используем существующий")
        # Создаем задачу в существующем loop
        loop.create_task(main())
    except RuntimeError:
        # Нет запущенного loop, создаем новый
        asyncio.run(main())
