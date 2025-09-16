# Настройка автоматической активации виртуального окружения

## 🚀 Автоматическая активация при открытии терминала

### Вариант 1: Автоматическая активация в директории проекта

1. **Добавьте в ваш `~/.bashrc`:**
```bash
# Автоматическая активация виртуального окружения для Telegram Bot проекта
source /home/agruzdov/projects/bot_answer/.bashrc_project
```

2. **Перезагрузите конфигурацию:**
```bash
source ~/.bashrc
```

3. **Теперь при переходе в директорию проекта виртуальное окружение активируется автоматически:**
```bash
cd /home/agruzdov/projects/bot_answer
# Виртуальное окружение активируется автоматически!
```

### Вариант 2: Ручная активация

**Запустите скрипт активации:**
```bash
cd /home/agruzdov/projects/bot_answer
./activate_env.sh
```

### Вариант 3: Алиас для быстрого доступа

**Добавьте в ваш `~/.bashrc`:**
```bash
# Алиас для быстрого перехода в проект с активацией окружения
alias telegram-bot='cd /home/agruzdov/projects/bot_answer && source venv/bin/activate && echo "🚀 Telegram Bot проект готов к работе!"'
```

**Использование:**
```bash
telegram-bot
# Автоматически переходит в проект и активирует окружение
```

## 🔧 Проверка настройки

### Проверить, что виртуальное окружение активировано:
```bash
which python
# Должно показать: /home/agruzdov/projects/bot_answer/venv/bin/python

echo $VIRTUAL_ENV
# Должно показать: /home/agruzdov/projects/bot_answer/venv
```

### Проверить доступные команды:
```bash
python cli.py --help
```

## 📋 Доступные команды после активации

```bash
# Скрапер
python cli.py scraper test        # Тестирование
python cli.py scraper run         # Запуск скрапера
python cli.py scraper analytics   # Аналитика

# Система
python cli.py system status       # Статус системы
python cli.py system docker-up    # Запуск контейнеров
```

## 🐛 Устранение проблем

### Если виртуальное окружение не активируется:
```bash
# Проверьте, что файл существует
ls -la /home/agruzdov/projects/bot_answer/venv/bin/activate

# Активируйте вручную
source /home/agruzdov/projects/bot_answer/venv/bin/activate
```

### Если команды не работают:
```bash
# Проверьте, что вы в правильной директории
pwd
# Должно показать: /home/agruzdov/projects/bot_answer

# Проверьте, что виртуальное окружение активировано
echo $VIRTUAL_ENV
```

## 🎯 Рекомендуемая настройка

**Для максимального удобства добавьте в `~/.bashrc`:**
```bash
# Telegram Bot проект - автоматическая активация
source /home/agruzdov/projects/bot_answer/.bashrc_project

# Алиас для быстрого доступа
alias telegram-bot='cd /home/agruzdov/projects/bot_answer && source venv/bin/activate && echo "🚀 Telegram Bot проект готов к работе!"'
```

**После этого:**
- При переходе в директорию проекта окружение активируется автоматически
- Команда `telegram-bot` быстро переводит в проект с активацией
- Все команды CLI доступны сразу
