#!/usr/bin/env python3
"""
Простая аналитика для собранных данных
"""

import requests
import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

class SimpleAnalytics:
    def __init__(self):
        self.host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.port = os.getenv('CLICKHOUSE_PORT', '8123')
        self.user = os.getenv('CLICKHOUSE_USER', 'clickhouse_admin')
        self.password = os.getenv('CLICKHOUSE_PASSWORD')
        self.database = os.getenv('CLICKHOUSE_DB', 'telegram_analytics')
        
        self.base_url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password) if self.user and self.password else None
    
    def execute_query(self, query):
        """Выполнение SQL запроса"""
        response = requests.get(
            self.base_url,
            params={'query': query, 'database': self.database},
            auth=self.auth
        )
        
        if response.status_code == 200:
            return response.text.strip().split('\n')
        else:
            raise Exception(f"ClickHouse error: {response.text}")
    
    def get_statistics(self):
        """Получение общей статистики"""
        print("📊 Общая статистика:")
        
        # Общее количество сообщений
        total = self.execute_query("SELECT count() FROM telegram_messages")[0]
        print(f"   Всего сообщений: {total}")
        
        # Количество каналов
        channels = self.execute_query("SELECT uniq(channel_username) FROM telegram_messages")[0]
        print(f"   Количество каналов: {channels}")
        
        # Общее количество просмотров
        views = self.execute_query("SELECT sum(views) FROM telegram_messages")[0]
        print(f"   Общее количество просмотров: {views}")
    
    def get_channel_stats(self):
        """Статистика по каналам"""
        print("\n📈 Статистика по каналам:")
        
        query = """
        SELECT 
            channel_username,
            count() as messages,
            sum(views) as total_views,
            avg(views) as avg_views
        FROM telegram_messages 
        GROUP BY channel_username
        ORDER BY messages DESC
        """
        
        results = self.execute_query(query)
        for line in results:
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    channel, messages, total_views, avg_views = parts
                    print(f"   {channel}: {messages} сообщений, {total_views} просмотров (ср. {avg_views})")
    
    def get_top_hashtags(self, limit=10):
        """Топ хештегов"""
        print(f"\n🏷️ Топ {limit} хештегов:")
        
        query = f"""
        SELECT 
            hashtag,
            count() as mentions
        FROM (
            SELECT arrayJoin(hashtags) as hashtag
            FROM telegram_messages 
        )
        GROUP BY hashtag
        ORDER BY mentions DESC
        LIMIT {limit}
        """
        
        results = self.execute_query(query)
        for line in results:
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    hashtag, mentions = parts
                    print(f"   {hashtag}: {mentions} упоминаний")
    
    def get_top_technologies(self, limit=10):
        """Топ технологий"""
        print(f"\n💻 Топ {limit} технологий:")
        
        query = f"""
        SELECT 
            technology,
            count() as mentions
        FROM (
            SELECT arrayJoin(technologies) as technology
            FROM telegram_messages 
        )
        GROUP BY technology
        ORDER BY mentions DESC
        LIMIT {limit}
        """
        
        results = self.execute_query(query)
        for line in results:
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    technology, mentions = parts
                    print(f"   {technology}: {mentions} упоминаний")
    
    def get_recent_messages(self, limit=5):
        """Последние сообщения"""
        print(f"\n📝 Последние {limit} сообщений:")
        
        query = f"""
        SELECT 
            channel_username,
            date,
            text,
            views
        FROM telegram_messages 
        ORDER BY date DESC
        LIMIT {limit}
        """
        
        results = self.execute_query(query)
        for line in results:
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    channel, date, text, views = parts
                    # Обрезаем длинный текст
                    short_text = text[:100] + "..." if len(text) > 100 else text
                    print(f"   [{channel}] {date}: {short_text} ({views} просмотров)")

def main():
    """Основная функция"""
    print("📊 Аналитика Telegram каналов")
    print("=" * 50)
    
    try:
        analytics = SimpleAnalytics()
        
        # Общая статистика
        analytics.get_statistics()
        
        # Статистика по каналам
        analytics.get_channel_stats()
        
        # Топ хештеги
        analytics.get_top_hashtags()
        
        # Топ технологии
        analytics.get_top_technologies()
        
        # Последние сообщения
        analytics.get_recent_messages()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
