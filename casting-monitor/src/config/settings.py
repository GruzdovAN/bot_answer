"""
Настройки приложения
"""

import os
from typing import Optional

class Settings:
    # Telegram API (из существующего .env)
    API_ID_TG: int = int(os.getenv('API_ID_TG', '0'))
    API_HASH_TG: str = os.getenv('API_HASH_TG', '')
    PHONE_NUMBER: str = os.getenv('PHONE_NUMBER', '')
    
    # ClickHouse (из существующего .env)
    CLICKHOUSE_HOST: str = os.getenv('CLICKHOUSE_HOST', 'clickhouse')
    CLICKHOUSE_PORT: int = int(os.getenv('CLICKHOUSE_PORT', '8123'))
    CLICKHOUSE_USER: str = os.getenv('CLICKHOUSE_USER', 'clickhouse_admin')
    CLICKHOUSE_PASSWORD: str = os.getenv('CLICKHOUSE_PASSWORD', '')
    CLICKHOUSE_DB: str = os.getenv('CLICKHOUSE_DB', 'telegram_analytics')
    
    # LLM (из существующего .env)
    DEEPSEEK_API_KEY: str = os.getenv('DEEPSEEK_API_KEY', '')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'deepseek-chat')
    
    # Мониторинг
    MONITOR_INTERVAL: int = int(os.getenv('MONITOR_INTERVAL', '5'))
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '10'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    def validate(self):
        """Проверка обязательных настроек"""
        required = [
            'API_ID_TG', 'API_HASH_TG', 'PHONE_NUMBER',
            'CLICKHOUSE_PASSWORD', 'DEEPSEEK_API_KEY'
        ]
        
        missing = []
        for field in required:
            if not getattr(self, field):
                missing.append(field)
        
        if missing:
            raise ValueError(f"Отсутствуют обязательные настройки: {', '.join(missing)}")
