# Тесты и утилиты

Эта директория содержит все тестовые файлы и утилиты для универсального Telegram скрапера.

## 📁 Содержимое

### 🧪 Тестовые файлы
- `test_components.py` - тестирование всех компонентов системы
- `test_period_scraper.py` - тестирование сбора данных за период
- `test_scraper.py` - тестирование основного скрапера
- `test_user_mode.py` - тестирование пользовательского режима

### 🔧 Утилиты
- `check_channel.py` - проверка доступности канала
- `simple_scraper.py` - простой скрапер для сбора нескольких сообщений
- `analytics.py` - просмотр аналитики собранных данных

### 📦 Зависимости
- `requirements_universal.txt` - зависимости для универсального скрапера

## 🚀 Использование

### Установка зависимостей
```bash
cd /home/agruzdov/projects/bot_answer
source venv/bin/activate
pip install -r tests/requirements_universal.txt
```

### Запуск тестов
```bash
# Тестирование компонентов
python tests/test_components.py

# Проверка канала
python tests/check_channel.py

# Простой сбор данных
python tests/simple_scraper.py

# Аналитика
python tests/analytics.py
```

## 📊 Результаты тестов

После запуска тестов вы увидите:
- ✅ Статус подключения к Telegram
- ✅ Работу парсеров
- ✅ Сохранение в ClickHouse
- ✅ Статистику собранных данных

## 🔍 Отладка

Если тесты не проходят:
1. Проверьте переменные окружения в `.env`
2. Убедитесь, что ClickHouse запущен
3. Проверьте доступность Telegram API
4. Запустите `python tests/check_channel.py` для диагностики
