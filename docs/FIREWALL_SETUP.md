# Настройка файрвола для ClickHouse

## Обзор

Добавлены правила файрвола для обеспечения внешнего доступа к ClickHouse сервису.

## Настроенные порты

### ClickHouse порты
- **8123/tcp** - HTTP интерфейс ClickHouse (для REST API и веб-запросов)
- **9000/tcp** - Native интерфейс ClickHouse (для клиентских библиотек)

### Существующие порты
- **5432/tcp** - PostgreSQL (уже был настроен)
- **22/tcp** - SSH (уже был настроен)

## Команды для настройки

### Добавление правил ClickHouse
```bash
# HTTP интерфейс
sudo ufw allow 8123/tcp comment "ClickHouse HTTP interface"

# Native интерфейс
sudo ufw allow 9000/tcp comment "ClickHouse Native interface"
```

### Проверка статуса файрвола
```bash
# Просмотр всех правил
sudo ufw status numbered

# Просмотр только активных правил
sudo ufw status
```

## Текущие правила файрвола

```
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 5432/tcp                   ALLOW IN    Anywhere                  
[ 2] 22/tcp                     ALLOW IN    Anywhere                  
[ 3] 8123/tcp                   ALLOW IN    Anywhere                   # ClickHouse HTTP interface
[ 4] 9000/tcp                   ALLOW IN    Anywhere                   # ClickHouse Native interface
[ 5] 5432/tcp (v6)              ALLOW IN    Anywhere (v6)             
[ 6] 22/tcp (v6)              ALLOW IN    Anywhere (v6)             
[ 7] 8123/tcp (v6)              ALLOW IN    Anywhere (v6)              # ClickHouse HTTP interface
[ 8] 9000/tcp (v6)              ALLOW IN    Anywhere (v6)              # ClickHouse Native interface
```

## Проверка доступности

### Проверка портов
```bash
# Проверка что порты слушаются
ss -tlnp | grep -E ":(8123|9000)"

# Проверка HTTP интерфейса
curl http://localhost:8123/ping

# Проверка с аутентификацией
curl "http://clickhouse_admin:password@localhost:8123/?query=SELECT%20version()"
```

### Ожидаемый результат
```
LISTEN 0      4096         0.0.0.0:9000       0.0.0.0:*                                     
LISTEN 0      4096         0.0.0.0:8123       0.0.0.0:*                                     
```

## Безопасность

### Рекомендации
1. **Ограничьте доступ** по IP адресам если возможно:
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8123
   sudo ufw allow from 192.168.1.0/24 to any port 9000
   ```

2. **Используйте сильные пароли** для ClickHouse пользователей

3. **Настройте SSL/TLS** для продакшена

4. **Регулярно обновляйте** ClickHouse до последней версии

### Удаление правил (если необходимо)
```bash
# Удаление по номеру правила
sudo ufw delete 3  # HTTP интерфейс
sudo ufw delete 4  # Native интерфейс

# Или удаление по порту
sudo ufw delete allow 8123/tcp
sudo ufw delete allow 9000/tcp
```

## Внешний доступ

После настройки файрвола ClickHouse доступен извне по адресам:
- **HTTP**: `http://YOUR_SERVER_IP:8123`
- **Native**: `YOUR_SERVER_IP:9000`

### Пример подключения извне
```bash
# HTTP запрос
curl "http://clickhouse_admin:password@YOUR_SERVER_IP:8123/?query=SELECT%20version()"

# Python клиент
from clickhouse_driver import Client
client = Client(host='YOUR_SERVER_IP', port=9000, user='clickhouse_admin', password='password')
```

## Мониторинг

### Проверка подключений
```bash
# Активные подключения к ClickHouse
ss -tuln | grep -E ":(8123|9000)"

# Логи файрвола
sudo tail -f /var/log/ufw.log | grep -E "(8123|9000)"
```

## Настройка завершена

ClickHouse теперь доступен извне через настроенные порты файрвола. Убедитесь, что используете сильные пароли и ограничиваете доступ по необходимости.
