# Docker контейнер для мониторинга кастингов

## Описание

Docker контейнер для автоматического мониторинга Telegram каналов с кастингами, обработки сообщений через LLM и сохранения результатов в ClickHouse.

## Функциональность

- 🔍 Мониторинг новых сообщений в каналах о кастингах
- 🤖 Обработка сообщений через DeepSeek LLM
- 💾 Сохранение сообщений и LLM результатов в ClickHouse
- 📊 Логирование всех операций
- 🔄 Автоматический перезапуск при сбоях

## Требования

- Docker и Docker Compose
- Существующий .env файл с настройками
- Telegram сессии в папке `../sessions/`
- Конфигурация каналов в `../config/`

## Установка

1. **Подготовка базы данных:**
   ```bash
   # Выполните SQL скрипт для добавления поля llm_analysis
   clickhouse-client < init_database.sql
   ```

2. **Запуск контейнера:**
   ```bash
   docker-compose up -d
   ```

3. **Просмотр логов:**
   ```bash
   docker-compose logs -f casting-monitor
   ```

## Переменные окружения

Все переменные берутся из существующего `.env` файла:

### Обязательные:
- `API_ID_TG` - ID Telegram API
- `API_HASH_TG` - Hash Telegram API  
- `PHONE_NUMBER` - Номер телефона для Telegram
- `CLICKHOUSE_PASSWORD` - Пароль ClickHouse
- `DEEPSEEK_API_KEY` - API ключ DeepSeek

### Опциональные:
- `CLICKHOUSE_HOST` - Хост ClickHouse (по умолчанию: clickhouse)
- `CLICKHOUSE_PORT` - Порт ClickHouse (по умолчанию: 8123)
- `CLICKHOUSE_USER` - Пользователь ClickHouse (по умолчанию: clickhouse_admin)
- `CLICKHOUSE_DB` - База данных (по умолчанию: telegram_analytics)
- `MONITOR_INTERVAL` - Интервал мониторинга в секундах (по умолчанию: 5)
- `BATCH_SIZE` - Размер пакета для обработки (по умолчанию: 10)
- `LOG_LEVEL` - Уровень логирования (по умолчанию: INFO)

## Структура проекта

```
casting-monitor/
├── Dockerfile                 # Конфигурация контейнера
├── docker-compose.yml         # Оркестрация сервисов
├── requirements.txt           # Python зависимости
├── init_database.sql          # SQL для инициализации БД
├── src/
│   ├── main.py               # Точка входа
│   ├── monitor.py            # Основной модуль мониторинга
│   ├── message_processor.py  # Обработчик сообщений
│   ├── llm_client.py         # Клиент для LLM
│   ├── clickhouse_client.py  # Клиент для ClickHouse
│   └── config/
│       ├── settings.py       # Настройки
│       └── channels.py       # Конфигурация каналов
├── scripts/
│   ├── entrypoint.sh         # Скрипт запуска
│   └── healthcheck.sh        # Проверка здоровья
└── logs/                     # Логи приложения
```

## Мониторинг

### Логи
- Основные логи: `logs/casting_monitor.log`
- Логи Docker: `docker-compose logs casting-monitor`

### Health Check
Контейнер автоматически проверяет:
- Доступность ClickHouse
- Работу основного процесса

### Метрики
- Количество обработанных сообщений
- Время обработки LLM
- Стоимость LLM запросов
- Количество ошибок

## Управление

### Запуск
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart casting-monitor
```

### Просмотр логов
```bash
docker-compose logs -f casting-monitor
```

### Подключение к контейнеру
```bash
docker-compose exec casting-monitor bash
```

## Устранение неполадок

### Контейнер не запускается
1. Проверьте переменные окружения в .env файле
2. Убедитесь, что ClickHouse доступен
3. Проверьте логи: `docker-compose logs casting-monitor`

### Ошибки Telegram API
1. Проверьте API ключи в .env файле
2. Убедитесь, что сессии в папке `../sessions/` валидны
3. Проверьте лимиты API

### Ошибки LLM
1. Проверьте API ключ DeepSeek
2. Убедитесь в наличии баланса на аккаунте
3. Проверьте лимиты запросов

### Ошибки ClickHouse
1. Проверьте подключение к БД
2. Убедитесь, что поле `llm_analysis` добавлено в таблицу
3. Проверьте права доступа

## Разработка

### Сборка образа
```bash
docker-compose build casting-monitor
```

### Запуск в режиме разработки
```bash
docker-compose up casting-monitor
```

### Тестирование
```bash
# Тест подключения к ClickHouse
docker-compose exec casting-monitor curl http://clickhouse:8123/ping

# Тест LLM API
docker-compose exec casting-monitor python -c "from src.llm_client import LLMClient; print('LLM OK')"
```

## Лицензия

Проект использует те же лицензии, что и основной проект.
