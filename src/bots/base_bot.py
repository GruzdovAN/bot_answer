"""
Базовый класс для всех типов ботов
"""
import asyncio
import os
from typing import Dict, Any, Optional
from telethon import TelegramClient, events
from ..config.settings import config
from ..config.logging_config import get_logger
from ..utils.permissions import check_bot_permissions, format_error_message
from ..database.database import db_manager

logger = get_logger("base_bot")


class BaseBot:
    """Базовый класс для всех ботов"""
    
    def __init__(self, name: str):
        """
        Инициализация базового бота
        
        Args:
            name: Имя бота для идентификации
        """
        self.name = name
        self.reader_client = None
        self.bot_client = None
        self.stats = {
            'total_messages': 0,
            'responses_sent': 0,
            'keywords_found': {}
        }
        self.db_session = None
        self.chat_db_id = None
    
    async def start(self):
        """Запуск бота"""
        # Создаем клиенты с правильными путями к сессиям
        session_dir = os.path.join(os.getcwd(), 'sessions')
        os.makedirs(session_dir, exist_ok=True)
        
        reader_session = os.path.join(session_dir, f'{self.name}_reader')
        bot_session = os.path.join(session_dir, f'{self.name}_bot')
        
        self.reader_client = TelegramClient(reader_session, config.API_ID, config.API_HASH)
        self.bot_client = TelegramClient(bot_session, config.API_ID, config.API_HASH)
        
        # Запускаем клиенты
        try:
            # Проверяем, есть ли уже сессия для reader
            if os.path.exists(f"{reader_session}.session"):
                logger.info("Используем существующую сессию для reader")
                await self.reader_client.start()
            else:
                logger.info("Создаем новую сессию для reader")
                await self.reader_client.start(config.PHONE_NUMBER)
            
            # Бот всегда использует токен
            await self.bot_client.start(bot_token=config.BOT_TOKEN)
        except Exception as e:
            logger.error(f"Ошибка авторизации: {e}")
            return False
        
        logger.info(f"Запуск {self.name}")
        logger.info(f"Читаем через: {config.PHONE_NUMBER}")
        
        if config.USE_USER_ACCOUNT:
            logger.info("Отвечаем от имени пользователя")
            # Проверяем права пользователя в чате
            logger.info("Проверка прав пользователя...")
            if not await check_bot_permissions(self.reader_client, config.CHANNEL_USERNAME):
                logger.error("Пользователь не может работать в этом чате. Завершение работы.")
                return False
        else:
            logger.info(f"Отвечаем через бота: {config.BOT_TOKEN[:10]}...")
            # Проверяем права бота в чате
            logger.info("Проверка прав бота...")
            if not await check_bot_permissions(self.bot_client, config.CHANNEL_USERNAME):
                logger.error("Бот не может работать в этом чате. Завершение работы.")
                return False
        
        # Инициализируем базу данных
        try:
            self.db_session = db_manager.get_session()
            # Получаем или создаем чат в базе данных
            # Используем reader_client для получения информации о чате
            chat_entity = await self.reader_client.get_entity(config.CHANNEL_USERNAME)
            self.chat_db_id = db_manager.get_or_create_chat(
                self.db_session,
                telegram_id=chat_entity.id,
                username=getattr(chat_entity, 'username', None),
                title=getattr(chat_entity, 'title', None),
                chat_type=chat_entity.__class__.__name__.lower()
            ).id
            logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            # Продолжаем работу без базы данных
            self.db_session = None
        
        return True
    
    async def stop(self):
        """Остановка бота"""
        if self.reader_client:
            await self.reader_client.disconnect()
        if self.bot_client:
            await self.bot_client.disconnect()
        if self.db_session:
            db_manager.close_session(self.db_session)
    
    async def send_response(self, response: str) -> bool:
        """
        Отправляет ответ в чат
        
        Args:
            response: Текст ответа
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            if config.USE_USER_ACCOUNT:
                # Отправляем от имени пользователя
                await self.reader_client.send_message(config.CHANNEL_USERNAME, response)
                logger.info(f"Ответ отправлен от имени пользователя: {response[:50]}...")
            else:
                # Отправляем от имени бота
                await self.bot_client.send_message(config.CHANNEL_USERNAME, response)
                logger.info(f"Ответ отправлен от имени бота: {response[:50]}...")
            
            self.stats['responses_sent'] += 1
            return True
        except Exception as e:
            logger.error(format_error_message(e, config.CHANNEL_USERNAME))
            return False
    
    def update_stats(self, keyword: str = None):
        """
        Обновляет статистику
        
        Args:
            keyword: Найденное ключевое слово
        """
        self.stats['total_messages'] += 1
        if keyword:
            self.stats['keywords_found'][keyword] = self.stats['keywords_found'].get(keyword, 0) + 1
    
    def save_message_to_db(self, message_data: Dict[str, Any]) -> Optional[int]:
        """
        Сохраняет сообщение в базу данных
        
        Args:
            message_data: Данные сообщения
            
        Returns:
            int or None: ID сообщения в базе данных
        """
        if not self.db_session or not self.chat_db_id:
            return None
        
        try:
            # Получаем или создаем пользователя
            user_id = None
            if message_data.get('user_id'):
                user = db_manager.get_or_create_user(
                    self.db_session,
                    telegram_id=message_data['user_id'],
                    username=message_data.get('username'),
                    first_name=message_data.get('first_name'),
                    last_name=message_data.get('last_name'),
                    is_bot=message_data.get('is_bot', False)
                )
                user_id = user.id
            
            # Сохраняем сообщение
            message = db_manager.save_message(
                self.db_session,
                telegram_id=message_data['telegram_id'],
                chat_id=self.chat_db_id,
                user_id=user_id,
                text=message_data.get('text'),
                message_type=message_data.get('message_type', 'text'),
                is_bot_response=message_data.get('is_bot_response', False),
                raw_data=message_data.get('raw_data')
            )
            return message.id
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения в БД: {e}")
            return None
    
    def save_bot_response_to_db(self, original_message_id: int, response_text: str,
                               response_type: str = 'auto', trigger_keyword: str = None,
                               response_time_ms: int = None, is_successful: bool = True,
                               error_message: str = None) -> Optional[int]:
        """
        Сохраняет ответ бота в базу данных
        
        Args:
            original_message_id: ID исходного сообщения
            response_text: Текст ответа
            response_type: Тип ответа
            trigger_keyword: Ключевое слово-триггер
            response_time_ms: Время ответа в миллисекундах
            is_successful: Успешность ответа
            error_message: Сообщение об ошибке
            
        Returns:
            int or None: ID ответа в базе данных
        """
        if not self.db_session:
            return None
        
        try:
            response = db_manager.save_bot_response(
                self.db_session,
                original_message_id=original_message_id,
                response_text=response_text,
                response_type=response_type,
                trigger_keyword=trigger_keyword,
                response_time_ms=response_time_ms,
                is_successful=is_successful,
                error_message=error_message
            )
            return response.id
        except Exception as e:
            logger.error(f"Ошибка сохранения ответа бота в БД: {e}")
            return None
    
    def _safe_serialize_message(self, message):
        """Безопасная сериализация сообщения для JSON"""
        try:
            if hasattr(message, 'to_dict'):
                data = message.to_dict()
                # Конвертируем datetime объекты в строки
                return self._convert_datetime_to_string(data)
            return None
        except Exception as e:
            logger.warning(f"Ошибка сериализации сообщения: {e}")
            return None
    
    def _convert_datetime_to_string(self, obj):
        """Рекурсивно конвертирует datetime объекты в строки"""
        if isinstance(obj, dict):
            return {key: self._convert_datetime_to_string(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetime_to_string(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime объекты
            return obj.isoformat()
        else:
            return obj

    def print_stats(self):
        """Выводит статистику работы бота"""
        logger.info("Итоговая статистика:")
        logger.info(f"   Всего сообщений: {self.stats['total_messages']}")
        logger.info(f"   Отправлено ответов: {self.stats['responses_sent']}")
        if self.stats['keywords_found']:
            logger.info(f"   Найденные ключевые слова: {self.stats['keywords_found']}")
    
    async def run_until_disconnected(self):
        """Запускает бота до отключения"""
        try:
            await self.reader_client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info(f"Остановка {self.name}")
            self.print_stats()
        except Exception as e:
            logger.error(f"Ошибка: {e}")
        finally:
            await self.stop()
