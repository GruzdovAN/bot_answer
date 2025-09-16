#!/usr/bin/env python3
"""
Проверка доступности канала
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

async def check_channel():
    client = TelegramClient(
        'sessions/reader',
        api_id=os.getenv('API_ID_TG'),
        api_hash=os.getenv('API_HASH_TG')
    )
    
    try:
        await client.start()
        print("✅ Подключение к Telegram успешно!")
        
        # Проверяем канал
        try:
            entity = await client.get_entity('@datasciencejobs')
            print(f"✅ Канал найден: {entity.title}")
            print(f"   ID: {entity.id}")
            print(f"   Тип: {type(entity).__name__}")
            
            # Пробуем получить несколько сообщений
            print("📋 Получаем последние 5 сообщений...")
            messages = []
            async for message in client.iter_messages(entity, limit=5):
                messages.append(message)
                print(f"   Сообщение {message.id}: {message.text[:50] if message.text else 'Медиа'}...")
            
            print(f"✅ Получено {len(messages)} сообщений")
            
        except Exception as e:
            print(f"❌ Ошибка с каналом: {e}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_channel())
