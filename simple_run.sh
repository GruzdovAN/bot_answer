#!/bin/bash

# Скрипт для запуска Telegram бота
echo "🚀 Запуск Telegram бота..."

# Активируем виртуальное окружение
source venv/bin/activate

# Создаем директорию для логов если её нет
mkdir -p logs

echo "📝 Логи будут сохранены в директории logs/"
echo "   - Основные логи: logs/telegram_bot.log"
echo "   - Логи ошибок: logs/telegram_bot_errors.log"

# Запускаем бота
python3 main.py
