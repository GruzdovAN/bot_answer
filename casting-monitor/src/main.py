#!/usr/bin/env python3
"""
Главный модуль для запуска мониторинга кастингов
"""

import asyncio
import logging
import signal
import sys
import os

# Добавляем пути для импорта модулей из основного проекта
sys.path.append('/app/src_modules')
sys.path.append('/app/config')

from monitor import CastingMonitor
from config.settings import Settings

async def main():
    """Основная функция приложения"""
    settings = Settings()
    
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/app/logs/casting_monitor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск мониторинга кастингов...")
    
    # Создание монитора
    monitor = CastingMonitor(settings)
    
    # Обработка сигналов для graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, завершение работы...")
        asyncio.create_task(monitor.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Запуск мониторинга
        await monitor.start()
    except Exception as e:
        logger.error(f"Ошибка при запуске мониторинга: {e}")
        sys.exit(1)
    finally:
        await monitor.stop()
        logger.info("Мониторинг остановлен")

if __name__ == "__main__":
    asyncio.run(main())
