# Документация по процессу обработки сообщений о кастингах

## 📋 Обзор системы

Система предназначена для автоматического мониторинга Telegram каналов с кастингами, извлечения структурированной информации из сообщений с помощью LLM и сохранения данных в ClickHouse.

## 🏗️ Архитектура системы

### Компоненты системы

1. **Docker контейнер-монитор** - слушает новые сообщения в каналах
2. **LLM обработчик** - извлекает структурированную информацию из текста
3. **ClickHouse база данных** - хранит сообщения и результаты LLM анализа
4. **Telegram клиент** - подключение к Telegram API

### Схема данных

```
Telegram Channel → Docker Container → LLM Processing → ClickHouse Storage
```

## 📊 Схема базы данных

### Таблица `castings_messages` (существующая)

Основная таблица для хранения сообщений о кастингах:

```sql
CREATE TABLE castings_messages (
    message_id UInt64,
    channel_id UInt64,
    channel_title String,
    channel_username String,
    date DateTime,
    text String,
    views UInt32,
    forwards UInt32,
    replies UInt32,
    media_type String,
    has_photo UInt8,
    has_video UInt8,
    has_document UInt8,
    -- Парсированные поля
    casting_type String,
    age_range String,
    location String,
    contact_info String,
    deadline String,
    payment String,
    project_name String,
    parsed_at DateTime DEFAULT now(),
    -- НОВОЕ ПОЛЕ: LLM анализ
    llm_analysis JSON DEFAULT '{}'
) ENGINE = MergeTree()
ORDER BY (channel_id, date)
PARTITION BY toYYYYMM(date)
```

### Новое поле `llm_analysis`

Структура JSON поля для хранения результатов LLM анализа:

```json
{
  "success": true,
  "message_type": "casting_analysis",
  "model_used": "deepseek-chat",
  "timestamp": "2025-09-17T23:20:30.018044",
  "extracted_data": {
    "message_type": "кастинг",
    "casting_type": "реклама",
    "actors": [
      {
        "gender": "мужчина",
        "age_range": "30-40 лет",
        "role_features": "спортивное телосложение"
      },
      {
        "gender": "женщина",
        "age_range": "25-35 лет",
        "role_features": "роль менеджера"
      }
    ],
    "has_target_woman": false
  },
  "cost_info": {
    "input_tokens": 534,
    "output_tokens": 100,
    "total_tokens": 634,
    "cache_hit": false,
    "input_cost_usd": 0.000299,
    "output_cost_usd": 0.000168,
    "total_cost_usd": 0.000467
  },
  "error": null
}
```

## 🔄 Процесс обработки сообщений

### 1. Мониторинг каналов

**Компонент:** Docker контейнер с Telegram клиентом

**Процесс:**
1. Подключение к Telegram API через существующую сессию
2. Подписка на обновления каналов из папки @castings
3. Получение новых сообщений в реальном времени
4. Фильтрация сообщений (только текстовые, от кастинговых каналов)

**Настройки:**
- Список каналов: из конфигурации `config/castings_channels.py`
- Типы сообщений: text, photo с подписью, document с описанием
- Исключения: рекламные сообщения, пересылки

### 2. Обработка LLM

**Компонент:** Модуль `src/llm/deepseek.py`

**Процесс:**
1. Получение текста сообщения
2. Отправка запроса к DeepSeek API
3. Извлечение структурированных данных о кастинге
4. Формирование JSON ответа

**Извлекаемые данные:**
- Тип сообщения (кастинг/реклама/прочее)
- Тип кастинга (кино/сериал/реклама/театр)
- Список актеров с характеристиками
- Наличие целевой аудитории (женщины 30-45 лет)

### 3. Сохранение в ClickHouse

**Компонент:** Модуль `src/database/clickhouse_client.py`

**Процесс:**
1. Подготовка данных сообщения
2. Обработка LLM результата
3. Вставка в таблицу `castings_messages`
4. Обновление поля `llm_analysis`

## 🐳 Docker контейнер

### Структура контейнера

```
casting-monitor/
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── monitor.py          # Основной модуль мониторинга
│   ├── message_processor.py # Обработчик сообщений
│   └── config/
│       └── settings.py     # Настройки контейнера
├── requirements.txt
└── .env                    # Переменные окружения
```

### Основные компоненты

#### 1. `monitor.py` - Основной модуль

```python
class CastingMonitor:
    def __init__(self):
        self.telegram_client = None
        self.llm_processor = None
        self.clickhouse_client = None
        
    async def start_monitoring(self):
        """Запуск мониторинга каналов"""
        
    async def process_new_message(self, message):
        """Обработка нового сообщения"""
        
    async def stop_monitoring(self):
        """Остановка мониторинга"""
```

#### 2. `message_processor.py` - Обработчик сообщений

```python
class MessageProcessor:
    def __init__(self):
        self.llm_client = None
        self.clickhouse_client = None
        
    async def process_message(self, message):
        """Полная обработка сообщения"""
        # 1. Сохранение в ClickHouse
        # 2. LLM анализ
        # 3. Обновление записи с LLM результатом
        
    async def save_to_clickhouse(self, message_data):
        """Сохранение в ClickHouse"""
        
    async def analyze_with_llm(self, text):
        """Анализ текста через LLM"""
```

### Переменные окружения

```bash
# Telegram API
API_ID_TG=your_api_id
API_HASH_TG=your_api_hash
PHONE_NUMBER=your_phone

# ClickHouse
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=clickhouse_admin
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DB=telegram_analytics

# LLM API
DEEPSEEK_API_KEY=your_deepseek_key

# Настройки мониторинга
MONITOR_INTERVAL=5  # секунд между проверками
BATCH_SIZE=10       # размер пакета для обработки
MAX_RETRIES=3       # количество повторов при ошибке
```

