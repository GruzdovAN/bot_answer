#!/bin/bash

# Скрипт для остановки Telegram бота в Docker

echo "🛑 Остановка Telegram бота..."

# Останавливаем контейнеры
sudo docker-compose down

echo "✅ Бот остановлен!"
echo "💾 Данные базы данных сохранены в volume postgres_data"
