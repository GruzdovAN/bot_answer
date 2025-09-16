# План реализации: Сохранение записей из @datasciencejobs в ClickHouse

## Обзор задачи

**Цель:** Собрать все сообщения из Telegram канала @datasciencejobs за последний месяц и сохранить их в ClickHouse для дальнейшего анализа.

## Архитектура решения

### 1. Компоненты системы

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Python Bot     │    │   ClickHouse    │
│   Channel       │───▶│   (Scraper)      │───▶│   Database      │
│ @datasciencejobs│    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 2. Технологический стек

- **Telegram API:** Telethon для работы с Telegram
- **База данных:** ClickHouse для хранения и аналитики
- **Язык:** Python 3.12
- **Контейнеризация:** Docker
- **Оркестрация:** Docker Compose

## Детальный план реализации

### Этап 1: Подготовка инфраструктуры

#### 1.1 Создание таблицы в ClickHouse
```sql
CREATE TABLE datascience_jobs (
    message_id UInt64,
    channel_id Int64,
    channel_username String,
    date DateTime,
    text String,
    views UInt32,
    forwards UInt32,
    replies UInt32,
    reactions Map(String, UInt32),
    media_type String,
    media_url String,
    hashtags Array(String),
    mentions Array(String),
    links Array(String),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (date, message_id)
PARTITION BY toYYYYMM(date);
```

#### 1.2 Настройка переменных окружения
```bash
# Добавить в .env
DATASCIENCE_CHANNEL=@datasciencejobs
SCRAPER_START_DATE=2024-08-16  # Месяц назад
SCRAPER_END_DATE=2024-09-16    # Сегодня
```

### Этап 2: Разработка скрапера

#### 2.1 Создание модуля скрапера
**Файл:** `src/scrapers/datascience_scraper.py`

**Основные функции:**
- `connect_to_telegram()` - подключение к Telegram API
- `get_channel_messages()` - получение сообщений из канала
- `parse_message()` - парсинг сообщения и извлечение данных
- `save_to_clickhouse()` - сохранение в ClickHouse
- `extract_entities()` - извлечение хештегов, упоминаний, ссылок

#### 2.2 Структура данных сообщения
```python
@dataclass
class JobMessage:
    message_id: int
    channel_id: int
    channel_username: str
    date: datetime
    text: str
    views: int
    forwards: int
    replies: int
    reactions: Dict[str, int]
    media_type: Optional[str]
    media_url: Optional[str]
    hashtags: List[str]
    mentions: List[str]
    links: List[str]
```

### Этап 3: Реализация парсинга

#### 3.1 Извлечение метаданных
- **Хештеги:** `#python`, `#machinelearning`, `#dataanalyst`
- **Упоминания:** `@company`, `@recruiter`
- **Ссылки:** job boards, company websites
- **Реакции:** количество лайков, репостов

#### 3.2 Классификация контента
- **Тип вакансии:** Full-time, Part-time, Contract, Internship
- **Уровень:** Junior, Middle, Senior, Lead
- **Технологии:** Python, R, SQL, ML frameworks
- **Локация:** Remote, On-site, Hybrid

### Этап 4: Интеграция с ClickHouse

#### 4.1 ClickHouse клиент
```python
from clickhouse_driver import Client

class ClickHouseClient:
    def __init__(self):
        self.client = Client(
            host='clickhouse',
            port=9000,
            user='clickhouse_admin',
            password=os.getenv('CLICKHOUSE_PASSWORD'),
            database='telegram_bot_analytics'
        )
    
    def insert_job_message(self, message: JobMessage):
        # Вставка данных в ClickHouse
        pass
```

#### 4.2 Batch вставка
- Группировка сообщений по 1000 штук
- Использование `INSERT INTO ... VALUES` для эффективности
- Обработка ошибок и retry логика

### Этап 5: Мониторинг и логирование

#### 5.1 Логирование процесса
- Количество обработанных сообщений
- Ошибки парсинга
- Время выполнения операций
- Статистика по типам контента

#### 5.2 Метрики
- Скорость обработки (сообщений/минуту)
- Успешность парсинга (%)
- Размер данных в ClickHouse
- Время последнего обновления

## Реализация по файлам

### 1. Основной скрипт
**Файл:** `scripts/scrape_datascience_jobs.py`

```python
#!/usr/bin/env python3
"""
Скрипт для сбора данных из канала @datasciencejobs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from src.scrapers.datascience_scraper import DataScienceJobsScraper
from src.database.clickhouse_client import ClickHouseClient

async def main():
    scraper = DataScienceJobsScraper()
    await scraper.scrape_channel(
        channel_username="@datasciencejobs",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now()
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Модуль скрапера
**Файл:** `src/scrapers/datascience_scraper.py`

```python
import re
import asyncio
from typing import List, Optional
from telethon import TelegramClient
from telethon.tl.types import Message
from dataclasses import dataclass
from datetime import datetime

