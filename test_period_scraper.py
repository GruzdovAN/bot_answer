#!/usr/bin/env python3
"""
Тест сбора данных за период
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient
from src.parsers.simple_parser import SimpleParser
from src.database.clickhouse_client import ClickHouseClient

load_dotenv()

async def test_period_scrape():
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
        
        # Тестируем сбор за разные периоды
        periods = [1, 3, 7]  # дни
        
        for days in periods:
            print(f"\n📅 Собираем данные за последние {days} дней...")
            
            # Вычисляем дату начала периода
            start_date = datetime.now() - timedelta(days=days)
            print(f"   Период: с {start_date.strftime('%Y-%m-%d %H:%M:%S')} до сейчас")
            
            # Собираем сообщения за период
            messages = []
            async for message in client.iter_messages(
                entity, 
                limit=50,  # Ограничиваем для теста
                offset_date=start_date
            ):
                messages.append(message)
                print(f"   Сообщение {message.id} от {message.date}: {message.text[:50] if message.text else 'Медиа'}...")
            
            print(f"✅ За {days} дней найдено {len(messages)} сообщений")
            
            if messages:
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
                print(f"✅ Сохранено {len(parsed_messages)} сообщений за {days} дней!")
            else:
                print(f"⚠️ За {days} дней сообщений не найдено")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_period_scrape())
