# Устранение проблем с ClickHouse

## Проблема: "Connection refused" при подключении из IDE

### Симптомы
- IDE показывает ошибку "Connection refused" при попытке подключения к ClickHouse
- Ошибка: `Connect to http://176.108.246.163:8123 [/176.108.246.163] failed: Connection refused`
- Ping показывает 35ms, но подключение не удается

### Причины и решения

#### 1. ClickHouse не запущен
**Проверка:**
```bash
docker ps | grep clickhouse
```

**Решение:**
```bash
cd /home/agruzdov/projects/bot_answer
docker-compose up -d clickhouse
```

#### 2. ClickHouse слушает только localhost
**Проблема:** ClickHouse по умолчанию слушает только 127.0.0.1, а не все интерфейсы.

**Проверка:**
```bash
docker exec telegram_bot_clickhouse cat /etc/clickhouse-server/config.xml | grep listen_host
```

**Решение:** Использовать стандартную конфигурацию Docker образа, которая автоматически настраивает внешний доступ.

#### 3. Проблемы с файрволом
**Проверка:**
```bash
sudo ufw status | grep -E "(8123|9000)"
```

**Решение:**
```bash
sudo ufw allow 8123/tcp comment "ClickHouse HTTP interface"
sudo ufw allow 9000/tcp comment "ClickHouse Native interface"
```

#### 4. Неправильные учетные данные
**Проверка:**
```bash
curl "http://clickhouse_admin:ClickHouse2024!SecurePassword@localhost:8123/?query=SELECT%20version()"
```

**Решение:** Убедиться, что в .env файле указаны правильные учетные данные:
```bash
CLICKHOUSE_USER=clickhouse_admin
CLICKHOUSE_PASSWORD=ClickHouse2024!SecurePassword
```

## Диагностика подключения

### Пошаговая проверка

1. **Проверить статус контейнера:**
```bash
docker ps | grep clickhouse
```

2. **Проверить логи:**
```bash
docker logs telegram_bot_clickhouse
```

3. **Проверить локальное подключение:**
```bash
curl http://localhost:8123/ping
```

4. **Проверить подключение с аутентификацией:**
```bash
curl "http://clickhouse_admin:password@localhost:8123/?query=SELECT%20version()"
```

5. **Проверить внешнее подключение:**
```bash
curl http://176.108.246.163:8123/ping
```

6. **Проверить привязку портов:**
```bash
ss -tlnp | grep -E ":(8123|9000)"
```

### Ожидаемые результаты

**Статус контейнера:**
```
ad09c0f72bec   clickhouse/clickhouse-server:latest   "/entrypoint.sh"   Up (healthy)   0.0.0.0:8123->8123/tcp, 0.0.0.0:9000->9000/tcp
```

**Привязка портов:**
```
LISTEN 0      4096         0.0.0.0:9000       0.0.0.0:*                                     
LISTEN 0      4096         0.0.0.0:8123       0.0.0.0:*                                     
```

**HTTP ping:**
```
Ok.
```

**Версия ClickHouse:**
```
25.8.3.66
```

## Настройка IDE

### JetBrains IDE (IntelliJ IDEA, PyCharm, DataGrip)

1. **Тип подключения:** ClickHouse
2. **Хост:** 176.108.246.163
3. **Порт:** 8123 (HTTP) или 9000 (Native)
4. **Пользователь:** clickhouse_admin
5. **Пароль:** ClickHouse2024!SecurePassword
6. **База данных:** telegram_bot_analytics

### Настройки подключения

**HTTP интерфейс (порт 8123):**
- URL: `http://176.108.246.163:8123`
- Используется для REST API и веб-запросов

**Native интерфейс (порт 9000):**
- Хост: `176.108.246.163`
- Порт: `9000`
- Используется для клиентских библиотек

## Команды для быстрого исправления

### Полный перезапуск ClickHouse
```bash
cd /home/agruzdov/projects/bot_answer
docker-compose stop clickhouse
docker-compose rm -f clickhouse
docker-compose up -d clickhouse
```

### Проверка всех компонентов
```bash
# Статус контейнера
docker ps | grep clickhouse

# Локальное подключение
curl http://localhost:8123/ping

# Внешнее подключение
curl http://176.108.246.163:8123/ping

# Файрвол
sudo ufw status | grep -E "(8123|9000)"

# Порты
ss -tlnp | grep -E ":(8123|9000)"
```

## Частые ошибки

### 1. "ContainerConfig" error
**Ошибка:** `KeyError: 'ContainerConfig'`

**Решение:** Удалить и пересоздать контейнер:
```bash
docker-compose rm -f clickhouse
docker-compose up -d clickhouse
```

### 2. "Not found: path" error
**Ошибка:** `Not found: path`, `Not found: tmp_path`

**Решение:** Использовать стандартную конфигурацию Docker образа без кастомных config.xml файлов.

### 3. "Authentication failed"
**Ошибка:** `Authentication failed: password is incorrect`

**Решение:** Проверить учетные данные в .env файле и убедиться, что используется правильный пользователь.

## Мониторинг

### Проверка здоровья ClickHouse
```bash
docker exec telegram_bot_clickhouse wget -qO- http://localhost:8123/ping
```

### Просмотр активных подключений
```bash
ss -tuln | grep -E ":(8123|9000)"
```

### Логи файрвола
```bash
sudo tail -f /var/log/ufw.log | grep -E "(8123|9000)"
```

## Заключение

После выполнения всех проверок ClickHouse должен быть доступен:
- Локально: `http://localhost:8123`
- Внешне: `http://176.108.246.163:8123`
- Native: `176.108.246.163:9000`

Если проблемы продолжаются, проверьте логи контейнера и убедитесь, что все переменные окружения заданы корректно.
