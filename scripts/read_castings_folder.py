#!/usr/bin/env python3
"""
Скрипт для чтения всех каналов из папки @castings в Telegram
"""

import asyncio
import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

# Импортируем существующие компоненты
try:
    from src.database.clickhouse_client import ClickHouseClient
    from config.castings_channels import CASTINGS_SETTINGS, CASTING_PARSER_CONFIG
except ImportError as e:
    print(f"Предупреждение: не удалось импортировать некоторые компоненты: {e}")
    ClickHouseClient = None
    CASTINGS_SETTINGS = {}
    CASTING_PARSER_CONFIG = {}

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CastingsFolderReader:
    def __init__(self):
        """Инициализация клиента Telegram"""
        self.api_id = os.getenv('API_ID_TG')
        self.api_hash = os.getenv('API_HASH_TG')
        self.phone_number = os.getenv('PHONE_NUMBER')
        
        if not all([self.api_id, self.api_hash, self.phone_number]):
            raise ValueError("Необходимо установить API_ID_TG, API_HASH_TG и PHONE_NUMBER в .env файле")
        
        # Автоматически выбираем лучшую доступную сессию
        self.client = self._get_best_session()
        
        # Инициализация ClickHouse клиента
        self.clickhouse = None
        if ClickHouseClient:
            try:
                self.clickhouse = ClickHouseClient()
                logger.info("ClickHouse клиент инициализирован")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать ClickHouse: {e}")
        
        # Настройки из конфигурации
        self.settings = CASTINGS_SETTINGS or {}
        self.parser_config = CASTING_PARSER_CONFIG or {}
    
    def _get_best_session(self):
        """Выбор лучшей доступной сессии"""
        # Приоритет сессий (от лучших к худшим) - только уже авторизованные
        session_priorities = [
            'sessions/reader',                 # Читатель (пользователь)
            'sessions/group_auto_responder_reader',  # Групповой ответчик (пользователь)
            'sessions/simple_auto_responder_reader',  # Простой ответчик (пользователь)
            'sessions/group_auto_responder_bot',      # Бот сессии
            'sessions/bot',                    # Основной бот
            'sessions/simple_auto_responder_bot'      # Простой бот
        ]
        
        for session_path in session_priorities:
            if os.path.exists(f"{session_path}.session"):
                try:
                    # Проверяем, что сессия валидна
                    client = TelegramClient(
                        session_path,
                        int(self.api_id),
                        self.api_hash
                    )
                    logger.info(f"Найдена подходящая сессия: {session_path}")
                    return client
                except Exception as e:
                    logger.warning(f"Сессия {session_path} недоступна: {e}")
                    continue
        
        # Если не нашли подходящую сессию, используем reader как fallback
        logger.info("Используем сессию reader как fallback")
        return TelegramClient(
            'sessions/reader',
            int(self.api_id),
            self.api_hash
        )
        
    async def start(self):
        """Запуск клиента"""
        try:
            # Запускаем только с существующей сессией (без запроса авторизации)
            await self.client.start()
            logger.info("Клиент Telegram запущен с существующей сессией")
            
            # Проверяем, что мы авторизованы
            me = await self.client.get_me()
            logger.info(f"Авторизован как: {me.first_name} {me.last_name or ''} (@{me.username or 'Нет username'})")
            
        except Exception as e:
            logger.error(f"Не удалось запустить с существующей сессией: {e}")
            raise Exception(f"Не удалось подключиться к Telegram. Проверьте сессии: {e}")
        
    async def stop(self):
        """Остановка клиента"""
        await self.client.disconnect()
        logger.info("Клиент Telegram остановлен")
        
    async def get_castings_folder_channels(self) -> List[Dict[str, Any]]:
        """Получение каналов, содержащих 'кастинг' в названии (без учета регистра)"""
        channels_info = []
        
        try:
            logger.info("🔍 Поиск каналов с 'кастинг' в названии...")
            
            # Получаем все диалоги и ищем каналы с "кастинг" в названии
            async for dialog in self.client.iter_dialogs():
                if dialog.entity and hasattr(dialog.entity, 'title'):
                    title = dialog.entity.title.lower()
                    if 'кастинг' in title or 'casting' in title:
                        channel_info = await self._get_channel_info(dialog.entity)
                        if channel_info:
                            channels_info.append(channel_info)
                            logger.info(f"✅ Найден кастинговый канал: {dialog.entity.title}")
            
            logger.info(f"🎭 Найдено {len(channels_info)} кастинговых каналов")
            return channels_info
            
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске кастинговых каналов: {e}")
            return []
    
    async def _search_castings_channels(self) -> List[Dict[str, Any]]:
        """Поиск каналов по ключевым словам"""
        channels_info = []
        
        try:
            # Ключевые слова для кастингов
            casting_keywords = [
                'casting', 'кастинг', 'audition', 'просмотр', 'talent', 'модель',
                'актер', 'актриса', 'ведущий', 'танцор', 'певец', 'фотомодель',
                'реклама', 'съемка', 'фильм', 'сериал', 'шоу', 'концерт'
            ]
            
            logger.info(f"Поиск каналов по ключевым словам: {casting_keywords[:5]}...")
            
            # Получаем все диалоги и ищем подходящие каналы
            dialog_count = 0
            async for dialog in self.client.iter_dialogs():
                dialog_count += 1
                entity = dialog.entity
                
                # Проверяем, что это канал или группа
                if isinstance(entity, (Channel, Chat)):
                    # Проверяем название на наличие ключевых слов
                    title = getattr(entity, 'title', '')
                    username = getattr(entity, 'username', '')
                    description = getattr(entity, 'about', '')
                    
                    # Проверяем совпадение с ключевыми словами
                    text_to_check = f"{title} {username} {description}".lower()
                    
                    if any(keyword.lower() in text_to_check for keyword in casting_keywords):
                        logger.info(f"🎯 Найден подходящий канал: {title} (@{username})")
                        logger.info(f"   Участников: {getattr(entity, 'participants_count', 'Неизвестно')}")
                        channel_info = await self._get_channel_info(entity)
                        if channel_info:
                            channels_info.append(channel_info)
                            logger.info(f"   ✅ Добавлен в список каналов")
                        else:
                            logger.warning(f"   ⚠️ Не удалось получить информацию о канале")
                            
                # Логируем прогресс каждые 100 диалогов
                if dialog_count % 100 == 0:
                    logger.info(f"📊 Проверено {dialog_count} диалогов, найдено {len(channels_info)} каналов")
                            
                # Ограничиваем поиск для производительности
                if dialog_count > 1000:  # Проверяем максимум 1000 диалогов
                    logger.info("🛑 Достигнут лимит поиска (1000 диалогов)")
                    break
                    
            logger.info(f"🔍 Поиск завершен: проверено {dialog_count} диалогов, найдено {len(channels_info)} подходящих каналов")
                            
        except Exception as e:
            logger.error(f"Ошибка при поиске каналов: {e}")
            
        return channels_info
    
    async def _get_channel_info(self, entity) -> Dict[str, Any]:
        """Получение информации о канале"""
        try:
            info = {
                'id': entity.id,
                'title': getattr(entity, 'title', ''),
                'username': getattr(entity, 'username', ''),
                'type': 'channel' if isinstance(entity, Channel) else 'chat',
                'participants_count': getattr(entity, 'participants_count', 0),
                'description': getattr(entity, 'about', ''),
                'created_date': getattr(entity, 'date', None),
                'is_verified': getattr(entity, 'verified', False),
                'is_scam': getattr(entity, 'scam', False),
                'is_fake': getattr(entity, 'fake', False),
            }
            
            # Получаем последние сообщения для анализа
            try:
                messages = []
                async for message in self.client.iter_messages(entity, limit=5):
                    messages.append({
                        'id': message.id,
                        'date': message.date,
                        'text': message.text[:100] if message.text else '',
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0)
                    })
                info['recent_messages'] = messages
            except Exception as e:
                logger.warning(f"Не удалось получить сообщения из {info['title']}: {e}")
                info['recent_messages'] = []
                
            return info
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о канале: {e}")
            return None
    
    async def read_channel_messages(self, channel_info: Dict[str, Any], days_back: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """Чтение сообщений из конкретного канала"""
        try:
            logger.info(f"🔍 Начинаем чтение сообщений из канала: {channel_info['title']} (@{channel_info['username']})")
            logger.info(f"   ID: {channel_info['id']}, участников: {channel_info['participants_count']}")
            
            entity = await self.client.get_entity(channel_info['id'])
            logger.info(f"✅ Получен доступ к каналу: {entity.title}")
            
            messages = []
            offset_date = datetime.now() - timedelta(days=days_back)
            logger.info(f"📅 Ищем сообщения с {offset_date.strftime('%Y-%m-%d %H:%M')} (последние {days_back} дней)")
            logger.info(f"📊 Лимит сообщений: {limit}")
            
            message_count = 0
            async for message in self.client.iter_messages(
                entity,
                limit=limit,
                offset_date=offset_date
            ):
                message_count += 1
                logger.info(f"   📝 Сообщение {message_count}: ID {message.id}, дата: {message.date.strftime('%Y-%m-%d %H:%M')}")
                
                message_data = {
                    'message_id': message.id,
                    'channel_id': channel_info['id'],
                    'channel_title': channel_info['title'],
                    'channel_username': channel_info['username'],
                    'date': message.date,
                    'text': message.text or '',
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0),
                    'replies': getattr(message.replies, 'replies', 0) if hasattr(message, 'replies') and message.replies else 0,
                    'media_type': type(message.media).__name__ if message.media else None,
                    'has_photo': bool(message.photo),
                    'has_video': bool(message.video),
                    'has_document': bool(message.document),
                }
                messages.append(message_data)
                
                # Логируем первые несколько символов сообщения
                if message.text:
                    preview = message.text[:100].replace('\n', ' ')
                    logger.info(f"      Текст: {preview}...")
                else:
                    logger.info(f"      Медиа сообщение: {message_data['media_type']}")
                
                # Небольшая задержка для избежания лимитов
                await asyncio.sleep(0.1)
            
            logger.info(f"✅ Прочитано {len(messages)} сообщений из {channel_info['title']}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Ошибка при чтении сообщений из {channel_info['title']}: {e}")
            import traceback
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            return []
    
    async def read_all_castings_channels(self, days_back: int = 7, limit_per_channel: int = 100) -> Dict[str, Any]:
        """Чтение всех каналов из папки @castings"""
        logger.info("🚀 Начинаем чтение каналов из папки @castings...")
        logger.info(f"📅 Параметры: {days_back} дней назад, {limit_per_channel} сообщений на канал")
        
        # Получаем список каналов
        logger.info("🔍 Поиск каналов...")
        channels = await self.get_castings_folder_channels()
        
        if not channels:
            logger.warning("⚠️ Каналы в папке @castings не найдены")
            return {'channels': [], 'total_messages': 0, 'error': 'Каналы не найдены'}
        
        logger.info(f"✅ Найдено {len(channels)} каналов в папке @castings")
        
        all_messages = []
        channels_data = []
        
        for i, channel in enumerate(channels, 1):
            logger.info(f"\n📺 Канал {i}/{len(channels)}: {channel['title']} (@{channel['username']})")
            logger.info(f"   ID: {channel['id']}, участников: {channel['participants_count']}")
            
            # Читаем сообщения из канала
            messages = await self.read_channel_messages(channel, days_back, limit_per_channel)
            
            channel_data = {
                'channel_info': channel,
                'messages_count': len(messages),
                'messages': messages
            }
            
            channels_data.append(channel_data)
            all_messages.extend(messages)
            
            logger.info(f"📊 Итого по каналу: {len(messages)} сообщений")
            
            # Задержка между каналами
            if i < len(channels):
                logger.info("⏳ Пауза 2 секунды перед следующим каналом...")
                await asyncio.sleep(2)
        
        result = {
            'channels': channels_data,
            'total_channels': len(channels),
            'total_messages': len(all_messages),
            'read_date': datetime.now().isoformat(),
            'days_back': days_back,
            'limit_per_channel': limit_per_channel
        }
        
        logger.info(f"\n🎉 Чтение завершено!")
        logger.info(f"📊 Итоговая статистика:")
        logger.info(f"   - Каналов обработано: {len(channels)}")
        logger.info(f"   - Сообщений прочитано: {len(all_messages)}")
        logger.info(f"   - Среднее сообщений на канал: {len(all_messages) / len(channels) if channels else 0:.1f}")
        
        return result
    
    def parse_casting_message(self, message_text: str) -> Dict[str, Any]:
        """Парсинг кастингового сообщения для извлечения структурированных данных"""
        import re
        
        parsed_data = {
            'original_text': message_text,
            'casting_type': None,
            'age_range': None,
            'location': None,
            'contact_info': None,
            'deadline': None,
            'payment': None,
            'project_name': None,
            'requirements': []
        }
        
        if not self.parser_config.get('patterns'):
            return parsed_data
        
        patterns = self.parser_config['patterns']
        
        # Извлекаем возрастной диапазон
        if 'age_range' in patterns:
            age_match = re.search(patterns['age_range'], message_text, re.IGNORECASE)
            if age_match:
                parsed_data['age_range'] = age_match.group(1)
        
        # Извлекаем местоположение
        if 'location' in patterns:
            location_match = re.search(patterns['location'], message_text, re.IGNORECASE)
            if location_match:
                parsed_data['location'] = location_match.group(1)
        
        # Извлекаем контактную информацию
        if 'contact' in patterns:
            contact_match = re.search(patterns['contact'], message_text, re.IGNORECASE)
            if contact_match:
                parsed_data['contact_info'] = contact_match.group(2)
        
        # Извлекаем дедлайн
        if 'deadline' in patterns:
            deadline_match = re.search(patterns['deadline'], message_text, re.IGNORECASE)
            if deadline_match:
                parsed_data['deadline'] = deadline_match.group(2)
        
        # Извлекаем информацию об оплате
        if 'payment' in patterns:
            payment_match = re.search(patterns['payment'], message_text, re.IGNORECASE)
            if payment_match:
                parsed_data['payment'] = payment_match.group(2)
        
        # Определяем тип кастинга по ключевым словам
        casting_types = ['модель', 'актер', 'актриса', 'ведущий', 'танцор', 'певец', 'фотомодель']
        for casting_type in casting_types:
            if casting_type.lower() in message_text.lower():
                parsed_data['casting_type'] = casting_type
                break
        
        return parsed_data
    
    async def save_to_database(self, messages: List[Dict[str, Any]], channels_info: List[Dict[str, Any]] = None) -> bool:
        """Сохранение сообщений в ClickHouse"""
        if not self.clickhouse:
            logger.warning("⚠️ ClickHouse клиент не инициализирован, пропускаем сохранение")
            return False
            
        if not messages:
            logger.info("📝 Нет сообщений для сохранения")
            return True
        
        try:
            logger.info(f"💾 Начинаем сохранение {len(messages)} сообщений в ClickHouse...")
            
            # Подготавливаем данные для сохранения
            db_messages = []
            for i, msg in enumerate(messages, 1):
                logger.info(f"   🔄 Обрабатываем сообщение {i}/{len(messages)}: ID {msg['message_id']}")
                
                # Парсим сообщение
                parsed = self.parse_casting_message(msg['text'])
                
                # Логируем найденные данные
                if any(parsed[key] for key in ['casting_type', 'age_range', 'location', 'contact_info', 'deadline', 'payment']):
                    logger.info(f"      🎯 Найдены данные: {', '.join([f'{k}: {v}' for k, v in parsed.items() if v])}")
                
                db_message = {
                    'message_id': msg['message_id'],
                    'channel_id': msg['channel_id'],
                    'channel_title': msg['channel_title'],
                    'channel_username': msg['channel_username'] or '',
                    'date': msg['date'],
                    'text': msg['text'],
                    'views': msg['views'],
                    'forwards': msg['forwards'],
                    'replies': msg['replies'],
                    'media_type': msg['media_type'] or '',
                    'has_photo': msg['has_photo'],
                    'has_video': msg['has_video'],
                    'has_document': msg['has_document'],
                    # Парсированные поля
                    'casting_type': parsed['casting_type'] or '',
                    'age_range': parsed['age_range'] or '',
                    'location': parsed['location'] or '',
                    'contact_info': parsed['contact_info'] or '',
                    'deadline': parsed['deadline'] or '',
                    'payment': parsed['payment'] or '',
                    'project_name': parsed['project_name'] or '',
                    'parsed_at': datetime.now()
                }
                db_messages.append(db_message)
            
            # Сохраняем в ClickHouse
            logger.info(f"💾 Сохраняем {len(db_messages)} сообщений в ClickHouse...")
            self.clickhouse.insert_castings_messages(db_messages)
            logger.info(f"✅ Успешно сохранено {len(db_messages)} сообщений в ClickHouse")
            
            # Сохраняем информацию о каналах
            if channels_info:
                # Сохраняем все каналы в таблицу all_channels
                logger.info(f"💾 Сохраняем информацию о {len(channels_info)} каналах в таблицу all_channels...")
                self.clickhouse.insert_all_channels(channels_info)
                logger.info(f"✅ Успешно сохранена информация о {len(channels_info)} каналах в таблицу all_channels")
                
                # Фильтруем только каналы с "кастинг" в названии для channels_info
                castings_channels = []
                for channel in channels_info:
                    title = (channel.get('title') or '').lower()
                    if 'кастинг' in title or 'casting' in title:
                        castings_channels.append(channel)
                
                if castings_channels:
                    logger.info(f"💾 Сохраняем информацию о {len(castings_channels)} кастинговых каналах в таблицу channels_info...")
                    self.clickhouse.insert_channels_info(castings_channels)
                    logger.info(f"✅ Успешно сохранена информация о {len(castings_channels)} кастинговых каналах в таблицу channels_info")
                else:
                    logger.warning("⚠️ Не найдено кастинговых каналов для сохранения в channels_info")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении в базу данных: {e}")
            import traceback
            logger.error(f"Детали ошибки: {traceback.format_exc()}")
            return False
    
    def update_channels_config(self, channels: List[Dict[str, Any]]) -> bool:
        """Обновление конфигурационного файла с найденными каналами"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'castings_channels.py')
            
            # Читаем существующий конфиг
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ""
            
            # Создаем новую конфигурацию каналов
            channels_config = {}
            for channel in channels:
                channel_id = str(channel['id'])
                channels_config[channel_id] = {
                    'username': f"@{channel['username']}" if channel['username'] else None,
                    'title': channel['title'],
                    'enabled': True,
                    'parser_type': 'casting_parser',
                    'days_back': self.settings.get('default_days_back', 7),
                    'batch_size': self.settings.get('default_batch_size', 50),
                    'auto_update': True,
                    'participants_count': channel['participants_count'],
                    'description': channel['description'],
                    'is_verified': channel['is_verified'],
                    'discovered_at': datetime.now().isoformat()
                }
            
            # Обновляем конфигурацию
            new_content = f"""# Конфигурация для каналов из папки @castings
