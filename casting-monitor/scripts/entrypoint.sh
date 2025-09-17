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

# Создание директории для логов если не существует
mkdir -p /app/logs

# Запуск приложения
exec "$@"
