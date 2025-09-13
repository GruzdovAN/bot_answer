# 🚀 Быстрая справка по базе данных

## 📊 Основные таблицы

| Таблица | Назначение | Ключевые поля |
|---------|------------|---------------|
| `chats` | Чаты/каналы/группы | `telegram_id`, `username`, `title` |
| `users` | Пользователи Telegram | `telegram_id`, `username`, `first_name` |
| `messages` | Все сообщения | `telegram_id`, `text`, `is_bot_response` |
| `bot_responses` | Ответы бота | `response_text`, `response_type`, `trigger_keyword` |
| `bot_stats` | Статистика по дням | `date`, `total_messages`, `bot_responses` |
| `bot_sessions` | Сессии работы бота | `bot_name`, `session_start`, `is_active` |

## 🔍 Быстрые запросы

### Последние сообщения
```sql
-- Реальный результат из работающего бота
SELECT m.text, u.username, m.created_at 
FROM messages m 
LEFT JOIN users u ON m.user_id = u.id 
ORDER BY m.created_at DESC 
LIMIT 10;

-- Результат:
--  text  | username  |         created_at         
-- -------+-----------+----------------------------
--  привет| gruzdovan | 2025-09-13 16:25:06.131154
--  ку    | gruzdovan | 2025-09-13 16:25:04.047787
```

### Статистика бота за сегодня
```sql
SELECT 
    COUNT(*) as total_messages,
    COUNT(CASE WHEN is_bot_response = true THEN 1 END) as bot_responses
FROM messages 
WHERE DATE(created_at) = CURRENT_DATE;
```

### Активные сессии
```sql
SELECT bot_name, session_start, messages_processed, responses_sent 
FROM bot_sessions 
WHERE is_active = true;
```

### Топ пользователей
```sql
SELECT u.username, COUNT(m.id) as message_count 
FROM users u 
JOIN messages m ON u.id = m.user_id 
GROUP BY u.id, u.username 
ORDER BY message_count DESC 
LIMIT 5;
```

## 📈 Мониторинг

### Проверка активности
```sql
-- Сообщения за последний час
SELECT COUNT(*) FROM messages 
WHERE created_at >= NOW() - INTERVAL '1 hour';

-- Ошибки бота
SELECT COUNT(*) FROM bot_responses 
WHERE is_successful = false 
AND created_at >= NOW() - INTERVAL '1 day';
```

### Производительность
```sql
-- Среднее время ответа
SELECT AVG(response_time_ms) as avg_response_time 
FROM bot_responses 
WHERE created_at >= NOW() - INTERVAL '1 day';

-- Самые медленные ответы
SELECT response_text, response_time_ms 
FROM bot_responses 
ORDER BY response_time_ms DESC 
LIMIT 5;
```

## 🔧 Администрирование

### Очистка старых данных
```sql
-- Удаление сообщений старше 1 года
DELETE FROM messages 
WHERE created_at < NOW() - INTERVAL '1 year';

-- Архивирование статистики
INSERT INTO bot_stats_archive 
SELECT * FROM bot_stats 
WHERE date < NOW() - INTERVAL '6 months';
```

### Проверка целостности
```sql
-- Сообщения без пользователя
SELECT COUNT(*) FROM messages WHERE user_id IS NULL;

-- Ответы без исходного сообщения
SELECT COUNT(*) FROM bot_responses br
LEFT JOIN messages m ON br.original_message_id = m.id
WHERE m.id IS NULL;
```

## 📋 Полезные команды

### Подключение к БД
```bash
# Через Docker
sudo docker exec -it telegram_bot_postgres psql -U telegram_admin -d telegram_bot

# Внешнее подключение
psql -h 176.108.246.163 -p 5432 -U telegram_admin -d telegram_bot
```

### Экспорт данных
```bash
# Экспорт всех таблиц
sudo docker exec telegram_bot_postgres pg_dump -U telegram_admin telegram_bot > backup.sql

# Экспорт только данных
sudo docker exec telegram_bot_postgres pg_dump -U telegram_admin -a telegram_bot > data.sql
```

### Импорт данных
```bash
# Импорт из файла
sudo docker exec -i telegram_bot_postgres psql -U telegram_admin -d telegram_bot < backup.sql
```

## 🚨 Устранение неполадок

### Проблемы с подключением
```sql
-- Проверка активных подключений
SELECT client_addr, client_port, state 
FROM pg_stat_activity 
WHERE datname = 'telegram_bot';

-- Проверка размера БД
SELECT pg_size_pretty(pg_database_size('telegram_bot'));
```

### Проблемы с производительностью
```sql
-- Медленные запросы
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Размеры таблиц
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 📚 Дополнительные ресурсы

- **[Полная схема БД](DATABASE_SCHEMA.md)** - детальное описание всех таблиц
- **[Поток данных](DATA_FLOW.md)** - как заполняются таблицы
- **[Внешний доступ](EXTERNAL_ACCESS.md)** - подключение к БД извне
- **[Безопасность](SECURITY.md)** - настройки безопасности
