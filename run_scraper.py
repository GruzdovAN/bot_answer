#!/usr/bin/env python3
"""
Запуск универсального скрапера
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from src.core.universal_scraper import UniversalScraper

# Загружаем переменные окружения
load_dotenv()

async def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Запуск универсального Telegram скрапера...")
    
    scraper = UniversalScraper()
    
    try:
        print("🔗 Подключаемся к Telegram...")
        await scraper.client.start()
        print("✅ Подключение к Telegram успешно!")
        
        print("📋 Начинаем сбор данных...")
        await scraper.scrape_all_channels()
        print("✅ Сбор данных завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logging.error(f"Ошибка при выполнении скрапера: {e}")
    finally:
        await scraper.client.disconnect()
        print("🔌 Отключение от Telegram")

if __name__ == "__main__":
    asyncio.run(main())
