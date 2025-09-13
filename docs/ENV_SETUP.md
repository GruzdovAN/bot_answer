# Настройка переменных окружения

## 🔧 Быстрая настройка

1. **Скопируйте пример конфигурации:**
```bash
cp env.example .env
```

2. **Отредактируйте файл .env:**
```bash
nano .env
```

3. **Проверьте настройки:**
```bash
./check_env.sh
```

4. **Запустите бота:**
```bash
./docker-start.sh
```

## 📋 Переменные окружения

### Telegram API
```bash
API_ID_TG=ваш_api_id                    # Получить на https://my.telegram.org
API_HASH_TG=ваш_api_hash                # Получить на https://my.telegram.org
PHONE_NUMBER=+79123456789               # Ваш номер телефона
CHANNEL_USERNAME=my_channel             # Имя канала (без @)
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ  # Токен от @BotFather
```

### База данных PostgreSQL
```bash
DB_HOST=postgres                        # Хост базы данных
DB_PORT=5432                           # Порт базы данных
DB_NAME=telegram_bot                   # Имя базы данных
DB_USER=telegram_admin                 # Пользователь базы данных
DB_PASSWORD="ваш_сложный_пароль"  # Пароль (в кавычках!)
```

### pgAdmin
```bash
PGADMIN_EMAIL=admin@telegram-bot.com    # Email для входа в pgAdmin
PGADMIN_PASSWORD=ваш_пароль_pgadmin  # Пароль для pgAdmin
```

### Логирование
```bash
LOG_LEVEL=INFO                         # Уровень логирования (DEBUG, INFO, WARNING, ERROR)
```

## ⚠️ Важные замечания

### Безопасность паролей
- **Всегда используйте кавычки** для паролей со специальными символами
- **Не коммитьте** файл `.env` в git
- **Регулярно меняйте** пароли в продакшене

### Пример правильного пароля в .env:
```bash
# ✅ Правильно (в кавычках)
DB_PASSWORD="ваш_сложный_пароль"

# ❌ Неправильно (без кавычек)
DB_PASSWORD=ваш_сложный_пароль
```

## 🔍 Проверка конфигурации

### Автоматическая проверка
```bash
./check_env.sh
```

### Ручная проверка
```bash
# Загрузить переменные
source .env

# Проверить конкретную переменную
echo $DB_PASSWORD
```

## 🚀 Запуск с переменными окружения

### Docker Compose
```bash
# Запуск с .env файлом
docker-compose up -d

# Запуск с конкретными переменными
DB_PASSWORD="мой_пароль" docker-compose up -d
```

### Локальный запуск
```bash
# Загрузка переменных и запуск
source .env
python3 main.py
```

## 📊 Получение информации о доступе

### Внешний IP и учетные данные
```bash
./get_external_ip.sh
```

### Только внешний IP
```bash
curl -s ifconfig.me
```

## 🔧 Устранение проблем

### Проблема: "command not found" при загрузке .env
**Причина**: Специальные символы в пароле не экранированы
**Решение**: Оберните пароль в кавычки
```bash
DB_PASSWORD="пароль_со_спец_символами"
```

### Проблема: Переменные не загружаются
**Причина**: Неправильный синтаксис в .env файле
**Решение**: Проверьте синтаксис
```bash
# ✅ Правильно
VARIABLE=value
VARIABLE="value with spaces"

# ❌ Неправильно
VARIABLE = value  # пробелы вокруг =
VARIABLE=value # комментарий без пробела
```

### Проблема: Docker не видит переменные
**Причина**: .env файл не в корне проекта
**Решение**: Убедитесь, что .env в той же папке, что и docker-compose.yml

## 📝 Примеры использования

### Python
```python
import os
from dotenv import load_dotenv

# Загрузка переменных
load_dotenv()

# Использование
db_password = os.getenv('DB_PASSWORD')
api_id = os.getenv('API_ID_TG')
```

### Bash
```bash
# Загрузка переменных
source .env

# Использование
echo "Пароль: $DB_PASSWORD"
echo "API ID: $API_ID_TG"
```

### Docker Compose
```yaml
services:
  app:
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
      - API_ID_TG=${API_ID_TG}
```
