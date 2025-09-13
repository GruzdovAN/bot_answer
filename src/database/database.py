"""
Модуль для работы с базой данных PostgreSQL
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Chat, User, Message, BotResponse, BotStats, BotSession
from ..config.logging_config import get_logger

logger = get_logger("database")


class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, database_url: str = None):
        """
        Инициализация менеджера базы данных
        
        Args:
            database_url: URL подключения к базе данных
        """
        self.database_url = database_url or self._get_database_url()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _get_database_url(self) -> str:
        """Получает URL базы данных из переменных окружения"""
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'telegram_bot')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    def _initialize_database(self):
        """Инициализирует подключение к базе данных"""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Установите True для отладки SQL запросов
                pool_pre_ping=True,
                pool_recycle=300
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("Подключение к базе данных инициализировано")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def create_tables(self):
        """Создает все таблицы в базе данных"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Таблицы базы данных созданы успешно")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            raise
    
    def get_session(self) -> Session:
        """Возвращает сессию базы данных"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Закрывает сессию базы данных"""
        session.close()
    
    # Методы для работы с чатами
    def get_or_create_chat(self, session: Session, telegram_id: int, username: str = None, 
                          title: str = None, chat_type: str = 'channel') -> Chat:
        """Получает или создает чат"""
        chat = session.query(Chat).filter(Chat.telegram_id == telegram_id).first()
        if not chat:
            chat = Chat(
                telegram_id=telegram_id,
                username=username,
                title=title,
                chat_type=chat_type
            )
            session.add(chat)
            session.commit()
            logger.info(f"Создан новый чат: {title or username}")
        return chat
    
    # Методы для работы с пользователями
    def get_or_create_user(self, session: Session, telegram_id: int, username: str = None,
                          first_name: str = None, last_name: str = None, is_bot: bool = False) -> User:
        """Получает или создает пользователя"""
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_bot=is_bot
            )
            session.add(user)
            session.commit()
            logger.info(f"Создан новый пользователь: {first_name or username}")
        return user
    
    # Методы для работы с сообщениями
    def save_message(self, session: Session, telegram_id: int, chat_id: int, 
                    user_id: int = None, text: str = None, message_type: str = 'text',
                    is_bot_response: bool = False, raw_data: Dict = None) -> Message:
        """Сохраняет сообщение в базу данных"""
        try:
            message = Message(
                telegram_id=telegram_id,
                chat_id=chat_id,
                user_id=user_id,
                text=text,
                message_type=message_type,
                is_bot_response=is_bot_response,
                raw_data=raw_data
            )
            session.add(message)
            session.commit()
            logger.debug(f"Сообщение сохранено: {telegram_id}")
            return message
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка сохранения сообщения: {e}")
            raise
    
    def save_bot_response(self, session: Session, original_message_id: int, response_text: str,
                         response_type: str = 'auto', trigger_keyword: str = None,
                         response_time_ms: int = None, is_successful: bool = True,
                         error_message: str = None) -> BotResponse:
        """Сохраняет ответ бота"""
        try:
            response = BotResponse(
                original_message_id=original_message_id,
                response_text=response_text,
                response_type=response_type,
                trigger_keyword=trigger_keyword,
                response_time_ms=response_time_ms,
                is_successful=is_successful,
                error_message=error_message
            )
            session.add(response)
            session.commit()
            logger.debug(f"Ответ бота сохранен: {response_text[:50]}...")
            return response
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка сохранения ответа бота: {e}")
            raise
    
    # Методы для статистики
    def get_chat_stats(self, session: Session, chat_id: int, days: int = 7) -> Dict[str, Any]:
        """Получает статистику чата за указанный период"""
        try:
            # Общее количество сообщений
            total_messages = session.query(Message).filter(
                Message.chat_id == chat_id,
                Message.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            # Количество ответов бота
            bot_responses = session.query(BotResponse).join(Message).filter(
                Message.chat_id == chat_id,
                BotResponse.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            # Уникальные пользователи
            unique_users = session.query(User).join(Message).filter(
                Message.chat_id == chat_id,
                Message.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).distinct().count()
            
            return {
                'total_messages': total_messages,
                'bot_responses': bot_responses,
                'unique_users': unique_users,
                'response_rate': (bot_responses / total_messages * 100) if total_messages > 0 else 0
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def get_recent_messages(self, session: Session, chat_id: int, limit: int = 10) -> List[Message]:
        """Получает последние сообщения чата"""
        try:
            return session.query(Message).filter(
                Message.chat_id == chat_id
            ).order_by(Message.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return []
    
    def health_check(self) -> bool:
        """Проверяет состояние базы данных"""
        try:
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка проверки состояния БД: {e}")
            return False


# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()
