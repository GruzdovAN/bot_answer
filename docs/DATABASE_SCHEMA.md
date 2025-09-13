# Схема базы данных Telegram бота

## 📊 Обзор таблиц

База данных содержит 6 основных таблиц для хранения информации о чатах, пользователях, сообщениях и работе бота.

## 🗂️ Структура таблиц

### 1. **chats** - Чаты/каналы/группы

Хранит информацию о чатах, каналах и группах, в которых работает бот.

| Поле | Тип | Описание | Индексы |
|------|-----|----------|---------|
| `id` | INTEGER | Первичный ключ | PRIMARY KEY |
| `telegram_id` | BIGINT | ID чата в Telegram | UNIQUE, INDEX |
| `username` | VARCHAR(255) | Username чата (@channel_name) | INDEX |
| `title` | VARCHAR(255) | Название чата | - |
| `chat_type` | VARCHAR(50) | Тип чата (channel, group, supergroup, private) | - |
| `is_active` | BOOLEAN | Активен ли чат | - |
| `created_at` | TIMESTAMP | Дата создания записи | - |
| `updated_at` | TIMESTAMP | Дата последнего обновления | - |

**Как заполняется:**
- Автоматически при первом получении сообщения из чата
- Метод: `get_or_create_chat()` в `DatabaseManager`
- Вызывается из ботов при обработке новых сообщений

**Пример данных:**
```sql
-- Реальные данные из работающего бота
INSERT INTO chats (telegram_id, username, title, chat_type, is_active) 
VALUES (2963417939, 'gruzdovan', 'test_art_ga', 'channel', true);
```

---

### 2. **users** - Пользователи

Хранит информацию о пользователях Telegram.

| Поле | Тип | Описание | Индексы |
|------|-----|----------|---------|
| `id` | INTEGER | Первичный ключ | PRIMARY KEY |
| `telegram_id` | BIGINT | ID пользователя в Telegram | UNIQUE, INDEX |
| `username` | VARCHAR(255) | Username пользователя (@username) | INDEX |
| `first_name` | VARCHAR(255) | Имя пользователя | - |
| `last_name` | VARCHAR(255) | Фамилия пользователя | - |
| `is_bot` | BOOLEAN | Является ли пользователь ботом | - |
| `created_at` | TIMESTAMP | Дата создания записи | - |
| `updated_at` | TIMESTAMP | Дата последнего обновления | - |

**Как заполняется:**
- Автоматически при первом получении сообщения от пользователя
- Метод: `get_or_create_user()` в `DatabaseManager`
- Вызывается из ботов при обработке новых сообщений

**Пример данных:**
```sql
-- Реальные данные из работающего бота
INSERT INTO users (telegram_id, username, first_name, last_name, is_bot) 
VALUES (-1002963417939, 'gruzdovan', NULL, NULL, false);
```

---

### 3. **messages** - Сообщения

Основная таблица для хранения всех сообщений.

| Поле | Тип | Описание | Индексы |
|------|-----|----------|---------|
| `id` | INTEGER | Первичный ключ | PRIMARY KEY |
| `telegram_id` | BIGINT | ID сообщения в Telegram | INDEX |
| `chat_id` | INTEGER | Ссылка на чат | FOREIGN KEY |
| `user_id` | INTEGER | Ссылка на пользователя | FOREIGN KEY |
| `text` | TEXT | Текст сообщения | - |
| `message_type` | VARCHAR(50) | Тип сообщения (text, photo, document, etc.) | - |
| `is_bot_response` | BOOLEAN | Является ли сообщение ответом бота | - |
| `raw_data` | JSON | Полные данные от Telegram API | - |
| `created_at` | TIMESTAMP | Дата создания сообщения | INDEX |

**Как заполняется:**
- Автоматически при получении каждого сообщения
- Метод: `save_message()` в `DatabaseManager`
- Вызывается из ботов при обработке входящих сообщений

**Пример данных:**
```sql
-- Реальные данные из работающего бота
INSERT INTO messages (telegram_id, chat_id, user_id, text, message_type, is_bot_response) 
VALUES (207, 1, 1, 'привет', 'text', false);
INSERT INTO messages (telegram_id, chat_id, user_id, text, message_type, is_bot_response) 
VALUES (208, 1, 1, 'ку', 'text', false);
```

---

### 4. **bot_responses** - Ответы бота

Хранит информацию о всех ответах, отправленных ботом.

| Поле | Тип | Описание | Индексы |
|------|-----|----------|---------|
| `id` | INTEGER | Первичный ключ | PRIMARY KEY |
| `original_message_id` | INTEGER | Ссылка на исходное сообщение | FOREIGN KEY |
| `response_text` | TEXT | Текст ответа бота | - |
| `response_type` | VARCHAR(50) | Тип ответа (auto, manual, smart) | - |
| `trigger_keyword` | VARCHAR(255) | Ключевое слово, вызвавшее ответ | - |
| `response_time_ms` | INTEGER | Время ответа в миллисекундах | - |
| `is_successful` | BOOLEAN | Успешен ли ответ | - |
| `error_message` | TEXT | Сообщение об ошибке (если есть) | - |
| `created_at` | TIMESTAMP | Дата создания ответа | - |

