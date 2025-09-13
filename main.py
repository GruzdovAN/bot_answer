"""
Главный файл для запуска Telegram бота-автоответчика
"""
import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.bot_manager import bot_manager
from src.config.logging_config import setup_logging, get_logger

# Настраиваем логирование
setup_logging(level="INFO", log_to_file=True)
logger = get_logger("main")


async def main():
    """Главная функция для запуска автоответчика"""
    logger.info("Запуск Telegram бота-автоответчика")
    logger.info("Выберите режим работы:")
    bot_manager.list_available_bots()
    
    # По умолчанию запускаем простой автоответчик
    await bot_manager.run_bot('simple')


async def run_smart_responder():
    """Запуск умного автоответчика"""
    logger.info("Запуск умного автоответчика")
    await bot_manager.run_bot('smart')


async def run_simple_responder():
    """Запуск простого автоответчика"""
    logger.info("Запуск простого автоответчика")
    await bot_manager.run_bot('simple')


# Универсальный запуск
if __name__ == "__main__":
    try:
        # Если уже есть event loop (Jupyter), используем await
        loop = asyncio.get_running_loop()
        # В Jupyter раскомментируйте нужную строку:
        # await run_smart_responder()
        # await run_simple_responder()
        # await main()
    except RuntimeError:
        # Если нет event loop (обычный Python), создаем новый
        asyncio.run(main())