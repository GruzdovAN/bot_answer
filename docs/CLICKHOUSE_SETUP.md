# Настройка ClickHouse

## Обзор

ClickHouse добавлен в docker-compose.yml как аналитическая база данных для хранения метрик и аналитики Telegram бота.

## Конфигурация

### Переменные окружения

Добавьте следующие переменные в ваш `.env` файл:

```bash
# ClickHouse настройки
CLICKHOUSE_DB=telegram_bot_analytics
CLICKHOUSE_USER=clickhouse_admin
CLICKHOUSE_PASSWORD=your_clickhouse_password_here

# ClickHouse внешний доступ
CLICKHOUSE_HOST=0.0.0.0
CLICKHOUSE_PORT=8123
CLICKHOUSE_NATIVE_PORT=9000
```

### Порты

- **8123** - HTTP интерфейс (для веб-запросов и REST API)
- **9000** - Native интерфейс (для клиентских библиотек)

## Запуск

### Запуск только ClickHouse
```bash
docker-compose up -d clickhouse
```

### Запуск всех сервисов
```bash
docker-compose up -d
```

## Подключение

### HTTP интерфейс
```bash
# Проверка доступности
curl http://localhost:8123/ping

# Выполнение запроса
curl "http://clickhouse_admin:password@localhost:8123/?query=SELECT%20version()"
```

### Python клиент
```python
from clickhouse_driver import Client

client = Client(
    host='localhost',
    port=9000,
    user='clickhouse_admin',
    password='your_password',
    database='telegram_bot_analytics'
)

result = client.execute('SELECT version()')
print(result)
```

## Volumes

- `clickhouse_data` - данные ClickHouse
- `clickhouse_logs` - логи сервера
- `clickhouse_config` - конфигурационные файлы

## Мониторинг

### Проверка статуса
```bash
docker ps | grep clickhouse
```

### Просмотр логов
```bash
docker logs telegram_bot_clickhouse
```

### Health check
ClickHouse автоматически проверяется каждые 10 секунд через HTTP ping.

## Безопасность

- ClickHouse настроен с пользователем `clickhouse_admin`
- Пароль задается через переменную окружения `CLICKHOUSE_PASSWORD`
- Доступ по внешнему IP настроен аналогично PostgreSQL
- Рекомендуется использовать сильные пароли в продакшене

## Примеры использования

### Создание таблицы для аналитики
```sql
CREATE TABLE telegram_events (
    event_id UUID DEFAULT generateUUIDv4(),
    user_id UInt64,
    event_type String,
    timestamp DateTime DEFAULT now(),
    metadata String
) ENGINE = MergeTree()
ORDER BY (timestamp, user_id);
```

### Вставка данных
```sql
INSERT INTO telegram_events (user_id, event_type, metadata) 
VALUES (12345, 'message_sent', '{"chat_id": 67890}');
```
