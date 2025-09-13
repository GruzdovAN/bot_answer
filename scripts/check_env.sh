#!/bin/bash

# Скрипт для проверки переменных окружения

echo "🔍 Проверка переменных окружения..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Создайте файл .env из примера:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Загружаем переменные окружения
source .env

echo "✅ Файл .env найден"
echo ""

# Проверяем обязательные переменные
echo "📋 Проверка обязательных переменных:"

# Telegram API
if [ -z "$API_ID_TG" ]; then
    echo "❌ API_ID_TG не задан"
else
    echo "✅ API_ID_TG: $API_ID_TG"
fi

if [ -z "$API_HASH_TG" ]; then
    echo "❌ API_HASH_TG не задан"
else
    echo "✅ API_HASH_TG: ${API_HASH_TG:0:10}..."
fi

if [ -z "$PHONE_NUMBER" ]; then
    echo "❌ PHONE_NUMBER не задан"
else
    echo "✅ PHONE_NUMBER: $PHONE_NUMBER"
fi

if [ -z "$CHANNEL_USERNAME" ]; then
    echo "❌ CHANNEL_USERNAME не задан"
else
    echo "✅ CHANNEL_USERNAME: $CHANNEL_USERNAME"
fi

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN не задан"
else
    echo "✅ BOT_TOKEN: ${BOT_TOKEN:0:10}..."
fi

echo ""

# База данных
echo "🗃️ Проверка настроек базы данных:"

if [ -z "$DB_HOST" ]; then
    echo "❌ DB_HOST не задан"
else
    echo "✅ DB_HOST: $DB_HOST"
fi

if [ -z "$DB_PORT" ]; then
    echo "❌ DB_PORT не задан"
else
    echo "✅ DB_PORT: $DB_PORT"
fi

if [ -z "$DB_NAME" ]; then
    echo "❌ DB_NAME не задан"
else
    echo "✅ DB_NAME: $DB_NAME"
fi

if [ -z "$DB_USER" ]; then
    echo "❌ DB_USER не задан"
else
    echo "✅ DB_USER: $DB_USER"
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD не задан"
else
    echo "✅ DB_PASSWORD: ${DB_PASSWORD:0:10}..."
fi

echo ""

# pgAdmin
echo "🗄️ Проверка настроек pgAdmin:"

if [ -z "$PGADMIN_EMAIL" ]; then
    echo "❌ PGADMIN_EMAIL не задан"
else
    echo "✅ PGADMIN_EMAIL: $PGADMIN_EMAIL"
fi

if [ -z "$PGADMIN_PASSWORD" ]; then
    echo "❌ PGADMIN_PASSWORD не задан"
else
    echo "✅ PGADMIN_PASSWORD: ${PGADMIN_PASSWORD:0:10}..."
fi

echo ""

# Проверяем, все ли переменные заданы
MISSING_VARS=()

[ -z "$API_ID_TG" ] && MISSING_VARS+=("API_ID_TG")
[ -z "$API_HASH_TG" ] && MISSING_VARS+=("API_HASH_TG")
[ -z "$PHONE_NUMBER" ] && MISSING_VARS+=("PHONE_NUMBER")
[ -z "$CHANNEL_USERNAME" ] && MISSING_VARS+=("CHANNEL_USERNAME")
[ -z "$BOT_TOKEN" ] && MISSING_VARS+=("BOT_TOKEN")
[ -z "$DB_PASSWORD" ] && MISSING_VARS+=("DB_PASSWORD")
[ -z "$PGADMIN_PASSWORD" ] && MISSING_VARS+=("PGADMIN_PASSWORD")

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "🎉 Все обязательные переменные настроены!"
    echo ""
    echo "🚀 Можно запускать бота:"
    echo "   ./docker-start.sh"
else
    echo "❌ Отсутствуют обязательные переменные:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "📝 Отредактируйте файл .env:"
    echo "   nano .env"
    exit 1
fi
