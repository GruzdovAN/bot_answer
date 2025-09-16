# Конфигурация базы данных ClickHouse

# Основные настройки подключения
CLICKHOUSE_CONFIG = {
    "host": "localhost",
    "port": "8123",
    "user": "clickhouse_admin",
    "password": "your_clickhouse_password_here",
    "database": "telegram_analytics"  # Используем существующую базу
}

# Конфигурация таблиц
TABLES_CONFIG = {
    # Таблица для общих сообщений Telegram
    "telegram_messages": {
        "table_name": "telegram_messages",
        "description": "Общие сообщения из Telegram каналов",
        "fields": [
            "message_id UInt64",
            "channel_username String",
            "date DateTime",
            "text String",
            "views UInt32",
            "forwards UInt32",
            "hashtags Array(String)",
            "mentions Array(String)",
            "links Array(String)",
            "technologies Array(String)",
            "companies Array(String)",
            "created_at DateTime DEFAULT now()"
        ]
    },
    
    # Таблица для кастинговых сообщений
    "castings_messages": {
        "table_name": "castings_messages",
        "description": "Сообщения из кастинговых каналов с парсированными данными",
        "fields": [
            "message_id UInt64",
            "channel_id UInt64",
            "channel_title String",
            "channel_username String",
            "date DateTime",
            "text String",
            "views UInt32",
            "forwards UInt32",
            "replies UInt32",
            "media_type String",
            "has_photo UInt8",
            "has_video UInt8",
            "has_document UInt8",
            # Парсированные поля для кастингов
            "casting_type String",
            "age_range String",
            "location String",
            "contact_info String",
            "deadline String",
            "payment String",
            "project_name String",
            "parsed_at DateTime DEFAULT now()"
        ]
    },
    
    # Таблица для информации о каналах
    "channels_info": {
        "table_name": "channels_info",
        "description": "Информация о каналах",
        "fields": [
            "channel_id UInt64",
            "title String",
            "username String",
            "type String",
            "participants_count UInt32",
            "description String",
            "is_verified UInt8",
            "is_scam UInt8",
            "is_fake UInt8",
            "created_date DateTime",
            "discovered_at DateTime DEFAULT now()"
        ]
    }
}

# SQL для создания таблиц
CREATE_TABLES_SQL = {
    "castings_messages": """
        CREATE TABLE IF NOT EXISTS {database}.castings_messages (
            message_id UInt64,
            channel_id UInt64,
            channel_title String,
            channel_username String,
            date DateTime,
            text String,
            views UInt32,
            forwards UInt32,
            replies UInt32,
            media_type String,
            has_photo UInt8,
            has_video UInt8,
            has_document UInt8,
            casting_type String,
            age_range String,
            location String,
            contact_info String,
            deadline String,
            payment String,
            project_name String,
            parsed_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (channel_id, date)
        PARTITION BY toYYYYMM(date)
    """,
    
    "channels_info": """
        CREATE TABLE IF NOT EXISTS {database}.channels_info (
            channel_id UInt64,
            title String,
            username String,
            type String,
            participants_count UInt32,
            description String,
            is_verified UInt8,
            is_scam UInt8,
            is_fake UInt8,
            created_date DateTime,
            discovered_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY channel_id
    """
}
