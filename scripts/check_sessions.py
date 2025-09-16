#!/usr/bin/env python3
"""
Скрипт для проверки доступности существующих Telegram сессий
"""

import asyncio
import os
import sys
from telethon import TelegramClient
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

async def check_session(session_path, api_id, api_hash):
    """Проверка доступности сессии"""
    try:
        client = TelegramClient(session_path, int(api_id), api_hash)
        await client.start()
        
        # Проверяем, что мы авторизованы
        me = await client.get_me()
        await client.disconnect()
        
        return {
            'session': session_path,
            'status': 'active',
            'user': f"{me.first_name} {me.last_name or ''}".strip(),
            'username': me.username or 'Нет username',
            'phone': me.phone or 'Нет телефона'
        }
    except Exception as e:
        return {
            'session': session_path,
            'status': 'error',
            'error': str(e)
        }

async def main():
    """Основная функция"""
    api_id = os.getenv('API_ID_TG')
    api_hash = os.getenv('API_HASH_TG')
    
    if not all([api_id, api_hash]):
        print("❌ Необходимо установить API_ID_TG и API_HASH_TG в .env файле")
        return
    
    # Список сессий для проверки
    sessions_dir = 'sessions'
    session_files = []
    
    if os.path.exists(sessions_dir):
        for file in os.listdir(sessions_dir):
            if file.endswith('.session'):
                session_path = os.path.join(sessions_dir, file[:-8])  # Убираем .session
                session_files.append(session_path)
    
    if not session_files:
        print("📁 Сессии не найдены в папке sessions/")
        return
    
    print("🔍 Проверка доступности Telegram сессий...")
    print("=" * 60)
    
    active_sessions = []
    
    for session_path in session_files:
        print(f"Проверяем: {session_path}")
        result = await check_session(session_path, api_id, api_hash)
        
        if result['status'] == 'active':
            print(f"✅ {result['session']}")
            print(f"   Пользователь: {result['user']}")
            print(f"   Username: @{result['username']}")
            print(f"   Телефон: {result['phone']}")
            active_sessions.append(result)
        else:
            print(f"❌ {result['session']}")
            print(f"   Ошибка: {result['error']}")
        
        print("-" * 40)
    
    print(f"\n📊 Результат: {len(active_sessions)} активных сессий из {len(session_files)}")
    
    if active_sessions:
        print("\n🎯 Рекомендуемые сессии для использования:")
        for session in active_sessions:
            print(f"   - {session['session']} ({session['user']})")
    
    return active_sessions

if __name__ == '__main__':
    asyncio.run(main())