# Автоматически обновлено: {datetime.now().isoformat()}

CASTINGS_CHANNELS = {self._dict_to_python(channels_config, indent=4)}

# Настройки для чтения каналов из папки @castings
CASTINGS_SETTINGS = {self._dict_to_python(self.settings, indent=4)}

# Парсер для кастинговых сообщений
CASTING_PARSER_CONFIG = {self._dict_to_python(self.parser_config, indent=4)}
"""
            
            # Сохраняем обновленный конфиг
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Конфигурация обновлена: {len(channels)} каналов")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении конфигурации: {e}")
            return False
    
    def _dict_to_python(self, data, indent=0):
        """Преобразование словаря в Python код"""
        if isinstance(data, dict):
            items = []
            for key, value in data.items():
                key_str = f'"{key}"' if isinstance(key, str) else str(key)
                value_str = self._dict_to_python(value, indent + 4)
                items.append(f"{' ' * indent}{key_str}: {value_str}")
            return "{\n" + ",\n".join(items) + "\n" + " " * (indent - 4) + "}"
        elif isinstance(data, list):
            items = []
            for item in data:
                items.append(self._dict_to_python(item, indent + 4))
            return "[\n" + ",\n".join(f"{' ' * indent}{item}" for item in items) + "\n" + " " * (indent - 4) + "]"
        elif isinstance(data, str):
            return f'"{data}"'
        elif isinstance(data, bool):
            return "True" if data else "False"
        elif data is None:
            return "None"
        else:
            return str(data)

async def main():
    """Основная функция"""
    reader = CastingsFolderReader()
    
    try:
        await reader.start()
        
        # Читаем все каналы из папки @castings
        result = await reader.read_all_castings_channels(days_back=7, limit_per_channel=50)
        
        # Выводим результаты
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ЧТЕНИЯ КАНАЛОВ ИЗ ПАПКИ @CASTINGS")
        print("="*50)
        
        print(f"Всего каналов найдено: {result['total_channels']}")
        print(f"Всего сообщений прочитано: {result['total_messages']}")
        print(f"Дата чтения: {result['read_date']}")
        print(f"Период: {result['days_back']} дней назад")
        print(f"Лимит на канал: {result['limit_per_channel']} сообщений")
        
        print("\n" + "-"*50)
        print("ДЕТАЛИ ПО КАНАЛАМ:")
        print("-"*50)
        
        all_messages = []
        for i, channel_data in enumerate(result['channels'], 1):
            channel = channel_data['channel_info']
            print(f"\n{i}. {channel['title']}")
            print(f"   Username: @{channel['username']}")
            print(f"   ID: {channel['id']}")
            print(f"   Тип: {channel['type']}")
            print(f"   Участников: {channel['participants_count']}")
            print(f"   Сообщений прочитано: {channel_data['messages_count']}")
            print(f"   Описание: {channel['description'][:100]}...")
            
            if channel_data['messages']:
                print(f"   Последние сообщения:")
                for msg in channel_data['messages'][:3]:  # Показываем первые 3 сообщения
                    print(f"     - {msg['date'].strftime('%Y-%m-%d %H:%M')}: {msg['text'][:50]}...")
                
                # Собираем все сообщения для сохранения
                all_messages.extend(channel_data['messages'])
        
        # Сохраняем в базу данных
        if all_messages:
            print(f"\n💾 Сохранение {len(all_messages)} сообщений в базу данных...")
            # Собираем информацию о каналах
            channels_info = [channel_data['channel_info'] for channel_data in result['channels']]
            saved = await reader.save_to_database(all_messages, channels_info)
            if saved:
                print("✅ Сообщения успешно сохранены в ClickHouse")
            else:
                print("⚠️ Не удалось сохранить в базу данных")
        
        # Обновляем конфигурацию каналов
        if result['channels']:
            print(f"\n📝 Обновление конфигурации каналов...")
            channels_info = [ch['channel_info'] for ch in result['channels']]
            config_updated = reader.update_channels_config(channels_info)
            if config_updated:
                print("✅ Конфигурация каналов обновлена")
            else:
                print("⚠️ Не удалось обновить конфигурацию")
        
        # Сохраняем результаты в файл
        output_file = f"castings_channels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 Результаты сохранены в файл: {output_file}")
        
        # Показываем статистику парсинга
        if all_messages:
            print(f"\n📊 СТАТИСТИКА ПАРСИНГА:")
            print("-"*30)
            
            casting_types = {}
            locations = {}
            payments = {}
            
            for msg in all_messages:
                parsed = reader.parse_casting_message(msg['text'])
                
                if parsed['casting_type']:
                    casting_types[parsed['casting_type']] = casting_types.get(parsed['casting_type'], 0) + 1
                
                if parsed['location']:
                    locations[parsed['location']] = locations.get(parsed['location'], 0) + 1
                
                if parsed['payment']:
                    payments[parsed['payment']] = payments.get(parsed['payment'], 0) + 1
            
            if casting_types:
                print(f"Типы кастингов: {dict(list(casting_types.items())[:5])}")
            if locations:
                print(f"Местоположения: {dict(list(locations.items())[:5])}")
            if payments:
                print(f"Оплата: {dict(list(payments.items())[:5])}")
        
    except Exception as e:
        logger.error(f"Ошибка в основной функции: {e}")
        print(f"❌ Ошибка: {e}")
        
    finally:
        await reader.stop()

if __name__ == '__main__':
    asyncio.run(main())
