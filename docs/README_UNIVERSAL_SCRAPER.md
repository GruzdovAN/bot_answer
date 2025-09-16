# Универсальный Telegram Scraper

Простая система для сбора сообщений из разных Telegram каналов с сохранением в ClickHouse.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements_universal.txt
```

### 2. Настройка

Убедитесь, что в `.env` файле указаны правильные настройки:

```bash
# Telegram API
API_ID_TG=your_api_id
API_HASH_TG=your_api_hash
PHONE_NUMBER=your_phone_number

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=clickhouse_admin
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DB=telegram_analytics
```

### 3. Запуск

```bash
# Тестирование компонентов
python test_components.py

# Запуск скрапера
python run_scraper.py

# Просмотр аналитики
python analytics.py
```

## 📁 Структура проекта

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
```

## ⚙️ Конфигурация

### Каналы (`config/channels.py`)

```python
CHANNELS = {
    "datascience_jobs": {
        "username": "@datasciencejobs",
        "enabled": True,
        "parser_type": "job_parser",
        "days_back": 30,
        "batch_size": 1000
    },
    # Добавьте свои каналы...
}
```

### Парсеры (`config/parsers.py`)

```python
PARSERS = {
    "job_parser": {
        "extract_hashtags": True,
        "extract_mentions": True,
        "extract_links": True,
        "extract_technologies": True,
        "technologies": ["python", "javascript", "java", ...]
    },
    # Добавьте свои парсеры...
}
```

## 📊 Аналитика

### Базовые запросы

```sql
-- Статистика по каналам
SELECT 
    channel_username,
    count() as total_messages,
    sum(views) as total_views
FROM telegram_analytics.telegram_messages 
GROUP BY channel_username;

-- Топ хештеги
SELECT 
    hashtag,
    count() as mentions
FROM (
    SELECT arrayJoin(hashtags) as hashtag
    FROM telegram_analytics.telegram_messages 
)
GROUP BY hashtag
ORDER BY mentions DESC
LIMIT 10;
```

### Готовые скрипты

- `analytics.py` - простая аналитика
- `test_components.py` - тестирование компонентов

## 🔧 Добавление нового канала

1. **Добавьте в `config/channels.py`:**
```python
"new_channel": {
    "username": "@new_channel",
    "enabled": True,
    "parser_type": "job_parser",
    "days_back": 30,
    "batch_size": 500
}
```

2. **Запустите скрапер:**
```bash
python run_scraper.py
```

## 🐛 Устранение проблем

### Ошибка подключения к ClickHouse
```bash
# Проверьте статус ClickHouse
docker ps | grep clickhouse

# Проверьте подключение
curl http://localhost:8123/ping
```

### Ошибка Telegram API
```bash
# Проверьте переменные окружения
python -c "import os; print('API_ID:', os.getenv('API_ID_TG'))"
```

### Ошибка парсинга
```bash
# Запустите тест компонентов
python test_components.py
```

## 📈 Мониторинг

### Проверка данных в ClickHouse

```bash
# Количество сообщений
curl "http://clickhouse_admin:password@localhost:8123/?query=SELECT%20count()%20FROM%20telegram_analytics.telegram_messages"

# Последние сообщения
curl "http://clickhouse_admin:password@localhost:8123/?query=SELECT%20*%20FROM%20telegram_analytics.telegram_messages%20ORDER%20BY%20date%20DESC%20LIMIT%205"
```

## 🎯 Возможности

- ✅ Поддержка множественных каналов
- ✅ Простые парсеры для извлечения сущностей
- ✅ Автоматическое сохранение в ClickHouse
- ✅ Готовые аналитические запросы
- ✅ Простая конфигурация через Python файлы
- ✅ Тестирование компонентов

## 📝 Логи

Логи сохраняются в консоль с уровнем INFO. Для изменения уровня логирования отредактируйте `run_scraper.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # Для подробных логов
```

## 🔒 Безопасность

- Все секреты хранятся в `.env` файле
- Файл `.env` добавлен в `.gitignore`
- Используйте сильные пароли для ClickHouse

## 📞 Поддержка

При возникновении проблем:

1. Запустите `python test_components.py`
2. Проверьте логи в консоли
3. Убедитесь, что все переменные окружения заданы
4. Проверьте доступность ClickHouse и Telegram API
