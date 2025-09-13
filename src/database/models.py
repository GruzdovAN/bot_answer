"""
Модели базы данных для Telegram бота
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Chat(Base):
    """Модель чата/канала/группы"""
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=True)
    chat_type = Column(String(50), nullable=False)  # 'channel', 'group', 'supergroup', 'private'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    messages = relationship("Message", back_populates="chat")
    bot_stats = relationship("BotStats", back_populates="chat")


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    messages = relationship("Message", back_populates="user")


class Message(Base):
    """Модель сообщения"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    text = Column(Text, nullable=True)
    message_type = Column(String(50), default='text')  # 'text', 'photo', 'document', etc.
    is_bot_response = Column(Boolean, default=False)
    
    # Метаданные
    raw_data = Column(JSON, nullable=True)  # Полные данные от Telegram API
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Связи
    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")
    responses = relationship("BotResponse", back_populates="original_message")


class BotResponse(Base):
    """Модель ответов бота"""
    __tablename__ = 'bot_responses'
    
    id = Column(Integer, primary_key=True)
    original_message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    response_text = Column(Text, nullable=False)
    response_type = Column(String(50), default='auto')  # 'auto', 'manual', 'smart'
    trigger_keyword = Column(String(255), nullable=True)
    response_time_ms = Column(Integer, nullable=True)  # Время ответа в миллисекундах
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    original_message = relationship("Message", back_populates="responses")


class BotStats(Base):
    """Модель статистики бота"""
    __tablename__ = 'bot_stats'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Статистика
    total_messages = Column(Integer, default=0)
    bot_responses = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    most_used_keywords = Column(JSON, nullable=True)
    response_time_avg = Column(Integer, nullable=True)  # Среднее время ответа в мс
    
    # Связи
    chat = relationship("Chat", back_populates="bot_stats")


class BotSession(Base):
    """Модель сессий бота"""
    __tablename__ = 'bot_sessions'
    
    id = Column(Integer, primary_key=True)
    bot_name = Column(String(100), nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Статистика сессии
    messages_processed = Column(Integer, default=0)
    responses_sent = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Связи
    chat = relationship("Chat")
