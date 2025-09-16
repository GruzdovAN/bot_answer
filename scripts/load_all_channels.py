#!/usr/bin/env python3
"""
Скрипт для загрузки всех каналов в ClickHouse и фильтрации кастинговых каналов
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class ClickHouseManager:
    def __init__(self):
        self.host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.port = os.getenv('CLICKHOUSE_PORT', '8123')
        self.user = os.getenv('CLICKHOUSE_USER', 'clickhouse_admin')
        self.password = os.getenv('CLICKHOUSE_PASSWORD')
        self.database = os.getenv('CLICKHOUSE_DB', 'telegram_analytics')
        
        self.base_url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password) if self.user and self.password else None
    
    def execute_query(self, query, database=None):
        """Выполнение SQL запроса"""
        db = database or self.database
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': db},
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception(f"ClickHouse error: {response.text}")
        
        return response.text.strip()
    
    def insert_channels_info(self, channels):
        """Вставка информации о каналах в ClickHouse"""
        if not channels:
            return
        
        values = []
        for channel in channels:
            # Обрабатываем все поля
            channel_id = channel.get('id', 0)
            title = (channel.get('title') or '').replace("'", "''")
            username = (channel.get('username') or '').replace("'", "''")
            channel_type = (channel.get('type') or '').replace("'", "''")
            participants_count = channel.get('participants_count', 0) or 0
            description = (channel.get('description') or '').replace("'", "''")
            is_verified = int(channel.get('is_verified', False))
            is_scam = int(channel.get('is_scam', False))
            is_fake = int(channel.get('is_fake', False))
            
            # Обрабатываем даты
            created_date = channel.get('created_date')
            if created_date and hasattr(created_date, 'strftime'):
                created_date_str = created_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                created_date_str = '1970-01-01 00:00:00'
            
            discovered_at_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values.append(f"({channel_id}, '{title}', '{username}', '{channel_type}', {participants_count}, '{description}', {is_verified}, {is_scam}, {is_fake}, '{created_date_str}', '{discovered_at_str}')")
        
        query = f"INSERT INTO channels_info (channel_id, title, username, type, participants_count, description, is_verified, is_scam, is_fake, created_date, discovered_at) VALUES {','.join(values)}"
        
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': self.database},
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception(f"ClickHouse error: {response.text}")

def load_channels_from_json(json_file_path):
    """Загрузка каналов из JSON файла"""
    if not os.path.exists(json_file_path):
        print(f"❌ Файл {json_file_path} не найден")
        return []
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return [channel_data['channel_info'] for channel_data in data['channels']]

def filter_castings_channels(channels):
    """Фильтрация каналов с кастингами"""
    # Ключевые слова для кастингов
    castings_keywords = [
        'кастинг', 'casting', 'актер', 'актриса', 'модель', 'model',
        'съемка', 'фильм', 'реклама', 'ролик', 'клип', 'сериал',
        'театр', 'спектакль', 'шоу', 'ведущий', 'ведущая'
    ]
    
    # Исключения - каналы, которые НЕ являются кастинговыми
    exclude_keywords = [
        'обучала', 'обучение', 'курс', 'школа', 'академия', 'университет',
        'концерт аутистов', 'аутист', 'болезнь', 'лечение', 'медицина',
        'психология', 'развитие', 'образование', 'тренинг', 'семинар'
    ]
    
    castings_channels = []
    
    for channel in channels:
        title = (channel.get('title') or '').lower()
        username = (channel.get('username') or '').lower()
        description = (channel.get('description') or '').lower()
        
        text_to_check = f"{title} {username} {description}"
        
        # СНАЧАЛА проверяем исключения - если есть, сразу пропускаем
        if any(exclude_keyword in text_to_check for exclude_keyword in exclude_keywords):
            print(f"🚫 Исключен: {channel.get('title')} (исключающие слова)")
            continue
        
        # ПОТОМ проверяем ключевые слова кастингов
        if any(keyword in text_to_check for keyword in castings_keywords):
            print(f"✅ Включен: {channel.get('title')} (ключевые слова кастингов)")
            castings_channels.append(channel)
        else:
            print(f"❌ Исключен: {channel.get('title')} (нет ключевых слов кастингов)")
    
    return castings_channels

def main():
    """Основная функция"""
    print("📺 ЗАГРУЗКА И ФИЛЬТРАЦИЯ КАНАЛОВ")
    print("=" * 50)
    
    # Инициализируем ClickHouse менеджер
    ch_manager = ClickHouseManager()
    
    # Ищем последний JSON файл
    json_files = [f for f in os.listdir('.') if f.startswith('castings_channels_') and f.endswith('.json')]
    
    if not json_files:
        print("❌ JSON файлы с каналами не найдены")
        return
    
    json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = json_files[0]
    
    print(f"📁 Используем файл: {latest_file}")
    
    # Загружаем каналы
    all_channels = load_channels_from_json(latest_file)
    print(f"📊 Всего каналов: {len(all_channels)}")
    
    # Фильтруем каналы с кастингами
    castings_channels = filter_castings_channels(all_channels)
    print(f"🎭 Каналов с кастингами: {len(castings_channels)}")
    
    # Показываем отфильтрованные каналы
    print("\n🎯 КАНАЛЫ С КАСТИНГАМИ:")
    print("=" * 40)
    for i, channel in enumerate(castings_channels, 1):
        print(f"{i:2d}. {channel['title']}")
        print(f"    Username: @{channel['username']}")
        print(f"    Участников: {channel['participants_count']:,}")
        print(f"    Тип: {channel['type']}")
        print()
    
    # Сохраняем все каналы в ClickHouse
    print("💾 Сохраняем все каналы в ClickHouse...")
    try:
        # Очищаем таблицу перед вставкой
        ch_manager.execute_query('TRUNCATE TABLE channels_info')
        ch_manager.insert_channels_info(all_channels)
        print("✅ Все каналы сохранены в ClickHouse")
        
        # Проверяем количество записей
        count = ch_manager.execute_query('SELECT COUNT(*) FROM channels_info')
        print(f"📋 Записей в channels_info: {count}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
    
    # Создаем отдельную таблицу для кастинговых каналов
    print("\n🎭 Создаем таблицу для кастинговых каналов...")
    try:
        # Создаем таблицу castings_channels
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS castings_channels (
            channel_id UInt64,
            title String,
            username String,
            type String,
            participants_count UInt32,
            description String,
            is_verified UInt8,
            is_scam UInt8,
            is_fake UInt8,
            created_date DateTime,
            discovered_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY channel_id
        """
        
        ch_manager.execute_query(create_table_sql)
        print("✅ Таблица castings_channels создана")
        
        # Очищаем таблицу и вставляем только кастинговые каналы
        ch_manager.execute_query('TRUNCATE TABLE castings_channels')
        
        # Вставляем кастинговые каналы
        if castings_channels:
            values = []
            for channel in castings_channels:
                channel_id = channel.get('id', 0)
                title = (channel.get('title') or '').replace("'", "''")
                username = (channel.get('username') or '').replace("'", "''")
                channel_type = (channel.get('type') or '').replace("'", "''")
                participants_count = channel.get('participants_count', 0) or 0
                description = (channel.get('description') or '').replace("'", "''")
                is_verified = int(channel.get('is_verified', False))
                is_scam = int(channel.get('is_scam', False))
                is_fake = int(channel.get('is_fake', False))
                
                created_date = channel.get('created_date')
                if created_date and hasattr(created_date, 'strftime'):
                    created_date_str = created_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_date_str = '1970-01-01 00:00:00'
                
                discovered_at_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                values.append(f"({channel_id}, '{title}', '{username}', '{channel_type}', {participants_count}, '{description}', {is_verified}, {is_scam}, {is_fake}, '{created_date_str}', '{discovered_at_str}')")
            
            query = f"INSERT INTO castings_channels (channel_id, title, username, type, participants_count, description, is_verified, is_scam, is_fake, created_date, discovered_at) VALUES {','.join(values)}"
            ch_manager.execute_query(query)
            print(f"✅ {len(castings_channels)} кастинговых каналов сохранены")
        
        # Проверяем результат
        count = ch_manager.execute_query('SELECT COUNT(*) FROM castings_channels')
        print(f"📋 Записей в castings_channels: {count}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы кастингов: {e}")

if __name__ == '__main__':
    main()
