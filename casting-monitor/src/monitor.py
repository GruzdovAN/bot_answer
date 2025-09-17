"""
Модуль мониторинга Telegram каналов с кастингами
"""

import asyncio
import logging
from typing import List, Dict, Any
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Message

from message_processor import MessageProcessor
from config.settings import Settings
from config.channels import get_monitored_channels

class CastingMonitor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self.processor = MessageProcessor(settings)
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    async def start(self):
        """Запуск мониторинга"""
        self.logger.info("Инициализация Telegram клиента...")
        
        # Инициализация Telegram клиента
        self.client = TelegramClient(
            '/app/sessions/reader',
            self.settings.API_ID_TG,
            self.settings.API_HASH_TG
        )
        
        await self.client.start()
        self.logger.info("Telegram клиент запущен")
        
        # Получение списка каналов для мониторинга
        try:
            channel_usernames = get_monitored_channels()
            self.logger.info(f"Получены каналы: {channel_usernames}")
            self.logger.info(f"Мониторинг {len(channel_usernames)} каналов")
        except Exception as e:
            self.logger.error(f"Ошибка при получении каналов: {e}")
            return
        
        # Получение объектов каналов
        channels = []
        for channel_identifier in channel_usernames:
            try:
                entity = await self.client.get_entity(channel_identifier)
                channels.append(entity)
                self.logger.info(f"Добавлен канал: {channel_identifier}")
            except Exception as e:
                self.logger.warning(f"Не удалось получить канал {channel_identifier}: {e}")
        
        if not channels:
            self.logger.error("Не удалось получить ни одного канала для мониторинга")
            return
        
        # Регистрация обработчиков событий
        @self.client.on(events.NewMessage(chats=channels))
        async def handle_new_message(event):
            await self.process_new_message(event.message)
        
        self.is_running = True
        self.logger.info("Мониторинг запущен, ожидание сообщений...")
        
        # Основной цикл
        while self.is_running:
            await asyncio.sleep(1)
    
    async def process_new_message(self, message: Message):
        """Обработка нового сообщения"""
        try:
            self.logger.info(f"Новое сообщение из канала {message.chat.username}")
            
            # Обработка сообщения
            await self.processor.process_message(message)
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке сообщения: {e}")
    
    async def stop(self):
        """Остановка мониторинга"""
        self.logger.info("Остановка мониторинга...")
        self.is_running = False
        
        if self.client:
            await self.client.disconnect()
            self.logger.info("Telegram клиент отключен")
        
        await self.processor.close()
        self.logger.info("Мониторинг остановлен")
