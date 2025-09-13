#!/usr/bin/env python3
"""
Тестовый скрипт для проверки режима ответов от имени пользователя
"""
import os
import sys
sys.path.append('src')

from src.config.settings import config
from src.config.logging_config import get_logger

logger = get_logger("test_user_mode")

def test_config():
    """Тестирует конфигурацию режима пользователя"""
    print("=== Тест конфигурации режима ответов ===")
    print(f"USE_USER_ACCOUNT: {config.USE_USER_ACCOUNT}")
    print(f"Режим работы: {'От имени пользователя' if config.USE_USER_ACCOUNT else 'От имени бота'}")
    
    if config.USE_USER_ACCOUNT:
        print("✅ Режим пользователя активен")
        print("   - Ответы будут отправляться от вашего имени")
        print("   - Токен бота не требуется")
    else:
        print("✅ Режим бота активен")
        print("   - Ответы будут отправляться от имени бота")
        print("   - Требуется токен бота")
    
    print(f"API_ID: {config.API_ID}")
    print(f"API_HASH: {config.API_HASH[:10]}...")
    print(f"PHONE_NUMBER: {config.PHONE_NUMBER}")
    print(f"CHANNEL_USERNAME: {config.CHANNEL_USERNAME}")
    
    if not config.USE_USER_ACCOUNT:
        print(f"BOT_TOKEN: {config.BOT_TOKEN[:10]}...")
    
    print("\n=== Проверка переменных окружения ===")
    env_vars = {
        'API_ID_TG': os.getenv('API_ID_TG'),
        'API_HASH_TG': os.getenv('API_HASH_TG'),
        'PHONE_NUMBER': os.getenv('PHONE_NUMBER'),
        'CHANNEL_USERNAME': os.getenv('CHANNEL_USERNAME'),
        'USE_USER_ACCOUNT': os.getenv('USE_USER_ACCOUNT'),
        'BOT_TOKEN': os.getenv('BOT_TOKEN')
    }
    
    for var, value in env_vars.items():
        if value:
            if 'TOKEN' in var or 'HASH' in var:
                print(f"✅ {var}: {value[:10]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            if var == 'BOT_TOKEN' and config.USE_USER_ACCOUNT:
                print(f"ℹ️  {var}: не требуется в режиме пользователя")
            else:
                print(f"❌ {var}: не задана")

if __name__ == "__main__":
    test_config()
