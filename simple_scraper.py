#!/usr/bin/env python3
"""
Простой скрапер для сбора нескольких сообщений
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from src.parsers.simple_parser import SimpleParser
from src.database.clickhouse_client import ClickHouseClient

load_dotenv()

async def simple_scrape():
    client = TelegramClient(
        'sessions/reader',
        api_id=os.getenv('API_ID_TG'),
        api_hash=os.getenv('API_HASH_TG')
    )
    
    try:
        await client.start()
        print("✅ Подключение к Telegram успешно!")
        
        # Получаем канал
        entity = await client.get_entity('@datasciencejobs')
        print(f"📋 Канал: {entity.title}")
        
        # Создаем парсер и ClickHouse клиент
        parser = SimpleParser('job_parser')
        clickhouse = ClickHouseClient()
        
        # Собираем только 10 последних сообщений
        print("📥 Собираем последние 10 сообщений...")
        messages = []
        async for message in client.iter_messages(entity, limit=10):
            messages.append(message)
            print(f"   Сообщение {message.id}: {message.text[:50] if message.text else 'Медиа'}...")
        
        print(f"✅ Получено {len(messages)} сообщений")
        
        # Парсим и сохраняем
        print("🔄 Парсим сообщения...")
        parsed_messages = []
        for message in messages:
            parsed = parser.parse_message(message)
            parsed['message_id'] = message.id
            parsed['channel_username'] = '@datasciencejobs'
            parsed['date'] = message.date
            parsed['views'] = getattr(message, 'views', 0)
            parsed['forwards'] = getattr(message, 'forwards', 0)
            parsed_messages.append(parsed)
        
        print("💾 Сохраняем в ClickHouse...")
        clickhouse.insert_messages(parsed_messages)
        
        print(f"✅ Сохранено {len(parsed_messages)} сообщений!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(simple_scrape())
