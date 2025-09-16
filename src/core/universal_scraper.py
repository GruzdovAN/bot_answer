import asyncio
import logging
import os
from typing import Dict, List
from telethon import TelegramClient
from datetime import datetime, timedelta

from .channel_manager import ChannelManager
from ..parsers.simple_parser import SimpleParser
from ..database.clickhouse_client import ClickHouseClient

class UniversalScraper:
    def __init__(self):
        self.channel_manager = ChannelManager()
        self.clickhouse = ClickHouseClient()
        self.client = TelegramClient(
            'sessions/universal_scraper',
            api_id=os.getenv('API_ID_TG'),
            api_hash=os.getenv('API_HASH_TG')
        )
        self.logger = logging.getLogger(__name__)
    
    async def scrape_all_channels(self):
        """Сбор данных со всех активных каналов"""
        channels = self.channel_manager.get_enabled_channels()
        
        for channel in channels:
            await self.scrape_channel(channel)
    
    async def scrape_channel(self, channel_config):
        """Сбор данных с конкретного канала"""
        try:
            self.logger.info(f"Начинаем сбор данных с {channel_config.username}")
            
            # Получение сообщений
            messages = await self.get_channel_messages(channel_config)
            
            # Парсинг сообщений
            parsed_messages = []
            parser = SimpleParser(channel_config.parser_type)
            
            for message in messages:
                parsed = parser.parse_message(message)
                parsed['message_id'] = message.id
                parsed['channel_username'] = channel_config.username
                parsed['date'] = message.date
                parsed['views'] = getattr(message, 'views', 0)
                parsed['forwards'] = getattr(message, 'forwards', 0)
                parsed_messages.append(parsed)
            
            # Сохранение в ClickHouse
            self.clickhouse.insert_messages(parsed_messages)
            
            self.logger.info(f"Собрано {len(parsed_messages)} сообщений с {channel_config.username}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при сборе данных с {channel_config.username}: {e}")
    
    async def get_channel_messages(self, channel_config):
        """Получение сообщений из канала"""
        entity = await self.client.get_entity(channel_config.username)
        
        messages = []
        async for message in self.client.iter_messages(
            entity,
            limit=channel_config.batch_size,
            offset_date=datetime.now() - timedelta(days=channel_config.days_back)
        ):
            messages.append(message)
            await asyncio.sleep(1.0)  # Простая задержка
        
        return messages
