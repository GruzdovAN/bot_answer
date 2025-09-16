#!/usr/bin/env python3
"""
Скрипт для очистки дублей в таблицах ClickHouse
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class ClickHouseCleaner:
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
    
    def check_duplicates(self, table_name):
        """Проверка дублей в таблице"""
        # Для разных таблиц используем разные поля для группировки
        if table_name == 'castings_messages':
            query = f"""
            SELECT channel_id, message_id, COUNT(*) as count 
            FROM {table_name} 
            GROUP BY channel_id, message_id 
            HAVING count > 1
            ORDER BY count DESC
            """
        else:
            query = f"""
            SELECT channel_id, title, COUNT(*) as count 
            FROM {table_name} 
            GROUP BY channel_id, title 
            HAVING count > 1
            ORDER BY count DESC
            """
        
        try:
            result = self.execute_query(query)
            lines = result.strip().split('\n')
            
            if lines and lines[0]:
                print(f"🔍 Найдены дубли в таблице {table_name}:")
                total_duplicates = 0
                for line in lines:
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            channel_id = parts[0]
                            title = parts[1]
                            count = int(parts[2])
                            duplicates = count - 1
                            total_duplicates += duplicates
                            print(f"  - {title} (ID: {channel_id}): {count} записей ({duplicates} дублей)")
                
                print(f"📊 Общее количество дублей: {total_duplicates}")
                return total_duplicates
            else:
                print(f"✅ Дубли в таблице {table_name} не найдены")
                return 0
                
        except Exception as e:
            print(f"❌ Ошибка при проверке дублей в {table_name}: {e}")
            return -1
    
    def clean_duplicates(self, table_name):
        """Очистка дублей в таблице"""
        print(f"🧹 Очистка дублей в таблице {table_name}...")
        
        try:
            # Создаем временную таблицу с уникальными записями
            temp_table = f"{table_name}_temp"
            
            # Удаляем временную таблицу если она существует
            try:
                self.execute_query(f"DROP TABLE IF EXISTS {temp_table}")
            except:
                pass
            
            # Создаем временную таблицу с уникальными записями
            create_temp_query = f"""
            CREATE TABLE {temp_table} AS
            SELECT DISTINCT channel_id, title, username, type, participants_count, 
                   description, is_verified, is_scam, is_fake, created_date, discovered_at
            FROM {table_name}
            """
            
            self.execute_query(create_temp_query)
            print(f"✅ Временная таблица {temp_table} создана")
            
            # Очищаем оригинальную таблицу
            self.execute_query(f"TRUNCATE TABLE {table_name}")
            print(f"✅ Таблица {table_name} очищена")
            
            # Копируем уникальные записи обратно
            self.execute_query(f"INSERT INTO {table_name} SELECT * FROM {temp_table}")
            print(f"✅ Уникальные записи скопированы в {table_name}")
            
            # Удаляем временную таблицу
            self.execute_query(f"DROP TABLE {temp_table}")
            print(f"✅ Временная таблица {temp_table} удалена")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при очистке дублей в {table_name}: {e}")
            return False
    
    def get_table_stats(self, table_name):
        """Получение статистики таблицы"""
        try:
            count = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
            print(f"📋 {table_name}: {count} записей")
            return int(count)
        except Exception as e:
            print(f"❌ Ошибка при получении статистики {table_name}: {e}")
            return 0

def main():
    """Основная функция"""
    print("🧹 ОЧИСТКА ДУБЛЕЙ В CLICKHOUSE")
    print("=" * 50)
    
    cleaner = ClickHouseCleaner()
    
    # Таблицы для проверки
    tables = ['channels_info', 'castings_channels', 'castings_messages']
    
    print("📊 ТЕКУЩЕЕ СОСТОЯНИЕ ТАБЛИЦ:")
    print("-" * 30)
    
    total_duplicates = 0
    for table in tables:
        cleaner.get_table_stats(table)
        duplicates = cleaner.check_duplicates(table)
        if duplicates > 0:
            total_duplicates += duplicates
        print()
    
    if total_duplicates == 0:
        print("✅ Дубли не найдены во всех таблицах!")
        return
    
    print(f"🔍 Общее количество дублей: {total_duplicates}")
    print()
    
    # Очищаем дубли
    print("🧹 НАЧИНАЕМ ОЧИСТКУ ДУБЛЕЙ:")
    print("-" * 30)
    
    for table in tables:
        duplicates = cleaner.check_duplicates(table)
        if duplicates > 0:
            success = cleaner.clean_duplicates(table)
            if success:
                print(f"✅ Дубли в {table} очищены")
            else:
                print(f"❌ Не удалось очистить дубли в {table}")
            print()
    
    # Финальная проверка
    print("📊 ФИНАЛЬНОЕ СОСТОЯНИЕ:")
    print("-" * 20)
    
    for table in tables:
        cleaner.get_table_stats(table)
        cleaner.check_duplicates(table)
        print()

if __name__ == '__main__':
    main()
