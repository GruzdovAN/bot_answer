#!/bin/bash

# Скрипт для просмотра логов Docker контейнеров

echo "📋 Логи Telegram бота:"
echo ""

# Показываем логи бота
sudo docker-compose logs -f telegram_bot
