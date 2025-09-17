# Быстрый старт Docker контейнера для мониторинга кастингов

## 🚀 Запуск

### 1. Подготовка базы данных
```bash
# Добавьте поле llm_analysis в таблицу castings_messages
cd /home/agruzdov/projects/bot_answer/casting-monitor
clickhouse-client < init_database.sql
```

### 2. Запуск контейнера
```bash
# Запуск всех сервисов
docker-compose up -d

# Или только мониторинг кастингов
docker-compose up -d casting-monitor
```

### 3. Просмотр логов
```bash
# Логи мониторинга
docker-compose logs -f casting-monitor

# Логи ClickHouse
docker-compose logs -f clickhouse
```

## 📊 Проверка работы

### Статус контейнеров
```bash
docker-compose ps
```

### Health check
```bash
# Проверка здоровья контейнера
docker-compose exec casting-monitor ./scripts/healthcheck.sh
```

### Подключение к ClickHouse
```bash
# Проверка данных
docker-compose exec clickhouse clickhouse-client --query "SELECT COUNT(*) FROM telegram_analytics.castings_messages"

# Проверка LLM анализа
docker-compose exec clickhouse clickhouse-client --query "SELECT message_id, llm_analysis FROM telegram_analytics.castings_messages WHERE llm_analysis != '{}' LIMIT 5"
```

## 🔧 Управление

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart casting-monitor
```

### Обновление
```bash
docker-compose build casting-monitor
docker-compose up -d casting-monitor
```

## 📝 Логи

Логи сохраняются в:
- `logs/casting_monitor.log` - основные логи приложения
- `docker-compose logs` - логи Docker контейнера

## ⚠️ Требования

- Существующий `.env` файл с настройками
- Telegram сессии в папке `../sessions/`
- Конфигурация каналов в `../config/castings_channels.py`

## 🐛 Устранение неполадок

### Контейнер не запускается
```bash
# Проверьте переменные окружения
docker-compose config

# Проверьте логи
docker-compose logs casting-monitor
```

### Ошибки ClickHouse
```bash
# Проверьте подключение
docker-compose exec casting-monitor curl http://clickhouse:8123/ping

# Проверьте таблицу
docker-compose exec clickhouse clickhouse-client --query "DESCRIBE telegram_analytics.castings_messages"
```

### Ошибки Telegram
```bash
# Проверьте сессии
ls -la ../sessions/

# Проверьте API ключи в .env файле
grep -E "API_ID_TG|API_HASH_TG|PHONE_NUMBER" ../.env
```
