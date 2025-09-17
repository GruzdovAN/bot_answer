#!/usr/bin/env python3
"""
Скрипт для управления базой данных ClickHouse
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

# Импортируем конфигурацию
from config.database_config import CLICKHOUSE_CONFIG, CREATE_TABLES_SQL

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('CLICKHOUSE_HOST', CLICKHOUSE_CONFIG['host'])
        self.port = os.getenv('CLICKHOUSE_PORT', CLICKHOUSE_CONFIG['port'])
        self.user = os.getenv('CLICKHOUSE_USER', CLICKHOUSE_CONFIG['user'])
        self.password = os.getenv('CLICKHOUSE_PASSWORD', CLICKHOUSE_CONFIG['password'])
        self.database = os.getenv('CLICKHOUSE_DB', CLICKHOUSE_CONFIG['database'])
        
        self.base_url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password) if self.user and self.password else None
    
    def execute_query(self, query, database=None):
        """Выполнение SQL запроса"""
        db = database or self.database
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': db}
        )
        
        if response.status_code != 200:
            raise Exception(f"ClickHouse error: {response.text}")
        
        return response.text.strip()
    
    def show_databases(self):
        """Показать все базы данных"""
        result = self.execute_query('SHOW DATABASES')
        databases = [db for db in result.split('\n') if db and db not in ['default', 'system', 'information_schema']]
        return databases
    
    def show_tables(self, database=None):
        """Показать все таблицы в базе"""
        db = database or self.database
        result = self.execute_query('SHOW TABLES', db)
        tables = [table for table in result.split('\n') if table]
        return tables
    
    def drop_database(self, database_name):
        """Удалить базу данных"""
        try:
            self.execute_query(f'DROP DATABASE IF EXISTS {database_name}')
            print(f"✅ База данных '{database_name}' удалена")
            return True
        except Exception as e:
            print(f"❌ Ошибка при удалении базы '{database_name}': {e}")
            return False
    
    def create_table(self, table_name, database=None):
        """Создать таблицу"""
        db = database or self.database
        
        if table_name not in CREATE_TABLES_SQL:
            print(f"❌ Неизвестная таблица: {table_name}")
            return False
        
        try:
            sql = CREATE_TABLES_SQL[table_name].format(database=db)
            self.execute_query(sql, db)
            print(f"✅ Таблица '{table_name}' создана в базе '{db}'")
            return True
        except Exception as e:
            print(f"❌ Ошибка при создании таблицы '{table_name}': {e}")
            return False
    
    def get_table_info(self, table_name, database=None):
        """Получить информацию о таблице"""
        db = database or self.database
        try:
            result = self.execute_query(f'DESCRIBE {table_name}', db)
            return result
        except Exception as e:
            print(f"❌ Ошибка при получении информации о таблице '{table_name}': {e}")
            return None
    
    def get_table_count(self, table_name, database=None):
        """Получить количество записей в таблице"""
        db = database or self.database
        try:
            result = self.execute_query(f'SELECT COUNT(*) FROM {table_name}', db)
            return int(result)
        except Exception as e:
            print(f"❌ Ошибка при подсчете записей в таблице '{table_name}': {e}")
            return 0

def main():
    """Основная функция"""
    manager = DatabaseManager()
    
    print("🗄️ УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ CLICKHOUSE")
    print("=" * 50)
    
    # Показываем текущие базы данных
    print("\n📊 СУЩЕСТВУЮЩИЕ БАЗЫ ДАННЫХ:")
    databases = manager.show_databases()
    for db in databases:
        print(f"  - {db}")
    
    # Показываем таблицы в основной базе
    print(f"\n📋 ТАБЛИЦЫ В БАЗЕ '{manager.database}':")
    tables = manager.show_tables()
    for table in tables:
        count = manager.get_table_count(table)
        print(f"  - {table} ({count} записей)")
    
    # Удаляем пустую базу telegram_bot_analytics
    if 'telegram_bot_analytics' in databases:
        print(f"\n🗑️ Удаляем пустую базу 'telegram_bot_analytics'...")
        manager.drop_database('telegram_bot_analytics')
    
    # Создаем новые таблицы для кастингов
    print(f"\n🔧 СОЗДАНИЕ ТАБЛИЦ ДЛЯ КАСТИНГОВ:")
    
    # Создаем таблицу для кастинговых сообщений
    if 'castings_messages' not in tables:
        manager.create_table('castings_messages')
    else:
        print("  - Таблица 'castings_messages' уже существует")
    
    # Создаем таблицу для информации о каналах
    if 'channels_info' not in tables:
        manager.create_table('channels_info')
    else:
        print("  - Таблица 'channels_info' уже существует")
    
    # Показываем финальное состояние
    print(f"\n📊 ФИНАЛЬНОЕ СОСТОЯНИЕ БАЗЫ '{manager.database}':")
    tables = manager.show_tables()
    for table in tables:
        count = manager.get_table_count(table)
        print(f"  - {table} ({count} записей)")
    
    print("\n✅ Управление базой данных завершено!")

if __name__ == '__main__':
    main()