class DataScienceJobsScraper:
    def __init__(self):
        self.client = TelegramClient(
            'datascience_scraper',
            api_id=os.getenv('API_ID_TG'),
            api_hash=os.getenv('API_HASH_TG')
        )
        self.clickhouse = ClickHouseClient()
    
    async def scrape_channel(self, channel_username: str, 
                           start_date: datetime, end_date: datetime):
        """Основная функция сбора данных"""
        pass
    
    def parse_message(self, message: Message) -> JobMessage:
        """Парсинг сообщения и извлечение данных"""
        pass
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Извлечение хештегов"""
        return re.findall(r'#\w+', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Извлечение упоминаний"""
        return re.findall(r'@\w+', text)
    
    def extract_links(self, text: str) -> List[str]:
        """Извлечение ссылок"""
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
```

### 3. ClickHouse клиент
**Файл:** `src/database/clickhouse_client.py`

```python
from clickhouse_driver import Client
import logging

class ClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=os.getenv('CLICKHOUSE_HOST', 'clickhouse'),
            port=int(os.getenv('CLICKHOUSE_NATIVE_PORT', '9000')),
            user=os.getenv('CLICKHOUSE_USER', 'clickhouse_admin'),
            password=os.getenv('CLICKHOUSE_PASSWORD'),
            database=os.getenv('CLICKHOUSE_DB', 'telegram_bot_analytics')
        )
    
    def create_tables(self):
        """Создание таблиц для хранения данных"""
        pass
    
    def insert_job_messages(self, messages: List[JobMessage]):
        """Batch вставка сообщений"""
        pass
    
    def get_statistics(self) -> dict:
        """Получение статистики по собранным данным"""
        pass
```

### 4. Конфигурация
**Файл:** `src/config/scraper_config.py`

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ScraperConfig:
    channel_username: str = "@datasciencejobs"
    start_date: datetime = datetime.now() - timedelta(days=30)
    end_date: datetime = datetime.now()
    batch_size: int = 1000
    max_retries: int = 3
    delay_between_requests: float = 1.0
```

## План выполнения

### Неделя 1: Подготовка
- [ ] Создание таблицы в ClickHouse
- [ ] Настройка переменных окружения
- [ ] Создание базовой структуры проекта

### Неделя 2: Разработка скрапера
- [ ] Реализация подключения к Telegram
- [ ] Парсинг сообщений
- [ ] Извлечение метаданных

### Неделя 3: Интеграция с ClickHouse
- [ ] ClickHouse клиент
- [ ] Batch вставка данных
- [ ] Обработка ошибок

### Неделя 4: Тестирование и оптимизация
- [ ] Тестирование на реальных данных
- [ ] Оптимизация производительности
- [ ] Мониторинг и логирование

## Ожидаемые результаты

### Количественные метрики
- **Количество сообщений:** ~1000-2000 за месяц
- **Размер данных:** ~50-100 MB
- **Время выполнения:** 30-60 минут
- **Точность парсинга:** >95%

### Качественные результаты
- Структурированные данные о вакансиях
- Возможность аналитики по технологиям
- Тренды в Data Science индустрии
- Географическое распределение вакансий

## Возможные проблемы и решения

### 1. Ограничения Telegram API
**Проблема:** Rate limiting, ограничения на количество запросов
**Решение:** Добавление задержек между запросами, batch обработка

### 2. Большой объем данных
**Проблема:** Медленная вставка в ClickHouse
**Решение:** Batch вставка, оптимизация структуры таблицы

### 3. Парсинг неструктурированных данных
**Проблема:** Разные форматы сообщений
**Решение:** Регулярные выражения, ML модели для классификации

### 4. Ошибки сети
**Проблема:** Нестабильное подключение
**Решение:** Retry логика, сохранение прогресса

## Мониторинг и аналитика

### Дашборд метрик
- Количество собранных сообщений
- Статистика по технологиям
- Тренды по времени
- Географическое распределение

### Алерты
- Ошибки парсинга >5%
- Время выполнения >2 часов
- Размер данных >200MB
- Отсутствие обновлений >24 часов

## Заключение

Данный план обеспечивает:
1. **Масштабируемость** - возможность обработки больших объемов данных
2. **Надежность** - обработка ошибок и retry логика
3. **Производительность** - оптимизированная работа с ClickHouse
4. **Мониторинг** - отслеживание процесса и результатов
5. **Расширяемость** - возможность добавления новых каналов

Реализация займет 4 недели и позволит получить структурированные данные о вакансиях в Data Science для дальнейшего анализа.
