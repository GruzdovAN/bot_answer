# Настройка Docker

## 🐳 Установка Docker

### Ubuntu/Debian
```bash
# Обновляем пакеты
sudo apt update

# Устанавливаем Docker и docker-compose
sudo apt install -y docker-compose

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Запускаем Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### После установки
**Важно**: После добавления в группу docker нужно **перелогиниться** или выполнить:
```bash
newgrp docker
```

## 🔧 Проверка установки

```bash
# Проверяем версии
docker --version
docker-compose --version

# Проверяем, что Docker работает
docker run hello-world
```

## 🚀 Запуск проекта

### С sudo (если не перелогинились)
```bash
# Запуск PostgreSQL
sudo docker-compose up -d postgres

# Проверка статуса
sudo docker-compose ps

# Остановка
sudo docker-compose down
```

### Без sudo (после перелогина)
```bash
# Запуск PostgreSQL
docker-compose up -d postgres

# Проверка статуса
docker-compose ps

# Остановка
docker-compose down
```

## 📋 Полезные команды

### Управление контейнерами
```bash
# Просмотр всех контейнеров
docker ps -a

# Просмотр логов
docker logs <container_name>

# Остановка контейнера
docker stop <container_name>

# Удаление контейнера
docker rm <container_name>
```

### Управление образами
```bash
# Просмотр образов
docker images

# Удаление образа
docker rmi <image_name>

# Очистка неиспользуемых образов
docker image prune
```

### Управление volumes
```bash
# Просмотр volumes
docker volume ls

# Удаление volume
docker volume rm <volume_name>

# Очистка неиспользуемых volumes
docker volume prune
```

## 🔍 Устранение проблем

### Проблема: "permission denied"
**Причина**: Пользователь не в группе docker
**Решение**: 
```bash
sudo usermod -aG docker $USER
# Перелогиниться или выполнить:
newgrp docker
```

### Проблема: "docker-compose: command not found"
**Причина**: docker-compose не установлен
**Решение**:
```bash
sudo apt install docker-compose
```

### Проблема: "Cannot connect to the Docker daemon"
**Причина**: Docker не запущен
**Решение**:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Проблема: "Port already in use"
**Причина**: Порт 5432 уже занят
**Решение**:
```bash
# Найти процесс, использующий порт
sudo lsof -i :5432

# Остановить процесс или изменить порт в docker-compose.yml
```

## 📊 Мониторинг

### Статус сервисов
```bash
# Статус всех контейнеров
docker-compose ps

# Статус конкретного сервиса
docker-compose ps postgres
```

### Логи
```bash
# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs postgres

# Следить за логами в реальном времени
docker-compose logs -f postgres
```

### Ресурсы
```bash
# Использование ресурсов
docker stats

# Информация о системе
docker system df
```

## 🔒 Безопасность

### Ограничения
- Не запускайте контейнеры с `--privileged` без необходимости
- Используйте не-root пользователей в контейнерах
- Регулярно обновляйте образы

### Сетевая безопасность
- Используйте внутренние сети Docker
- Ограничивайте доступ к портам
- Настройте файрвол

## 📝 Примеры использования

### Разработка
```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Пересборка образа
docker-compose build --no-cache

# Выполнение команд в контейнере
docker-compose exec postgres psql -U telegram_admin -d telegram_bot
```

### Продакшн
```bash
# Запуск в фоновом режиме
docker-compose up -d

# Масштабирование сервисов
docker-compose up -d --scale telegram_bot=3

# Обновление сервисов
docker-compose pull
docker-compose up -d
```
