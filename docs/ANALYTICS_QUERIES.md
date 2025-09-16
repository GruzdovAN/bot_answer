# SQL запросы для анализа данных @datasciencejobs

## Обзор

После сбора данных из канала @datasciencejobs в ClickHouse, можно выполнять различные аналитические запросы для изучения трендов в Data Science индустрии.

## Базовые запросы

### 1. Общая статистика
```sql
-- Количество сообщений по дням
SELECT 
    toDate(date) as day,
    count() as messages_count,
    sum(views) as total_views,
    avg(views) as avg_views
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY day
ORDER BY day;

-- Топ-10 самых популярных сообщений
SELECT 
    message_id,
    date,
    text,
    views,
    forwards,
    replies
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
ORDER BY views DESC
LIMIT 10;
```

### 2. Анализ технологий
```sql
-- Топ технологий по хештегам
SELECT 
    hashtag,
    count() as mentions_count,
    sum(views) as total_views
FROM (
    SELECT 
        arrayJoin(hashtags) as hashtag,
        views
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
)
GROUP BY hashtag
ORDER BY mentions_count DESC
LIMIT 20;

-- Анализ комбинаций технологий
SELECT 
    hashtag1,
    hashtag2,
    count() as co_occurrence
FROM (
    SELECT 
        hashtags[1] as hashtag1,
        hashtags[2] as hashtag2
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
    AND length(hashtags) >= 2
)
WHERE hashtag1 != hashtag2
GROUP BY hashtag1, hashtag2
ORDER BY co_occurrence DESC
LIMIT 20;
```

### 3. Временной анализ
```sql
-- Активность по дням недели
SELECT 
    dayOfWeek(date) as day_of_week,
    count() as messages_count,
    avg(views) as avg_views
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY day_of_week
ORDER BY day_of_week;

-- Активность по часам
SELECT 
    hour(date) as hour_of_day,
    count() as messages_count,
    avg(views) as avg_views
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- Тренд популярности технологий
SELECT 
    toDate(date) as day,
    hashtag,
    count() as mentions
FROM (
    SELECT 
        date,
        arrayJoin(hashtags) as hashtag
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
    AND hashtag IN ('#python', '#machinelearning', '#tensorflow', '#pytorch')
)
GROUP BY day, hashtag
ORDER BY day, hashtag;
```

## Продвинутые запросы

### 4. Анализ компаний
```sql
-- Топ компаний по упоминаниям
SELECT 
    mention,
    count() as mentions_count,
    sum(views) as total_views,
    avg(views) as avg_views_per_post
FROM (
    SELECT 
        arrayJoin(mentions) as mention,
        views
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
)
WHERE mention LIKE '@%'
GROUP BY mention
ORDER BY mentions_count DESC
LIMIT 20;

-- Анализ активности компаний
SELECT 
    mention,
    count() as posts_count,
    min(date) as first_post,
    max(date) as last_post,
    dateDiff('day', min(date), max(date)) as activity_span
FROM (
    SELECT 
        arrayJoin(mentions) as mention,
        date
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
)
WHERE mention LIKE '@%'
GROUP BY mention
HAVING posts_count >= 3
ORDER BY posts_count DESC;
```

### 5. Анализ контента
```sql
-- Анализ длины сообщений
SELECT 
    CASE 
        WHEN length(text) < 100 THEN 'short'
        WHEN length(text) < 300 THEN 'medium'
        WHEN length(text) < 500 THEN 'long'
        ELSE 'very_long'
    END as message_length,
    count() as count,
    avg(views) as avg_views,
    avg(forwards) as avg_forwards
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY message_length
ORDER BY count DESC;

-- Анализ медиа контента
SELECT 
    media_type,
    count() as count,
    avg(views) as avg_views,
    avg(forwards) as avg_forwards
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
AND media_type != ''
GROUP BY media_type
ORDER BY count DESC;
```

