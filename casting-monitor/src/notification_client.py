"""
Клиент для отправки уведомлений в Telegram
"""

import asyncio
import logging
from typing import Dict, Any
import requests

class NotificationClient:
    def __init__(self, bot_token: str, notification_chat_id: str = "@gruzdovan"):
        self.bot_token = bot_token
        self.notification_chat_id = notification_chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.logger = logging.getLogger(__name__)
    
    async def send_new_message_notification(self, message_data: Dict[str, Any], llm_result: Dict[str, Any] = None):
        """Отправка уведомления о новом сообщении в канале"""
        try:
            # Формирование текста уведомления
            notification_text = self._format_notification(message_data, llm_result)
            
            # Отправка сообщения
            await self._send_message(notification_text)
            
            self.logger.info(f"Уведомление отправлено в {self.notification_chat_id}")
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомления: {e}")
    
    def _format_notification(self, message_data: Dict[str, Any], llm_result: Dict[str, Any] = None) -> str:
        """Форматирование текста уведомления"""
        channel_title = message_data.get('channel_title', 'Неизвестный канал')
        channel_username = message_data.get('channel_username', 'N/A')
        message_text = message_data.get('text', '')
        
        # Обрезаем текст сообщения если он слишком длинный
        if len(message_text) > 200:
            message_text = message_text[:200] + "..."
        
        notification = f"🔔 **Новое сообщение о кастинге**\n\n"
        notification += f"📺 **Канал:** {channel_title}\n"
        notification += f"🔗 **Username:** {channel_username}\n\n"
        notification += f"📝 **Сообщение:**\n{message_text}\n\n"
        
        # Добавляем информацию о LLM анализе если есть
        if llm_result and llm_result.get('success'):
            extracted_data = llm_result.get('extracted_data', {})
            if extracted_data:
                notification += "🤖 **LLM Анализ:**\n"
                
                # Тип кастинга
                casting_type = extracted_data.get('casting_type', 'N/A')
                notification += f"🎬 Тип: {casting_type}\n"
                
                # Количество актеров
                actors = extracted_data.get('actors', [])
                if actors:
                    notification += f"👥 Актеров: {len(actors)}\n"
                
                # Локация
                location = extracted_data.get('location', 'N/A')
                if location != 'N/A':
                    notification += f"📍 Локация: {location}\n"
                
                # Оплата
                payment = extracted_data.get('payment', 'N/A')
                if payment != 'N/A':
                    notification += f"💰 Оплата: {payment}\n"
                
                notification += "\n"
        else:
            notification += "⚠️ LLM анализ не выполнен\n\n"
        
        notification += f"⏰ Время: {message_data.get('date', 'N/A')}"
        
        return notification
    
    async def _send_message(self, text: str):
        """Отправка сообщения через Telegram Bot API"""
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': self.notification_chat_id,
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        # Используем asyncio для неблокирующего запроса
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(url, json=payload, timeout=10)
        )
        
        if response.status_code != 200:
            raise Exception(f"Telegram API error: {response.text}")
    
    async def send_error_notification(self, error_message: str, channel_info: str = ""):
        """Отправка уведомления об ошибке"""
        try:
            text = f"❌ **Ошибка в мониторинге кастингов**\n\n"
            text += f"🔍 **Детали:** {error_message}\n"
            if channel_info:
                text += f"📺 **Канал:** {channel_info}\n"
            text += f"⏰ **Время:** {asyncio.get_event_loop().time()}"
            
            await self._send_message(text)
            self.logger.info("Уведомление об ошибке отправлено")
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомления об ошибке: {e}")
    
    async def close(self):
        """Закрытие клиента"""
        pass
