"""
Простой автоответчик для группы с переменной окружения GROUP_NAME
"""
import asyncio
import os
from telethon import events
from .base_bot import BaseBot
from ..config.settings import config
from ..config.logging_config import get_logger
from ..database.database import db_manager
from ..utils.permissions import check_bot_permissions

logger = get_logger("group_responder")


class GroupResponder(BaseBot):
    """Простой автоответчик для группы с переменной окружения GROUP_NAME"""
    
    def __init__(self):
        super().__init__("group_auto_responder")
        self.responses = self._get_responses()
        self.start_time = None  # Время запуска бота
        self.group_name = os.getenv('GROUP_NAME')
        
        if not self.group_name:
            logger.error("Переменная окружения GROUP_NAME не задана!")
            raise ValueError("GROUP_NAME environment variable is required")
        
        # Валидируем формат GROUP_NAME
        self._validate_group_name()
    
    def _validate_group_name(self):
        """Валидирует формат GROUP_NAME"""
        if not self.group_name:
            return
        
        # Проверяем базовые форматы
        valid_formats = []
        
        # Формат с @
        if self.group_name.startswith('@'):
            valid_formats.append("публичная группа с @")
        # Числовой ID (начинается с -100)
        elif self.group_name.startswith('-100') and self.group_name[4:].isdigit():
            valid_formats.append("приватная группа с числовым ID")
        # Обычное имя без @
        elif self.group_name.replace('_', '').replace('.', '').isalnum():
            valid_formats.append("имя группы без @")
        else:
            logger.warning(f"Необычный формат GROUP_NAME: '{self.group_name}'")
            logger.warning("Рекомендуемые форматы:")
            logger.warning("- @group_username (для публичных групп)")
            logger.warning("- -1001234567890 (для приватных групп)")
            logger.warning("- group_username (без @)")
        
        if valid_formats:
            logger.info(f"Формат GROUP_NAME распознан как: {valid_formats[0]}")
    
    async def list_available_groups(self):
        """Показывает список доступных групп/чатов"""
        try:
            logger.info("Поиск доступных групп и чатов...")
            dialogs = await self.reader_client.get_dialogs()
            
            groups = []
            for dialog in dialogs:
                if hasattr(dialog.entity, 'megagroup') or hasattr(dialog.entity, 'broadcast'):
                    groups.append({
                        'title': getattr(dialog.entity, 'title', 'Без названия'),
                        'username': getattr(dialog.entity, 'username', None),
                        'id': dialog.entity.id,
                        'type': 'supergroup' if hasattr(dialog.entity, 'megagroup') else 'channel'
                    })
            
            if groups:
                logger.info(f"Найдено {len(groups)} групп/каналов:")
                for i, group in enumerate(groups, 1):
                    username_str = f" (@{group['username']})" if group['username'] else ""
                    logger.info(f"{i}. {group['title']}{username_str} (ID: {group['id']})")
            else:
                logger.warning("Группы не найдены. Убедитесь, что бот добавлен в группы.")
                
        except Exception as e:
            logger.error(f"Ошибка при получении списка групп: {e}")
    
    def _get_responses(self):
        """Возвращает простые правила ответов для группы"""
        return {
            'привет': "👋 Привет всем! Я бот-помощник группы!",
            'как дела': "😊 У меня всё отлично! А у вас как дела?",
            'помощь': "🆘 Чем могу помочь группе?",
            'спасибо': "😊 Пожалуйста! Рад помочь!",
            'пока': "👋 До свидания всем!",
            'добро пожаловать': "🎉 Добро пожаловать в нашу группу!",
            'правила': "📋 Правила группы можно найти в закрепленном сообщении",
            'админ': "👨‍💼 Обратитесь к администраторам группы за помощью",
            'спам': "🚫 Пожалуйста, не спамьте в группе",
            'оффтоп': "💬 Давайте обсудим это в личных сообщениях"
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
                # Добавляем подпись, если отвечаем от имени пользователя
                if config.USE_USER_ACCOUNT:
                    reply += "\n\n— Отвечает автоматически"
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
    
    async def send_response(self, response: str) -> bool:
        """
        Отправляет ответ в группу
        
        Args:
            response: Текст ответа
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            if config.USE_USER_ACCOUNT:
                # Отправляем от имени пользователя в группу
                await self.reader_client.send_message(self.group_name, response)
                logger.info(f"Ответ отправлен от имени пользователя в группу {self.group_name}: {response[:50]}...")
            else:
                # Отправляем от имени бота в группу
                await self.bot_client.send_message(self.group_name, response)
                logger.info(f"Ответ отправлен от имени бота в группу {self.group_name}: {response[:50]}...")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки ответа в группу {self.group_name}: {e}")
            return False
    
    async def start(self):
        """Переопределяем start для работы с группой"""
        # Инициализируем клиенты
        if not await super().start():
            return False
        
        # Проверяем права бота в группе (не в канале)
        if not config.USE_USER_ACCOUNT:
            logger.info("Проверка прав бота...")
            try:
                # Проверяем права в группе, а не в канале
                can_send = await check_bot_permissions(self.bot_client, self.group_name)
                if not can_send:
                    logger.error(f"Бот не может отправлять сообщения в группу {self.group_name}")
                    return False
                logger.info(f"Бот может отправлять сообщения в группу {self.group_name}")
            except Exception as e:
                logger.error(f"Ошибка проверки прав бота в группе {self.group_name}: {e}")
                return False
        
        # Инициализируем базу данных для группы
        try:
            group_entity = await self.reader_client.get_entity(self.group_name)
            self.chat_db_id = db_manager.get_or_create_chat(
                self.db_session,
                telegram_id=group_entity.id,
                username=getattr(group_entity, 'username', None),
                title=getattr(group_entity, 'title', None),
                chat_type=group_entity.__class__.__name__.lower()
            ).id
            logger.info(f"База данных настроена для группы: {self.group_name}")
        except Exception as e:
            logger.error(f"Ошибка настройки базы данных для группы: {e}")
            self.db_session = None
        
        return True
    
    async def start_monitoring(self):
        """Запускает мониторинг сообщений в группе"""
        if not await self.start():
            return
        
        # Проверяем, что группа существует и доступна
        try:
            logger.info(f"Проверка доступности группы: {self.group_name}")
            group_entity = await self.reader_client.get_entity(self.group_name)
            logger.info(f"Группа найдена: {getattr(group_entity, 'title', self.group_name)}")
        except Exception as e:
            logger.error(f"Ошибка при поиске группы '{self.group_name}': {e}")
            logger.error("Возможные причины:")
            logger.error("1. Группа не существует")
            logger.error("2. Бот не добавлен в группу")
            logger.error("3. Неправильный формат имени группы")
            logger.error("4. Группа приватная и нужен числовой ID")
            logger.error("")
            logger.error("Правильные форматы:")
            logger.error("- @group_username (для публичных групп)")
            logger.error("- -1001234567890 (для приватных групп)")
            logger.error("- group_username (без @ для некоторых случаев)")
            logger.error("")
            logger.error("Показываем доступные группы...")
            await self.list_available_groups()
            return
        
        # Записываем время запуска
        import time
        self.start_time = time.time()
        
        logger.info(f"Запуск автоответчика для группы: {self.group_name}")
        
        @self.reader_client.on(events.NewMessage(chats=self.group_name))
        async def group_response_handler(event):
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
                            response_type='group_simple',
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
                            response_type='group_simple',
                            trigger_keyword=self._find_trigger_keyword(text),
                            response_time_ms=response_time,
                            is_successful=False,
                            error_message="Ошибка отправки сообщения"
                        )
            else:
                logger.debug(f"Сообщение #{self.stats['total_messages']}: {message.text} (без ответа)")
        
        logger.info("Мониторинг группы запущен. Нажмите Ctrl+C для остановки")
        if config.USE_USER_ACCOUNT:
            logger.info("Отвечаем от имени пользователя")
        else:
            logger.info(f"Отвечаем через бота: {config.BOT_TOKEN[:10]}...")
        
        await self.run_until_disconnected()
    
    async def send_response(self, response: str) -> bool:
        """
        Отправляет ответ в группу
        
        Args:
            response: Текст ответа
            
        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            if config.USE_USER_ACCOUNT:
                # Отправляем от имени пользователя
                await self.reader_client.send_message(self.group_name, response)
                logger.info(f"Ответ отправлен от имени пользователя в группу {self.group_name}: {response[:50]}...")
            else:
                # Отправляем от имени бота
                await self.bot_client.send_message(self.group_name, response)
                logger.info(f"Ответ отправлен от имени бота в группу {self.group_name}: {response[:50]}...")
            
            self.stats['responses_sent'] += 1
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в группу {self.group_name}: {e}")
            return False
