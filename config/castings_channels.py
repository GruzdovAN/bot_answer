# Конфигурация для каналов из папки @castings
# Автоматически обновлено: 2025-09-17T00:51:20.971931

CASTINGS_CHANNELS = {
    "1933304552": {
        "username": "@castingsactors",
        "title": "Кастинги для актеров в Москве",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 26720,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971903"
    },
    "1278379037": {
        "username": "@castings",
        "title": "Кастинги в Москве",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 61848,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971915"
    },
    "2137328150": {
        "username": None,
        "title": "Кастинги для актеров и моделей в Москве",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 18040,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971918"
    },
    "1764655029": {
        "username": "@castingsmsc",
        "title": "Кастинги для маркетплейсов и каталогов одежды в Москве",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 26213,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971921"
    },
    "2569890697": {
        "username": None,
        "title": "Кастинг ПРО | Москва",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 6883,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971923"
    },
    "2764210937": {
        "username": None,
        "title": "Кастинги для девушек | Москва",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 5930,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971925"
    },
    "2090693689": {
        "username": None,
        "title": "Кастинги в рекламу | Москва",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 18800,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971927"
    },
    "2407554401": {
        "username": None,
        "title": "Кастинги Москва | Актеры и модели",
        "enabled": True,
        "parser_type": "casting_parser",
        "days_back": 7,
        "batch_size": 50,
        "auto_update": True,
        "participants_count": 10834,
        "description": "",
        "is_verified": False,
        "discovered_at": "2025-09-17T00:51:20.971929"
    }
}

# Настройки для чтения каналов из папки @castings
CASTINGS_SETTINGS = {
    "folder_name": "@castings",
    "default_days_back": 7,
    "default_batch_size": 50,
    "auto_discovery": True,
    "update_interval_hours": 24,
    "keywords": [
        "casting",
        "кастинг",
        "audition",
        "просмотр",
        "talent",
        "модель",
        "актер",
        "актриса"
    ]
}

# Парсер для кастинговых сообщений
CASTING_PARSER_CONFIG = {
    "extract_fields": [
        "casting_type",
        "age_range",
        "location",
        "requirements",
        "contact_info",
        "deadline",
        "payment",
        "project_name",
        "director",
        "production_company"
    ],
    "patterns": {
        "age_range": "возраст[а-я]*\s*:?\s*(\d+[-–]\d+|\d+\+)",
        "location": "(москва|санкт-петербург|спб|мск|питер|россия)",
        "contact": "(телефон|тел|контакт|звонить|писать)[\s:]*([+\d\s\-\(\)]+)",
        "deadline": "(до|до\s+\d+|срок|дедлайн)[\s:]*(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "payment": "(оплата|гонорар|бюджет)[\s:]*(\d+[,\s]*\d*[,\s]*\d*)\s*(руб|₽|долл|$|евро|€)"
    }
}