**Как заполняется:**
- Автоматически при отправке ответа ботом
- Метод: `save_bot_response()` в `DatabaseManager`
- Вызывается из ботов после отправки ответа

**Пример данных:**
```sql
-- Реальные данные из работающего бота
INSERT INTO bot_responses (original_message_id, response_text, response_type, trigger_keyword, response_time_ms, is_successful) 
VALUES (2, '👋 Привет! Я бот-помощник!', 'auto', 'привет', 118, true);
```

---

### 5. **bot_stats** - Статистика бота

Хранит ежедневную статистику работы бота по чатам.

| Поле | Тип | Описание | Индексы |
|------|-----|----------|---------|
| `id` | INTEGER | Первичный ключ | PRIMARY KEY |
| `chat_id` | INTEGER | Ссылка на чат | FOREIGN KEY |
| `date` | TIMESTAMP | Дата статистики | INDEX |
| `total_messages` | INTEGER | Общее количество сообщений | - |
| `bot_responses` | INTEGER | Количество ответов бота | - |
| `unique_users` | INTEGER | Количество уникальных пользователей | - |
| `most_used_keywords` | JSON | Самые используемые ключевые слова | - |
| `response_time_avg` | INTEGER | Среднее время ответа в мс | - |

**Как заполняется:**
- Автоматически по расписанию (ежедневно)
- Метод: `get_chat_stats()` в `DatabaseManager`
- Может вызываться вручную для получения статистики

**Пример данных:**
```sql
INSERT INTO bot_stats (chat_id, date, total_messages, bot_responses, unique_users, response_time_avg) 
VALUES (1, '2025-09-13', 150, 45, 25, 200);
```

---

### 6. **bot_sessions** - Сессии бота

Хранит информацию о сессиях работы бота.

| Поле | Тип | Описание | Индексы |
|------|-----|----------|---------|
| `id` | INTEGER | Первичный ключ | PRIMARY KEY |
| `bot_name` | VARCHAR(100) | Название бота | - |
| `chat_id` | INTEGER | Ссылка на чат | FOREIGN KEY |
| `session_start` | TIMESTAMP | Начало сессии | - |
| `session_end` | TIMESTAMP | Конец сессии | - |
| `is_active` | BOOLEAN | Активна ли сессия | - |
| `messages_processed` | INTEGER | Количество обработанных сообщений | - |
| `responses_sent` | INTEGER | Количество отправленных ответов | - |
| `errors_count` | INTEGER | Количество ошибок | - |

**Как заполняется:**
- При запуске бота создается новая сессия
- При остановке бота сессия закрывается
- Статистика обновляется в реальном времени

**Пример данных:**
```sql
INSERT INTO bot_sessions (bot_name, chat_id, session_start, is_active, messages_processed, responses_sent, errors_count) 
VALUES ('simple_responder', 1, '2025-09-13 15:00:00', true, 0, 0, 0);
```

---

## 🔗 Связи между таблицами

```
chats (1) ←→ (N) messages
users (1) ←→ (N) messages
messages (1) ←→ (N) bot_responses
chats (1) ←→ (N) bot_stats
chats (1) ←→ (N) bot_sessions
```

## 📈 Полезные запросы

### Статистика по чату за последние 7 дней
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_messages,
    COUNT(CASE WHEN is_bot_response = true THEN 1 END) as bot_responses,
    COUNT(DISTINCT user_id) as unique_users
FROM messages 
WHERE chat_id = 1 
    AND created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Топ пользователей по активности
```sql
SELECT 
    u.username,
    u.first_name,
    COUNT(m.id) as message_count
FROM users u
JOIN messages m ON u.id = m.user_id
WHERE m.chat_id = 1
    AND m.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.username, u.first_name
ORDER BY message_count DESC
LIMIT 10;
```

### Эффективность бота
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_responses,
    AVG(response_time_ms) as avg_response_time,
    COUNT(CASE WHEN is_successful = true THEN 1 END) as successful_responses
FROM bot_responses br
JOIN messages m ON br.original_message_id = m.id
WHERE m.chat_id = 1
    AND br.created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(br.created_at)
ORDER BY date DESC;
```

### Самые популярные ключевые слова
```sql
SELECT 
    trigger_keyword,
    COUNT(*) as usage_count
FROM bot_responses
WHERE trigger_keyword IS NOT NULL
    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY trigger_keyword
ORDER BY usage_count DESC
LIMIT 20;
```

## 🔧 Технические детали

### Индексы
- **telegram_id** - для быстрого поиска по ID Telegram
- **username** - для поиска по username
- **created_at** - для временных запросов
- **date** - для статистических запросов

### Типы данных
- **BIGINT** для telegram_id (поддержка больших чисел Telegram)
- **JSON** для raw_data и most_used_keywords (гибкое хранение)
- **TEXT** для длинных текстов сообщений
- **TIMESTAMP** для всех временных меток

### Ограничения
- Все telegram_id уникальны
- Внешние ключи обеспечивают целостность данных
- Автоматические временные метки для created_at/updated_at
