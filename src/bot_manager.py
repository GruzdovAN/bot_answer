"""
Менеджер для управления различными типами ботов
"""
import asyncio
from typing import Dict, Type
from .bots import BaseBot, SmartResponder, SimpleResponder, GroupResponder
from .config.logging_config import get_logger

logger = get_logger("bot_manager")


class BotManager:
    """Менеджер для управления бота"""
    
    def __init__(self):
        self.bots: Dict[str, Type[BaseBot]] = {
            'smart': SmartResponder,
            'simple': SimpleResponder,
            'group': GroupResponder
        }
        self.current_bot: BaseBot = None
    
    def list_available_bots(self):
        """Выводит список доступных ботов"""
        logger.info("Доступные типы ботов:")
        for i, (key, bot_class) in enumerate(self.bots.items(), 1):
            logger.info(f"{i}. {bot_class.__name__} ({key})")
    
    def get_bot_by_choice(self, choice: str) -> BaseBot:
        """
        Возвращает бота по выбору пользователя
        
        Args:
            choice: Выбор пользователя ('smart', 'simple' или номер)
            
        Returns:
            BaseBot: Экземпляр выбранного бота
        """
        if choice in self.bots:
            return self.bots[choice]()
        
        # Попытка парсинга номера
        try:
            choice_num = int(choice)
            bot_keys = list(self.bots.keys())
            if 1 <= choice_num <= len(bot_keys):
                bot_key = bot_keys[choice_num - 1]
                return self.bots[bot_key]()
        except ValueError:
            pass
        
        # По умолчанию возвращаем простой бот
        logger.warning("Неверный выбор, запускаем простой автоответчик")
        return self.bots['simple']()
    
    async def run_bot(self, bot_type: str = 'simple'):
        """
        Запускает бота указанного типа
        
        Args:
            bot_type: Тип бота ('smart', 'simple' или 'group')
        """
        self.current_bot = self.get_bot_by_choice(bot_type)
        await self.current_bot.start_monitoring()
    
    async def stop_current_bot(self):
        """Останавливает текущего бота"""
        if self.current_bot:
            await self.current_bot.stop()
            self.current_bot = None


# Глобальный экземпляр менеджера
bot_manager = BotManager()
