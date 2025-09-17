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
