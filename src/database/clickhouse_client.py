import os
import requests
from typing import List, Dict, Any

class ClickHouseClient:
    def __init__(self):
        self.host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.port = os.getenv('CLICKHOUSE_PORT', '8123')
        self.user = os.getenv('CLICKHOUSE_USER', 'clickhouse_admin')
        self.password = os.getenv('CLICKHOUSE_PASSWORD')
        self.database = os.getenv('CLICKHOUSE_DB', 'telegram_analytics')
        
        self.base_url = f"http://{self.host}:{self.port}"
        self.auth = (self.user, self.password) if self.user and self.password else None
    
    def insert_messages(self, messages: List[Dict[str, Any]]):
        """Вставка сообщений в ClickHouse"""
        if not messages:
            return
        
        # Формируем SQL запрос
        values = []
        for msg in messages:
            # Экранируем специальные символы
            text = msg['text'].replace("'", "''")
            hashtags = "['" + "','".join(msg.get('hashtags', [])) + "']"
            mentions = "['" + "','".join(msg.get('mentions', [])) + "']"
            links = "['" + "','".join(msg.get('links', [])) + "']"
            technologies = "['" + "','".join(msg.get('technologies', [])) + "']"
            companies = "['" + "','".join(msg.get('companies', [])) + "']"
            
            # Форматируем дату для ClickHouse
            date_str = msg['date'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(msg['date'], 'strftime') else str(msg['date'])
            values.append(f"({msg['message_id']}, '{msg['channel_username']}', '{date_str}', '{text}', {msg.get('views', 0)}, {msg.get('forwards', 0)}, {hashtags}, {mentions}, {links}, {technologies}, {companies})")
        
        query = f"INSERT INTO {self.database}.telegram_messages (message_id, channel_username, date, text, views, forwards, hashtags, mentions, links, technologies, companies) VALUES {','.join(values)}"
        
        # Выполняем запрос через HTTP
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': self.database}
        )
        
        if response.status_code != 200:
            raise Exception(f"ClickHouse error: {response.text}")
