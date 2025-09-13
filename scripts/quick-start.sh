#!/bin/bash

# 🚀 Быстрый запуск Telegram бота в Docker

echo "🤖 Telegram Bot - Быстрый запуск"
echo "=================================="

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "📋 Создайте .env файл на основе config/env.example:"
    echo "   cp config/env.example .env"
    echo "   nano .env"
    exit 1
fi

# Проверка наличия сессий
if [ ! -d "sessions" ] || [ -z "$(ls -A sessions/*.session 2>/dev/null)" ]; then
    echo "⚠️  Сессии Telegram не найдены!"
    echo "📱 Выполните первоначальную авторизацию:"
    echo "   1. ./run.sh (локально)"
    echo "   2. Введите код авторизации"
    echo "   3. cp *.session sessions/"
    echo "   4. Запустите этот скрипт снова"
    exit 1
fi

# Проверка Docker
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не установлен!"
    echo "📋 Установите Docker: см. DOCKER_SETUP.md"
    exit 1
fi

echo "✅ Проверки пройдены"
echo "🐳 Запуск Docker контейнеров..."

# Запуск сервисов
sudo docker-compose up -d

echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo "📊 Статус сервисов:"
sudo docker-compose ps

echo ""
echo "🎉 Бот запущен!"
echo ""
echo "📋 Полезные команды:"
echo "   Логи бота:     ./scripts/docker-logs.sh"
echo "   Остановка:     ./scripts/docker-stop.sh"
echo "   Внешний IP:    ./scripts/get_external_ip.sh"
echo "   Статус:        sudo docker-compose ps"
echo ""
echo "📖 Документация:"
echo "   - docs/SESSION_MANAGEMENT.md - управление сессиями"
echo "   - docs/EXTERNAL_ACCESS.md - доступ к базе данных"
echo "   - docs/ENV_SETUP.md - настройка переменных"
echo ""
echo "🔍 Для просмотра логов в реальном времени:"
echo "   sudo docker-compose logs -f telegram_bot"
