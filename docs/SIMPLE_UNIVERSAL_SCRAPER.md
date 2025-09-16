# Простой универсальный Telegram скрапер

## Обзор

Простая система для сбора сообщений из разных Telegram каналов с сохранением в ClickHouse. Без сложных конфигураций и планировщиков.

## Что нужно

- Python 3.12+
- ClickHouse (уже настроен)
- Telegram API ключи

## Структура проекта

```
src/
├── core/
│   ├── channel_manager.py    # Управление каналами
│   └── universal_scraper.py  # Основной скрапер
├── parsers/
│   └── simple_parser.py      # Простой парсер
├── database/
│   └── clickhouse_client.py  # Клиент ClickHouse
config/
├── channels.py               # Список каналов
└── parsers.py               # Настройки парсеров
main.py                      # Запуск скрапера
```

## Конфигурация

### 1. Каналы (`config/channels.py`)

```python
# Простой список каналов
CHANNELS = {
    "datascience_jobs": {
        "username": "@datasciencejobs",
        "enabled": True,
        "parser_type": "job_parser",
        "days_back": 30,
        "batch_size": 1000
    },
    "python_jobs": {
        "username": "@python_jobs", 
        "enabled": True,
        "parser_type": "job_parser",
        "days_back": 30,
        "batch_size": 500
    },
    "tech_news": {
        "username": "@technews",
        "enabled": True,
        "parser_type": "news_parser", 
        "days_back": 7,
        "batch_size": 200
    }
}
```

### 2. Парсеры (`config/parsers.py`)

```python
# Простые настройки парсеров
PARSERS = {
    "job_parser": {
        "extract_hashtags": True,
        "extract_mentions": True,
        "extract_links": True,
        "extract_technologies": True,
        "technologies": ["python", "javascript", "java", "react", "node.js"]
    },
    "news_parser": {
        "extract_hashtags": True,
        "extract_mentions": True,
        "extract_links": True,
        "extract_companies": True,
        "companies": ["Google", "Apple", "Microsoft", "Amazon"]
    }
}
```

## База данных

### Создание таблиц в ClickHouse

```sql
-- Основная таблица сообщений
CREATE TABLE telegram_messages (
    message_id UInt64,
    channel_username String,
    date DateTime,
    text String,
    views UInt32,
    forwards UInt32,
    hashtags Array(String),
    mentions Array(String),
    links Array(String),
    technologies Array(String),
    companies Array(String),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (channel_username, date, message_id)
PARTITION BY toYYYYMM(date);
```

## Код

### 1. Менеджер каналов (`src/core/channel_manager.py`)

```python
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ChannelConfig:
    username: str
    enabled: bool
    parser_type: str
    days_back: int
    batch_size: int

class ChannelManager:
    def __init__(self):
        from config.channels import CHANNELS
        self.channels = {}
        self.load_config()
    
    def load_config(self):
        for name, channel_config in CHANNELS.items():
            self.channels[name] = ChannelConfig(**channel_config)
    
    def get_enabled_channels(self) -> List[ChannelConfig]:
        return [ch for ch in self.channels.values() if ch.enabled]
```

### 2. Простой парсер (`src/parsers/simple_parser.py`)

```python
import re
from typing import Dict, List, Any

class SimpleParser:
    def __init__(self, parser_type: str):
        from config.parsers import PARSERS
        self.config = PARSERS.get(parser_type, {})
    
    def parse_message(self, message) -> Dict[str, Any]:
        text = message.text or ""
        
        return {
            'text': text,
            'hashtags': self.extract_hashtags(text),
            'mentions': self.extract_mentions(text),
            'links': self.extract_links(text),
            'technologies': self.extract_technologies(text),
            'companies': self.extract_companies(text),
        }
    
    def extract_hashtags(self, text: str) -> List[str]:
        if not self.config.get('extract_hashtags', False):
            return []
        return re.findall(r'#\w+', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        if not self.config.get('extract_mentions', False):
            return []
        return re.findall(r'@\w+', text)
    
    def extract_links(self, text: str) -> List[str]:
        if not self.config.get('extract_links', False):
            return []
        return re.findall(r'https?://[^\s]+', text)
    
    def extract_technologies(self, text: str) -> List[str]:
        if not self.config.get('extract_technologies', False):
            return []
        
        technologies = []
        tech_list = self.config.get('technologies', [])
        for tech in tech_list:
            if tech.lower() in text.lower():
                technologies.append(tech)
        return technologies
    
    def extract_companies(self, text: str) -> List[str]:
        if not self.config.get('extract_companies', False):
            return []
        
        companies = []
        company_list = self.config.get('companies', [])
        for company in company_list:
            if company.lower() in text.lower():
                companies.append(company)
        return companies
```

