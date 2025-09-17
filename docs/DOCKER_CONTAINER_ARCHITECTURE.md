# Архитектура Docker контейнера для мониторинга кастингов

## 🎯 Цель контейнера

Создать автономный Docker контейнер, который:
1. Слушает новые сообщения в Telegram каналах о кастингах
2. Сохраняет сообщения в существующую таблицу ClickHouse
3. Обрабатывает каждое сообщение через LLM
4. Сохраняет результаты LLM анализа в JSON формате в новое поле таблицы

## 🏗️ Архитектура контейнера

### Структура проекта

```
casting-monitor/
├── Dockerfile                 # Конфигурация контейнера
├── docker-compose.yml         # Оркестрация сервисов
├── requirements.txt           # Python зависимости
├── .env.example              # Пример переменных окружения
├── src/
│   ├── __init__.py
│   ├── main.py               # Точка входа приложения
│   ├── monitor.py            # Основной модуль мониторинга
│   ├── message_processor.py  # Обработчик сообщений
│   ├── llm_client.py         # Клиент для работы с LLM
│   ├── clickhouse_client.py  # Клиент для ClickHouse
│   └── config/
│       ├── __init__.py
│       ├── settings.py       # Настройки приложения
│       └── channels.py       # Конфигурация каналов
├── sessions/                 # Telegram сессии (volume)
├── logs/                     # Логи приложения (volume)
└── scripts/
    ├── entrypoint.sh         # Скрипт запуска
    └── healthcheck.sh        # Проверка здоровья
```

## 📦 Dockerfile

```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY scripts/ ./scripts/

# Создание директорий для данных
RUN mkdir -p /app/sessions /app/logs

# Установка прав на выполнение скриптов
RUN chmod +x scripts/*.sh

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Точка входа
ENTRYPOINT ["./scripts/entrypoint.sh"]

# Команда по умолчанию
CMD ["python", "src/main.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ./scripts/healthcheck.sh
```

## 🐳 Docker Compose

```yaml
version: '3.8'

services:
  casting-monitor:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: casting-monitor
    restart: unless-stopped
    
    environment:
      # Telegram API
      - API_ID_TG=${API_ID_TG}
      - API_HASH_TG=${API_HASH_TG}
      - PHONE_NUMBER=${PHONE_NUMBER}
      
      # ClickHouse
      - CLICKHOUSE_HOST=${CLICKHOUSE_HOST:-clickhouse}
      - CLICKHOUSE_PORT=${CLICKHOUSE_PORT:-8123}
      - CLICKHOUSE_USER=${CLICKHOUSE_USER:-clickhouse_admin}
      - CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD}
      - CLICKHOUSE_DB=${CLICKHOUSE_DB:-telegram_analytics}
      
      # LLM API
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      
      # Настройки мониторинга
      - MONITOR_INTERVAL=${MONITOR_INTERVAL:-5}
      - BATCH_SIZE=${BATCH_SIZE:-10}
      - MAX_RETRIES=${MAX_RETRIES:-3}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    volumes:
      # Telegram сессии
      - ./sessions:/app/sessions:ro
      # Логи
      - ./logs:/app/logs
      # Конфигурация каналов
      - ./config:/app/config:ro
    
    depends_on:
      - clickhouse
    
    networks:
      - telegram-network
    
    # Ограничения ресурсов
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    container_name: clickhouse
    restart: unless-stopped
    
    ports:
      - "8123:8123"
      - "9000:9000"
    
    environment:
      - CLICKHOUSE_DB=telegram_analytics
      - CLICKHOUSE_USER=clickhouse_admin
      - CLICKHOUSE_PASSWORD=${CLICKHOUSE_PASSWORD}
    
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - ./docker/clickhouse/config.xml:/etc/clickhouse-server/config.xml:ro
      - ./docker/clickhouse/users.xml:/etc/clickhouse-server/users.xml:ro
    
    networks:
      - telegram-network

volumes:
  clickhouse_data:

networks:
  telegram-network:
    driver: bridge
```

## 🔧 Основные модули

### 1. `main.py` - Точка входа

