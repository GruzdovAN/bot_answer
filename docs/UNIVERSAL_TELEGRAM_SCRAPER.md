# Универсальный Telegram Scraper для ClickHouse

## Обзор системы

**Цель:** Создать универсальную систему для сбора и анализа сообщений из любых Telegram каналов с сохранением в ClickHouse.

**Возможности:**
- Поддержка множественных каналов
- Конфигурируемые парсеры для разных типов контента
- Гибкая система фильтрации и классификации
- Масштабируемая архитектура
- Готовые аналитические запросы

## Архитектура решения

### 1. Компоненты системы

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM CHANNELS                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ @jobs_tech  │  │ @ml_jobs    │  │ @python_dev │           │
│  │ @startup_jobs│  │ @remote_jobs│  │ @data_science│          │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                UNIVERSAL SCRAPER ENGINE                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Channel Manager                                       │   │
│  │  ├─ Multi-channel support                             │   │
│  │  ├─ Channel configuration                             │   │
│  │  └─ Scheduling & monitoring                          │   │
│  │                                                       │   │
│  │  Message Parser                                       │   │
│  │  ├─ Universal text extraction                        │   │
│  │  ├─ Configurable entity extraction                   │   │
│  │  ├─ Custom parsers per channel type                  │   │
│  │  └─ Content classification                           │   │
│  │                                                       │   │
│  │  Data Processor                                       │   │
│  │  ├─ Content filtering                                │   │
│  │  ├─ Data enrichment                                  │   │
│  │  ├─ Deduplication                                    │   │
│  │  └─ Batch processing                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLICKHOUSE DATABASE                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Universal Tables                                      │   │
│  │  ├─ telegram_messages (основная таблица)              │   │
│  │  ├─ channel_metadata (метаданные каналов)             │   │
│  │  ├─ parsed_entities (извлеченные сущности)            │   │
│  │  └─ analytics_cache (кеш для аналитики)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Технологический стек

- **Telegram API:** Telethon для работы с Telegram
- **База данных:** ClickHouse для хранения и аналитики
- **Язык:** Python 3.12
- **Конфигурация:** YAML/JSON для настройки каналов
- **Планировщик:** APScheduler для автоматизации
- **Мониторинг:** Prometheus + Grafana
- **Контейнеризация:** Docker + Docker Compose

## Конфигурация системы

### 1. Простая конфигурация каналов

**Файл:** `config/channels.py`

```python
# Простая конфигурация каналов
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

### 2. Простая конфигурация парсеров

**Файл:** `config/parsers.py`

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

### 3. Переменные окружения

**Файл:** `.env`

```bash
# Telegram API
API_ID_TG=your_api_id
API_HASH_TG=your_api_hash
PHONE_NUMBER=your_phone_number

# ClickHouse
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=clickhouse_admin
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DB=telegram_analytics

