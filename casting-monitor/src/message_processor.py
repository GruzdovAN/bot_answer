"""
Модуль обработки сообщений о кастингах
"""

import asyncio
import logging
from typing import Dict, Any
from telethon.tl.types import Message

from llm_client import LLMClient
from clickhouse_client import ClickHouseClient
from config.settings import Settings

class MessageProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
        self.clickhouse_client = ClickHouseClient(settings)
        self.logger = logging.getLogger(__name__)
    
    async def process_message(self, message: Message):
        """Полная обработка сообщения"""
        try:
            # 1. Подготовка данных сообщения
            message_data = self._prepare_message_data(message)
            
            # 2. Сохранение в ClickHouse
            await self._save_to_clickhouse(message_data)
            
            # 3. LLM анализ
            llm_result = await self._analyze_with_llm(message_data['text'])
            
            # 4. Обновление записи с LLM результатом
            await self._update_with_llm_result(message_data['message_id'], llm_result)
            
            self.logger.info(f"Сообщение {message_data['message_id']} обработано успешно")
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке сообщения: {e}")
            raise
    
    def _prepare_message_data(self, message: Message) -> Dict[str, Any]:
        """Подготовка данных сообщения для сохранения"""
        return {
            'message_id': message.id,
            'channel_id': message.chat.id,
            'channel_title': getattr(message.chat, 'title', ''),
            'channel_username': getattr(message.chat, 'username', ''),
            'date': message.date,
            'text': message.text or '',
            'views': getattr(message, 'views', 0),
            'forwards': getattr(message, 'forwards', 0),
            'replies': getattr(message, 'replies', 0),
            'media_type': self._get_media_type(message),
            'has_photo': 1 if message.photo else 0,
            'has_video': 1 if message.video else 0,
            'has_document': 1 if message.document else 0,
        }
    
    def _get_media_type(self, message: Message) -> str:
        """Определение типа медиа"""
        if message.photo:
            return 'photo'
        elif message.video:
            return 'video'
        elif message.document:
            return 'document'
        else:
            return 'text'
    
    async def _save_to_clickhouse(self, message_data: Dict[str, Any]):
        """Сохранение сообщения в ClickHouse"""
        await self.clickhouse_client.insert_castings_message(message_data)
        self.logger.debug(f"Сообщение {message_data['message_id']} сохранено в ClickHouse")
    
    async def _analyze_with_llm(self, text: str) -> Dict[str, Any]:
        """Анализ текста через LLM"""
        if not text.strip():
            return {'success': False, 'error': 'Пустой текст сообщения'}
        
        return await self.llm_client.process_message(text)
    
    async def _update_with_llm_result(self, message_id: int, llm_result: Dict[str, Any]):
        """Обновление записи с результатом LLM анализа"""
        await self.clickhouse_client.update_llm_analysis(message_id, llm_result)
        self.logger.debug(f"LLM результат для сообщения {message_id} сохранен")
    
    async def close(self):
        """Закрытие соединений"""
        await self.llm_client.close()
        await self.clickhouse_client.close()
