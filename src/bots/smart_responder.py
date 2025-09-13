"""
Умный автоответчик с продвинутыми правилами ответов
"""
import asyncio
from telethon import events
from .base_bot import BaseBot
from ..config.settings import config
from ..config.logging_config import get_logger

logger = get_logger("smart_responder")


class SmartResponder(BaseBot):
    """Умный автоответчик с приоритетными правилами"""
    
    def __init__(self):
        super().__init__("smart_auto_responder")
        self.response_rules = self._get_response_rules()
    
    def _get_response_rules(self):
        """Возвращает правила ответов с приоритетами"""
        return [
            {
                'keywords': ['как дела', 'как ты', 'что нового'],
                'response': "😊 Всё отлично! Работаю, мониторю сообщения. А у тебя как дела?",
                'priority': 1
            },
            {
                'keywords': ['помощь', 'помоги', 'нужна помощь'],
                'response': "🆘 Конечно помогу! Опиши подробнее, что нужно сделать?",
                'priority': 2
            },
            {
                'keywords': ['время', 'который час', 'сколько времени'],
                'response': f"🕐 Сейчас {asyncio.get_event_loop().time():.0f} секунд с начала работы бота!",
                'priority': 1
            },
            {
                'keywords': ['спасибо', 'благодарю', 'thanks'],
                'response': "😊 Пожалуйста! Рад помочь!",
                'priority': 1
            },
            {
                'keywords': ['привет', 'hello', 'hi', 'ку'],
                'response': "👋 Привет! Я здесь, слежу за сообщениями!",
                'priority': 1
            },
            {
                'keywords': ['пока', 'до свидания', 'bye'],
                'response': "👋 До свидания! Буду ждать новых сообщений!",
                'priority': 1
            }
        ]
    
    def _find_best_rule(self, text: str):
        """
        Находит лучшее правило для ответа на основе текста
        
        Args:
            text: Текст сообщения
            
        Returns:
            dict or None: Лучшее правило или None
        """
        text_lower = text.lower()
        
        # Ищем подходящее правило (с приоритетом)
        for rule in sorted(self.response_rules, key=lambda x: x['priority']):
            if any(keyword in text_lower for keyword in rule['keywords']):
                return rule
        
        return None
    
    def _get_matched_keyword(self, text: str, rule: dict) -> str:
        """
        Возвращает найденное ключевое слово из правила
        
        Args:
            text: Текст сообщения
            rule: Правило ответа
            
        Returns:
            str: Найденное ключевое слово
        """
        text_lower = text.lower()
        for keyword in rule['keywords']:
            if keyword in text_lower:
                return keyword
        return rule['keywords'][0]  # Возвращаем первое ключевое слово по умолчанию
    
    async def start_monitoring(self):
        """Запускает мониторинг сообщений"""
        if not await self.start():
            return
        
        logger.info(f"Запуск умного автоответчика для {config.CHANNEL_USERNAME}")
        
        @self.reader_client.on(events.NewMessage(chats=config.CHANNEL_USERNAME))
        async def smart_response_handler(event):
            message = event.message
            text = message.text or ""
            
            if not text.strip():
                return
            
            # Проверяем, что сообщение не от самого бота
            if message.sender_id is not None:
                try:
                    bot_me = await self.bot_client.get_me()
                    if message.sender_id == bot_me.id:
                        logger.debug(f"Игнорируем сообщение от самого бота: {text}")
                        return
                except Exception as e:
                    logger.warning(f"Не удалось получить информацию о боте: {e}")
                    # Если не можем получить ID бота, пропускаем проверку
            
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
            
            # Ищем подходящее правило
            best_rule = self._find_best_rule(text)
            
            if best_rule:
                start_time = asyncio.get_event_loop().time()
                # Отправляем ответ
                success = await self.send_response(best_rule['response'])
                response_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
                
                if success:
                    # Обновляем статистику ключевых слов
                    matched_keyword = self._get_matched_keyword(text, best_rule)
                    self.stats['keywords_found'][matched_keyword] = self.stats['keywords_found'].get(matched_keyword, 0) + 1
                    
                    # Сохраняем ответ бота в базу данных
                    if message_db_id:
                        self.save_bot_response_to_db(
                            original_message_id=message_db_id,
                            response_text=best_rule['response'],
                            response_type='smart',
                            trigger_keyword=matched_keyword,
                            response_time_ms=response_time,
                            is_successful=True
                        )
                    
                    logger.info(f"Сообщение #{self.stats['total_messages']}")
                    logger.info(f"   Текст: {text}")
                    logger.info(f"   Ответ: {best_rule['response']}")
                    logger.info(f"   Статистика: {self.stats['responses_sent']}/{self.stats['total_messages']} ответов")
                    logger.info(f"   Время ответа: {response_time}мс")
                else:
                    # Сохраняем неудачный ответ
                    if message_db_id:
                        self.save_bot_response_to_db(
                            original_message_id=message_db_id,
                            response_text=best_rule['response'],
                            response_type='smart',
                            trigger_keyword=matched_keyword,
                            response_time_ms=response_time,
                            is_successful=False,
                            error_message="Ошибка отправки сообщения"
                        )
            else:
                # Сообщение без ключевых слов
                logger.debug(f"Сообщение #{self.stats['total_messages']} (без ответа)")
                logger.debug(f"   Текст: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        logger.info("Умный автоответчик запущен. Нажмите Ctrl+C для остановки")
        logger.info(f"Читаем сообщения через: {config.PHONE_NUMBER}")
        if config.USE_USER_ACCOUNT:
            logger.info("Отвечаем от имени пользователя")
        else:
            logger.info(f"Отвечаем через бота: {config.BOT_TOKEN[:10]}...")
        
        await self.run_until_disconnected()
