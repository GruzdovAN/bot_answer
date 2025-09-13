"""
Модуль конфигурации для Telegram бота
"""
import os
from dotenv import load_dotenv
from .logging_config import get_logger

logger = get_logger("config")


class Config:
    """Класс для управления конфигурацией бота"""
    
    def __init__(self, env_path=".env"):
        """Инициализация конфигурации"""
        self.env_path = env_path
        self._load_environment()
        self._validate_config()
    
    def _load_environment(self):
        """Загружает переменные окружения из файла .env"""
        load_dotenv(self.env_path)
        
        # API данные Telegram
        self.API_ID = os.getenv('API_ID_TG')
        self.API_HASH = os.getenv('API_HASH_TG')
        
        # Данные для авторизации
        self.PHONE_NUMBER = os.getenv('PHONE_NUMBER')
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        
        # Настройки чата
        self.CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
        
        # Настройка режима ответов (bot/user)
        self.USE_USER_ACCOUNT = os.getenv('USE_USER_ACCOUNT', 'false').lower() in ['true', '1', 'yes']
    
    def _validate_config(self):
        """Проверяет, что все необходимые переменные заданы"""
        required_vars = {
            'API_ID_TG': self.API_ID,
            'API_HASH_TG': self.API_HASH,
            'PHONE_NUMBER': self.PHONE_NUMBER,
            'CHANNEL_USERNAME': self.CHANNEL_USERNAME
        }
        
        # BOT_TOKEN обязателен только если не используется пользовательский аккаунт
        if not self.USE_USER_ACCOUNT:
            required_vars['BOT_TOKEN'] = self.BOT_TOKEN
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            logger.error(f"Не заданы следующие переменные окружения: {', '.join(missing_vars)}")
            logger.error("Убедитесь, что файл .env содержит все необходимые переменные:")
            for var in missing_vars:
                logger.error(f"   {var}=ваше_значение")
            exit(1)
        
        # Логируем режим работы
        if self.USE_USER_ACCOUNT:
            logger.info("Режим работы: ответы от имени пользователя")
        else:
            logger.info("Режим работы: ответы от имени бота")
        
        logger.info("Конфигурация загружена успешно")
    
    def get_telegram_config(self):
        """Возвращает конфигурацию для Telegram клиента"""
        return {
            'api_id': self.API_ID,
            'api_hash': self.API_HASH,
            'phone': self.PHONE_NUMBER,
            'bot_token': self.BOT_TOKEN,
            'channel': self.CHANNEL_USERNAME
        }
    
    def __str__(self):
        """Строковое представление конфигурации (без чувствительных данных)"""
        return f"Config(channel={self.CHANNEL_USERNAME}, phone={self.PHONE_NUMBER[:3]}***)"


# Глобальный экземпляр конфигурации
config = Config()