# Простые настройки скрапера
SCRAPER_DEFAULT_BATCH_SIZE=1000
SCRAPER_DEFAULT_DELAY=1.0
SCRAPER_MAX_RETRIES=3
```

## Структура базы данных

### 1. Основная таблица сообщений

```sql
CREATE TABLE telegram_messages (
    message_id UInt64,
    channel_id Int64,
    channel_username String,
    channel_type String,  -- 'job', 'news', 'general'
    date DateTime,
    text String,
    views UInt32,
    forwards UInt32,
    replies UInt32,
    reactions Map(String, UInt32),
    media_type String,
    media_url String,
    is_forwarded UInt8,
    forward_from_channel String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (channel_username, date, message_id)
PARTITION BY toYYYYMM(date);
```

### 2. Таблица метаданных каналов

```sql
CREATE TABLE channel_metadata (
    channel_username String,
    channel_id Int64,
    channel_type String,
    title String,
    description String,
    subscribers_count UInt32,
    is_verified UInt8,
    is_scam UInt8,
    is_fake UInt8,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY channel_username;
```

### 3. Таблица извлеченных сущностей

```sql
CREATE TABLE parsed_entities (
    message_id UInt64,
    channel_username String,
    entity_type String,  -- 'hashtag', 'mention', 'link', 'technology'
    entity_value String,
    confidence Float32,
    position_start UInt16,
    position_end UInt16,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (channel_username, entity_type, entity_value, message_id)
PARTITION BY toYYYYMM(created_at);
```

### 4. Таблица аналитики

```sql
CREATE TABLE analytics_cache (
    metric_name String,
    channel_username String,
    date Date,
    value Float64,
    metadata String,
    created_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(created_at)
ORDER BY (metric_name, channel_username, date);
```

## Реализация по модулям

### 1. Менеджер каналов

**Файл:** `src/core/channel_manager.py`

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
        """Загрузка конфигурации каналов"""
        for name, channel_config in CHANNELS.items():
            self.channels[name] = ChannelConfig(**channel_config)
    
    def get_enabled_channels(self) -> List[ChannelConfig]:
        """Получение активных каналов"""
        return [ch for ch in self.channels.values() if ch.enabled]
    
    def get_channel_config(self, channel_name: str) -> ChannelConfig:
        """Получение конфигурации канала"""
        return self.channels.get(channel_name)
```

### 2. Простой парсер

**Файл:** `src/parsers/simple_parser.py`

```python
import re
from typing import Dict, List, Any

class SimpleParser:
    """Простой парсер для извлечения сущностей"""
    
    def __init__(self, parser_type: str):
        from config.parsers import PARSERS
        self.config = PARSERS.get(parser_type, {})
    
    def parse_message(self, message) -> Dict[str, Any]:
        """Парсинг сообщения"""
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
        """Извлечение хештегов"""
        if not self.config.get('extract_hashtags', False):
            return []
        return re.findall(r'#\w+', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Извлечение упоминаний"""
        if not self.config.get('extract_mentions', False):
            return []
        return re.findall(r'@\w+', text)
    
    def extract_links(self, text: str) -> List[str]:
        """Извлечение ссылок"""
        if not self.config.get('extract_links', False):
            return []
        return re.findall(r'https?://[^\s]+', text)
    
    def extract_technologies(self, text: str) -> List[str]:
        """Извлечение технологий"""
        if not self.config.get('extract_technologies', False):
            return []
        
        technologies = []
        tech_list = self.config.get('technologies', [])
        for tech in tech_list:
            if tech.lower() in text.lower():
                technologies.append(tech)
        return technologies
    
    def extract_companies(self, text: str) -> List[str]:
        """Извлечение компаний"""
        if not self.config.get('extract_companies', False):
            return []
        
        companies = []
        company_list = self.config.get('companies', [])
        for company in company_list:
            if company.lower() in text.lower():
                companies.append(company)
        return companies
```

### 3. Основной скрапер

**Файл:** `src/core/universal_scraper.py`

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
            await self.clickhouse.insert_messages(parsed_messages)
            
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
            
            # Простая задержка
            await asyncio.sleep(1.0)
        
        return messages
```

### 4. Простой запуск

**Файл:** `main.py`

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

## Аналитические запросы

### 1. Универсальные запросы

```sql
-- Статистика по всем каналам
SELECT 
    channel_username,
    channel_type,
    count() as total_messages,
    sum(views) as total_views,
    avg(views) as avg_views,
    countDistinct(toDate(date)) as active_days
FROM telegram_messages 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY channel_username, channel_type
ORDER BY total_messages DESC;

-- Топ сущностей по типам
SELECT 
    entity_type,
    entity_value,
    count() as mentions,
    countDistinct(channel_username) as channels_count
FROM parsed_entities 
WHERE created_at >= now() - INTERVAL 30 DAY
GROUP BY entity_type, entity_value
ORDER BY mentions DESC
LIMIT 50;

-- Анализ активности по времени
SELECT 
    channel_username,
    hour(date) as hour_of_day,
    count() as messages_count,
    avg(views) as avg_views
FROM telegram_messages 
WHERE date >= now() - INTERVAL 7 DAY
GROUP BY channel_username, hour_of_day
ORDER BY channel_username, hour_of_day;
```

### 2. Специализированные запросы

```sql
-- Анализ вакансий (только job каналы)
SELECT 
    channel_username,
    count() as job_posts,
    countIf(has_salary) as posts_with_salary,
    uniqExact(technologies) as unique_technologies
FROM telegram_messages 
WHERE channel_type = 'job'
AND date >= now() - INTERVAL 30 DAY
GROUP BY channel_username;

-- Топ технологий в вакансиях
SELECT 
    entity_value as technology,
    count() as mentions,
    countDistinct(channel_username) as channels,
    avg(views) as avg_views
FROM parsed_entities 
WHERE entity_type = 'technology'
AND created_at >= now() - INTERVAL 30 DAY
GROUP BY technology
ORDER BY mentions DESC
LIMIT 20;
```

## Мониторинг и метрики

### 1. Prometheus метрики

```python
from prometheus_client import Counter, Histogram, Gauge

# Метрики
messages_scraped = Counter('telegram_messages_scraped_total', 
                          'Total scraped messages', ['channel', 'status'])
scraping_duration = Histogram('telegram_scraping_duration_seconds',
                             'Time spent scraping', ['channel'])
active_channels = Gauge('telegram_active_channels',
                       'Number of active channels')
```

### 2. Дашборд Grafana

- Количество сообщений по каналам
- Топ сущности и технологии
- Активность по времени
- Ошибки и производительность
- Тренды и аномалии

## Развертывание

### 1. Простой Docker Compose

```yaml
version: '3.8'
services:
  universal-scraper:
    build: .
    environment:
      - API_ID_TG=${API_ID_TG}
      - API_HASH_TG=${API_HASH_TG}
      - CLICKHOUSE_HOST=clickhouse
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - clickhouse
    restart: unless-stopped
  
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    environment:
      - CLICKHOUSE_DB=telegram_analytics
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse

volumes:
  clickhouse_data:
```

## Заключение

Универсальная система обеспечивает:

1. **Масштабируемость** - поддержка множественных каналов
2. **Гибкость** - конфигурируемые парсеры и фильтры
3. **Надежность** - мониторинг, логирование, обработка ошибок
4. **Производительность** - batch обработка, кэширование
5. **Аналитика** - готовые запросы и дашборды

Система готова для сбора данных из любых Telegram каналов с возможностью легкого добавления новых источников и типов контента.
