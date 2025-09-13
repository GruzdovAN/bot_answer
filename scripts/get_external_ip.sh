#!/bin/bash

# Скрипт для получения внешнего IP адреса сервера

echo "🌐 Получение внешнего IP адреса..."

# Попробуем несколько сервисов
EXTERNAL_IP=""

# Метод 1: ifconfig.me
if command -v curl &> /dev/null; then
    EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null)
fi

# Метод 2: ipinfo.io (если первый не сработал)
if [ -z "$EXTERNAL_IP" ] && command -v curl &> /dev/null; then
    EXTERNAL_IP=$(curl -s ipinfo.io/ip 2>/dev/null)
fi

# Метод 3: icanhazip.com (если предыдущие не сработали)
if [ -z "$EXTERNAL_IP" ] && command -v curl &> /dev/null; then
    EXTERNAL_IP=$(curl -s icanhazip.com 2>/dev/null)
fi

# Метод 4: wget (если curl недоступен)
if [ -z "$EXTERNAL_IP" ] && command -v wget &> /dev/null; then
    EXTERNAL_IP=$(wget -qO- ifconfig.me 2>/dev/null)
fi

# Загружаем переменные окружения
if [ -f .env ]; then
    source .env
fi

if [ -n "$EXTERNAL_IP" ]; then
    echo "✅ Внешний IP: $EXTERNAL_IP"
    echo ""
    echo "🔗 Доступ к сервисам:"
    echo "🗄️ pgAdmin: http://$EXTERNAL_IP:8080"
    echo "🗃️ PostgreSQL: $EXTERNAL_IP:5432"
    echo ""
    echo "📋 Учетные данные:"
    echo "PostgreSQL:"
    echo "  Пользователь: ${DB_USER:-telegram_admin}"
    echo "  Пароль: ${DB_PASSWORD}"
    echo "  База данных: ${DB_NAME:-telegram_bot}"
    echo ""
    echo "pgAdmin:"
    echo "  Email: ${PGADMIN_EMAIL:-admin@telegram-bot.com}"
    echo "  Пароль: ${PGADMIN_PASSWORD}"
    echo ""
    echo "📖 Подробная документация: EXTERNAL_ACCESS.md"
else
    echo "❌ Не удалось получить внешний IP"
    echo "Проверьте подключение к интернету"
fi
