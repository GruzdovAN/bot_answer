-- Добавление поля llm_analysis в таблицу castings_messages
-- Этот скрипт нужно выполнить перед запуском контейнера

-- Проверяем, существует ли поле llm_analysis
-- Если нет, добавляем его
ALTER TABLE telegram_analytics.castings_messages 
ADD COLUMN IF NOT EXISTS llm_analysis JSON DEFAULT '{}';

-- Создаем индекс для быстрого поиска по llm_analysis
CREATE INDEX IF NOT EXISTS idx_castings_messages_llm_analysis 
ON telegram_analytics.castings_messages (llm_analysis) TYPE bloom_filter;

-- Проверяем структуру таблицы
DESCRIBE telegram_analytics.castings_messages;
