import os
import requests
from typing import List, Dict, Any

# Импортируем конфигурацию
try:
    from config.database_config import CLICKHOUSE_CONFIG, TABLES_CONFIG
except ImportError:
    CLICKHOUSE_CONFIG = {
        "host": "localhost",
        "port": "8123",
        "user": "clickhouse_admin",
        "password": "your_clickhouse_password_here",
        "database": "telegram_analytics"
    }
    TABLES_CONFIG = {}

class ClickHouseClient:
    def __init__(self):
        self.host = os.getenv('CLICKHOUSE_HOST', CLICKHOUSE_CONFIG['host'])
        self.port = os.getenv('CLICKHOUSE_PORT', CLICKHOUSE_CONFIG['port'])
        self.user = os.getenv('CLICKHOUSE_USER', CLICKHOUSE_CONFIG['user'])
        self.password = os.getenv('CLICKHOUSE_PASSWORD', CLICKHOUSE_CONFIG['password'])
        self.database = os.getenv('CLICKHOUSE_DB', CLICKHOUSE_CONFIG['database'])
        
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
    
    def insert_castings_messages(self, messages: List[Dict[str, Any]]):
        """Вставка кастинговых сообщений в ClickHouse"""
        if not messages:
            return
        
        # Формируем SQL запрос для таблицы castings_messages
        values = []
        for msg in messages:
            # Экранируем специальные символы и обрабатываем None значения
            text = (msg.get('text') or '').replace("'", "''")
            channel_title = (msg.get('channel_title') or '').replace("'", "''")
            channel_username = (msg.get('channel_username') or '').replace("'", "''")
            media_type = (msg.get('media_type') or '').replace("'", "''")
            casting_type = (msg.get('casting_type') or '').replace("'", "''")
            age_range = (msg.get('age_range') or '').replace("'", "''")
            location = (msg.get('location') or '').replace("'", "''")
            contact_info = (msg.get('contact_info') or '').replace("'", "''")
            deadline = (msg.get('deadline') or '').replace("'", "''")
            payment = (msg.get('payment') or '').replace("'", "''")
            project_name = (msg.get('project_name') or '').replace("'", "''")
            
            # Форматируем дату для ClickHouse
            date_str = msg['date'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(msg['date'], 'strftime') else str(msg['date'])
            parsed_at_str = msg['parsed_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(msg['parsed_at'], 'strftime') else str(msg['parsed_at'])
            
            # Обрабатываем все числовые значения
            message_id = msg.get('message_id', 0)
            channel_id = msg.get('channel_id', 0)
            views = msg.get('views', 0) or 0
            forwards = msg.get('forwards', 0) or 0
            replies = msg.get('replies', 0) or 0
            has_photo = int(msg.get('has_photo', False))
            has_video = int(msg.get('has_video', False))
            has_document = int(msg.get('has_document', False))
            
            values.append(f"({message_id}, {channel_id}, '{channel_title}', '{channel_username}', '{date_str}', '{text}', {views}, {forwards}, {replies}, '{media_type}', {has_photo}, {has_video}, {has_document}, '{casting_type}', '{age_range}', '{location}', '{contact_info}', '{deadline}', '{payment}', '{project_name}', '{parsed_at_str}')")
        
        query = f"INSERT INTO {self.database}.castings_messages (message_id, channel_id, channel_title, channel_username, date, text, views, forwards, replies, media_type, has_photo, has_video, has_document, casting_type, age_range, location, contact_info, deadline, payment, project_name, parsed_at) VALUES {','.join(values)}"
        
        # Выполняем запрос через HTTP
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': self.database}
        )
        
        if response.status_code != 200:
            print(f"DEBUG: SQL Query: {query[:500]}...")
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            raise Exception(f"ClickHouse error: {response.text}")
    
    def insert_channels_info(self, channels: List[Dict[str, Any]]):
        """Вставка информации о каналах в ClickHouse"""
        if not channels:
            return
        
        # Формируем SQL запрос для таблицы channels_info
        values = []
        for channel in channels:
            # Экранируем специальные символы и обрабатываем None значения
            title = (channel.get('title') or '').replace("'", "''")
            username = (channel.get('username') or '').replace("'", "''")
            channel_type = (channel.get('type') or '').replace("'", "''")
            description = (channel.get('description') or '').replace("'", "''")
            
            # Обрабатываем числовые значения
            channel_id = channel.get('id', 0)
            participants_count = channel.get('participants_count', 0) or 0
            is_verified = int(channel.get('is_verified', False))
            is_scam = int(channel.get('is_scam', False))
            is_fake = int(channel.get('is_fake', False))
            
            # Форматируем дату для ClickHouse
            created_date = channel.get('created_date')
            if created_date and hasattr(created_date, 'strftime'):
                created_date_str = created_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                created_date_str = '1970-01-01 00:00:00'
            
            discovered_at = channel.get('discovered_at')
            if discovered_at and hasattr(discovered_at, 'strftime'):
                discovered_at_str = discovered_at.strftime('%Y-%m-%d %H:%M:%S')
            else:
                from datetime import datetime
                discovered_at_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values.append(f"({channel_id}, '{title}', '{username}', '{channel_type}', {participants_count}, '{description}', {is_verified}, {is_scam}, {is_fake}, '{created_date_str}', '{discovered_at_str}')")
        
        query = f"INSERT INTO {self.database}.channels_info (channel_id, title, username, type, participants_count, description, is_verified, is_scam, is_fake, created_date, discovered_at) VALUES {','.join(values)}"
        
        # Выполняем запрос через HTTP
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': self.database}
        )
        
        if response.status_code != 200:
            print(f"DEBUG: SQL Query: {query[:500]}...")
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            raise Exception(f"ClickHouse error: {response.text}")

    def insert_all_channels(self, channels: List[Dict[str, Any]]):
        """Вставка информации о всех каналах в ClickHouse"""
        if not channels:
            return
        
        # Формируем SQL запрос для таблицы all_channels
        values = []
        for channel in channels:
            # Экранируем специальные символы и обрабатываем None значения
            title = (channel.get('title') or '').replace("'", "''")
            username = (channel.get('username') or '').replace("'", "''")
            channel_type = (channel.get('type') or '').replace("'", "''")
            description = (channel.get('description') or '').replace("'", "''")
            
            # Обрабатываем числовые значения
            channel_id = channel.get('id', 0)
            participants_count = channel.get('participants_count', 0) or 0
            is_verified = int(channel.get('is_verified', False))
            is_scam = int(channel.get('is_scam', False))
            is_fake = int(channel.get('is_fake', False))
            
            # Форматируем дату для ClickHouse
            created_date = channel.get('created_date')
            if created_date and hasattr(created_date, 'strftime'):
                created_date_str = created_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                created_date_str = '1970-01-01 00:00:00'
            
            discovered_at = channel.get('discovered_at')
            if discovered_at and hasattr(discovered_at, 'strftime'):
                discovered_at_str = discovered_at.strftime('%Y-%m-%d %H:%M:%S')
            else:
                from datetime import datetime
                discovered_at_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            values.append(f"({channel_id}, '{title}', '{username}', '{channel_type}', {participants_count}, '{description}', {is_verified}, {is_scam}, {is_fake}, '{created_date_str}', '{discovered_at_str}')")
        
        query = f"INSERT INTO {self.database}.all_channels (channel_id, title, username, type, participants_count, description, is_verified, is_scam, is_fake, created_date, discovered_at) VALUES {','.join(values)}"
        
        # Выполняем запрос через HTTP
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': self.database}
        )
        
        if response.status_code != 200:
            print(f"DEBUG: SQL Query: {query[:500]}...")
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            raise Exception(f"ClickHouse error: {response.text}")
