#!/usr/bin/env python3
"""
Запуск универсального скрапера с использованием существующей сессии
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Загружаем переменные окружения
load_dotenv()

async def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Запуск универсального Telegram скрапера...")
    
    # Используем существующую сессию
    session_name = 'sessions/reader'
    
    client = TelegramClient(
        session_name,
        api_id=os.getenv('API_ID_TG'),
        api_hash=os.getenv('API_HASH_TG')
    )
    
    try:
        print("🔗 Подключаемся к Telegram...")
        await client.start()
        print("✅ Подключение к Telegram успешно!")
        
        # Импортируем и запускаем скрапер
        from src.core.universal_scraper import UniversalScraper
        scraper = UniversalScraper()
        scraper.client = client  # Используем существующий клиент
        
        print("📋 Начинаем сбор данных...")
        await scraper.scrape_all_channels()
        print("✅ Сбор данных завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logging.error(f"Ошибка при выполнении скрапера: {e}")
    finally:
        await client.disconnect()
        print("🔌 Отключение от Telegram")

if __name__ == "__main__":
    asyncio.run(main())
