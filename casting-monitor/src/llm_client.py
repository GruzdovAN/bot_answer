"""
Клиент для работы с LLM API
"""

import asyncio
import logging
from typing import Dict, Any

class LLMClient:
    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
    
    async def process_message(self, text: str) -> Dict[str, Any]:
        """Обработка сообщения через LLM"""
        try:
            self.logger.debug(f"Отправка текста в LLM: {text[:100]}...")
            
            # Импортируем функцию из основного проекта
            import sys
            sys.path.append('/app/src_modules')
            from llm.deepseek import process_telegram_message
            
            # Используем существующую функцию из deepseek.py
            result = process_telegram_message(text, self.settings.LLM_MODEL)
            
            self.logger.debug(f"LLM анализ завершен: success={result['success']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка LLM анализа: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_message': text
            }
    
    async def close(self):
        """Закрытие клиента"""
        pass
