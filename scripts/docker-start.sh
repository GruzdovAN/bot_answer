#!/bin/bash

# Скрипт для запуска Telegram бота в Docker

echo "🐳 Запуск Telegram бота в Docker..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Скопируйте config/env.example в .env и заполните переменные:"
    echo "   cp config/env.example .env"
    echo "   nano .env"
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Запускаем контейнеры
echo "🚀 Запуск контейнеров..."
sudo docker-compose up -d postgres

# Ждем готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
sleep 10

# Инициализируем базу данных
echo "🗄️ Инициализация базы данных..."
sudo docker-compose run --rm telegram_bot python config/init_database.py

# Запускаем бота
echo "🤖 Запуск Telegram бота..."
sudo docker-compose up telegram_bot

echo "✅ Бот запущен!"
echo ""
# Загружаем переменные окружения
if [ -f .env ]; then
    source .env
fi

# Получаем внешний IP
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")

echo "🔗 Доступ к сервисам:"
echo "📝 Логи: docker-compose logs -f telegram_bot"
echo "🗄️ pgAdmin: http://$EXTERNAL_IP:8080"
echo "   Email: ${PGADMIN_EMAIL:-admin@telegram-bot.com}"
echo "   Пароль: ${PGADMIN_PASSWORD}"
echo ""
echo "🗃️ PostgreSQL:"
echo "   Хост: $EXTERNAL_IP"
echo "   Порт: 5432"
echo "   База: ${DB_NAME:-telegram_bot}"
echo "   Пользователь: ${DB_USER:-telegram_admin}"
echo "   Пароль: ${DB_PASSWORD}"
echo ""
echo "📖 Подробная документация: EXTERNAL_ACCESS.md"