### 6. Анализ реакций
```sql
-- Анализ реакций по типам
SELECT 
    reaction_type,
    sum(reaction_count) as total_reactions,
    count() as posts_with_reaction,
    avg(reaction_count) as avg_reactions_per_post
FROM (
    SELECT 
        arrayJoin(mapKeys(reactions)) as reaction_type,
        reactions[reaction_type] as reaction_count
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
    AND reactions != map()
)
GROUP BY reaction_type
ORDER BY total_reactions DESC;

-- Корреляция между реакциями и просмотрами
SELECT 
    views_bucket,
    avg(total_reactions) as avg_reactions,
    count() as posts_count
FROM (
    SELECT 
        CASE 
            WHEN views < 100 THEN '0-100'
            WHEN views < 500 THEN '100-500'
            WHEN views < 1000 THEN '500-1000'
            WHEN views < 2000 THEN '1000-2000'
            ELSE '2000+'
        END as views_bucket,
        arraySum(mapValues(reactions)) as total_reactions
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
)
GROUP BY views_bucket
ORDER BY views_bucket;
```

## Специализированные запросы

### 7. Анализ вакансий
```sql
-- Поиск вакансий по уровню
SELECT 
    text,
    date,
    views,
    hashtags
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
AND (
    has(text, 'senior') OR 
    has(text, 'lead') OR 
    has(text, 'principal')
)
ORDER BY views DESC
LIMIT 20;

-- Анализ удаленной работы
SELECT 
    count() as remote_jobs,
    avg(views) as avg_views,
    sum(views) as total_views
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
AND (
    has(text, 'remote') OR 
    has(text, 'work from home') OR 
    has(text, 'distributed')
);
```

### 8. Географический анализ
```sql
-- Анализ локаций (если есть в тексте)
SELECT 
    location,
    count() as jobs_count,
    avg(views) as avg_views
FROM (
    SELECT 
        extractGroups(text, '([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)')[1] as location,
        views
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
    AND match(text, '[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*')
)
WHERE location != ''
GROUP BY location
ORDER BY jobs_count DESC
LIMIT 20;
```

## Агрегированные отчеты

### 9. Еженедельный отчет
```sql
-- Сводка за неделю
SELECT 
    toMonday(date) as week_start,
    count() as total_posts,
    sum(views) as total_views,
    avg(views) as avg_views_per_post,
    countIf(length(hashtags) > 0) as posts_with_hashtags,
    countIf(length(mentions) > 0) as posts_with_mentions,
    countIf(length(links) > 0) as posts_with_links
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY
GROUP BY week_start
ORDER BY week_start;
```

### 10. Топ-тренды
```sql
-- Топ-10 трендов за месяц
WITH trends AS (
    SELECT 
        hashtag,
        count() as mentions,
        sum(views) as total_views,
        countDistinct(toDate(date)) as active_days
    FROM (
        SELECT 
            arrayJoin(hashtags) as hashtag,
            views,
            date
        FROM datascience_jobs 
        WHERE date >= now() - INTERVAL 30 DAY
    )
    GROUP BY hashtag
)
SELECT 
    hashtag,
    mentions,
    total_views,
    active_days,
    total_views / mentions as avg_views_per_mention
FROM trends
ORDER BY mentions DESC, total_views DESC
LIMIT 10;
```

## Дашборд метрики

### 11. KPI дашборд
```sql
-- Основные метрики для дашборда
SELECT 
    'Total Posts' as metric,
    toString(count()) as value
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY

UNION ALL

SELECT 
    'Total Views' as metric,
    toString(sum(views)) as value
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY

UNION ALL

SELECT 
    'Avg Views per Post' as metric,
    toString(round(avg(views), 2)) as value
FROM datascience_jobs 
WHERE date >= now() - INTERVAL 30 DAY

UNION ALL

SELECT 
    'Most Popular Technology' as metric,
    hashtag as value
FROM (
    SELECT 
        arrayJoin(hashtags) as hashtag,
        count() as mentions
    FROM datascience_jobs 
    WHERE date >= now() - INTERVAL 30 DAY
    GROUP BY hashtag
    ORDER BY mentions DESC
    LIMIT 1
);
```

## Заключение

Эти запросы позволяют:
- **Отслеживать тренды** в Data Science индустрии
- **Анализировать популярность** технологий и компаний
- **Изучать поведение** аудитории канала
- **Выявлять паттерны** в публикациях
- **Создавать отчеты** для бизнес-анализа

Регулярное выполнение этих запросов поможет понять динамику рынка Data Science вакансий и технологий.