```python
#!/usr/bin/env python3
"""
Главный модуль для запуска мониторинга кастингов
"""

import asyncio
import logging
import signal
import sys
from src.monitor import CastingMonitor
from src.config.settings import Settings

async def main():
    """Основная функция приложения"""
    settings = Settings()
    
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/app/logs/casting_monitor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Запуск мониторинга кастингов...")
    
    # Создание монитора
    monitor = CastingMonitor(settings)
    
    # Обработка сигналов для graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, завершение работы...")
        asyncio.create_task(monitor.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Запуск мониторинга
        await monitor.start()
    except Exception as e:
        logger.error(f"Ошибка при запуске мониторинга: {e}")
        sys.exit(1)
    finally:
        await monitor.stop()
        logger.info("Мониторинг остановлен")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. `monitor.py` - Основной модуль мониторинга

```python
"""
Модуль мониторинга Telegram каналов с кастингами
"""

import asyncio
import logging
from typing import List, Dict, Any
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Message

from .message_processor import MessageProcessor
from .config.settings import Settings
from .config.channels import get_monitored_channels

class CastingMonitor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self.processor = MessageProcessor(settings)
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    async def start(self):
        """Запуск мониторинга"""
        self.logger.info("Инициализация Telegram клиента...")
        
        # Инициализация Telegram клиента
        self.client = TelegramClient(
            'sessions/monitor',
            self.settings.API_ID_TG,
            self.settings.API_HASH_TG
        )
        
        await self.client.start()
        self.logger.info("Telegram клиент запущен")
        
        # Получение списка каналов для мониторинга
        channels = get_monitored_channels()
        self.logger.info(f"Мониторинг {len(channels)} каналов")
        
        # Регистрация обработчиков событий
        @self.client.on(events.NewMessage(chats=channels))
        async def handle_new_message(event):
            await self.process_new_message(event.message)
        
        self.is_running = True
        self.logger.info("Мониторинг запущен, ожидание сообщений...")
        
        # Основной цикл
        while self.is_running:
            await asyncio.sleep(1)
    
    async def process_new_message(self, message: Message):
        """Обработка нового сообщения"""
        try:
            self.logger.info(f"Новое сообщение из канала {message.chat.username}")
            
            # Обработка сообщения
            await self.processor.process_message(message)
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке сообщения: {e}")
    
    async def stop(self):
        """Остановка мониторинга"""
        self.logger.info("Остановка мониторинга...")
        self.is_running = False
        
        if self.client:
            await self.client.disconnect()
            self.logger.info("Telegram клиент отключен")
        
        await self.processor.close()
        self.logger.info("Мониторинг остановлен")
```

### 3. `message_processor.py` - Обработчик сообщений

```python
"""
Модуль обработки сообщений о кастингах
"""

import asyncio
import logging
from typing import Dict, Any
from telethon.tl.types import Message

from .llm_client import LLMClient
from .clickhouse_client import ClickHouseClient
from .config.settings import Settings

class MessageProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
        self.clickhouse_client = ClickHouseClient(settings)
        self.logger = logging.getLogger(__name__)
    
    async def process_message(self, message: Message):
        """Полная обработка сообщения"""
        try:
            # 1. Подготовка данных сообщения
            message_data = self._prepare_message_data(message)
            
            # 2. Сохранение в ClickHouse
            await self._save_to_clickhouse(message_data)
            
            # 3. LLM анализ
            llm_result = await self._analyze_with_llm(message_data['text'])
            
            # 4. Обновление записи с LLM результатом
            await self._update_with_llm_result(message_data['message_id'], llm_result)
            
            self.logger.info(f"Сообщение {message_data['message_id']} обработано успешно")
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке сообщения: {e}")
            raise
    
    def _prepare_message_data(self, message: Message) -> Dict[str, Any]:
        """Подготовка данных сообщения для сохранения"""
        return {
            'message_id': message.id,
            'channel_id': message.chat.id,
            'channel_title': getattr(message.chat, 'title', ''),
            'channel_username': getattr(message.chat, 'username', ''),
            'date': message.date,
            'text': message.text or '',
            'views': getattr(message, 'views', 0),
            'forwards': getattr(message, 'forwards', 0),
            'replies': getattr(message, 'replies', 0),
            'media_type': self._get_media_type(message),
            'has_photo': 1 if message.photo else 0,
            'has_video': 1 if message.video else 0,
            'has_document': 1 if message.document else 0,
        }
    
    def _get_media_type(self, message: Message) -> str:
        """Определение типа медиа"""
        if message.photo:
            return 'photo'
        elif message.video:
            return 'video'
        elif message.document:
            return 'document'
        else:
            return 'text'
    
    async def _save_to_clickhouse(self, message_data: Dict[str, Any]):
        """Сохранение сообщения в ClickHouse"""
        await self.clickhouse_client.insert_castings_message(message_data)
        self.logger.debug(f"Сообщение {message_data['message_id']} сохранено в ClickHouse")
    
    async def _analyze_with_llm(self, text: str) -> Dict[str, Any]:
        """Анализ текста через LLM"""
        if not text.strip():
            return {'success': False, 'error': 'Пустой текст сообщения'}
        
        return await self.llm_client.process_message(text)
    
    async def _update_with_llm_result(self, message_id: int, llm_result: Dict[str, Any]):
        """Обновление записи с результатом LLM анализа"""
        await self.clickhouse_client.update_llm_analysis(message_id, llm_result)
        self.logger.debug(f"LLM результат для сообщения {message_id} сохранен")
    
    async def close(self):
        """Закрытие соединений"""
        await self.llm_client.close()
        await self.clickhouse_client.close()
