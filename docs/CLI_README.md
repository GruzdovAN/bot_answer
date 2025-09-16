# CLI для управления Telegram Bot проектом

Удобный интерфейс командной строки для управления всеми функциями проекта, построенный на библиотеке Click.

## 🚀 Быстрый старт

```bash
# Показать все доступные команды
python cli.py --help

# Показать команды скрапера
python cli.py scraper --help

# Показать команды бота
python cli.py bot --help

# Показать системные команды
python cli.py system --help
```

## 📋 Доступные команды

### 🔍 Скрапер

```bash
# Тестирование компонентов
python cli.py scraper test

# Проверка доступности канала
python cli.py scraper check

# Простой сбор данных
python cli.py scraper simple

# Запуск полного скрапера
python cli.py scraper run

# Запуск скрапера с существующей сессией
python cli.py scraper run --session

# Показать аналитику
python cli.py scraper analytics
```

### 🤖 Бот

```bash
# Запуск основного бота
python cli.py bot run

# Запуск группового ответчика
python cli.py bot group-responder

# Запуск в Docker
python cli.py bot docker
```

### ⚙️ Система

```bash
# Установка зависимостей
python cli.py system install

# Запуск Docker контейнеров
python cli.py system docker-up

# Остановка Docker контейнеров
python cli.py system docker-down

# Показ логов
python cli.py system logs

# Статус контейнеров
python cli.py system status
```

## 📁 Структура проекта

```
├── 📄 main.py                    # Основной скрипт
├── 📄 cli.py                     # CLI для управления
├── 📂 scripts/                   # Функциональные скрипты
│   ├── main_docker.py           # Docker версия
│   ├── run_group_responder.py   # Групповой ответчик
│   ├── run_scraper.py           # Основной скрапер
│   └── run_scraper_with_session.py # Скрапер с сессией
├── 📂 tests/                     # Тесты и утилиты
│   ├── test_components.py       # Тестирование компонентов
│   ├── check_channel.py         # Проверка каналов
│   ├── simple_scraper.py        # Простой скрапер
│   └── analytics.py             # Аналитика
├── 📂 src/                       # Исходный код
├── 📂 config/                    # Конфигурация
└── 📂 docs/                      # Документация
```

## 🎯 Примеры использования

### Сбор данных с канала

```bash
# 1. Проверить доступность канала
python cli.py scraper check

# 2. Протестировать компоненты
python cli.py scraper test

# 3. Запустить сбор данных
python cli.py scraper run --session

# 4. Посмотреть результаты
python cli.py scraper analytics
```

### Управление ботом

```bash
# Запустить бота
python cli.py bot run

# Запустить в Docker
python cli.py bot docker
```

### Системное администрирование

```bash
# Установить зависимости
python cli.py system install

# Запустить все сервисы
python cli.py system docker-up

# Посмотреть логи
python cli.py system logs

# Проверить статус
python cli.py system status
```

## 🔧 Настройка

Убедитесь, что в файле `.env` указаны все необходимые переменные:

```bash
# Telegram API
API_ID_TG=your_api_id
API_HASH_TG=your_api_hash
PHONE_NUMBER=your_phone_number

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=clickhouse_admin
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DB=telegram_analytics
```

## 🐛 Устранение проблем

### Ошибка "No module named 'src'"
```bash
# Убедитесь, что запускаете из корневой директории проекта
cd /home/agruzdov/projects/bot_answer
python cli.py scraper test
```

### Ошибка подключения к ClickHouse
```bash
# Проверьте статус контейнеров
python cli.py system status

# Запустите контейнеры
python cli.py system docker-up
```

### Ошибка Telegram API
```bash
# Проверьте переменные окружения
python cli.py scraper check
```

## 📊 Мониторинг

```bash
# Показать аналитику
python cli.py scraper analytics

# Посмотреть логи
python cli.py system logs

# Проверить статус
python cli.py system status
```

## 🎉 Готово!

Теперь у вас есть удобный CLI для управления всеми функциями проекта!
