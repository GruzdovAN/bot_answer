#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы скрапера
"""

import asyncio
import logging
from src.core.universal_scraper import UniversalScraper

async def test_scraper():
    """Тестирование скрапера"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = UniversalScraper()
    
    try:
        print("🔗 Подключаемся к Telegram...")
        await scraper.client.start()
        print("✅ Подключение успешно!")
        
        print("📋 Получаем список каналов...")
        channels = scraper.channel_manager.get_enabled_channels()
        print(f"✅ Найдено {len(channels)} активных каналов:")
        for ch in channels:
            print(f"   - {ch.username} ({ch.parser_type})")
        
        print("🧪 Тестируем парсер...")
        from src.parsers.simple_parser import SimpleParser
        parser = SimpleParser('job_parser')
        
        # Создаем тестовое сообщение
        class MockMessage:
            def __init__(self, text):
                self.text = text
        
        test_msg = MockMessage("Senior Python Developer at Google #python #ml @google")
        parsed = parser.parse_message(test_msg)
        print("✅ Парсер работает:")
        print(f"   - Хештеги: {parsed['hashtags']}")
        print(f"   - Упоминания: {parsed['mentions']}")
        print(f"   - Технологии: {parsed['technologies']}")
        
        print("💾 Тестируем ClickHouse...")
        test_data = [{
            'message_id': 12345,
            'channel_username': '@test_channel',
            'date': '2024-09-16 20:00:00',
            'text': 'Test message',
            'views': 100,
            'forwards': 5,
            'hashtags': ['#test'],
            'mentions': ['@test'],
            'links': [],
            'technologies': ['python'],
            'companies': []
        }]
        
        scraper.clickhouse.insert_messages(test_data)
        print("✅ Тестовые данные записаны в ClickHouse!")
        
        print("🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await scraper.client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_scraper())