```

### 4. `llm_client.py` - Клиент для LLM

```python
"""
Клиент для работы с LLM API
"""

import asyncio
import logging
from typing import Dict, Any
from src.llm.deepseek import process_telegram_message

class LLMClient:
    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
    
    async def process_message(self, text: str) -> Dict[str, Any]:
        """Обработка сообщения через LLM"""
        try:
            self.logger.debug(f"Отправка текста в LLM: {text[:100]}...")
            
            # Используем существующую функцию из deepseek.py
            result = process_telegram_message(text, self.settings.LLM_MODEL)
            
            self.logger.debug(f"LLM анализ завершен: success={result['success']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка LLM анализа: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_message': text
            }
    
    async def close(self):
        """Закрытие клиента"""
        pass
```

### 5. `clickhouse_client.py` - Клиент для ClickHouse

```python
"""
Клиент для работы с ClickHouse
"""

import asyncio
import logging
import json
from typing import Dict, Any
import requests

class ClickHouseClient:
    def __init__(self, settings):
        self.settings = settings
        self.base_url = f"http://{settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}"
        self.auth = (settings.CLICKHOUSE_USER, settings.CLICKHOUSE_PASSWORD)
        self.database = settings.CLICKHOUSE_DB
        self.logger = logging.getLogger(__name__)
    
    async def insert_castings_message(self, message_data: Dict[str, Any]):
        """Вставка сообщения о кастинге"""
        # Используем существующую логику из clickhouse_client.py
        from src.database.clickhouse_client import ClickHouseClient as BaseClient
        
        base_client = BaseClient()
        base_client.insert_castings_messages([message_data])
    
    async def update_llm_analysis(self, message_id: int, llm_result: Dict[str, Any]):
        """Обновление записи с результатом LLM анализа"""
        llm_json = json.dumps(llm_result, ensure_ascii=False)
        
        query = f"""
        ALTER TABLE {self.database}.castings_messages 
        UPDATE llm_analysis = '{llm_json}'
        WHERE message_id = {message_id}
        """
        
        response = requests.post(
            self.base_url,
            data=query,
            auth=self.auth,
            params={'database': self.database}
        )
        
        if response.status_code != 200:
            raise Exception(f"ClickHouse error: {response.text}")
        
        self.logger.debug(f"LLM анализ для сообщения {message_id} обновлен")
    
    async def close(self):
        """Закрытие клиента"""
        pass
```

## 🔧 Конфигурация

### `settings.py` - Настройки приложения

```python
"""
Настройки приложения
"""

import os
from typing import Optional

class Settings:
    # Telegram API
    API_ID_TG: int = int(os.getenv('API_ID_TG', '0'))
    API_HASH_TG: str = os.getenv('API_HASH_TG', '')
    PHONE_NUMBER: str = os.getenv('PHONE_NUMBER', '')
    
    # ClickHouse
    CLICKHOUSE_HOST: str = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
    CLICKHOUSE_PORT: int = int(os.getenv('CLICKHOUSE_PORT', '8123'))
    CLICKHOUSE_USER: str = os.getenv('CLICKHOUSE_USER', 'clickhouse_admin')
    CLICKHOUSE_PASSWORD: str = os.getenv('CLICKHOUSE_PASSWORD', '')
    CLICKHOUSE_DB: str = os.getenv('CLICKHOUSE_DB', 'telegram_analytics')
    
    # LLM
    DEEPSEEK_API_KEY: str = os.getenv('DEEPSEEK_API_KEY', '')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'deepseek-chat')
    
    # Мониторинг
    MONITOR_INTERVAL: int = int(os.getenv('MONITOR_INTERVAL', '5'))
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '10'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    def validate(self):
        """Проверка обязательных настроек"""
        required = [
            'API_ID_TG', 'API_HASH_TG', 'PHONE_NUMBER',
            'CLICKHOUSE_PASSWORD', 'DEEPSEEK_API_KEY'
        ]
        
        missing = []
        for field in required:
            if not getattr(self, field):
                missing.append(field)
        
        if missing:
            raise ValueError(f"Отсутствуют обязательные настройки: {', '.join(missing)}")
