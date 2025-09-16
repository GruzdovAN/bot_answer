#!/usr/bin/env python3
"""
Тестовый скрипт для проверки компонентов без Telegram
"""

import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

def test_components():
    """Тестирование компонентов"""
    print("🧪 Тестируем компоненты скрапера...")
    
    # Тест 1: Менеджер каналов
    print("\n1️⃣ Тестируем менеджер каналов...")
    try:
        from src.core.channel_manager import ChannelManager
        cm = ChannelManager()
        channels = cm.get_enabled_channels()
        print(f"✅ Найдено {len(channels)} активных каналов:")
        for ch in channels:
            print(f"   - {ch.username} ({ch.parser_type}, {ch.days_back} дней)")
    except Exception as e:
        print(f"❌ Ошибка в менеджере каналов: {e}")
    
    # Тест 2: Парсер
    print("\n2️⃣ Тестируем парсер...")
    try:
        from src.parsers.simple_parser import SimpleParser
        
        # Создаем тестовое сообщение
        class MockMessage:
            def __init__(self, text):
                self.text = text
        
        # Тест job_parser
        parser = SimpleParser('job_parser')
        test_msg = MockMessage("Senior Python Developer at Google #python #ml @google https://example.com")
        parsed = parser.parse_message(test_msg)
        
        print("✅ Job parser работает:")
        print(f"   - Хештеги: {parsed['hashtags']}")
        print(f"   - Упоминания: {parsed['mentions']}")
        print(f"   - Ссылки: {parsed['links']}")
        print(f"   - Технологии: {parsed['technologies']}")
        
        # Тест news_parser
        parser = SimpleParser('news_parser')
        test_msg = MockMessage("Google announces new AI features #AI #Google @Google")
        parsed = parser.parse_message(test_msg)
        
        print("✅ News parser работает:")
        print(f"   - Хештеги: {parsed['hashtags']}")
        print(f"   - Упоминания: {parsed['mentions']}")
        print(f"   - Компании: {parsed['companies']}")
        
    except Exception as e:
        print(f"❌ Ошибка в парсере: {e}")
    
    # Тест 3: ClickHouse клиент
    print("\n3️⃣ Тестируем ClickHouse клиент...")
    try:
        from src.database.clickhouse_client import ClickHouseClient
        ch = ClickHouseClient()
        print("✅ ClickHouse клиент создан успешно")
        
        # Тест вставки данных
        test_data = [{
            'message_id': 12345,
            'channel_username': '@test_channel',
            'date': '2024-09-16 20:00:00',
            'text': 'Test message for universal scraper',
            'views': 100,
            'forwards': 5,
            'hashtags': ['#test', '#universal'],
            'mentions': ['@test'],
            'links': ['https://example.com'],
            'technologies': ['python'],
            'companies': []
        }]
        
        ch.insert_messages(test_data)
        print("✅ Тестовые данные записаны в ClickHouse!")
        
    except Exception as e:
        print(f"❌ Ошибка в ClickHouse клиенте: {e}")
    
    # Тест 4: Проверка переменных окружения
    print("\n4️⃣ Проверяем переменные окружения...")
    required_vars = ['API_ID_TG', 'API_HASH_TG', 'CLICKHOUSE_PASSWORD']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
        else:
            print(f"❌ {var}: не задана")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_components()
