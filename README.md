# 🤖 Telegram Bot Auto-Responder

Автоматический ответчик для Telegram с поддержкой Docker, PostgreSQL и внешнего доступа.

## 🚀 Быстрый старт

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd bot_answer

# 2. Настройте переменные окружения
cp config/env.example .env
nano .env

# 3. Запустите бота
./scripts/quick-start.sh
```

## 📁 Структура проекта

```
bot_answer/
├── src/                    # Исходный код приложения
│   ├── bots/              # Реализации ботов
│   ├── config/            # Конфигурация
│   ├── database/          # Модели и работа с БД
│   └── utils/             # Утилиты
├── scripts/               # Скрипты управления
│   ├── docker-start.sh    # Запуск Docker
│   ├── docker-stop.sh     # Остановка Docker
│   ├── quick-start.sh     # Быстрый запуск
│   └── security_check.sh  # Проверка безопасности
├── docs/                  # Документация
│   ├── README.md          # Основная документация
│   ├── DOCKER_SETUP.md    # Установка Docker
│   ├── ENV_SETUP.md       # Настройка переменных
│   ├── EXTERNAL_ACCESS.md # Внешний доступ к БД
│   ├── SESSION_MANAGEMENT.md # Управление сессиями
│   └── SECURITY.md        # Безопасность
├── config/                # Конфигурационные файлы
│   └── init_database.py   # Инициализация БД
├── docker/                # Docker конфигурация
│   └── postgres/          # Настройки PostgreSQL
├── sessions/              # Файлы сессий Telegram
├── logs/                  # Логи приложения
├── docker-compose.yml     # Docker Compose
├── Dockerfile            # Docker образ
└── requirements.txt      # Python зависимости
```

## 🛠️ Основные команды

### Запуск и остановка
```bash
# Быстрый запуск
./scripts/quick-start.sh

# Запуск Docker
./scripts/docker-start.sh

# Остановка
./scripts/docker-stop.sh

# Просмотр логов
./scripts/docker-logs.sh
```

### Управление
```bash
# Проверка безопасности
./scripts/security_check.sh

# Проверка переменных окружения
./scripts/check_env.sh

# Получение внешнего IP
./scripts/get_external_ip.sh
```

## 📖 Документация

- **[Основная документация](docs/README.md)** - полное руководство
- **[Установка Docker](docs/DOCKER_SETUP.md)** - настройка Docker
- **[Настройка переменных](docs/ENV_SETUP.md)** - конфигурация .env
- **[Внешний доступ](docs/EXTERNAL_ACCESS.md)** - подключение к БД
- **[Схема базы данных](docs/DATABASE_SCHEMA.md)** - структура таблиц
- **[Поток данных](docs/DATA_FLOW.md)** - как заполняются таблицы
- **[Быстрая справка](docs/QUICK_REFERENCE.md)** - основные запросы и команды
- **[Управление сессиями](docs/SESSION_MANAGEMENT.md)** - сессии Telegram
- **[Безопасность](docs/SECURITY.md)** - безопасность проекта

## 🔧 Настройка

### 1. Переменные окружения
```bash
cp config/env.example .env
nano .env
```

### 2. Авторизация Telegram
```bash
# Локальная авторизация (один раз)
./scripts/run.sh

# Копирование сессий
cp *.session sessions/
```

### 3. Запуск
```bash
./scripts/quick-start.sh
```

## 🐳 Docker

Проект полностью контейнеризован:

- **PostgreSQL** - база данных
- **Telegram Bot** - основное приложение
- **pgAdmin** - веб-интерфейс для БД

## 🔒 Безопасность

- ✅ Все пароли в переменных окружения
- ✅ Нет хардкодных паролей в коде
- ✅ Автоматическая проверка безопасности
- ✅ Ограниченные права доступа к файлам

## 📊 Мониторинг

- **Логи**: `./scripts/docker-logs.sh`
- **Статус**: `sudo docker-compose ps`
- **База данных**: pgAdmin на порту 8080
- **PostgreSQL**: порт 5432

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи: `./scripts/docker-logs.sh`
2. Проверьте переменные: `./scripts/check_env.sh`
3. Проверьте безопасность: `./scripts/security_check.sh`
4. Обратитесь к документации в `docs/`

## 📝 Лицензия

MIT License

---

**Версия**: 1.0.0  
**Автор**: Telegram Bot Team  
**Дата**: 2025