## 📈 Мониторинг и логирование

### Логирование

**Уровни логов:**
- `INFO` - нормальная работа (новые сообщения, успешная обработка)
- `WARNING` - предупреждения (пропуск сообщений, временные ошибки)
- `ERROR` - ошибки (сбои API, проблемы с БД)
- `DEBUG` - детальная отладочная информация

**Структура логов:**
```
2025-09-17 23:20:30 - casting_monitor - INFO - Новое сообщение из канала @casting_channel
2025-09-17 23:20:31 - llm_processor - INFO - LLM анализ завершен успешно
2025-09-17 23:20:32 - clickhouse_client - INFO - Сообщение сохранено в БД
```

### Метрики

**Собираемые метрики:**
- Количество обработанных сообщений
- Время обработки LLM
- Стоимость LLM запросов
- Количество ошибок
- Статус подключений

**Хранение метрик:**
- Логи в stdout (для Docker)
- Метрики в ClickHouse (таблица `monitoring_metrics`)

## 🔧 Конфигурация

### Список каналов для мониторинга

Файл: `config/castings_channels.py`

```python
CASTINGS_CHANNELS = [
    {
        "username": "@casting_channel_1",
        "title": "Кастинги Москвы",
        "enabled": True,
        "priority": 1
    },
    {
        "username": "@casting_channel_2", 
        "title": "Актерские кастинги",
        "enabled": True,
        "priority": 2
    }
]
```

### Настройки LLM

```python
LLM_CONFIG = {
    "model": "deepseek-chat",
    "max_tokens": 1000,
    "temperature": 0.1,
    "timeout": 30,
    "retry_attempts": 3
}
```

## 🚀 Развертывание

### 1. Подготовка окружения

```bash
# Клонирование репозитория
git clone <repository>
cd bot_answer

# Создание .env файла
cp env.example .env
# Заполнение переменных окружения
```

### 2. Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск только монитора кастингов
docker-compose up -d casting-monitor

# Просмотр логов
docker-compose logs -f casting-monitor
```

### 3. Мониторинг работы

```bash
# Статус контейнеров
docker-compose ps

# Логи монитора
docker-compose logs casting-monitor

# Подключение к ClickHouse
docker-compose exec clickhouse clickhouse-client
```

## 📊 Аналитика и отчеты

### Полезные запросы

#### Статистика по каналам за последние 7 дней
```sql
SELECT 
    channel_username,
    COUNT(*) as total_messages,
    COUNT(CASE WHEN JSONExtractString(llm_analysis, 'success') = 'true' THEN 1 END) as successful_llm,
    AVG(JSONExtractFloat(llm_analysis, 'cost_info.total_cost_usd')) as avg_cost
FROM castings_messages 
WHERE date >= now() - INTERVAL 7 DAY
GROUP BY channel_username
ORDER BY total_messages DESC;
```

#### Топ типов кастингов
```sql
SELECT 
    JSONExtractString(llm_analysis, 'extracted_data.casting_type') as casting_type,
    COUNT(*) as count
FROM castings_messages 
WHERE JSONExtractString(llm_analysis, 'success') = 'true'
    AND date >= now() - INTERVAL 30 DAY
GROUP BY casting_type
ORDER BY count DESC;
```

#### Статистика по актерам
```sql
SELECT 
    JSONExtractString(actor, 'gender') as gender,
    JSONExtractString(actor, 'age_range') as age_range,
    COUNT(*) as count
FROM castings_messages 
ARRAY JOIN JSONExtractArrayRaw(llm_analysis, 'extracted_data.actors') as actor
WHERE JSONExtractString(llm_analysis, 'success') = 'true'
    AND date >= now() - INTERVAL 30 DAY
GROUP BY gender, age_range
ORDER BY count DESC;
```

## 🔒 Безопасность

### Защита API ключей
- Все ключи в переменных окружения
- Отдельные .env файлы для разных окружений
- Ротация ключей по расписанию

### Ограничения доступа
- ClickHouse доступ только из внутренней сети
- Telegram API через авторизованные сессии
- Логирование всех операций

### Резервное копирование
- Ежедневные бэкапы ClickHouse
- Сохранение конфигураций в Git
- Мониторинг доступности сервисов

## 🐛 Устранение неполадок

### Частые проблемы

1. **Ошибки подключения к Telegram**
   - Проверка сессий в папке `sessions/`
   - Обновление API ключей
   - Проверка лимитов API

2. **Ошибки LLM API**
   - Проверка API ключа DeepSeek
   - Мониторинг лимитов запросов
   - Проверка баланса аккаунта

3. **Проблемы с ClickHouse**
   - Проверка подключения к БД
   - Мониторинг места на диске
   - Проверка логов ClickHouse

### Команды диагностики

```bash
# Проверка статуса сервисов
docker-compose ps

# Логи всех сервисов
docker-compose logs

# Проверка подключения к ClickHouse
docker-compose exec clickhouse clickhouse-client --query "SELECT 1"

# Проверка последних сообщений
docker-compose exec clickhouse clickhouse-client --query "SELECT * FROM castings_messages ORDER BY date DESC LIMIT 10"
```

## 📝 Планы развития

### Краткосрочные задачи
- [ ] Реализация Docker контейнера
- [ ] Добавление поля `llm_analysis` в таблицу
- [ ] Настройка мониторинга и алертов
- [ ] Создание дашборда для аналитики

### Долгосрочные задачи
- [ ] Поддержка других LLM провайдеров
- [ ] Автоматическая категоризация каналов
- [ ] Интеграция с внешними API
- [ ] Машинное обучение для улучшения парсинга
