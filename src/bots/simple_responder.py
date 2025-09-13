"""
Простой автоответчик с базовыми правилами ответов
"""
import asyncio
from telethon import events
from .base_bot import BaseBot
from ..config.settings import config
from ..config.logging_config import get_logger

logger = get_logger("simple_responder")


class SimpleResponder(BaseBot):
    """Простой автоответчик с базовыми правилами"""
    
    def __init__(self):
        super().__init__("simple_auto_responder")
        self.responses = self._get_responses()
        self.start_time = None  # Время запуска бота
    
    def _get_responses(self):
        """Возвращает простые правила ответов"""
        return {
            'привет': "👋 Привет! Я бот-помощник!",
            'как дела': "😊 У меня всё отлично! А у тебя?",
            'помощь': "🆘 Чем могу помочь?",
            'спасибо': "😊 Пожалуйста!",
            'пока': "👋 До свидания!"
        }
    
    def _find_response(self, text: str) -> str:
        """
        Находит подходящий ответ для текста
        
        Args:
            text: Текст сообщения
            
        Returns:
            str or None: Ответ или None
        """
        text_lower = text.lower().strip()
        
        for keyword, reply in self.responses.items():
            if keyword in text_lower:
                return reply
        
        return None
    
    def _find_trigger_keyword(self, text: str) -> str:
        """
        Находит ключевое слово-триггер в тексте
        
        Args:
            text: Текст сообщения
            
        Returns:
            str: Найденное ключевое слово
        """
        text_lower = text.lower().strip()
        
        for keyword in self.responses.keys():
            if keyword in text_lower:
                return keyword
        
        return None
    
    async def start_monitoring(self):
        """Запускает мониторинг сообщений"""
        if not await self.start():
            return
        
        # Записываем время запуска
        import time
        self.start_time = time.time()
        
        logger.info("Запуск автоответчика с отдельным ботом")
        
        @self.reader_client.on(events.NewMessage(chats=config.CHANNEL_USERNAME))
        async def simple_response_handler(event):
            message = event.message
            text = message.text or ""
            
            if not text.strip():
                return
            
            # Проверяем, что сообщение не от самого бота
            logger.info(f"DEBUG: sender_id={message.sender_id}, text='{text}'")
            if message.sender_id is not None:
                try:
                    bot_me = await self.bot_client.get_me()
                    logger.info(f"DEBUG: bot_me.id={bot_me.id}, sender_id={message.sender_id}")
                    if message.sender_id == bot_me.id:
                        logger.info(f"ИГНОРИРУЕМ сообщение от самого бота: {text}")
                        return
                except Exception as e:
                    logger.warning(f"Не удалось получить информацию о боте: {e}")
                    # Если не можем получить ID бота, пропускаем проверку
            else:
                logger.info(f"DEBUG: sender_id is None, пропускаем проверку")
            
            # Проверяем, что сообщение отправлено после запуска бота
            if self.start_time and message.date.timestamp() < self.start_time:
                logger.debug(f"Игнорируем старое сообщение (до запуска бота): {text}")
                return
            
            # Дополнительная проверка: игнорируем сообщения, которые являются ответами бота
            for response_text in self.responses.values():
                if text.strip() == response_text.strip():
                    logger.info(f"ИГНОРИРУЕМ сообщение-ответ бота: {text}")
                    return
            
            # Подготавливаем данные для базы данных
            message_data = {
                'telegram_id': message.id,
                'user_id': message.sender_id,
                'username': getattr(message.sender, 'username', None) if message.sender else None,
                'first_name': getattr(message.sender, 'first_name', None) if message.sender else None,
                'last_name': getattr(message.sender, 'last_name', None) if message.sender else None,
                'is_bot': getattr(message.sender, 'bot', False) if message.sender else False,
                'text': text,
                'message_type': 'text',
                'is_bot_response': False,
                'raw_data': self._safe_serialize_message(message)
            }
            
            # Сохраняем сообщение в базу данных
            message_db_id = self.save_message_to_db(message_data)
            
            # Обновляем статистику
            self.update_stats()
            
            # Ищем подходящий ответ
            response = self._find_response(text)
            
            if response:
                start_time = asyncio.get_event_loop().time()
                # Отправляем ответ
                success = await self.send_response(response)
                response_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
                
                if success:
                    # Сохраняем ответ бота в базу данных
                    if message_db_id:
                        self.save_bot_response_to_db(
                            original_message_id=message_db_id,
                            response_text=response,
                            response_type='simple',
                            trigger_keyword=self._find_trigger_keyword(text),
                            response_time_ms=response_time,
                            is_successful=True
                        )
                    
                    logger.info(f"Сообщение #{self.stats['total_messages']}: {message.text}")
                    logger.info(f"Ответ бота: {response}")
                    logger.info(f"Статистика: {self.stats['responses_sent']}/{self.stats['total_messages']}")
                    logger.info(f"Время ответа: {response_time}мс")
                else:
                    # Сохраняем неудачный ответ
                    if message_db_id:
                        self.save_bot_response_to_db(
                            original_message_id=message_db_id,
                            response_text=response,
                            response_type='simple',
                            trigger_keyword=self._find_trigger_keyword(text),
                            response_time_ms=response_time,
                            is_successful=False,
                            error_message="Ошибка отправки сообщения"
                        )
            else:
                logger.debug(f"Сообщение #{self.stats['total_messages']}: {message.text} (без ответа)")
        
        logger.info("Мониторинг запущен. Нажмите Ctrl+C для остановки")
        if config.USE_USER_ACCOUNT:
            logger.info("Отвечаем от имени пользователя")
        else:
            logger.info(f"Отвечаем через бота: {config.BOT_TOKEN[:10]}...")
        
        await self.run_until_disconnected()
