"""
Клиент для работы с ClickHouse
"""

import asyncio
import logging
import json
from typing import Dict, Any
import requests

class ClickHouseClient:
    def __init__(self, settings):
        self.settings = settings
        self.base_url = f"http://{settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}"
        self.auth = (settings.CLICKHOUSE_USER, settings.CLICKHOUSE_PASSWORD)
        self.database = settings.CLICKHOUSE_DB
        self.logger = logging.getLogger(__name__)
    
    async def insert_castings_message(self, message_data: Dict[str, Any]):
        """Вставка сообщения о кастинге"""
        try:
            # Импортируем клиент из основного проекта
            import sys
            sys.path.append('/app/src_modules')
            from database.clickhouse_client import ClickHouseClient as BaseClient
            
            # Используем существующую логику
            base_client = BaseClient()
            base_client.insert_castings_messages([message_data])
            
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении в ClickHouse: {e}")
            raise
    
    async def update_llm_analysis(self, message_id: int, llm_result: Dict[str, Any]):
        """Обновление записи с результатом LLM анализа"""
        try:
            llm_json = json.dumps(llm_result, ensure_ascii=False)
            
            query = f"""
            ALTER TABLE {self.database}.castings_messages 
            UPDATE llm_analysis = '{llm_json}'
            WHERE message_id = {message_id}
            """
            
            response = requests.post(
                self.base_url,
                data=query,
                auth=self.auth,
                params={'database': self.database}
            )
            
            if response.status_code != 200:
                raise Exception(f"ClickHouse error: {response.text}")
            
            self.logger.debug(f"LLM анализ для сообщения {message_id} обновлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении LLM анализа: {e}")
            raise
    
    async def close(self):
        """Закрытие клиента"""
        pass
