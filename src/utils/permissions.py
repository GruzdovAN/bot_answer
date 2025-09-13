"""
Модуль для проверки прав бота в чатах
"""
from telethon import TelegramClient
from ..config.logging_config import get_logger

logger = get_logger("permissions")


async def check_bot_permissions(bot_client: TelegramClient, chat_username: str) -> bool:
    """
    Проверяет права бота в указанном чате
    
    Args:
        bot_client: Клиент Telegram бота
        chat_username: Имя чата/канала/группы
        
    Returns:
        bool: True если бот может отправлять сообщения, False иначе
    """
    try:
        # Получаем информацию о чате
        chat = await bot_client.get_entity(chat_username)
        logger.info(f"Чат найден: {chat.title if hasattr(chat, 'title') else chat_username}")
        
        # Проверяем, может ли бот отправлять сообщения
        try:
            await bot_client.send_message(chat_username, "🔍 Проверка прав бота...")
            logger.info("Бот может отправлять сообщения в чат")
            return True
        except Exception as e:
            if "You can't write in this chat" in str(e):
                logger.error("Бот не может отправлять сообщения в чат")
                logger.error("Необходимо:")
                logger.error("   1. Добавить бота в канал/группу как администратора")
                logger.error("   2. Дать боту права на отправку сообщений")
                return False
            else:
                logger.error(f"Ошибка при проверке прав: {e}")
                return False
    except Exception as e:
        logger.error(f"Ошибка при получении информации о чате: {e}")
        logger.error("Проверьте правильность имени канала/группы")
        return False


def format_error_message(error: Exception, chat_username: str) -> str:
    """
    Форматирует сообщение об ошибке для пользователя
    
    Args:
        error: Исключение
        chat_username: Имя чата
        
    Returns:
        str: Отформатированное сообщение об ошибке
    """
    error_msg = str(error)
    
    if "You can't write in this chat" in error_msg:
        return f"""❌ Ошибка: Бот не может писать в чат '{chat_username}'
🔧 Решения:
   1. Добавьте бота в канал/группу как администратора
   2. Дайте боту права на отправку сообщений
   3. Проверьте правильность имени канала/группы
   4. Убедитесь, что бот не заблокирован в чате"""
    
    elif "Chat not found" in error_msg:
        return f"""❌ Ошибка: Чат '{chat_username}' не найден
🔧 Проверьте правильность имени канала/группы"""
    
    else:
        return f"❌ Ошибка отправки: {error_msg}"