```

### `channels.py` - Конфигурация каналов

```python
"""
Конфигурация каналов для мониторинга
"""

from typing import List, Dict

def get_monitored_channels() -> List[str]:
    """Получение списка каналов для мониторинга"""
    # Импортируем из существующей конфигурации
    try:
        from config.castings_channels import CASTINGS_CHANNELS
        return [channel['username'] for channel in CASTINGS_CHANNELS if channel.get('enabled', True)]
    except ImportError:
        # Fallback конфигурация
        return [
            '@casting_channel_1',
            '@casting_channel_2',
            '@casting_channel_3'
        ]

def get_channel_config(username: str) -> Dict:
    """Получение конфигурации канала"""
    try:
        from config.castings_channels import CASTINGS_CHANNELS
        for channel in CASTINGS_CHANNELS:
            if channel['username'] == username:
                return channel
    except ImportError:
        pass
    
    # Fallback конфигурация
    return {
        'username': username,
        'title': username,
        'enabled': True,
        'priority': 1
    }
```

## 🚀 Скрипты запуска

### `entrypoint.sh` - Скрипт запуска

```bash
#!/bin/bash
set -e

echo "Запуск мониторинга кастингов..."

# Проверка переменных окружения
if [ -z "$API_ID_TG" ] || [ -z "$API_HASH_TG" ] || [ -z "$PHONE_NUMBER" ]; then
    echo "Ошибка: Не установлены переменные Telegram API"
    exit 1
fi

if [ -z "$CLICKHOUSE_PASSWORD" ]; then
    echo "Ошибка: Не установлен пароль ClickHouse"
    exit 1
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "Ошибка: Не установлен API ключ DeepSeek"
    exit 1
fi

# Ожидание готовности ClickHouse
echo "Ожидание готовности ClickHouse..."
until curl -s "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/ping" > /dev/null; do
    echo "ClickHouse не готов, ожидание..."
    sleep 2
done

echo "ClickHouse готов"

# Запуск приложения
exec "$@"
```

### `healthcheck.sh` - Проверка здоровья

```bash
#!/bin/bash

# Проверка доступности ClickHouse
if ! curl -s "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/ping" > /dev/null; then
    echo "ClickHouse недоступен"
    exit 1
fi

# Проверка процесса Python
if ! pgrep -f "python.*main.py" > /dev/null; then
    echo "Процесс мониторинга не запущен"
    exit 1
fi

echo "Сервис работает нормально"
exit 0
```

## 📊 Мониторинг и логирование

### Структура логов

```
logs/
├── casting_monitor.log      # Основные логи приложения
├── telegram_client.log      # Логи Telegram клиента
├── llm_requests.log         # Логи LLM запросов
└── clickhouse_operations.log # Логи операций с БД
```

### Метрики

Контейнер собирает следующие метрики:
- Количество обработанных сообщений
- Время обработки LLM
- Стоимость LLM запросов
- Количество ошибок
- Статус подключений

### Алерты

Настроены алерты на:
- Остановку контейнера
- Ошибки подключения к Telegram
- Ошибки LLM API
- Проблемы с ClickHouse
- Превышение лимитов API

## 🔒 Безопасность

### Изоляция сети
- Контейнер работает в изолированной сети
- Доступ к ClickHouse только из внутренней сети
- Нет внешних портов

### Управление секретами
- Все секреты через переменные окружения
- Отдельные .env файлы для разных окружений
- Ротация ключей по расписанию

### Логирование безопасности
- Логирование всех операций
- Мониторинг подозрительной активности
- Аудит доступа к данным

## 📈 Масштабирование

### Горизонтальное масштабирование
- Возможность запуска нескольких экземпляров
- Распределение каналов между экземплярами
- Балансировка нагрузки

### Вертикальное масштабирование
- Настройка лимитов ресурсов
- Мониторинг использования CPU/памяти
- Автоматическое масштабирование

### Оптимизация производительности
- Батчинг запросов к LLM
- Кэширование результатов
- Асинхронная обработка