### 3. ClickHouse клиент (`src/database/clickhouse_client.py`)

```python
import os
from clickhouse_driver import Client
from typing import List, Dict, Any

class ClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=os.getenv('CLICKHOUSE_HOST', 'clickhouse'),
            port=int(os.getenv('CLICKHOUSE_PORT', '9000')),
            user=os.getenv('CLICKHOUSE_USER', 'clickhouse_admin'),
            password=os.getenv('CLICKHOUSE_PASSWORD'),
            database=os.getenv('CLICKHOUSE_DB', 'telegram_analytics')
        )
    
    def insert_messages(self, messages: List[Dict[str, Any]]):
        """Вставка сообщений в ClickHouse"""
        if not messages:
            return
        
        data = []
        for msg in messages:
            data.append((
                msg['message_id'],
                msg['channel_username'],
                msg['date'],
                msg['text'],
                msg.get('views', 0),
                msg.get('forwards', 0),
                msg.get('hashtags', []),
                msg.get('mentions', []),
                msg.get('links', []),
                msg.get('technologies', []),
                msg.get('companies', [])
            ))
        
        self.client.execute(
            """INSERT INTO telegram_messages 
            (message_id, channel_username, date, text, views, forwards, 
             hashtags, mentions, links, technologies, companies) 
            VALUES""",
            data
        )
```

### 4. Основной скрапер (`src/core/universal_scraper.py`)

```python
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
            'universal_scraper',
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
```

### 5. Запуск (`main.py`)

```python
#!/usr/bin/env python3
"""
Простой запуск универсального скрапера
"""

import asyncio
import logging
from src.core.universal_scraper import UniversalScraper

async def main():
    """Основная функция"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scraper = UniversalScraper()
    
    try:
        await scraper.client.start()
        await scraper.scrape_all_channels()
    finally:
        await scraper.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Запуск

### 1. Установка зависимостей

```bash
pip install telethon clickhouse-driver python-dotenv
```

### 2. Настройка переменных окружения

```bash
# В .env файле
API_ID_TG=your_api_id
API_HASH_TG=your_api_hash
PHONE_NUMBER=your_phone_number
CLICKHOUSE_PASSWORD=your_password
```

### 3. Запуск

```bash
python main.py
```

## Аналитические запросы

### Базовые запросы

```sql
-- Статистика по каналам
SELECT 
    channel_username,
    count() as total_messages,
    sum(views) as total_views,
    avg(views) as avg_views
FROM telegram_messages 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY channel_username
ORDER BY total_messages DESC;

-- Топ хештеги
SELECT 
    hashtag,
    count() as mentions
FROM (
    SELECT arrayJoin(hashtags) as hashtag
    FROM telegram_messages 
    WHERE date >= now() - INTERVAL 30 DAY
)
GROUP BY hashtag
ORDER BY mentions DESC
LIMIT 20;

-- Топ технологии
SELECT 
    technology,
    count() as mentions
FROM (
    SELECT arrayJoin(technologies) as technology
    FROM telegram_messages 
    WHERE date >= now() - INTERVAL 30 DAY
)
GROUP BY technology
ORDER BY mentions DESC
LIMIT 20;
```

## Добавление нового канала

1. **Добавить в `config/channels.py`:**
```python
"new_channel": {
    "username": "@new_channel",
    "enabled": True,
    "parser_type": "job_parser",
    "days_back": 30,
    "batch_size": 500
}
```

2. **Запустить скрапер:**
```bash
python main.py
```

## Заключение

Простая система для сбора данных из Telegram каналов:
- ✅ Без сложных конфигураций
- ✅ Легко добавлять новые каналы
- ✅ Простые парсеры
- ✅ Готовые аналитические запросы
- ✅ Работает с существующим ClickHouse
