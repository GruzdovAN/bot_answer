-- Инициализация базы данных для Telegram бота
-- Этот скрипт выполняется при первом запуске PostgreSQL контейнера

-- Создаем расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Создаем индексы для оптимизации
-- (Таблицы будут созданы через SQLAlchemy)

-- Настройки для производительности
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Создаем пользователя для приложения (опционально)
-- CREATE USER bot_user WITH PASSWORD 'bot_password';
-- GRANT ALL PRIVILEGES ON DATABASE telegram_bot TO bot_user;

-- Логируем успешную инициализацию
DO $$
BEGIN
    RAISE NOTICE 'База данных telegram_bot инициализирована успешно';
END $$;
